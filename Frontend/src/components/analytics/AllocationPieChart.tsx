'use client'

import { Pie, PieChart, Cell, ResponsiveContainer } from 'recharts'

interface AllocationPieChartProps {
  data: {
    name: string
    value: number
    percentage: string
  }[]
}

export function AllocationPieChart({ data }: AllocationPieChartProps) {
  const COLORS = ['#3B82F6', '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8B5CF6', '#1aff1a']

  const RADIAN = 360

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={(entry) => `${entry.name}: ${entry.percentage}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  )
}
