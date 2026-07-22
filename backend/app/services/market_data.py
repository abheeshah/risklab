"""Market data via yfinance with Diskcache."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Callable

import pandas as pd
import yfinance as yf

from app.core.cache import cache_get, cache_set
from app.core.config import get_settings


class MarketDataError(Exception):
    """Raised when market data cannot be retrieved or is invalid."""


Downloader = Callable[..., pd.DataFrame]


def _default_download(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    data = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
        threads=True,
        group_by="column",
    )
    if data is None or data.empty:
        raise MarketDataError(f"No price data returned for {tickers}")
    if isinstance(data.columns, pd.MultiIndex):
        if "Adj Close" in data.columns.get_level_values(0):
            prices = data["Adj Close"].copy()
        else:
            prices = data["Close"].copy()
    else:
        # Single ticker
        col = "Adj Close" if "Adj Close" in data.columns else "Close"
        prices = data[[col]].copy()
        prices.columns = [tickers[0]]
    prices = prices.dropna(how="all")
    return prices


def lookback_window(years: int) -> tuple[str, str]:
    end = date.today()
    start = end - timedelta(days=int(years * 365.25) + 7)
    return start.isoformat(), end.isoformat()


def fetch_prices(
    tickers: list[str],
    start: str,
    end: str,
    download: Downloader | None = None,
) -> pd.DataFrame:
    if not tickers:
        raise MarketDataError("At least one ticker is required")
    normalized = [t.strip().upper() for t in tickers]
    key = f"prices:{','.join(sorted(normalized))}:{start}:{end}"
    cached = cache_get(key)
    if cached is not None:
        return cached

    dl = download or _default_download
    prices = dl(normalized, start, end)
    # Ensure columns match requested tickers where possible
    missing = [t for t in normalized if t not in prices.columns]
    if missing:
        raise MarketDataError(f"Unknown or delisted tickers: {', '.join(missing)}")
    prices = prices[normalized].dropna(how="any")
    if prices.empty or len(prices) < 30:
        raise MarketDataError("Insufficient historical price data for analysis")
    cache_set(key, prices)
    return prices


def fetch_risk_free_rate(
    override: float | None = None,
    download: Downloader | None = None,
) -> tuple[float, str]:
    if override is not None:
        return float(override), "request"

    settings = get_settings()
    key = "tnx:latest"
    cached = cache_get(key)
    if cached is not None:
        return float(cached), "tnx"

    try:
        start, end = lookback_window(1)
        dl = download or _default_download
        prices = dl([settings.tnx_ticker], start, end)
        col = settings.tnx_ticker if settings.tnx_ticker in prices.columns else prices.columns[0]
        latest = float(prices[col].dropna().iloc[-1])
        # ^TNX is quoted as percent yield (e.g. 4.25)
        rate = latest / 100.0 if latest > 1.0 else latest
        if rate <= 0 or rate > 0.5:
            raise MarketDataError("Invalid TNX yield")
        cache_set(key, rate)
        return rate, "tnx"
    except Exception:
        return settings.risk_free_fallback, "fallback"
