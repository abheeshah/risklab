import { HelpCircle } from 'lucide-react'

type Props = {
  label: string
  value: string
  explanation: string
  sub?: string
}

export function MetricCard({ label, value, explanation, sub }: Props) {
  return (
    <div className="metric-card">
      <div className="metric-card__head">
        <span className="metric-card__label">{label}</span>
        <span className="tooltip">
          <HelpCircle size={14} aria-hidden />
          <span className="tooltip__text">{explanation}</span>
        </span>
      </div>
      <div className="metric-card__value">{value}</div>
      {sub ? <div className="metric-card__sub">{sub}</div> : null}
    </div>
  )
}
