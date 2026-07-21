import { Plus, Trash2 } from 'lucide-react'
import type { HoldingInput } from '../types/analytics'
import { normalizeWeights } from '../lib/weights'

type Props = {
  holdings: HoldingInput[]
  totalValue: number
  lookbackYears: 1 | 2 | 3
  loading: boolean
  onChangeHoldings: (h: HoldingInput[]) => void
  onTotalValue: (v: number) => void
  onLookback: (y: 1 | 2 | 3) => void
  onSubmit: () => void
}

function uid() {
  return Math.random().toString(36).slice(2, 9)
}

export function PortfolioForm({
  holdings,
  totalValue,
  lookbackYears,
  loading,
  onChangeHoldings,
  onTotalValue,
  onLookback,
  onSubmit,
}: Props) {
  const updateWeight = (id: string, weightPct: number) => {
    onChangeHoldings(holdings.map((h) => (h.id === id ? { ...h, weightPct } : h)))
  }

  const addRow = () => {
    onChangeHoldings([...holdings, { id: uid(), ticker: '', weightPct: 0 }])
  }

  const removeRow = (id: string) => {
    const filtered = holdings.filter((h) => h.id !== id)
    if (filtered.length === 0) return
    onChangeHoldings(filtered)
  }

  const rebalance = () => {
    const pcts = normalizeWeights(holdings.map((h) => h.weightPct))
    onChangeHoldings(
      holdings.map((h, i) => ({ ...h, weightPct: Math.round(pcts[i] * 10) / 10 })),
    )
  }

  const weightSum = holdings.reduce((a, h) => a + h.weightPct, 0)

  return (
    <section className="form-panel">
      <header className="form-panel__header">
        <div>
          <p className="eyebrow">Portfolio input</p>
          <h2>Build your book</h2>
        </div>
      </header>

      <div className="holdings">
        {holdings.map((h) => (
          <div className="holding-row" key={h.id}>
            <input
              className="ticker-input"
              placeholder="Ticker"
              value={h.ticker}
              onChange={(e) =>
                onChangeHoldings(
                  holdings.map((x) =>
                    x.id === h.id ? { ...x, ticker: e.target.value.toUpperCase() } : x,
                  ),
                )
              }
            />
            <div className="weight-input-wrap">
              <input
                type="number"
                min={0}
                max={100}
                step={0.1}
                value={h.weightPct}
                onChange={(e) => updateWeight(h.id, Number(e.target.value))}
                aria-label={`${h.ticker || 'Holding'} weight percent`}
              />
              <span className="mono">%</span>
            </div>
            <button type="button" className="icon-btn" onClick={() => removeRow(h.id)} aria-label="Remove">
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>

      <div className="form-actions">
        <div className="form-actions__left">
          <button type="button" className="ghost-btn" onClick={addRow}>
            <Plus size={16} /> Add ticker
          </button>
          <button type="button" className="ghost-btn" onClick={rebalance}>
            Rebalance to 100%
          </button>
        </div>
        <span className={`mono weight-sum ${Math.abs(weightSum - 100) < 0.2 ? 'ok' : 'bad'}`}>
          Σ {weightSum.toFixed(1)}%
        </span>
      </div>

      <div className="form-grid">
        <label>
          Total portfolio value (USD)
          <input
            type="number"
            min={1}
            value={totalValue}
            onChange={(e) => onTotalValue(Number(e.target.value))}
          />
        </label>
        <label>
          Lookback years
          <select
            value={lookbackYears}
            onChange={(e) => onLookback(Number(e.target.value) as 1 | 2 | 3)}
          >
            <option value={1}>1 year</option>
            <option value={2}>2 years</option>
            <option value={3}>3 years</option>
          </select>
        </label>
      </div>

      <button type="button" className="primary-btn" disabled={loading} onClick={onSubmit}>
        {loading ? 'Analyzing…' : 'Analyze portfolio'}
      </button>
    </section>
  )
}
