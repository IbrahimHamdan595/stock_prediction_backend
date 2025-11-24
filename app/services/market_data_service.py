from datetime import datetime

from app.schemas.market import CandleIn, CandleOut, CandleQuery


class MarketDataService:
    def __init__(self, db):
        self.collection = db.market_data

    async def add_candle(self, payload: CandleIn | dict) -> CandleOut:
        data = payload if isinstance(payload, dict) else payload.model_dump()
        doc = {**data, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
        await self.collection.insert_one(doc)
        return CandleOut(**doc, _id=str(doc.get("_id", doc["timestamp"])))

    async def get_candles(self, symbol: str, query: CandleQuery):
        filters: dict = {"symbol": symbol}
        if query.timeframe:
            filters["timeframe"] = query.timeframe
        if query.start:
            filters["timestamp"] = filters.get("timestamp", {})
            filters["timestamp"]["$gte"] = query.start
        if query.end:
            filters["timestamp"] = filters.get("timestamp", {})
            filters["timestamp"]["$lte"] = query.end

        results = []
        async for doc in self.collection.find(filters).sort("timestamp", 1):
            results.append(CandleOut(**doc))
        return results
