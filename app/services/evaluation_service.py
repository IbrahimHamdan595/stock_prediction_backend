from __future__ import annotations

from math import sqrt
from typing import Iterable, List, Sequence


def equity_curve(trades: Sequence[dict], initial_capital: float) -> List[float]:
    balance = initial_capital
    curve = [balance]
    for trade in trades:
        balance += trade.get("realized_pnl", 0.0)
        curve.append(balance)
    return curve


def max_drawdown(curve: Iterable[float]) -> float:
    peak = float("-inf")
    max_dd = 0.0
    for value in curve:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak if peak else 0
        if drawdown > max_dd:
            max_dd = drawdown
    return max_dd


def win_ratio(trades: Sequence[dict]) -> float:
    if not trades:
        return 0.0
    wins = sum(1 for t in trades if t.get("realized_pnl", 0) > 0)
    return wins / len(trades)


def profit_factor(trades: Sequence[dict]) -> float:
    gross_profit = sum(t.get("realized_pnl", 0) for t in trades if t.get("realized_pnl", 0) > 0)
    gross_loss = -sum(t.get("realized_pnl", 0) for t in trades if t.get("realized_pnl", 0) < 0)
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def volatility(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return variance ** 0.5


def total_return(curve: Sequence[float]) -> float:
    if not curve:
        return 0.0
    return (curve[-1] - curve[0]) / curve[0]


def sharpe_ratio(trades: Sequence[dict], risk_free_rate: float = 0.0) -> float:
    if not trades:
        return 0.0
    returns = [t.get("realized_pnl", 0) for t in trades]
    mean_ret = sum(returns) / len(returns)
    variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
    std_dev = variance ** 0.5
    if std_dev == 0:
        return 0.0
    return (mean_ret - risk_free_rate) / std_dev


def conservative_score(drawdown: float, volatility: float, win_rate: float) -> float:
    stability = max(0.0, 1 - volatility)
    return max(0.0, 1 - drawdown) * 0.6 + stability * 0.2 + win_rate * 0.2


def max_drawdown_duration(curve: Sequence[float]) -> int:
    peak = curve[0] if curve else 0
    duration = 0
    max_duration = 0
    for value in curve:
        if value >= peak:
            peak = value
            duration = 0
        else:
            duration += 1
            max_duration = max(max_duration, duration)
    return max_duration


def sortino_ratio(trades: Sequence[dict], target_return: float = 0.0) -> float:
    if not trades:
        return 0.0
    returns = [t.get("realized_pnl", 0) for t in trades]
    downside = [min(0, r - target_return) for r in returns]
    downside_std = sqrt(sum(d ** 2 for d in downside) / len(downside))
    if downside_std == 0:
        return 0.0
    avg = sum(returns) / len(returns)
    return (avg - target_return) / downside_std


def expectancy(trades: Sequence[dict]) -> float:
    if not trades:
        return 0.0
    win_rate = win_ratio(trades)
    avg_win = sum(t.get("realized_pnl", 0) for t in trades if t.get("realized_pnl", 0) > 0) / max(
        1, sum(1 for t in trades if t.get("realized_pnl", 0) > 0)
    )
    avg_loss = -sum(t.get("realized_pnl", 0) for t in trades if t.get("realized_pnl", 0) < 0) / max(
        1, sum(1 for t in trades if t.get("realized_pnl", 0) < 0)
    )
    return win_rate * avg_win - (1 - win_rate) * avg_loss


def cagr(curve: Sequence[float], years: float) -> float:
    if not curve or years <= 0:
        return 0.0
    return (curve[-1] / curve[0]) ** (1 / years) - 1


def risk_of_ruin(trades: Sequence[dict], capital: float) -> float:
    if capital <= 0 or not trades:
        return 1.0
    losses = [abs(t.get("realized_pnl", 0)) for t in trades if t.get("realized_pnl", 0) < 0]
    avg_loss = sum(losses) / len(losses) if losses else 0
    if avg_loss == 0:
        return 0.0
    steps_to_ruin = capital / avg_loss
    return max(0.0, 1 / (steps_to_ruin + 1))
