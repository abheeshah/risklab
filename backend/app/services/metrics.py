"""Risk metric calculations (pure functions, no network)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

TRADING_DAYS = 252


def portfolio_log_returns(prices: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """Weighted portfolio daily log returns from Adj Close prices."""
    log_rets = np.log(prices / prices.shift(1)).dropna()
    w = np.asarray(weights, dtype=float)
    port = log_rets.values @ w
    return pd.Series(port, index=log_rets.index, name="portfolio")


def annualized_volatility(returns: pd.Series) -> float:
    return float(returns.std(ddof=1) * np.sqrt(TRADING_DAYS))


def annualized_return(returns: pd.Series) -> float:
    if len(returns) == 0:
        return 0.0
    total = float(np.exp(returns.sum()) - 1.0)
    years = len(returns) / TRADING_DAYS
    if years <= 0:
        return 0.0
    return float((1.0 + total) ** (1.0 / years) - 1.0)


def sharpe_ratio(returns: pd.Series, risk_free_rate: float) -> float:
    vol = annualized_volatility(returns)
    if vol == 0 or np.isnan(vol):
        return 0.0
    excess = annualized_return(returns) - risk_free_rate
    return float(excess / vol)


def sortino_ratio(returns: pd.Series, risk_free_rate: float) -> float:
    downside = returns[returns < 0]
    if len(downside) < 2:
        return 0.0
    downside_vol = float(downside.std(ddof=1) * np.sqrt(TRADING_DAYS))
    if downside_vol == 0 or np.isnan(downside_vol):
        return 0.0
    excess = annualized_return(returns) - risk_free_rate
    return float(excess / downside_vol)


def max_drawdown(returns: pd.Series) -> float:
    wealth = np.exp(returns.cumsum())
    peak = wealth.cummax()
    dd = (wealth - peak) / peak
    return float(dd.min())


def herfindahl_hirschman_index(weights: np.ndarray) -> float:
    w = np.asarray(weights, dtype=float)
    return float(np.sum(w**2))


def beta(portfolio_returns: pd.Series, market_returns: pd.Series) -> float:
    aligned = pd.concat([portfolio_returns, market_returns], axis=1, join="inner").dropna()
    if len(aligned) < 2:
        return 0.0
    cov = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1], ddof=1)
    var_m = cov[1, 1]
    if var_m == 0:
        return 0.0
    return float(cov[0, 1] / var_m)


def correlation_matrix(prices: pd.DataFrame) -> tuple[list[str], list[list[float]]]:
    log_rets = np.log(prices / prices.shift(1)).dropna()
    corr = log_rets.corr()
    tickers = list(corr.columns.astype(str))
    matrix = corr.values.tolist()
    return tickers, [[float(x) for x in row] for row in matrix]


def historical_var(returns: pd.Series, alpha: float, horizon_days: int = 1) -> float:
    """Return VaR as a positive loss fraction (of portfolio value)."""
    if horizon_days == 1:
        series = returns
    else:
        series = returns.rolling(horizon_days).sum().dropna()
    if len(series) == 0:
        return 0.0
    q = float(np.quantile(series, 1.0 - alpha))
    return float(max(-q, 0.0))


def parametric_var(returns: pd.Series, alpha: float, horizon_days: int = 1) -> float:
    mu = float(returns.mean())
    sigma = float(returns.std(ddof=1))
    if np.isnan(sigma) or sigma == 0:
        return 0.0
    z = float(stats.norm.ppf(1.0 - alpha))
    # Loss fraction for horizon: -(mu*h + z*sigma*sqrt(h))
    h = horizon_days
    q = mu * h + z * sigma * np.sqrt(h)
    return float(max(-q, 0.0))


def cvar(returns: pd.Series, alpha: float, horizon_days: int = 1) -> float:
    if horizon_days == 1:
        series = returns
    else:
        series = returns.rolling(horizon_days).sum().dropna()
    if len(series) == 0:
        return 0.0
    threshold = float(np.quantile(series, 1.0 - alpha))
    tail = series[series <= threshold]
    if len(tail) == 0:
        return 0.0
    return float(max(-tail.mean(), 0.0))


def cumulative_wealth(returns: pd.Series) -> pd.Series:
    return np.exp(returns.cumsum())
