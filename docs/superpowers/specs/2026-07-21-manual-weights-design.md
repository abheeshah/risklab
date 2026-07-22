# Manual weight inputs + one-shot rebalance

Date: 2026-07-21  
Status: approved approach A (pending user review of this spec)

## Goal

Let users type exact portfolio weights instead of using sliders, offer a one-shot “Rebalance to 100%” action after the holdings inputs, and simplify the topbar subtitle.

## Non-goals

- Auto-normalize on every keystroke
- Auto-normalize on Analyze submit
- Backend / API changes
- README / copy changes outside the frontend headline and form error text

## UI changes

### Topbar (`App.tsx`)

- Current: `Portfolio risk analytics — plain English`
- New: `Portfolio risk analytics`
- Remove the em dash and the “plain English” phrase.

### Holdings form (`PortfolioForm.tsx`)

1. **Number inputs** — Replace each weight `range` slider with a number input:
   - `type="number"`, `min={0}`, `max={100}`, `step={0.1}`
   - Show a `%` suffix (layout: ticker | weight input + `%` | remove)
   - Editing a weight updates only that row (no live renormalization)

2. **Remove live auto-rebalance** — Delete the checkbox toggle and `autoRebalance` prop/state from `PortfolioForm` and `App`.

3. **One-shot button** — Place **Rebalance to 100%** in the form actions row *after* the holdings list (alongside Add ticker and Σ), not in the panel header.
   - On click: call existing `normalizeWeights` on current `weightPct` values; round to 1 decimal as today.
   - Does not run automatically when adding/removing rows or editing inputs.

4. **Error copy** (`App.tsx` submit guard) — If weights do not sum to ~100%, mention adjusting inputs or using Rebalance to 100% (no “sliders” / “auto-rebalance” wording).

### Styles (`index.css`)

- Replace `.slider-wrap` / range styles with a compact weight number-input layout (e.g. `.weight-input-wrap`).
- Remove unused `.toggle` styles if nothing else uses them.

## Behavior

| Action | Effect |
|--------|--------|
| Edit weight number | Updates that holding only |
| Add / remove ticker | Does not rebalance |
| Click Rebalance to 100% | Normalizes all weights to sum 100% once |
| Analyze | Still requires Σ ≈ 100%; no silent normalize |

## Files touched

- `frontend/src/App.tsx`
- `frontend/src/components/PortfolioForm.tsx`
- `frontend/src/index.css`

`frontend/src/lib/weights.ts` unchanged (reuse `normalizeWeights`).

## Acceptance

- No range sliders for weights; number inputs work.
- No live auto-rebalance toggle.
- Rebalance button appears below holdings and normalizes once.
- Topbar subtitle is `Portfolio risk analytics` only.
- Analyze still rejects non-100% sums with updated message.
