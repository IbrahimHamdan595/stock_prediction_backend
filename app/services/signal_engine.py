"""
Rule-based signal engine combining trend, momentum, volatility, price action, and sentiment inputs.
This is a simple example that can be expanded with ML/AI models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from app.schemas.strategy import SignalOut
from indicators import ta


class SignalEngine:
    def __init__(self, db):
        self.db = db
        self.collection = db.signals

    async def generate_from_data(
        self,
        symbol: str,
        closes: List[float],
        highs: List[float],
        lows: List[float],
        sentiments: Optional[Dict[str, float]],
        strategy_id: str,
        timestamp: datetime,
        algorithm_version: str = "v1-rule",
    ) -> List[SignalOut]:
        """Generate a mock-but-structured signal using a rule blend."""
        ema_20 = ta.ema(closes, 20)
        ema_50 = ta.ema(closes, 50)
        rsi_val = ta.rsi(closes, 14)
        macd_line, macd_signal_line, _ = ta.macd(closes)
        atr_val = ta.atr(highs, lows, closes, 14)
        bb_upper, bb_middle, bb_lower, _ = ta.bollinger_bands(closes)
        sentiment_score = (sentiments or {}).get("score", 0.0)

        side = "hold"
        reasoning_parts = []
        if closes and closes[-1] > ema_50 and rsi_val < 30 and sentiment_score > 0:
            side = "buy"
            reasoning_parts.append("uptrend with oversold + positive sentiment")
        elif closes and closes[-1] < ema_50 and rsi_val > 70 and sentiment_score < 0:
            side = "sell"
            reasoning_parts.append("downtrend with overbought + negative sentiment")
        else:
            reasoning_parts.append("no strong confluence")

        entry_price = closes[-1] if closes else 0
        stop_loss = entry_price - 1.5 * atr_val if side == "buy" else entry_price + 1.5 * atr_val
        take_profit = entry_price + 2 * atr_val if side == "buy" else entry_price - 2 * atr_val
        confidence = max(0.1, min(0.9, 0.5 + 0.2 * sentiment_score))

        doc = {
            "symbol": symbol,
            "timestamp": timestamp,
            "side": side,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "confidence_score": confidence,
            "strategy_id": strategy_id,
            "reasoning": "; ".join(reasoning_parts),
            "indicator_snapshot": {
                "ema_20": ema_20,
                "ema_50": ema_50,
                "rsi": rsi_val,
                "macd": macd_line,
                "macd_signal": macd_signal_line,
                "bb_upper": bb_upper,
                "bb_lower": bb_lower,
            },
            "sentiment_snapshot": sentiments or {},
            "algorithm_version": algorithm_version,
            "metadata": {"source": "rule-engine"},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await self.collection.insert_one(doc)
        return [SignalOut(**doc, _id=str(doc.get("_id", timestamp.timestamp())))]
