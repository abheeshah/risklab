# Manual Weight Inputs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace weight sliders with number inputs, add a one-shot Rebalance to 100% button after holdings, and simplify the topbar subtitle.

**Architecture:** Keep `normalizeWeights` in `frontend/src/lib/weights.ts`. Remove live `autoRebalance` state. PortfolioForm owns number inputs and a button that calls normalize once. App owns headline copy and submit validation message.

**Tech Stack:** React, TypeScript, Vite, existing CSS in `frontend/src/index.css`

## Global Constraints

- No live auto-rebalance on edit/add/remove
- No silent normalize on Analyze submit
- No backend/API changes
- No new npm dependencies
- Subtitle must be exactly `Portfolio risk analytics` (no em dash, no “plain English”)

---

### Task 1: PortfolioForm — number inputs + one-shot rebalance

**Files:**
- Modify: `frontend/src/components/PortfolioForm.tsx`
- Modify: `frontend/src/index.css` (slider/toggle → weight input styles)

**Interfaces:**
- Consumes: `normalizeWeights(weights: number[]): number[]` from `../lib/weights`
- Produces: `PortfolioForm` props without `autoRebalance` / `onAutoRebalance`; `onRebalance` handled internally via `onChangeHoldings`

- [ ] **Step 1: Rewrite PortfolioForm**

Replace the component with:

```tsx
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
```

- [ ] **Step 2: Update CSS**

In `frontend/src/index.css`:

1. Remove `.toggle` block.
2. Replace `.slider-wrap` and `.slider-wrap input[type='range']` with:

```css
.weight-input-wrap {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.35rem;
  align-items: center;
}

.weight-input-wrap input[type='number'] {
  width: 100%;
  background: #0b1220;
  border: 1px solid #334155;
  color: var(--rl-text);
  border-radius: 0.35rem;
  padding: 0.45rem 0.55rem;
  font: inherit;
  font-variant-numeric: tabular-nums;
}

.form-actions__left {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}
```

3. Also add `.weight-input-wrap input` to the shared ticker/form input selector group if helpful, or keep standalone as above.

- [ ] **Step 3: Verify TypeScript still fails on App props (expected until Task 2)**

Run: `cd frontend && npx tsc --noEmit`
Expected: errors about `autoRebalance` / `onAutoRebalance` on `PortfolioForm` usage in `App.tsx`

---

### Task 2: App — headline + props + error copy

**Files:**
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: updated `PortfolioForm` props from Task 1
- Produces: no `autoRebalance` state; subtitle `Portfolio risk analytics`

- [ ] **Step 1: Update App.tsx**

1. Remove `const [autoRebalance, setAutoRebalance] = useState(true)`.
2. Change subtitle from `Portfolio risk analytics — plain English` to `Portfolio risk analytics`.
3. Remove `autoRebalance={...}` and `onAutoRebalance={...}` from `<PortfolioForm />`.
4. Change submit error to:
   `Weights must sum to 100% (currently ${weightSum.toFixed(1)}%). Adjust weights or use Rebalance to 100%.`

- [ ] **Step 2: Typecheck and build**

Run: `cd frontend && npx tsc --noEmit && npm run build`
Expected: PASS / build succeeds

- [ ] **Step 3: Manual smoke (dev server if running)**

- Edit a weight → other weights unchanged
- Click Rebalance to 100% → Σ shows ~100.0%
- Confirm topbar shows `Portfolio risk analytics` only

---

## Spec coverage

| Spec requirement | Task |
|------------------|------|
| Number inputs for weights | Task 1 |
| Remove live auto-rebalance | Task 1 + 2 |
| One-shot button after holdings | Task 1 |
| Headline cleanup | Task 2 |
| Error copy update | Task 2 |
| CSS for weight inputs | Task 1 |
