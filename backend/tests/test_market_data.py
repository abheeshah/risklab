"""Tests for market data caching and risk-free rate."""

from __future__ import annotations

import pandas as pd
import pytest

from app.core.cache import cache_get
from app.services.market_data import MarketDataError, fetch_prices, fetch_risk_free_rate


def test_fetch_prices_caches(synthetic_prices):
    calls = {"n": 0}

    def fake_download(tickers, start, end):
        calls["n"] += 1
        return synthetic_prices[tickers]

    p1 = fetch_prices(["AAA", "BBB"], "2023-01-01", "2024-01-01", download=fake_download)
    p2 = fetch_prices(["AAA", "BBB"], "2023-01-01", "2024-01-01", download=fake_download)
    assert calls["n"] == 1
    assert list(p1.columns) == ["AAA", "BBB"]
    assert p2.equals(p1)
    assert cache_get("prices:AAA,BBB:2023-01-01:2024-01-01") is not None


def test_fetch_prices_missing_ticker(synthetic_prices):
    def fake_download(tickers, start, end):
        return synthetic_prices[["AAA"]]

    with pytest.raises(MarketDataError, match="Unknown"):
        fetch_prices(["AAA", "MISSING"], "2023-01-01", "2024-01-01", download=fake_download)


def test_risk_free_override():
    rate, source = fetch_risk_free_rate(override=0.03)
    assert rate == 0.03
    assert source == "request"


def test_risk_free_tnx_and_fallback():
    def fake_tnx(tickers, start, end):
        idx = pd.bdate_range("2023-01-01", periods=50)
        return pd.DataFrame({"^TNX": [4.25] * 50}, index=idx)

    rate, source = fetch_risk_free_rate(download=fake_tnx)
    assert abs(rate - 0.0425) < 1e-9
    assert source == "tnx"

    def boom(tickers, start, end):
        raise RuntimeError("network")

    # Clear cache so fallback path runs
    from app.core.cache import get_cache

    get_cache().clear()
    rate2, source2 = fetch_risk_free_rate(download=boom)
    assert rate2 == 0.045
    assert source2 == "fallback"
