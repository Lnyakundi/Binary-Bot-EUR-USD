import os, asyncio, json
from datetime import datetime
from deriv_api import DerivAPI
import numpy as np, pandas as pd
import ta
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("DERIV_TOKEN")
APP_ID = int(os.getenv("DERIV_APP_ID", 1089))
SYMBOL = "frxEURUSD"
AMOUNT = 10
DURATION = 30
INTERVAL = 600

app = FastAPI()
trades_log = []

@app.get("/status")
async def status():
    return {"balance": getattr(app, "balance", None), "last_trades": trades_log[-5:]}

@app.websocket("/ws")
async def ws_dashboard(ws: WebSocket):
    await ws.accept()
    while True:
        await ws.send_json({"balance": app.balance, "recent": trades_log[-5:]})
        await asyncio.sleep(5)

async def strategy(prices):
    df = pd.DataFrame({"close": prices})
    df["ema5"] = ta.trend.EMAIndicator(df["close"], 5).ema_indicator()
    df["ema10"] = ta.trend.EMAIndicator(df["close"], 10).ema_indicator()
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], 14).rsi()
    last = df.iloc[-1]
    if last.ema5 > last.ema10 and last.rsi < 70: return "CALL"
    if last.ema5 < last.ema10 and last.rsi > 30: return "PUT"
    return None

async def bot_loop():
    api = DerivAPI(endpoint="wss://ws.derivws.com/websockets/v3", app_id=APP_ID)
    await api.connect()
    await api.authorize(API_TOKEN)
    app.balance = None

    async def update_balance():
        resp = await api.get_account_balance()
        app.balance = resp.get("balance")

    prices = []
    while True:
        tick = await api.ticks(SYMBOL)
        prices.append(tick["tick"]["quote"])
        if len(prices) > 50:
            prices.pop(0)
        if len(prices) >= 50 and (datetime.utcnow().minute * 60 + datetime.utcnow().second) % INTERVAL < DURATION:
            direction = await strategy(prices)
            if direction:
                resp = await api.buy(
                    symbol=SYMBOL, contract_type=direction, duration=DURATION, duration_unit="s",
                    amount=AMOUNT, basis="stake", currency="USD"
                )
                trades_log.append({"time": datetime.utcnow().isoformat(), **resp["buy"]})
                await update_balance()
        await asyncio.sleep(0.5)

@app.on_event("startup")
async def start_bot():
    asyncio.create_task(bot_loop())
