"""Tests for risk metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.services import metrics


def test_hhi_equal_weight():
    w = np.array([0.25, 0.25, 0.25, 0.25])
    assert abs(metrics.herfindahl_hirschman_index(w) - 0.25) < 1e-9


def test_hhi_concentrated():
    w = np.array([1.0, 0.0])
    assert abs(metrics.herfindahl_hirschman_index(w) - 1.0) < 1e-9


def test_annualized_volatility_known():
    # Constant daily returns → ~zero vol (float noise)
    r = pd.Series([0.001] * 252)
    assert metrics.annualized_volatility(r) < 1e-12


def test_max_drawdown_negative():
    # Up then crash
    r = pd.Series([0.01] * 10 + [-0.05] * 5)
    mdd = metrics.max_drawdown(r)
    assert mdd < 0


def test_portfolio_log_returns_shape(synthetic_prices):
    prices = synthetic_prices[["AAA", "BBB"]]
    rets = metrics.portfolio_log_returns(prices, np.array([0.5, 0.5]))
    assert len(rets) == len(prices) - 1


def test_historical_var_positive_loss():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(-0.001, 0.02, 500))
    v = metrics.historical_var(r, 0.95, 1)
    assert v >= 0


def test_parametric_var_scales_with_horizon():
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0, 0.01, 500))
    v1 = metrics.parametric_var(r, 0.95, 1)
    v30 = metrics.parametric_var(r, 0.95, 30)
    assert v30 > v1


def test_beta_market_to_self():
    r = pd.Series(np.linspace(-0.01, 0.01, 100))
    b = metrics.beta(r, r)
    assert abs(b - 1.0) < 1e-6


def test_correlation_matrix_identity_diagonal(synthetic_prices):
    tickers, matrix = metrics.correlation_matrix(synthetic_prices[["AAA", "BBB"]])
    assert tickers == ["AAA", "BBB"]
    assert abs(matrix[0][0] - 1.0) < 1e-9
    assert abs(matrix[1][1] - 1.0) < 1e-9
