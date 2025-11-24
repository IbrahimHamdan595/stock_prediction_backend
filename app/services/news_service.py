from datetime import datetime

from app.schemas.market import NewsIn, NewsOut


class NewsService:
    def __init__(self, db):
        self.collection = db.news

    async def add_news(self, payload: NewsIn) -> NewsOut:
        doc = payload.model_dump()
        doc["created_at"] = datetime.utcnow()
        doc["updated_at"] = datetime.utcnow()
        await self.collection.insert_one(doc)
        return NewsOut(**doc, _id=str(doc.get("_id", doc["timestamp"])))

    async def get_news(self, symbol: str, sentiment_label: str | None = None):
        filters = {"symbols": symbol}
        if sentiment_label:
            filters["sentiment_label"] = sentiment_label
        results = [NewsOut(**doc) async for doc in self.collection.find(filters).sort("timestamp", -1)]
        return results
