from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.v1.dependencies.auth import get_current_active_user
from app.db.mongo import get_db
from app.schemas.analytics import DataFetchQuery, DataLoadRequest, EvaluateRequest, IndicatorsRequest, PredictRequest, SentimentRequest
from app.schemas.market import CandleOut, CandleQuery
from app.services import evaluation_service
from app.services.backtest_service import BacktestService
from app.services.market_data_service import MarketDataService
from app.services.sentiment_service import SentimentService
from app.services.signal_engine import SignalEngine
from indicators import ta

router = APIRouter()


@router.post("/data", response_model=list[CandleOut])
async def load_data(payload: DataLoadRequest, db=Depends(get_db), user=Depends(get_current_active_user)):
    """Bulk insert candle data."""
    service = MarketDataService(db)
    candles = []
    for c in payload.candles:
        candles.append(await service.add_candle(c))
    return candles


@router.get("/data", response_model=list[CandleOut])
async def fetch_data(symbol: str, start: str | None = None, end: str | None = None, timeframe: str | None = None, db=Depends(get_db), user=Depends(get_current_active_user)):
    query = DataFetchQuery(
        symbol=symbol,
        start=datetime.fromisoformat(start) if start else None,
        end=datetime.fromisoformat(end) if end else None,
        timeframe=timeframe,
    )
    service = MarketDataService(db)
    return await service.get_candles(symbol, query=CandleQuery(start=query.start, end=query.end, timeframe=query.timeframe))


@router.post("/predict")
async def predict(payload: PredictRequest, db=Depends(get_db), user=Depends(get_current_active_user)):
    engine = SignalEngine(db)
    return await engine.generate_from_data(
        symbol=payload.symbol,
        closes=payload.closes,
        highs=payload.highs,
        lows=payload.lows,
        sentiments=payload.sentiments,
        strategy_id=payload.strategy_id,
        timestamp=payload.timestamp,
        algorithm_version=payload.algorithm_version,
    )


@router.post("/backtest")
async def backtest(payload: EvaluateRequest, db=Depends(get_db), user=Depends(get_current_active_user)):
    curve = evaluation_service.equity_curve(payload.trades, payload.initial_capital)
    summary = {
        "total_return": evaluation_service.total_return(curve),
        "win_ratio": evaluation_service.win_ratio(payload.trades),
        "max_drawdown": evaluation_service.max_drawdown(curve),
        "max_drawdown_duration": evaluation_service.max_drawdown_duration(curve),
        "profit_factor": evaluation_service.profit_factor(payload.trades),
        "sharpe_ratio": evaluation_service.sharpe_ratio(payload.trades),
        "sortino_ratio": evaluation_service.sortino_ratio(payload.trades),
        "expectancy": evaluation_service.expectancy(payload.trades),
        "cagr": evaluation_service.cagr(curve, payload.years),
        "risk_of_ruin": evaluation_service.risk_of_ruin(payload.trades, payload.initial_capital),
    }
    doc = {
        "strategy_id": payload.strategy_id or "ad-hoc",
        "symbols": ["SYMBOL"],
        "tested_timeframe": {"start": datetime.utcnow(), "end": datetime.utcnow()},
        "initial_capital": payload.initial_capital,
        "trades": payload.trades,
        "summary": summary,
        "conservative_score": evaluation_service.conservative_score(
            summary["max_drawdown"], summary["sharpe_ratio"], summary["win_ratio"]
        ),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    await BacktestService(db).collection.insert_one(doc)
    return doc


@router.post("/evaluate")
async def evaluate(payload: EvaluateRequest):
    curve = evaluation_service.equity_curve(payload.trades, payload.initial_capital)
    metrics = {
        "win_ratio": evaluation_service.win_ratio(payload.trades),
        "max_drawdown": evaluation_service.max_drawdown(curve),
        "max_drawdown_duration": evaluation_service.max_drawdown_duration(curve),
        "sharpe_ratio": evaluation_service.sharpe_ratio(payload.trades),
        "profit_factor": evaluation_service.profit_factor(payload.trades),
        "expectancy": evaluation_service.expectancy(payload.trades),
        "cagr": evaluation_service.cagr(curve, payload.years),
        "risk_of_ruin": evaluation_service.risk_of_ruin(payload.trades, payload.initial_capital),
        "conservative_score": evaluation_service.conservative_score(
            evaluation_service.max_drawdown(curve), evaluation_service.volatility(curve), evaluation_service.win_ratio(payload.trades)
        ),
    }
    return metrics


@router.post("/sentiment")
async def sentiment(payload: SentimentRequest, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = SentimentService(db)
    return await service.analyze_text(payload.text)


@router.post("/indicators")
async def indicators(payload: IndicatorsRequest):
    highs = payload.highs or payload.closes
    lows = payload.lows or payload.closes
    close = payload.closes
    macd_line, macd_signal_line, macd_hist = ta.macd(close)
    bb_upper, bb_middle, bb_lower, bb_width = ta.bollinger_bands(close)
    return {
        "rsi": ta.rsi(close),
        "macd": macd_line,
        "macd_signal": macd_signal_line,
        "macd_hist": macd_hist,
        "ema_20": ta.ema(close, 20),
        "ema_50": ta.ema(close, 50),
        "sma_20": ta.sma(close, 20),
        "sma_50": ta.sma(close, 50),
        "sma_200": ta.sma(close, 200),
        "atr": ta.atr(highs, lows, close),
        "bb_upper": bb_upper,
        "bb_middle": bb_middle,
        "bb_lower": bb_lower,
        "bb_width": bb_width,
        "volatility": ta.volatility(close),
        "returns_1d": ta.returns(close),
    }
