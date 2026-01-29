'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface PerformanceAttributionChartProps {
  data: Array<{
    symbol: string
    contribution: number
    value: number
  }>
}

export default function PerformanceAttributionChart({ data }: PerformanceAttributionChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={data.sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution))}
        layout="horizontal"
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" tick={{ fontSize: 12 }} tickFormatter={(value) => `${value}%`} />
        <YAxis dataKey="symbol" type="category" width={80} tick={{ fontSize: 12 }} />
        <Tooltip
          formatter={(value: number, name: string) => {
            if (name === 'contribution') return [`${value.toFixed(2)}%`, 'Contribution']
            return [`$${value.toLocaleString()}`, 'Value']
          }}
        />
        <Bar
          dataKey="contribution"
          fill="#3b82f6"
          name="contribution"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.contribution >= 0 ? '#22c55e' : '#ef4444'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
