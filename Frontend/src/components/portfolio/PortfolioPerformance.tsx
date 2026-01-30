'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import type { PortfolioHistory, PortfolioMetrics } from '@/lib/types'
import type { PnLHistoryPoint } from '@/lib/types/holdings'
import { TrendingUp, TrendingDown, Activity, Percent, RefreshCw } from 'lucide-react'
import { HoldingsPnLChart } from '@/components/charts/HoldingsPnLChart'
import { useMemo } from 'react'

interface PortfolioPerformanceProps {
  history: PortfolioHistory[]
  metrics: PortfolioMetrics | null
  period: string
  onPeriodChange: (period: '1m' | '3m' | '6m' | '1y' | 'all') => void
}

export default function PortfolioPerformance({ history, metrics, period, onPeriodChange }: PortfolioPerformanceProps) {
  const periods = [
    { value: '1m', label: '1M' },
    { value: '3m', label: '3M' },
    { value: '6m', label: '6M' },
    { value: '1y', label: '1Y' },
    { value: 'all', label: 'All' },
  ] as const

  const pnlHistoryData: PnLHistoryPoint[] = useMemo(() => {
    if (history.length === 0) return []

    const firstValue = history[0]?.value || 0
    return history.map((point) => ({
      date: point.date,
      value: point.value,
      pnl: point.value - firstValue,
      pnl_percent: firstValue > 0 ? ((point.value - firstValue) / firstValue) * 100 : 0,
    }))
  }, [history])

  const maxValue = Math.max(...history.map((h) => h.value))
  const minValue = Math.min(...history.map((h) => h.value))
  const range = maxValue - minValue

  if (history.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance</CardTitle>
          <CardDescription>Portfolio performance over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            No historical data available
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Performance</CardTitle>
            <CardDescription>Portfolio performance over time</CardDescription>
          </div>
          <div className="flex gap-1">
            {periods.map((p) => (
              <button
                key={p.value}
                onClick={() => onPeriodChange(p.value)}
                className={cn(
                  'px-3 py-1 text-sm rounded-md transition-colors',
                  period === p.value
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted'
                )}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* P&L Chart */}
        <div className="h-80">
          <HoldingsPnLChart data={pnlHistoryData} loading={false} />
        </div>

        {/* Metrics Grid */}
        {metrics && (
          <div className="grid gap-4 md:grid-cols-4 mt-6">
            <div className="p-4 rounded-lg bg-muted/50">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Percent className="w-4 h-4" />
                <span className="text-sm">Total Return</span>
              </div>
              <p className={cn('text-2xl font-bold', metrics.total_return >= 0 ? 'text-green-600' : 'text-red-600')}>
                {formatPercent(metrics.total_return_percent)}
              </p>
            </div>

            <div className="p-4 rounded-lg bg-muted/50">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Activity className="w-4 h-4" />
                <span className="text-sm">Volatility</span>
              </div>
              <p className="text-2xl font-bold">{formatPercent(metrics.volatility)}</p>
            </div>

            <div className="p-4 rounded-lg bg-muted/50">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm">Sharpe Ratio</span>
              </div>
              <p className="text-2xl font-bold">{metrics.sharpe_ratio.toFixed(2)}</p>
            </div>

            <div className="p-4 rounded-lg bg-muted/50">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <TrendingDown className="w-4 h-4" />
                <span className="text-sm">Max Drawdown</span>
              </div>
              <p className="text-2xl font-bold text-red-600">-{formatPercent(metrics.max_drawdown_percent)}</p>
            </div>
          </div>
        )}

        {/* Additional Metrics */}
        {metrics && (
          <div className="grid gap-4 md:grid-cols-2 mt-4">
            <div className="flex justify-between p-3 rounded-lg bg-muted/30">
              <span className="text-muted-foreground">Annualized Return</span>
              <span className="font-medium">{formatPercent(metrics.annualized_return)}</span>
            </div>
            <div className="flex justify-between p-3 rounded-lg bg-muted/30">
              <span className="text-muted-foreground">Alpha</span>
              <span className={cn('font-medium', metrics.alpha >= 0 ? 'text-green-600' : 'text-red-600')}>
                {metrics.alpha >= 0 ? '+' : ''}{metrics.alpha.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between p-3 rounded-lg bg-muted/30">
              <span className="text-muted-foreground">Beta</span>
              <span className="font-medium">{metrics.beta.toFixed(2)}</span>
            </div>
            <div className="flex justify-between p-3 rounded-lg bg-muted/30">
              <span className="text-muted-foreground">Max Drawdown</span>
              <span className="font-medium text-red-600">-{formatCurrency(metrics.max_drawdown)}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
