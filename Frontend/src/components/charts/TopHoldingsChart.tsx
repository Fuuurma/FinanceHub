'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import type { Holding } from '@/lib/types/holdings'
import type { PortfolioHolding } from '@/lib/types/portfolio'
import { ASSET_CLASS_COLORS } from '@/lib/types/holdings'
import { cn } from '@/lib/utils'

type HoldingItem = Holding | PortfolioHolding

interface TopHoldingsChartProps {
  holdings: HoldingItem[]
  loading?: boolean
  topN?: number
}

function getAssetClass(holding: HoldingItem): string {
  if ('asset_class' in holding) {
    return holding.asset_class
  }
  return holding.asset_type || 'other'
}

export function TopHoldingsChart({
  holdings,
  loading = false,
  topN = 10,
}: TopHoldingsChartProps) {
  if (loading) {
    return (
      <div className="h-[400px] w-full bg-muted animate-pulse rounded-lg" />
    )
  }

  const topHoldings = [...holdings]
    .sort((a, b) => b.current_value - a.current_value)
    .slice(0, topN)

  if (topHoldings.length === 0) {
    return (
      <div className="h-[400px] w-full flex items-center justify-center bg-muted/50 rounded-lg">
        <p className="text-muted-foreground">No holdings data available</p>
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

  const formatPercent = (value: number) => `${value.toFixed(1)}%`

  interface TooltipProps {
    active?: boolean
    payload?: Array<{
      payload: {
        symbol: string
        current_value: number
        weight: number
        unrealized_pnl: number
        unrealized_pnl_percent: number
      }
    }>
  }

  const CustomTooltip = ({ active, payload }: TooltipProps) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border rounded-lg shadow-lg p-3">
          <p className="font-medium mb-2">{data.symbol}</p>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">
              Value: {formatCurrency(data.current_value)}
            </p>
            <p className="text-sm text-muted-foreground">
              Weight: {formatPercent(data.weight)}
            </p>
            <p className="text-sm text-muted-foreground">
              P&L: {data.unrealized_pnl >= 0 ? '+' : ''}{formatCurrency(data.unrealized_pnl)}
              {' '}
              ({data.unrealized_pnl_percent >= 0 ? '+' : ''}{data.unrealized_pnl_percent.toFixed(2)}%)
            </p>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="h-[400px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={topHoldings}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 60, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis
            type="number"
            tickFormatter={formatCurrency}
            tick={{ fontSize: 12, fill: '#6B7280' }}
            axisLine={{ stroke: '#E5E7EB' }}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="symbol"
            tick={{ fontSize: 12, fill: '#6B7280' }}
            axisLine={false}
            tickLine={false}
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="current_value" radius={[0, 4, 4, 0]}>
            {topHoldings.map((holding, index) => (
              <Cell
                key={`cell-${index}`}
                fill={
                  ASSET_CLASS_COLORS[
                    getAssetClass(holding) as keyof typeof ASSET_CLASS_COLORS
                  ] || '#6B7280'
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
