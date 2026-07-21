import { useState } from 'react'
import { PortfolioForm } from './components/PortfolioForm'
import { HealthBadge } from './components/HealthBadge'
import { MetricCard } from './components/MetricCard'
import { Toast } from './components/Toast'
import { CorrelationHeatmap } from './components/charts/CorrelationHeatmap'
import { AllocationDonut } from './components/charts/AllocationDonut'
import { CumulativeReturnChart } from './components/charts/CumulativeReturnChart'
import { BenchmarkRadar } from './components/charts/BenchmarkRadar'
import { useAnalyze } from './hooks/useAnalyze'
import type { HoldingInput } from './types/analytics'
import { formatNumber, formatPct, formatUsd, pctToFraction } from './lib/weights'
import './index.css'

function seedHoldings(): HoldingInput[] {
  return [
    { id: '1', ticker: 'AAPL', weightPct: 40 },
    { id: '2', ticker: 'MSFT', weightPct: 35 },
    { id: '3', ticker: 'NVDA', weightPct: 25 },
  ]
}

export default function App() {
  const [holdings, setHoldings] = useState<HoldingInput[]>(seedHoldings)
  const [totalValue, setTotalValue] = useState(100_000)
  const [lookbackYears, setLookbackYears] = useState<1 | 2 | 3>(2)
  const { data, loading, error, analyze, clearError, setError } = useAnalyze()

  const onSubmit = async () => {
    const cleaned = holdings.filter((h) => h.ticker.trim())
    if (cleaned.length === 0) {
      setError('Add at least one ticker.')
      return
    }
    const weightSum = cleaned.reduce((a, h) => a + h.weightPct, 0)
    if (Math.abs(weightSum - 100) > 0.5) {
      setError(`Weights must sum to 100% (currently ${weightSum.toFixed(1)}%). Adjust weights or use Rebalance to 100%.`)
      return
    }
    try {
      await analyze({
        holdings: cleaned.map((h) => ({
          ticker: h.ticker.trim(),
          weight: pctToFraction(h.weightPct),
        })),
        total_value: totalValue,
        lookback_years: lookbackYears,
      })
    } catch {
      /* toast via error state */
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand__mark" aria-hidden />
          <div>
            <h1>RiskLab</h1>
            <p>Portfolio risk analytics</p>
          </div>
        </div>
      </header>

      <main className="layout">
        <PortfolioForm
          holdings={holdings}
          totalValue={totalValue}
          lookbackYears={lookbackYears}
          loading={loading}
          onChangeHoldings={setHoldings}
          onTotalValue={setTotalValue}
          onLookback={setLookbackYears}
          onSubmit={onSubmit}
        />

        {data ? (
          <div className="dashboard">
            <HealthBadge health={data.health} />

            <div className="metrics-grid">
              <MetricCard
                label="Annualized return"
                value={formatPct(data.annualized_return.value)}
                explanation={data.annualized_return.explanation}
              />
              <MetricCard
                label="Volatility"
                value={formatPct(data.volatility.value)}
                explanation={data.volatility.explanation}
              />
              <MetricCard
                label="Sharpe"
                value={formatNumber(data.sharpe.value)}
                explanation={data.sharpe.explanation}
                sub={`Rf ${(data.risk_free_rate_used * 100).toFixed(2)}% (${data.risk_free_rate_source})`}
              />
              <MetricCard
                label="Sortino"
                value={formatNumber(data.sortino.value)}
                explanation={data.sortino.explanation}
              />
              <MetricCard
                label="Max drawdown"
                value={formatPct(data.max_drawdown.value)}
                explanation={data.max_drawdown.explanation}
              />
              <MetricCard
                label="Beta"
                value={formatNumber(data.beta.value)}
                explanation={data.beta.explanation}
              />
              <MetricCard
                label="HHI"
                value={formatNumber(data.hhi.value, 3)}
                explanation={data.hhi.explanation}
              />
              <MetricCard
                label="VaR 95% (1d)"
                value={formatUsd(data.var.var_95.historical_1d.value)}
                explanation={data.var.var_95.historical_1d.explanation}
                sub={`CVaR ${formatUsd(data.var.cvar_95.value)}`}
              />
            </div>

            <div className="charts-grid">
              <CumulativeReturnChart series={data.cumulative_returns} />
              <AllocationDonut allocation={data.allocation} />
              <CorrelationHeatmap
                tickers={data.correlation.tickers}
                matrix={data.correlation.matrix}
              />
              <BenchmarkRadar radar={data.radar} />
            </div>
          </div>
        ) : (
          <section className="empty-dash">
            <p className="eyebrow">Dashboard</p>
            <h2>Run an analysis to see your Health Score</h2>
            <p>
              Enter tickers and weights, then analyze. Metrics arrive with plain-English
              explanations — hover the ? icons after results load.
            </p>
          </section>
        )}
      </main>

      <Toast message={error} onClose={clearError} />
    </div>
  )
}
