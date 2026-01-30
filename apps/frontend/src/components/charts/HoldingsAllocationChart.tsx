'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import type { AssetAllocationItem } from '@/lib/types/holdings'
import { ASSET_CLASS_COLORS } from '@/lib/types/holdings'
import { cn } from '@/lib/utils'

interface HoldingsAllocationChartProps {
  data: AssetAllocationItem[]
  loading?: boolean
  type?: 'pie' | 'donut'
}

export function HoldingsAllocationChart({
  data,
  loading = false,
  type = 'donut',
}: HoldingsAllocationChartProps) {
  if (loading) {
    return (
      <div className="h-[300px] w-full bg-muted animate-pulse rounded-lg" />
    )
  }

  if (data.length === 0) {
    return (
      <div className="h-[300px] w-full flex items-center justify-center bg-muted/50 rounded-lg">
        <p className="text-muted-foreground">No allocation data available</p>
      </div>
    )
  }

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)

  const RADIAN = Math.PI / 180
  const renderCustomizedLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
  }: {
    cx: number
    cy: number
    midAngle: number
    innerRadius: number
    outerRadius: number
    percent: number
  }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    if (percent < 0.05) return null

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
        className="text-xs font-medium"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  interface TooltipPayloadItem {
    payload: {
      asset_class: string
      value: number
      percentage: number
      holdings_count: number
    }
  }

  interface TooltipProps {
    active?: boolean
    payload?: TooltipPayloadItem[]
  }

  const CustomTooltip = ({ active, payload }: TooltipProps) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border rounded-lg shadow-lg p-3">
          <p className="font-medium capitalize mb-1">
            {data.asset_class.replace('_', ' ')}
          </p>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">
              Value: {formatCurrency(data.value)}
            </p>
            <p className="text-sm text-muted-foreground">
              Percentage: {data.percentage.toFixed(1)}%
            </p>
            <p className="text-sm text-muted-foreground">
              Holdings: {data.holdings_count}
            </p>
          </div>
        </div>
      )
    }
    return null
  }

  interface LegendProps {
    payload: Array<{
      color: string
      value: string
    }>
  }

  const renderLegend = (props: LegendProps) => {
    const { payload } = props

    return (
      <ul className="flex flex-wrap justify-center gap-4 mt-4">
        {payload.map((entry, index) => (
          <li key={`legend-${index}`} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm capitalize">
              {entry.value.replace('_', ' ')}
            </span>
          </li>
        ))}
      </ul>
    )
  }

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomizedLabel}
            outerRadius={type === 'donut' ? 100 : 120}
            innerRadius={type === 'donut' ? 60 : 0}
            fill="#8884d8"
            dataKey="value"
            nameKey="asset_class"
            paddingAngle={2}
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={
                  ASSET_CLASS_COLORS[
                    entry.asset_class as keyof typeof ASSET_CLASS_COLORS
                  ] || '#6B7280'
                }
              />
            ))}
          </Pie>
          <Tooltip content={CustomTooltip as any} />
          <Legend content={renderLegend as any} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
