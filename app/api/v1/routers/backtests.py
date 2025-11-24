from fastapi import APIRouter, Depends

from app.api.v1.dependencies.auth import get_current_active_user
from app.db.mongo import get_db
from app.schemas.strategy import BacktestOut, BacktestRunRequest, StrategyComparison
from app.services.backtest_service import BacktestService

router = APIRouter()


@router.post("/run", response_model=BacktestOut)
async def run_backtest(payload: BacktestRunRequest, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = BacktestService(db)
    return await service.run_backtest(payload)


@router.get("/{backtest_id}", response_model=BacktestOut)
async def get_backtest(backtest_id: str, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = BacktestService(db)
    return await service.get_backtest(backtest_id)


@router.get("/strategy/{strategy_id}", response_model=list[BacktestOut])
async def get_backtests_for_strategy(strategy_id: str, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = BacktestService(db)
    return await service.get_backtests_for_strategy(strategy_id)


@router.get("/compare", response_model=dict)
async def compare_strategies(strategy_ids: str, db=Depends(get_db), user=Depends(get_current_active_user)):
    ids = strategy_ids.split(",")
    service = BacktestService(db)
    return await service.compare_strategies(ids)
