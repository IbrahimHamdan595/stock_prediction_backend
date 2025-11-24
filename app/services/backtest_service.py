from datetime import datetime
from typing import List

from app.schemas.strategy import BacktestOut, BacktestRunRequest
from app.services import evaluation_service as evals


class BacktestService:
    def __init__(self, db):
        self.collection = db.backtests

    async def run_backtest(self, payload: BacktestRunRequest) -> BacktestOut:
        trades = self._mock_trades(payload)
        curve = evals.equity_curve(trades, payload.initial_capital)
        summary = {
            "total_return": evals.total_return(curve),
            "win_ratio": evals.win_ratio(trades),
            "max_drawdown": evals.max_drawdown(curve),
            "max_drawdown_duration": evals.max_drawdown_duration(curve),
            "profit_factor": evals.profit_factor(trades),
            "sharpe_ratio": evals.sharpe_ratio(trades),
            "sortino_ratio": evals.sortino_ratio(trades),
            "expectancy": evals.expectancy(trades),
            "cagr": evals.cagr(curve, years=1),  # caller can adjust timeframe later
            "risk_of_ruin": evals.risk_of_ruin(trades, payload.initial_capital),
        }
        score = evals.conservative_score(summary["max_drawdown"], summary["sharpe_ratio"], summary["win_ratio"])
        doc = {
            "strategy_id": payload.strategy_id,
            "symbols": payload.symbols,
            "tested_timeframe": {"start": payload.start_date, "end": payload.end_date},
            "initial_capital": payload.initial_capital,
            "trades": trades,
            "summary": summary,
            "conservative_score": score,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await self.collection.insert_one(doc)
        doc["_id"] = str(doc.get("_id", payload.strategy_id + "-bt"))
        return BacktestOut(**doc)

    async def get_backtest(self, backtest_id: str) -> BacktestOut:
        doc = await self.collection.find_one({"_id": backtest_id})
        if not doc:
            raise ValueError("Backtest not found")
        return BacktestOut(**doc)

    async def get_backtests_for_strategy(self, strategy_id: str) -> List[BacktestOut]:
        return [BacktestOut(**doc) async for doc in self.collection.find({"strategy_id": strategy_id}).sort("created_at", -1)]

    async def compare_strategies(self, strategy_ids: List[str]):
        results = []
        for sid in strategy_ids:
            doc = await self.collection.find_one({"strategy_id": sid}, sort=[("created_at", -1)])
            if doc:
                results.append({"strategy_id": sid, **doc.get("summary", {}), "conservative_score": doc.get("conservative_score")})
        return {"strategies": results}

    def _mock_trades(self, payload: BacktestRunRequest):
        # Simple mock trades that alternate PnL to demonstrate metrics.
        base = 1 + (payload.initial_capital % 5) / 10
        return [
            {
                "entry_timestamp": payload.start_date,
                "exit_timestamp": payload.end_date,
                "entry_price": 100,
                "exit_price": 102,
                "quantity": base,
                "side": "long",
                "realized_pnl": 2 * base,
            },
            {
                "entry_timestamp": payload.start_date,
                "exit_timestamp": payload.end_date,
                "entry_price": 102,
                "exit_price": 100,
                "quantity": base,
                "side": "long",
                "realized_pnl": -2 * base,
            },
            {
                "entry_timestamp": payload.start_date,
                "exit_timestamp": payload.end_date,
                "entry_price": 100,
                "exit_price": 103,
                "quantity": base,
                "side": "long",
                "realized_pnl": 3 * base,
            },
        ]
