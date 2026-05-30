import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export default function PowerChart({ points }) {
  return (
    <div className="rounded-3xl border border-cyan-900/10 bg-white/80 p-5 shadow-panel backdrop-blur-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Live Power Feed</h2>
        <p className="font-mono text-xs uppercase tracking-wide text-slate-500">Rolling window</p>
      </div>

      <div className="h-64 w-full sm:h-80">
        <ResponsiveContainer>
          <LineChart data={points} margin={{ top: 12, right: 8, left: -10, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#d5e5ef" />
            <XAxis dataKey="tick" tick={{ fontSize: 12, fill: '#3d5567' }} />
            <YAxis
              domain={[0, 20]}
              tick={{ fontSize: 12, fill: '#3d5567' }}
              label={{ value: 'Watts', angle: -90, position: 'insideLeft', fill: '#3d5567' }}
            />
            <Tooltip
              contentStyle={{
                borderRadius: '14px',
                border: '1px solid #dcecf4',
                backgroundColor: 'rgba(245, 252, 255, 0.95)',
              }}
            />
            <Line
              type="monotone"
              dataKey="current_power"
              stroke="#0f8f83"
              strokeWidth={3}
              dot={false}
              isAnimationActive
              animationDuration={320}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
