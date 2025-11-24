from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies.auth import get_current_active_user
from app.db.mongo import get_db
from app.schemas.strategy import StrategyCreate, StrategyOut, StrategyUpdate
from app.services.strategy_service import StrategyService

router = APIRouter()


@router.post("/", response_model=StrategyOut, status_code=status.HTTP_201_CREATED)
async def create_strategy(payload: StrategyCreate, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = StrategyService(db)
    return await service.create_strategy(payload, created_by=user.id or user.email)


@router.get("/", response_model=list[StrategyOut])
async def list_strategies(db=Depends(get_db), user=Depends(get_current_active_user)):
    service = StrategyService(db)
    return await service.list_strategies()


@router.get("/{strategy_id}", response_model=StrategyOut)
async def get_strategy(strategy_id: str, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = StrategyService(db)
    strategy = await service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.patch("/{strategy_id}", response_model=StrategyOut)
async def update_strategy(strategy_id: str, payload: StrategyUpdate, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = StrategyService(db)
    updated = await service.update_strategy(strategy_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return updated


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(strategy_id: str, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = StrategyService(db)
    await service.delete_strategy(strategy_id)
    return None
