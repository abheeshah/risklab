"""Pydantic request/response models for RiskLab API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Holding(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=16)
    weight: float = Field(..., ge=0.0, le=1.0)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, v: str) -> str:
        return v.strip().upper()


class AnalyzeRequest(BaseModel):
    holdings: list[Holding] = Field(..., min_length=1)
    total_value: float = Field(..., gt=0)
    lookback_years: Literal[1, 2, 3] = 2
    risk_free_rate: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> AnalyzeRequest:
        total = sum(h.weight for h in self.holdings)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Holding weights must sum to 1.0 (got {total:.6f})")
        tickers = [h.ticker for h in self.holdings]
        if len(tickers) != len(set(tickers)):
            raise ValueError("Duplicate tickers are not allowed")
        return self


class MetricValue(BaseModel):
    value: float
    explanation: str


class VaRBreakdown(BaseModel):
    historical_1d: MetricValue
    historical_30d: MetricValue
    parametric_1d: MetricValue
    parametric_30d: MetricValue


class ConfidenceVaR(BaseModel):
    var_95: VaRBreakdown
    var_99: VaRBreakdown
    cvar_95: MetricValue
    cvar_99: MetricValue


class HealthFactors(BaseModel):
    sharpe_score: float
    diversification_score: float
    drawdown_score: float
    beta_stability_score: float


class HealthScoreResult(BaseModel):
    score: float
    tier: str
    summary: str
    explanation: str
    factors: HealthFactors


class SeriesPoint(BaseModel):
    date: str
    portfolio: float
    benchmark: float


class CorrelationMatrix(BaseModel):
    tickers: list[str]
    matrix: list[list[float]]
    explanation: str


class AllocationItem(BaseModel):
    ticker: str
    weight: float


class RadarPoint(BaseModel):
    sector: str
    label: str
    portfolio_return: float
    portfolio_volatility: float
    portfolio_sharpe: float
    benchmark_return: float
    benchmark_volatility: float
    benchmark_sharpe: float


class AnalyzeResponse(BaseModel):
    health: HealthScoreResult
    volatility: MetricValue
    sharpe: MetricValue
    sortino: MetricValue
    max_drawdown: MetricValue
    hhi: MetricValue
    beta: MetricValue
    var: ConfidenceVaR
    correlation: CorrelationMatrix
    allocation: list[AllocationItem]
    cumulative_returns: list[SeriesPoint]
    radar: list[RadarPoint]
    risk_free_rate_used: float
    risk_free_rate_source: Literal["tnx", "fallback", "request"]
    lookback_years: int
    total_value: float
    annualized_return: MetricValue


class BenchmarkStats(BaseModel):
    sector: str
    ticker: str
    annualized_return: float
    volatility: float
    sharpe: float
    lookback_years: int
    explanation: str


class HealthResponse(BaseModel):
    status: str
    cache_ok: bool
    app: str = "RiskLab"
