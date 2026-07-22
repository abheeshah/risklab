"""API integration tests with mocked market data."""

from __future__ import annotations

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.services import market_data


client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in {"ok", "degraded"}
    assert "cache_ok" in body


def test_analyze_validation_weights():
    resp = client.post(
        "/api/v1/analyze",
        json={
            "holdings": [{"ticker": "AAPL", "weight": 0.5}],
            "total_value": 10000,
            "lookback_years": 1,
        },
    )
    assert resp.status_code == 422


def test_analyze_success(monkeypatch, synthetic_prices):
    def fake_fetch(tickers, start, end, download=None):
        cols = []
        for t in tickers:
            if t in synthetic_prices.columns:
                cols.append(t)
            elif t == "AAPL":
                cols.append("AAA")
            elif t == "MSFT":
                cols.append("BBB")
            else:
                cols.append("^GSPC")
        # Build frame with requested column names
        data = {}
        for req_t, src in zip(tickers, cols):
            data[req_t] = synthetic_prices[src].values
        return pd.DataFrame(data, index=synthetic_prices.index)

    def fake_rf(override=None, download=None):
        if override is not None:
            return override, "request"
        return 0.045, "fallback"

    monkeypatch.setattr(market_data, "fetch_prices", fake_fetch)
    monkeypatch.setattr("app.services.analyze.fetch_prices", fake_fetch)
    monkeypatch.setattr("app.services.analyze.fetch_risk_free_rate", fake_rf)
    monkeypatch.setattr("app.services.benchmarks.fetch_prices", fake_fetch)
    monkeypatch.setattr("app.services.benchmarks.fetch_risk_free_rate", fake_rf)
    monkeypatch.setattr(
        "app.services.analyze.get_benchmark_stats",
        lambda sector, years: {
            "sector": sector,
            "ticker": "XLK",
            "annualized_return": 0.1,
            "volatility": 0.2,
            "sharpe": 0.5,
            "lookback_years": years,
            "explanation": "x",
        },
    )

    resp = client.post(
        "/api/v1/analyze",
        json={
            "holdings": [
                {"ticker": "AAPL", "weight": 0.4},
                {"ticker": "MSFT", "weight": 0.6},
            ],
            "total_value": 100000,
            "lookback_years": 1,
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "health" in body
    assert 0 <= body["health"]["score"] <= 100
    assert body["volatility"]["explanation"]
    assert len(body["allocation"]) == 2
    assert len(body["cumulative_returns"]) > 0


def test_benchmark_unknown_sector():
    resp = client.get("/api/v1/benchmarks/notasector")
    assert resp.status_code == 400
