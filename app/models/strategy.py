from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pydantic import ConfigDict, Field

from app.models.base import MongoModel


class Strategy(MongoModel):
    strategy_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_profile: str = "conservative"
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class Signal(MongoModel):
    signal_id: Optional[str] = None
    symbol: str
    timestamp: datetime
    side: str
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence_score: float
    strategy_id: str
    reasoning: Optional[str] = None
    indicator_snapshot: Dict[str, Any] = Field(default_factory=dict)
    sentiment_snapshot: Dict[str, Any] = Field(default_factory=dict)
    algorithm_version: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class Trade(MongoModel):
    trade_id: Optional[str] = None
    entry_timestamp: datetime
    exit_timestamp: datetime
    entry_price: float
    exit_price: float
    quantity: float
    side: str
    realized_pnl: float
    max_favorable_excursion: Optional[float] = None
    max_adverse_excursion: Optional[float] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class Backtest(MongoModel):
    backtest_id: Optional[str] = None
    strategy_id: str
    symbols: List[str]
    tested_timeframe: Dict[str, datetime]
    initial_capital: float
    trades: List[Trade] = Field(default_factory=list)
    summary: Dict[str, float] = Field(default_factory=dict)
    conservative_score: Optional[float] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
