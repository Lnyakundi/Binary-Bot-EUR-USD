# Deriv Bot Project

## 🔧 Features
- Auto trades EUR/USD every 10 minutes on a 30s window
- EMA + RSI indicator logic
- Dockerized FastAPI backend
- Android app with Flutter dashboard
- CI/CD for APK + test runs

## 🚀 How to Run

### Python Bot
1. Set your `.env` file:
```
DERIV_TOKEN=your_api_token
DERIV_APP_ID=1089
```

2. Build Docker:
```
docker build -t deriv-bot docker/
docker run --env-file docker/.env -p 8000:8000 deriv-bot
```

### Flutter App
- Replace `YOUR_SERVER` in `main.dart` with your local IP or domain
- Run:
```
flutter build apk --release
```

### CI/CD
- Push to GitHub main branch
- APK downloadable under Actions → deriv-bot-app
