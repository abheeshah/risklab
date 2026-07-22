import { Fragment } from 'react'

type Props = {
  tickers: string[]
  matrix: number[][]
}

function cellColor(v: number): string {
  if (v >= 0) {
    const a = 0.15 + v * 0.55
    return `rgba(45, 212, 191, ${a})`
  }
  const a = 0.15 + Math.abs(v) * 0.55
  return `rgba(251, 113, 133, ${a})`
}

export function CorrelationHeatmap({ tickers, matrix }: Props) {
  return (
    <div className="chart-card">
      <h3>Correlation heatmap</h3>
      <div className="heatmap" style={{ gridTemplateColumns: `auto repeat(${tickers.length}, minmax(2.5rem, 1fr))` }}>
        <div />
        {tickers.map((t) => (
          <div key={`h-${t}`} className="heatmap__label mono">
            {t}
          </div>
        ))}
        {tickers.map((rowT, i) => (
          <Fragment key={`row-${rowT}`}>
            <div className="heatmap__label mono">{rowT}</div>
            {matrix[i]?.map((v, j) => (
              <div
                key={`${i}-${j}`}
                className="heatmap__cell mono"
                style={{ background: cellColor(v) }}
                title={`${tickers[i]} / ${tickers[j]}: ${v.toFixed(2)}`}
              >
                {v.toFixed(2)}
              </div>
            ))}
          </Fragment>
        ))}
      </div>
    </div>
  )
}
