"""Portfolio Health Score (0–100)."""

from __future__ import annotations

from dataclasses import dataclass

from app.services import explanations


@dataclass
class HealthResult:
    score: float
    tier: str
    summary: str
    explanation: str
    sharpe_score: float
    diversification_score: float
    drawdown_score: float
    beta_stability_score: float


def _clip(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return float(max(lo, min(hi, x)))


def _map_linear(value: float, in_lo: float, in_hi: float, out_lo: float, out_hi: float) -> float:
    if in_hi == in_lo:
        return out_lo
    t = (value - in_lo) / (in_hi - in_lo)
    return out_lo + t * (out_hi - out_lo)


def sharpe_component(sharpe: float) -> float:
    return _clip(_map_linear(sharpe, -0.5, 2.0, 0.0, 100.0))


def diversification_component(hhi: float, n_assets: int) -> float:
    """Invert HHI relative to equal-weight baseline."""
    n = max(n_assets, 1)
    equal = 1.0 / n
    # HHI in [equal, 1]; map equal→100, 1→0
    return _clip(_map_linear(hhi, equal, 1.0, 100.0, 0.0))


def drawdown_component(max_dd: float) -> float:
    # max_dd is negative or zero; use absolute magnitude
    mag = abs(max_dd)
    return _clip(_map_linear(mag, 0.0, 0.5, 100.0, 0.0))


def beta_stability_component(beta: float) -> float:
    # |β−1| of 0 → 100; ≥1.0 → 0
    return _clip(_map_linear(abs(beta - 1.0), 0.0, 1.0, 100.0, 0.0))


def tier_for_score(score: float) -> str:
    if score >= 80:
        return "Excellent / Resilient"
    if score >= 60:
        return "Moderate / Balanced"
    if score >= 40:
        return "At Risk / Concentrated"
    return "High Vulnerability"


def summary_for_tier(tier: str, score: float) -> str:
    rounded = round(score)
    if tier.startswith("Excellent"):
        return (
            f"Your portfolio scores {rounded}/100 — well-balanced, risk-adjusted, "
            "and comparatively resilient to market shocks."
        )
    if tier.startswith("Moderate"):
        return (
            f"Your portfolio scores {rounded}/100 — reasonably balanced, with room to "
            "improve diversification or drawdown control."
        )
    if tier.startswith("At Risk"):
        return (
            f"Your portfolio scores {rounded}/100 — concentration or drawdown risk is "
            "elevated; consider spreading exposure."
        )
    return (
        f"Your portfolio scores {rounded}/100 — high vulnerability from concentration, "
        "weak risk-adjusted returns, or deep drawdowns."
    )


def compute_health_score(
    sharpe: float,
    hhi: float,
    max_dd: float,
    beta: float,
    n_assets: int,
) -> HealthResult:
    s = sharpe_component(sharpe)
    d = diversification_component(hhi, n_assets)
    dd = drawdown_component(max_dd)
    b = beta_stability_component(beta)
    score = _clip(0.30 * s + 0.25 * d + 0.25 * dd + 0.20 * b)
    tier = tier_for_score(score)
    return HealthResult(
        score=round(score, 1),
        tier=tier,
        summary=summary_for_tier(tier, score),
        explanation=explanations.HEALTH,
        sharpe_score=round(s, 1),
        diversification_score=round(d, 1),
        drawdown_score=round(dd, 1),
        beta_stability_score=round(b, 1),
    )
