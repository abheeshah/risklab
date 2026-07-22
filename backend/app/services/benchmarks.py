"""Sector ETF benchmark stats with caching."""

from __future__ import annotations

from typing import Any

import numpy as np

from app.core.cache import cache_get, cache_set
from app.services import explanations, metrics
from app.services.market_data import MarketDataError, fetch_prices, fetch_risk_free_rate, lookback_window

SECTOR_ETFS: dict[str, str] = {
    "tech": "XLK",
    "healthcare": "XLV",
    "energy": "XLE",
    "financials": "XLF",
    "consumer": "XLY",
}


def list_sectors() -> list[str]:
    return list(SECTOR_ETFS.keys())


def get_benchmark_stats(sector: str, lookback_years: int = 2) -> dict[str, Any]:
    sector_key = sector.lower().strip()
    if sector_key not in SECTOR_ETFS:
        raise MarketDataError(
            f"Unknown sector '{sector}'. Valid: {', '.join(SECTOR_ETFS)}"
        )
    ticker = SECTOR_ETFS[sector_key]
    cache_key = f"benchmark:{sector_key}:{lookback_years}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    start, end = lookback_window(lookback_years)
    prices = fetch_prices([ticker], start, end)
    rets = metrics.portfolio_log_returns(prices, np.array([1.0]))
    rf, _ = fetch_risk_free_rate()
    result = {
        "sector": sector_key,
        "ticker": ticker,
        "annualized_return": metrics.annualized_return(rets),
        "volatility": metrics.annualized_volatility(rets),
        "sharpe": metrics.sharpe_ratio(rets, rf),
        "lookback_years": lookback_years,
        "explanation": explanations.BENCHMARK,
    }
    cache_set(cache_key, result)
    return result
