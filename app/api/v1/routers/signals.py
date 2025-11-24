from fastapi import APIRouter, Depends

from app.api.v1.dependencies.auth import get_current_active_user
from app.db.mongo import get_db
from app.schemas.strategy import SignalIn, SignalOut
from app.services.signal_service import SignalService

router = APIRouter()


@router.post("/generate", response_model=list[SignalOut])
async def generate_signals(payload: SignalIn, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = SignalService(db)
    return await service.generate(payload)


@router.get("/{symbol}", response_model=list[SignalOut])
async def signals_by_symbol(symbol: str, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = SignalService(db)
    return await service.list_by_symbol(symbol)


@router.get("/strategy/{strategy_id}", response_model=list[SignalOut])
async def signals_by_strategy(strategy_id: str, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = SignalService(db)
    return await service.list_by_strategy(strategy_id)
