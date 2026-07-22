import { healthColor } from '../lib/weights'
import type { AnalyzeResponse } from '../types/analytics'

type Props = {
  health: AnalyzeResponse['health']
}

export function HealthBadge({ health }: Props) {
  const color = healthColor(health.score)
  const factors = [
    { label: 'Sharpe', value: health.factors.sharpe_score, weight: '30%' },
    { label: 'Diversification', value: health.factors.diversification_score, weight: '25%' },
    { label: 'Drawdown', value: health.factors.drawdown_score, weight: '25%' },
    { label: 'Beta stability', value: health.factors.beta_stability_score, weight: '20%' },
  ]

  return (
    <section className="health-hero" style={{ ['--score-color' as string]: color }}>
      <div className="health-hero__score">
        <div className="health-hero__ring">
          <span className="health-hero__number">{Math.round(health.score)}</span>
          <span className="health-hero__of">/ 100</span>
        </div>
        <div>
          <p className="eyebrow">RiskLab Health Score</p>
          <h2>{health.tier}</h2>
          <p className="health-hero__summary">{health.summary}</p>
        </div>
      </div>
      <div className="health-hero__factors">
        {factors.map((f) => (
          <div key={f.label} className="factor">
            <div className="factor__meta">
              <span>{f.label}</span>
              <span className="mono">
                {f.value.toFixed(0)} · {f.weight}
              </span>
            </div>
            <div className="factor__bar">
              <div className="factor__fill" style={{ width: `${f.value}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
