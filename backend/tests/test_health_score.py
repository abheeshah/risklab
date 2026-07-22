"""Tests for health score mapping."""

from app.services.health_score import compute_health_score, tier_for_score


def test_excellent_portfolio():
    result = compute_health_score(
        sharpe=1.8,
        hhi=0.25,
        max_dd=-0.05,
        beta=1.0,
        n_assets=4,
    )
    assert result.score >= 80
    assert result.tier.startswith("Excellent")


def test_high_vulnerability():
    result = compute_health_score(
        sharpe=-0.5,
        hhi=1.0,
        max_dd=-0.55,
        beta=2.5,
        n_assets=1,
    )
    assert result.score < 40
    assert result.tier == "High Vulnerability"


def test_tier_boundaries():
    assert tier_for_score(80).startswith("Excellent")
    assert tier_for_score(60).startswith("Moderate")
    assert tier_for_score(40).startswith("At Risk")
    assert tier_for_score(39) == "High Vulnerability"
