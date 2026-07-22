# RiskLab

Open-source **portfolio risk analytics** you run on your own machine. Enter ticker weights and a portfolio value; RiskLab fetches market data, computes risk metrics with plain-English explanations, and returns a single **Portfolio Health Score (0–100)**.

This is a local full-stack app (FastAPI + React), not a hosted product. There is no cloud account, auth, or paid data vendor — market data comes from [yfinance](https://github.com/ranaroussi/yfinance) and is cached on disk.

## What you get

- Risk metrics: volatility, Sharpe, Sortino, VaR/CVaR, max drawdown, HHI, beta vs S&P 500
- Correlation heatmap, allocation chart, cumulative return vs `^GSPC`, sector benchmark radar
- A composite Health Score (Sharpe 30% · diversification/HHI 25% · max drawdown 25% · beta stability 20%)

## Prerequisites

| Tool | Version | Used for |
|------|---------|----------|
| [Python](https://www.python.org/) | 3.11+ | Backend API |
| [Node.js](https://nodejs.org/) | 22+ (LTS fine) | Frontend SPA |
| [Docker](https://docs.docker.com/get-docker/) + Compose | optional | One-command stack |

Internet access is required on first run so yfinance can download price history. Subsequent requests reuse a local Diskcache (24h TTL).

## Run locally (recommended for development)

You need **two terminals**: backend on `:8000`, frontend on `:5173`. Vite proxies `/api` → `http://127.0.0.1:8000`, so the UI talks to the API without CORS hassle in day-to-day use.

### 1. Backend

```bash
cd backend
python3.11 -m venv ../.venv
source ../.venv/bin/activate   # Windows: ..\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API: http://127.0.0.1:8000  
- Interactive OpenAPI docs: http://127.0.0.1:8000/docs  
- Healthcheck: http://127.0.0.1:8000/api/v1/health  

Optional env vars (prefix `RISKLAB_`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `RISKLAB_CACHE_DIR` | `.cache/risklab` | Price / benchmark cache directory |
| `RISKLAB_CACHE_TTL_SECONDS` | `86400` | Cache TTL (seconds) |
| `RISKLAB_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed browser origins |

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — enter holdings, set total value / lookback, and analyze.

### 3. Verify

```bash
# Backend tests
cd backend && source ../.venv/bin/activate && pytest -v

# Frontend lint + production build
cd frontend && npm run lint && npm run build
```

## Run with Docker Compose

If you prefer containers over a local venv/Node install:

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| UI (nginx serving the built SPA) | http://localhost:5173 |
| API + docs | http://localhost:8000/docs |

Compose mounts a named volume for the backend cache (`risklab_cache`). Stop with `Ctrl+C`, or `docker compose down` to tear down containers (add `-v` to drop the cache volume).

**Note:** Docker serves a production build of the frontend. For UI iteration, use the local npm/Vite flow above.

## Project layout

```
risklab/
├── backend/                 # FastAPI app
│   ├── app/
│   │   ├── api/             # HTTP routes
│   │   ├── core/            # config + Diskcache
│   │   ├── schemas/         # request/response models
│   │   └── services/        # market data, metrics, health score
│   └── tests/
├── frontend/                # React + Vite + TypeScript SPA
│   └── src/
├── docker-compose.yml
└── docs/                    # design specs & implementation plans
```

Flow: **React SPA → FastAPI → MarketData / Metrics / HealthScore / Benchmarks → Diskcache ↔ yfinance**

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/analyze` | Full portfolio risk analysis |
| `GET` | `/api/v1/benchmarks/{sector}` | Cached sector ETF stats (`tech`, `healthcare`, `energy`, `financials`, `consumer`) |
| `GET` | `/api/v1/health` | API + cache healthcheck |

### Example `POST /api/v1/analyze`

```json
{
  "holdings": [
    { "ticker": "AAPL", "weight": 0.4 },
    { "ticker": "MSFT", "weight": 0.35 },
    { "ticker": "NVDA", "weight": 0.25 }
  ],
  "total_value": 100000,
  "lookback_years": 2
}
```

- Weights must be in `[0, 1]` and sum to `1.0` (within a tiny float tolerance).
- Optional `risk_free_rate` overrides the live 10-year Treasury (`^TNX`) rate (fallback 4.5%).

Quick smoke test with the backend running:

```bash
curl -s http://127.0.0.1:8000/api/v1/health | jq
```

## Metrics glossary

| Metric | Plain English |
|--------|----------------|
| **Health Score** | Composite of Sharpe (30%), diversification/HHI (25%), max drawdown (25%), and beta stability (20%). Tiers: 80–100 Excellent, 60–79 Moderate, 40–59 At Risk, 0–39 High Vulnerability. |
| **Volatility** | How much portfolio value swings over a year (annualized). |
| **Sharpe** | Excess return per unit of total risk. |
| **Sortino** | Like Sharpe, but only penalizes downside moves. |
| **VaR / CVaR** | Estimated loss on a bad / worst-case day. |
| **Max drawdown** | Worst peak-to-trough decline in the lookback window. |
| **HHI** | Concentration — higher means more single-stock risk. |
| **Beta** | Sensitivity vs the S&P 500 (`^GSPC`). |

## Tech stack

- **Backend:** Python 3.11+, FastAPI, Pandas, NumPy, SciPy, yfinance, Diskcache  
- **Frontend:** React 19, Vite, TypeScript, Tailwind CSS, Recharts  
- **Ops:** Docker Compose, GitHub Actions CI  

## Roadmap (v2)

Portfolio optimization via **PyPortfolioOpt** (`POST /api/v1/optimize` + suggested allocation UI). Maintainer trigger phrase: **“make v2”**.

## License

MIT — see [LICENSE](LICENSE).
