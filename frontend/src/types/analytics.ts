export type MetricValue = {
  value: number
  explanation: string
}

export type VaRBreakdown = {
  historical_1d: MetricValue
  historical_30d: MetricValue
  parametric_1d: MetricValue
  parametric_30d: MetricValue
}

export type HealthFactors = {
  sharpe_score: number
  diversification_score: number
  drawdown_score: number
  beta_stability_score: number
}

export type AnalyzeResponse = {
  health: {
    score: number
    tier: string
    summary: string
    explanation: string
    factors: HealthFactors
  }
  volatility: MetricValue
  sharpe: MetricValue
  sortino: MetricValue
  max_drawdown: MetricValue
  hhi: MetricValue
  beta: MetricValue
  var: {
    var_95: VaRBreakdown
    var_99: VaRBreakdown
    cvar_95: MetricValue
    cvar_99: MetricValue
  }
  correlation: {
    tickers: string[]
    matrix: number[][]
    explanation: string
  }
  allocation: { ticker: string; weight: number }[]
  cumulative_returns: { date: string; portfolio: number; benchmark: number }[]
  radar: {
    sector: string
    label: string
    portfolio_return: number
    portfolio_volatility: number
    portfolio_sharpe: number
    benchmark_return: number
    benchmark_volatility: number
    benchmark_sharpe: number
  }[]
  risk_free_rate_used: number
  risk_free_rate_source: 'tnx' | 'fallback' | 'request'
  lookback_years: number
  total_value: number
  annualized_return: MetricValue
}

export type HoldingInput = {
  id: string
  ticker: string
  weightPct: number
}

export type AnalyzeRequest = {
  holdings: { ticker: string; weight: number }[]
  total_value: number
  lookback_years: 1 | 2 | 3
}
