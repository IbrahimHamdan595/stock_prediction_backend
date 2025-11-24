from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.v1.dependencies.auth import get_current_active_user
from app.db.mongo import get_db
from app.schemas.market import CandleIn, CandleOut, CandleQuery
from app.services.market_data_service import MarketDataService

router = APIRouter()


@router.post("/", response_model=CandleOut)
async def ingest_candle(payload: CandleIn, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = MarketDataService(db)
    return await service.add_candle(payload)


@router.get("/{symbol}", response_model=list[CandleOut])
async def get_candles(symbol: str, start: str | None = None, end: str | None = None, timeframe: str | None = None, db=Depends(get_db), user=Depends(get_current_active_user)):
    query = CandleQuery(
        start=datetime.fromisoformat(start) if start else None,
        end=datetime.fromisoformat(end) if end else None,
        timeframe=timeframe,
    )
    service = MarketDataService(db)
    return await service.get_candles(symbol, query)


@router.get("/{symbol}/indicators", response_model=list[CandleOut])
async def get_candles_with_indicators(symbol: str, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = MarketDataService(db)
    return await service.get_candles(symbol, CandleQuery())
