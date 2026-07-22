# RiskLab

Zero-cost, open-source **Portfolio Risk Analytics Engine**. Submit ticker weights and a portfolio value; RiskLab returns risk metrics with plain-English explanations and a single **Portfolio Health Score (0–100)**.

## Quick start (Docker)

```bash
docker compose up --build
```

- Frontend: http://localhost:5173  
- API + OpenAPI docs: http://localhost:8000/docs  

## Local development

### Backend

```bash
cd backend
python3.11 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` → `http://127.0.0.1:8000`.

### Tests

```bash
cd backend && pytest -v
cd frontend && npm run lint && npm run build
```

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/analyze` | Full portfolio risk analysis |
| `GET` | `/api/v1/benchmarks/{sector}` | Cached sector ETF stats (`tech`, `healthcare`, `energy`, `financials`, `consumer`) |
| `GET` | `/api/v1/health` | API + cache healthcheck |

### Example analyze payload

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

Weights must be in `[0, 1]` and sum to `1.0`. Optional `risk_free_rate` overrides the live 10-year Treasury (`^TNX`) rate (fallback 4.5%).

## Metrics glossary

| Metric | Plain English |
|--------|----------------|
| **Health Score** | Composite of Sharpe (30%), diversification/HHI (25%), max drawdown (25%), and beta stability (20%). |
| **Volatility** | How violently portfolio value swings over a year. |
| **Sharpe** | Excess return per unit of total risk. |
| **Sortino** | Like Sharpe, but only penalizes downside moves. |
| **VaR / CVaR** | Estimated loss on a bad / worst-case day. |
| **Max drawdown** | Worst peak-to-trough decline in the lookback. |
| **HHI** | Concentration — high means single-stock risk. |
| **Beta** | Sensitivity vs the S&P 500 (`^GSPC`). |

Market data comes from [yfinance](https://github.com/ranaroussi/yfinance). Price series and sector benchmarks are cached locally with Diskcache (24h TTL).

## Tech stack

- **Backend:** Python 3.11+, FastAPI, Pandas, NumPy, SciPy, yfinance, Diskcache  
- **Frontend:** React, Vite, TypeScript, Tailwind CSS, Recharts, Lucide  
- **Ops:** Docker Compose, GitHub Actions CI  

## Roadmap (v2)

Portfolio optimization via **PyPortfolioOpt** (`POST /api/v1/optimize` + suggested allocation UI). Trigger phrase for maintainers: **“make v2”**.

## License

MIT — see [LICENSE](LICENSE).
