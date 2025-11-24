from datetime import datetime
from typing import List

from app.schemas.strategy import SignalIn, SignalOut


class SignalService:
    def __init__(self, db):
        self.collection = db.signals

    async def generate(self, payload: SignalIn) -> List[SignalOut]:
        # Mock logic: simple buy signal capturing provided snapshots for explainability
        close_price = 100.0
        signal = {
            "symbol": payload.symbol,
            "timestamp": payload.timestamp,
            "side": "buy",
            "entry_price": close_price,
            "stop_loss": close_price * 0.98,
            "take_profit": close_price * 1.04,
            "confidence_score": 0.6,
            "strategy_id": payload.strategy_id,
            "reasoning": "RSI oversold with positive sentiment weight",
            "indicator_snapshot": payload.indicator_snapshot or {},
            "sentiment_snapshot": payload.sentiment_snapshot or {},
            "algorithm_version": payload.algorithm_version or "v1-mock",
            "metadata": {"timeframe": payload.timeframe, "note": "mock signal"},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await self.collection.insert_one(signal)
        return [SignalOut(**signal, _id=str(signal.get("_id", payload.timestamp.timestamp())))]

    async def list_by_symbol(self, symbol: str) -> List[SignalOut]:
        return [SignalOut(**doc) async for doc in self.collection.find({"symbol": symbol}).sort("timestamp", -1)]

    async def list_by_strategy(self, strategy_id: str) -> List[SignalOut]:
        return [SignalOut(**doc) async for doc in self.collection.find({"strategy_id": strategy_id}).sort("timestamp", -1)]
