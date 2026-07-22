# RiskLab Design Spec (2026-07-21)

## Goal

Zero-cost, open-source full-stack Portfolio Risk Analytics Engine. Users submit ticker weights and portfolio value; the API returns risk metrics with plain-English explanations and a single Portfolio Health Score (0–100).

## Architecture

Modular FastAPI monolith + React/Vite SPA + Diskcache (24h TTL) + Docker Compose.

```
React SPA → FastAPI → MarketData / Metrics / HealthScore / Benchmarks → Diskcache ↔ yfinance
```

## Locked decisions (v1)

| Topic | Decision |
|-------|----------|
| Optimization | Deferred to v2 (`make v2` → PyPortfolioOpt + `POST /api/v1/optimize`) |
| Risk-free rate | Live `^TNX` / 100; fallback 4.5%; optional request override |
| Charts | Recharts |
| Holdings input | Weights only (`[0,1]`, sum ≈ 1); total portfolio value |
| Cache | Diskcache, TTL 86400s |
| Sectors | tech→XLK, healthcare→XLV, energy→XLE, financials→XLF, consumer→XLY |
| UI | Slate canvas, IBM Plex Sans/Mono, teal accent |

## API

- `POST /api/v1/analyze` — full risk analysis
- `GET /api/v1/benchmarks/{sector}` — cached sector ETF stats
- `GET /api/v1/health` — API + cache status

### Analyze request

```json
{
  "holdings": [{"ticker": "AAPL", "weight": 0.4}, {"ticker": "MSFT", "weight": 0.6}],
  "total_value": 100000,
  "lookback_years": 2,
  "risk_free_rate": null
}
```

Weights in `[0, 1]`, must sum to `1.0 ± 1e-6`.

## Metrics

Each metric returns `{ value, explanation }`.

1. Annualized volatility — σ(daily log returns) × √252  
2. Sharpe / Sortino — excess return over Rf; Sortino uses downside σ  
3. VaR 95/99 — historical + parametric; 1-day and 30-day  
4. CVaR — mean loss beyond VaR  
5. Max drawdown — peak-to-trough on cumulative returns  
6. Correlation matrix — Pearson on asset daily returns  
7. HHI — Σ wᵢ²  
8. Beta — vs `^GSPC`

## Health Score

```
0.30·SharpeScore + 0.25·DiversificationScore + 0.25·DrawdownScore + 0.20·BetaStabilityScore
```

Tiers: 80–100 Excellent, 60–79 Moderate, 40–59 At Risk, 0–39 High Vulnerability.

## Frontend

Weights-only form with auto-rebalance; Health Score hero; metric cards with tooltips; correlation heatmap, allocation donut, cumulative return vs S&P 500, radar vs sector benchmarks; toast errors.

## Out of scope (v1)

- PyPortfolioOpt / optimize UI  
- Share-count input  
- Auth, cloud DB, paid data vendors  
