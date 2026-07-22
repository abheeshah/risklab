/** Normalize percentage weights to sum to 100. */
export function normalizeWeights(weights: number[]): number[] {
  const sum = weights.reduce((a, b) => a + b, 0)
  if (sum <= 0) {
    const n = weights.length || 1
    return weights.map(() => 100 / n)
  }
  return weights.map((w) => (w / sum) * 100)
}

export function pctToFraction(pct: number): number {
  return pct / 100
}

export function formatPct(value: number, digits = 1): string {
  return `${(value * 100).toFixed(digits)}%`
}

export function formatNumber(value: number, digits = 2): string {
  return value.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })
}

export function formatUsd(value: number): string {
  return value.toLocaleString(undefined, {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  })
}

export function healthColor(score: number): string {
  if (score >= 80) return 'var(--rl-good)'
  if (score >= 60) return 'var(--rl-warn)'
  return 'var(--rl-bad)'
}
