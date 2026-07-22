import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

const COLORS = ['#2dd4bf', '#38bdf8', '#fbbf24', '#fb7185', '#a3e635', '#c084fc', '#f97316']

type Props = {
  allocation: { ticker: string; weight: number }[]
}

export function AllocationDonut({ allocation }: Props) {
  const data = allocation.map((a) => ({ name: a.ticker, value: a.weight * 100 }))

  return (
    <div className="chart-card">
      <h3>Asset allocation</h3>
      <div className="chart-h">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius="55%"
              outerRadius="80%"
              paddingAngle={2}
            >
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="transparent" />
              ))}
            </Pie>
            <Tooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <ul className="legend">
        {data.map((d, i) => (
          <li key={d.name}>
            <span className="swatch" style={{ background: COLORS[i % COLORS.length] }} />
            {d.name} · {d.value.toFixed(1)}%
          </li>
        ))}
      </ul>
    </div>
  )
}
