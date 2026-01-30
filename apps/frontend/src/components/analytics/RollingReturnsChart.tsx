'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

interface RollingReturnsChartProps {
  data: Array<{
    date: string
    '7d': number
    '30d': number
    '90d': number
  }>
  selectedPeriod: '7d' | '30d' | '90d'
  onPeriodChange: (period: '7d' | '30d' | '90d') => void
}

export default function RollingReturnsChart({ data, selectedPeriod, onPeriodChange }: RollingReturnsChartProps) {
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button
          onClick={() => onPeriodChange('7d')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            selectedPeriod === '7d'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground hover:bg-muted/80'
          }`}
        >
          7-Day
        </button>
        <button
          onClick={() => onPeriodChange('30d')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            selectedPeriod === '30d'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground hover:bg-muted/80'
          }`}
        >
          30-Day
        </button>
        <button
          onClick={() => onPeriodChange('90d')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            selectedPeriod === '90d'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground hover:bg-muted/80'
          }`}
        >
          90-Day
        </button>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorReturn" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => new Date(value).toLocaleDateString()}
          />
          <YAxis tick={{ fontSize: 12 }} tickFormatter={(value) => `${value}%`} />
          <Tooltip
            labelFormatter={(value) => new Date(value).toLocaleDateString()}
            formatter={(value: number) => [`${value.toFixed(2)}%`, 'Return']}
          />
          <Area
            type="monotone"
            dataKey={selectedPeriod}
            stroke="#0ea5e9"
            fillOpacity={1}
            fill="url(#colorReturn)"
            name="Rolling Return"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
