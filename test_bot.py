import pytest
from bot import strategy

@pytest.mark.asyncio
async def test_strategy_logic():
    prices = [1.1000 + i * 0.0001 for i in range(50)]
    result = await strategy(prices)
    assert result in ("CALL","PUT",None)
