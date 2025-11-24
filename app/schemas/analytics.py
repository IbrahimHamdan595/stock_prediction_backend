from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DataLoadRequest(BaseModel):
    candles: List[Dict]


class DataFetchQuery(BaseModel):
    symbol: str
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    timeframe: Optional[str] = None


class PredictRequest(BaseModel):
    symbol: str
    strategy_id: str
    closes: List[float]
    highs: List[float]
    lows: List[float]
    sentiments: Optional[Dict[str, float]] = None
    timestamp: datetime
    algorithm_version: str = "v1-rule"


class EvaluateRequest(BaseModel):
    initial_capital: float
    trades: List[Dict]
    years: float = 1.0
    strategy_id: str | None = None


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=3)


class IndicatorsRequest(BaseModel):
    closes: List[float]
    highs: Optional[List[float]] = None
    lows: Optional[List[float]] = None
