"""Thin wrapper to expose evaluation metrics with clarity."""

from app.services import evaluation_service

win_ratio = evaluation_service.win_ratio
max_drawdown = evaluation_service.max_drawdown
max_drawdown_duration = evaluation_service.max_drawdown_duration
sharpe_ratio = evaluation_service.sharpe_ratio
profit_factor = evaluation_service.profit_factor
expectancy = evaluation_service.expectancy
cagr = evaluation_service.cagr
risk_of_ruin = evaluation_service.risk_of_ruin
conservative_score = evaluation_service.conservative_score
sortino_ratio = evaluation_service.sortino_ratio
volatility = evaluation_service.volatility
