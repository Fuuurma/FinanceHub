'use client'

import { Bar, BarChart, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'

interface PerformanceChartProps {
  data: {
    symbol: string
    return: number
    current_value: number
  }[]
}

export function PerformanceChart({ data }: PerformanceChartProps) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="symbol" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip 
          formatter={(value, name, props) => (
            <div>
              <p className="font-semibold">{name}</p>
              <p>Return: {typeof value === 'number' ? `${value.toFixed(2)}%` : value}</p>
            </div>
          )}
        />
        <Legend />
        <Bar 
          dataKey="return" 
          fill="#8884d8"
          name="Return %"
          radius={[4, 4, 0, 0]}
        />
        <Bar 
          dataKey="current_value" 
          fill="#82ca9d"
          name="Current Value"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}
