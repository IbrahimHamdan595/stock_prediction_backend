from app.services import evaluation_service as evals


def test_max_drawdown_detects_peak_to_trough():
    curve = [100, 120, 80, 90, 150, 120]
    dd = evals.max_drawdown(curve)
    assert round(dd, 2) == 0.33  # 120 -> 80 = 33%


def test_profit_factor_and_win_ratio():
    trades = [{"realized_pnl": 10}, {"realized_pnl": -5}, {"realized_pnl": 5}]
    assert evals.win_ratio(trades) == 2 / 3
    assert evals.profit_factor(trades) == 3.0


def test_conservative_score_prefers_low_drawdown():
    low_dd = evals.conservative_score(drawdown=0.05, volatility=0.2, win_rate=0.5)
    high_dd = evals.conservative_score(drawdown=0.4, volatility=0.2, win_rate=0.5)
    assert low_dd > high_dd


def test_drawdown_duration_and_sortino():
    curve = [100, 95, 90, 92, 105]
    assert evals.max_drawdown_duration(curve) == 3
    trades = [{"realized_pnl": 5}, {"realized_pnl": -2}, {"realized_pnl": 3}]
    assert evals.sortino_ratio(trades) != 0
