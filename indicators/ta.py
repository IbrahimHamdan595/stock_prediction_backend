"""
Technical analysis utilities for computing common indicators without external deps.
These functions operate on raw price arrays and return floats for the latest value.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple


def _ema(values: Sequence[float], period: int) -> float:
    if not values or period <= 0:
        return 0.0
    k = 2 / (period + 1)
    ema_val = values[0]
    for price in values[1:]:
        ema_val = price * k + ema_val * (1 - k)
    return ema_val


def sma(values: Sequence[float], period: int) -> float:
    if len(values) < period or period <= 0:
        return 0.0
    return sum(values[-period:]) / period


def ema(values: Sequence[float], period: int) -> float:
    return _ema(values[-(period * 2) :] if len(values) > period * 2 else values, period)


def rsi(values: Sequence[float], period: int = 14) -> float:
    if len(values) < period + 1:
        return 0.0
    gains = []
    losses = []
    for i in range(1, period + 1):
        delta = values[-i] - values[-i - 1]
        if delta >= 0:
            gains.append(delta)
        else:
            losses.append(-delta)
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period if losses else 0.0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(values: Sequence[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
    if len(values) < slow:
        return 0.0, 0.0, 0.0
    macd_line = ema(values, fast) - ema(values, slow)
    signal_line = ema([macd_line] * signal, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int = 14) -> float:
    trs: List[float] = []
    for i in range(1, min(len(highs), len(lows), len(closes))):
        tr = max(
            highs[-i] - lows[-i],
            abs(highs[-i] - closes[-i - 1]),
            abs(lows[-i] - closes[-i - 1]),
        )
        trs.append(tr)
    if len(trs) < period:
        return 0.0
    return sum(trs[-period:]) / period


def bollinger_bands(values: Sequence[float], period: int = 20, std_mult: float = 2.0) -> Tuple[float, float, float, float]:
    if len(values) < period:
        return 0.0, 0.0, 0.0, 0.0
    window = values[-period:]
    mean = sum(window) / period
    variance = sum((v - mean) ** 2 for v in window) / period
    std_dev = variance ** 0.5
    upper = mean + std_mult * std_dev
    lower = mean - std_mult * std_dev
    width = upper - lower
    return upper, mean, lower, width


def volatility(values: Sequence[float], period: int = 20) -> float:
    if len(values) < period:
        return 0.0
    window = values[-period:]
    mean = sum(window) / period
    variance = sum((v - mean) ** 2 for v in window) / period
    return variance ** 0.5


def returns(values: Sequence[float], period: int = 1) -> float:
    if len(values) <= period:
        return 0.0
    return (values[-1] - values[-period - 1]) / values[-period - 1]
