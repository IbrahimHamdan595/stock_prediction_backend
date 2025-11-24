from datetime import datetime
from typing import Optional

from app.schemas.strategy import StrategyCreate, StrategyOut, StrategyUpdate


class StrategyService:
    def __init__(self, db):
        self.collection = db.strategies

    async def create_strategy(self, payload: StrategyCreate, created_by: str) -> StrategyOut:
        doc = payload.model_dump()
        doc["created_by"] = created_by
        doc["created_at"] = datetime.utcnow()
        doc["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(doc.get("_id", result.inserted_id))
        return StrategyOut(**doc)

    async def get_strategy(self, strategy_id: str) -> Optional[StrategyOut]:
        doc = await self.collection.find_one({"_id": strategy_id})
        return StrategyOut(**doc) if doc else None

    async def list_strategies(self):
        return [StrategyOut(**doc) async for doc in self.collection.find().sort("created_at", -1)]

    async def update_strategy(self, strategy_id: str, payload: StrategyUpdate) -> Optional[StrategyOut]:
        updates = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
        if not updates:
            return await self.get_strategy(strategy_id)
        updates["updated_at"] = datetime.utcnow()
        doc = await self.collection.find_one_and_update({"_id": strategy_id}, {"$set": updates}, return_document=True)
        return StrategyOut(**doc) if doc else None

    async def delete_strategy(self, strategy_id: str):
        await self.collection.delete_one({"_id": strategy_id})
