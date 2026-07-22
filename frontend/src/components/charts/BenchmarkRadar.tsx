import {
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import type { AnalyzeResponse } from '../../types/analytics'

type Props = {
  radar: AnalyzeResponse['radar']
}

export function BenchmarkRadar({ radar }: Props) {
  if (!radar.length) {
    return (
      <div className="chart-card">
        <h3>Sector benchmark radar</h3>
        <p className="muted">No benchmark data available.</p>
      </div>
    )
  }

  // Compare Sharpe across sectors: portfolio vs each sector ETF
  const data = radar.map((r) => ({
    sector: r.sector,
    Portfolio: Number(r.portfolio_sharpe.toFixed(2)),
    Benchmark: Number(r.benchmark_sharpe.toFixed(2)),
  }))

  return (
    <div className="chart-card">
      <h3>Risk radar vs sector ETFs (Sharpe)</h3>
      <div className="chart-h chart-h--tall">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data}>
            <PolarGrid stroke="rgba(148,163,184,0.25)" />
            <PolarAngleAxis dataKey="sector" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <PolarRadiusAxis tick={{ fill: '#64748b', fontSize: 10 }} />
            <Radar name="Portfolio" dataKey="Portfolio" stroke="#2dd4bf" fill="#2dd4bf" fillOpacity={0.25} />
            <Radar name="Sector ETF" dataKey="Benchmark" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.15} />
            <Legend />
            <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
