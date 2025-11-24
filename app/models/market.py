from datetime import datetime
from typing import Dict, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.models.base import MongoModel


class TechnicalIndicators(BaseModel):
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

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class SupportResistance(BaseModel):
    pivot_points: Optional[Dict[str, float]] = None
    horizontal_levels: Optional[list[float]] = None
    swing_highs: Optional[list[float]] = None
    swing_lows: Optional[list[float]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class MarketCandle(MongoModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str = Field(default="1d")
    indicators: Optional[TechnicalIndicators] = None
    support_resistance: Optional[SupportResistance] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class NewsItem(MongoModel):
    symbols: list[str]
    timestamp: datetime
    headline: str
    body: str
    source: Optional[str] = None
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"
    weighted_sentiment_index: Optional[float] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
