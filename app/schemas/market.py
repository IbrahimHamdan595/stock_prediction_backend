from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TechnicalIndicatorsIn(BaseModel):
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    atr: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_width: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    volatility: Optional[float] = None
    returns_1d: Optional[float] = None


class SupportResistanceIn(BaseModel):
    pivot_points: Optional[Dict[str, float]] = None
    horizontal_levels: Optional[list[float]] = None
    swing_highs: Optional[list[float]] = None
    swing_lows: Optional[list[float]] = None


class CandleIn(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str = "1d"
    indicators: Optional[TechnicalIndicatorsIn] = None
    support_resistance: Optional[SupportResistanceIn] = None


class CandleQuery(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    timeframe: Optional[str] = None


class CandleOut(CandleIn):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}


class NewsIn(BaseModel):
    symbols: List[str]
    timestamp: datetime
    headline: str
    body: str
    source: Optional[str] = None
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"
    weighted_sentiment_index: Optional[float] = None


class NewsOut(NewsIn):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}
