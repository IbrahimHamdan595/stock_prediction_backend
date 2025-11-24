from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = {}
    risk_profile: str = "conservative"


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    risk_profile: Optional[str] = None


class StrategyOut(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: Optional[str]
    parameters: Dict[str, Any]
    risk_profile: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}


class SignalIn(BaseModel):
    symbol: str
    strategy_id: str
    timestamp: datetime
    timeframe: str = "1d"
    indicator_snapshot: Optional[Dict[str, Any]] = None
    sentiment_snapshot: Optional[Dict[str, Any]] = None
    algorithm_version: Optional[str] = None


class SignalOut(BaseModel):
    id: str = Field(alias="_id")
    symbol: str
    timestamp: datetime
    side: str
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence_score: float
    strategy_id: str
    reasoning: Optional[str] = None
    indicator_snapshot: Dict[str, Any]
    sentiment_snapshot: Dict[str, Any]
    algorithm_version: Optional[str] = None
    metadata: Dict[str, Any]

    model_config = {"populate_by_name": True}


class BacktestRunRequest(BaseModel):
    strategy_id: str
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10000
    slippage: float = 0.0
    fee_rate: float = 0.0


class TradeOut(BaseModel):
    entry_timestamp: datetime
    exit_timestamp: datetime
    entry_price: float
    exit_price: float
    quantity: float
    side: str
    realized_pnl: float


class BacktestOut(BaseModel):
    id: str = Field(alias="_id")
    strategy_id: str
    symbols: List[str]
    tested_timeframe: Dict[str, datetime]
    initial_capital: float
    trades: List[TradeOut]
    summary: Dict[str, float]
    conservative_score: float

    model_config = {"populate_by_name": True}


class StrategyComparison(BaseModel):
    strategy_ids: List[str]
    timeframe: Dict[str, datetime]
