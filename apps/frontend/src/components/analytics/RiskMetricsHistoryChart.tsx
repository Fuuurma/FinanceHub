'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface RiskMetricsHistoryChartProps {
  data: Array<{
    date: string
    volatility: number
    sharpeRatio: number
  }>
}

export default function RiskMetricsHistoryChart({ data }: RiskMetricsHistoryChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => new Date(value).toLocaleDateString()}
        />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip
          labelFormatter={(value) => new Date(value).toLocaleDateString()}
          formatter={(value: number, name: string) => {
            if (name === 'volatility') return [value.toFixed(2), 'Volatility']
            return [value.toFixed(2), 'Sharpe Ratio']
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="volatility"
          stroke="#ef4444"
          name="Volatility"
          strokeWidth={2}
          dot={{ r: 3 }}
        />
        <Line
          type="monotone"
          dataKey="sharpeRatio"
          stroke="#22c55e"
          name="Sharpe Ratio"
          strokeWidth={2}
          dot={{ r: 3 }}
          yAxisId="right"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
