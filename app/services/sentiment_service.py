"""Sentiment analysis service placeholder (FinBERT-ready)."""

from __future__ import annotations

from typing import Dict


class SentimentService:
    def __init__(self, db):
        self.collection = db.news

    async def analyze_text(self, text: str) -> Dict[str, float]:
        # Placeholder: in production, call FinBERT or external model
        score = 0.1 if "good" in text.lower() else -0.1 if "bad" in text.lower() else 0.0
        return {"score": score, "positive": max(score, 0), "negative": -min(score, 0), "label": "positive" if score > 0 else "negative" if score < 0 else "neutral"}

    async def store_with_sentiment(self, doc: Dict):
        await self.collection.insert_one(doc)
