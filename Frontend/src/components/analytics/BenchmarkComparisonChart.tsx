'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface BenchmarkComparisonChartProps {
  data: Array<{
    date: string
    portfolio: number
    benchmark: number
  }>
}

export default function BenchmarkComparisonChart({ data }: BenchmarkComparisonChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => new Date(value).toLocaleDateString()}
        />
        <YAxis tick={{ fontSize: 12 }} tickFormatter={(value) => `${value}%`} />
        <Tooltip
          labelFormatter={(value) => new Date(value).toLocaleDateString()}
          formatter={(value: number) => [`${value.toFixed(2)}%`, '']}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="portfolio"
          stroke="#22c55e"
          name="Portfolio"
          strokeWidth={2}
          dot={{ r: 4 }}
        />
        <Line
          type="monotone"
          dataKey="benchmark"
          stroke="#ef4444"
          name="Benchmark"
          strokeWidth={2}
          dot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
