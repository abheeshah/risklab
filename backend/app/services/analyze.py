"""Orchestrate full portfolio analysis."""

from __future__ import annotations

import numpy as np

from app.core.config import get_settings
from app.schemas.portfolio import (
    AllocationItem,
    AnalyzeRequest,
    AnalyzeResponse,
    ConfidenceVaR,
    CorrelationMatrix,
    HealthFactors,
    HealthScoreResult,
    MetricValue,
    RadarPoint,
    SeriesPoint,
    VaRBreakdown,
)
from app.services import explanations, metrics
from app.services.benchmarks import SECTOR_ETFS, get_benchmark_stats
from app.services.health_score import compute_health_score
from app.services.market_data import fetch_prices, fetch_risk_free_rate, lookback_window


def _mv(value: float, explanation: str) -> MetricValue:
    return MetricValue(value=float(value), explanation=explanation)


def _var_block(
    returns,
    alpha: float,
    total_value: float,
) -> VaRBreakdown:
    def pack(frac: float) -> MetricValue:
        return _mv(frac * total_value, explanations.VAR)

    return VaRBreakdown(
        historical_1d=pack(metrics.historical_var(returns, alpha, 1)),
        historical_30d=pack(metrics.historical_var(returns, alpha, 30)),
        parametric_1d=pack(metrics.parametric_var(returns, alpha, 1)),
        parametric_30d=pack(metrics.parametric_var(returns, alpha, 30)),
    )


def analyze_portfolio(req: AnalyzeRequest) -> AnalyzeResponse:
    settings = get_settings()
    tickers = [h.ticker for h in req.holdings]
    weights = np.array([h.weight for h in req.holdings], dtype=float)
    start, end = lookback_window(req.lookback_years)

    all_tickers = tickers + [settings.market_benchmark]
    prices_all = fetch_prices(all_tickers, start, end)
    asset_prices = prices_all[tickers]
    market_prices = prices_all[[settings.market_benchmark]]

    port_rets = metrics.portfolio_log_returns(asset_prices, weights)
    mkt_rets = metrics.portfolio_log_returns(market_prices, np.array([1.0]))
    # Align
    aligned = port_rets.to_frame("p").join(mkt_rets.rename("m"), how="inner").dropna()
    port_rets = aligned["p"]
    mkt_rets = aligned["m"]

    rf, rf_source = fetch_risk_free_rate(req.risk_free_rate)

    vol = metrics.annualized_volatility(port_rets)
    ann_ret = metrics.annualized_return(port_rets)
    sharpe = metrics.sharpe_ratio(port_rets, rf)
    sortino = metrics.sortino_ratio(port_rets, rf)
    mdd = metrics.max_drawdown(port_rets)
    hhi = metrics.herfindahl_hirschman_index(weights)
    beta = metrics.beta(port_rets, mkt_rets)
    corr_tickers, corr_matrix = metrics.correlation_matrix(asset_prices)

    health = compute_health_score(sharpe, hhi, mdd, beta, len(tickers))

    port_wealth = metrics.cumulative_wealth(port_rets)
    mkt_wealth = metrics.cumulative_wealth(mkt_rets)
    # Normalize to 1.0 at start
    port_wealth = port_wealth / port_wealth.iloc[0]
    mkt_wealth = mkt_wealth / mkt_wealth.iloc[0]
    series = [
        SeriesPoint(
            date=d.strftime("%Y-%m-%d"),
            portfolio=float(port_wealth.loc[d]),
            benchmark=float(mkt_wealth.loc[d]),
        )
        for d in port_wealth.index
    ]

    radar: list[RadarPoint] = []
    for sector in SECTOR_ETFS:
        try:
            b = get_benchmark_stats(sector, req.lookback_years)
            radar.append(
                RadarPoint(
                    sector=sector,
                    label=b["ticker"],
                    portfolio_return=ann_ret,
                    portfolio_volatility=vol,
                    portfolio_sharpe=sharpe,
                    benchmark_return=b["annualized_return"],
                    benchmark_volatility=b["volatility"],
                    benchmark_sharpe=b["sharpe"],
                )
            )
        except Exception:
            continue

    return AnalyzeResponse(
        health=HealthScoreResult(
            score=health.score,
            tier=health.tier,
            summary=health.summary,
            explanation=health.explanation,
            factors=HealthFactors(
                sharpe_score=health.sharpe_score,
                diversification_score=health.diversification_score,
                drawdown_score=health.drawdown_score,
                beta_stability_score=health.beta_stability_score,
            ),
        ),
        volatility=_mv(vol, explanations.VOLATILITY),
        sharpe=_mv(sharpe, explanations.SHARPE),
        sortino=_mv(sortino, explanations.SORTINO),
        max_drawdown=_mv(mdd, explanations.MAX_DRAWDOWN),
        hhi=_mv(hhi, explanations.HHI),
        beta=_mv(beta, explanations.BETA),
        var=ConfidenceVaR(
            var_95=_var_block(port_rets, 0.95, req.total_value),
            var_99=_var_block(port_rets, 0.99, req.total_value),
            cvar_95=_mv(
                metrics.cvar(port_rets, 0.95, 1) * req.total_value,
                explanations.CVAR,
            ),
            cvar_99=_mv(
                metrics.cvar(port_rets, 0.99, 1) * req.total_value,
                explanations.CVAR,
            ),
        ),
        correlation=CorrelationMatrix(
            tickers=corr_tickers,
            matrix=corr_matrix,
            explanation=explanations.CORRELATION,
        ),
        allocation=[AllocationItem(ticker=h.ticker, weight=h.weight) for h in req.holdings],
        cumulative_returns=series,
        radar=radar,
        risk_free_rate_used=rf,
        risk_free_rate_source=rf_source,  # type: ignore[arg-type]
        lookback_years=req.lookback_years,
        total_value=req.total_value,
        annualized_return=_mv(ann_ret, explanations.ANNUALIZED_RETURN),
    )
