import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

type Props = {
  series: { date: string; portfolio: number; benchmark: number }[]
}

export function CumulativeReturnChart({ series }: Props) {
  // Downsample for readability if long
  const step = Math.max(1, Math.floor(series.length / 180))
  const data = series.filter((_, i) => i % step === 0).map((p) => ({
    date: p.date,
    Portfolio: Number(((p.portfolio - 1) * 100).toFixed(2)),
    'S&P 500': Number(((p.benchmark - 1) * 100).toFixed(2)),
  }))

  return (
    <div className="chart-card chart-card--wide">
      <h3>Cumulative return vs S&P 500</h3>
      <div className="chart-h chart-h--tall">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke="rgba(148,163,184,0.15)" />
            <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }} minTickGap={40} />
            <YAxis
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              tickFormatter={(v) => `${v}%`}
              width={48}
            />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #334155' }}
              formatter={(v) => `${Number(v).toFixed(2)}%`}
            />
            <Legend />
            <Line type="monotone" dataKey="Portfolio" stroke="#2dd4bf" dot={false} strokeWidth={2} />
            <Line type="monotone" dataKey="S&P 500" stroke="#94a3b8" dot={false} strokeWidth={1.5} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
