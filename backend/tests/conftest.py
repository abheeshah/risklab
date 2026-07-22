"""Shared pytest fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.cache import reset_cache_for_tests  # noqa: E402
from app.core.config import get_settings  # noqa: E402


@pytest.fixture(autouse=True)
def _tmp_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("RISKLAB_CACHE_DIR", str(tmp_path / "cache"))
    get_settings.cache_clear()
    reset_cache_for_tests()
    yield
    reset_cache_for_tests()
    get_settings.cache_clear()


@pytest.fixture
def synthetic_prices() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 252
    dates = pd.bdate_range("2023-01-01", periods=n)
    # Geometric Brownian-ish paths
    a = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, n)))
    b = 50 * np.exp(np.cumsum(rng.normal(0.0004, 0.012, n)))
    m = 4000 * np.exp(np.cumsum(rng.normal(0.0003, 0.008, n)))
    return pd.DataFrame({"AAA": a, "BBB": b, "^GSPC": m}, index=dates)
