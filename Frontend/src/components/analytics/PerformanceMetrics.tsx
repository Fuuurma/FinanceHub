'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { PerformanceMetrics } from '@/lib/types/portfolio-analytics'
import { TrendingUp, TrendingDown, Activity, Target, BarChart3, Percent } from 'lucide-react'
import { cn } from '@/lib/utils'

interface PerformanceMetricsProps {
  metrics: PerformanceMetrics
  className?: string
}

export function PerformanceMetrics({ metrics, className }: PerformanceMetricsProps) {
  const formatPercent = (value: number | null) => {
    if (value === null || value === undefined) return 'N/A'
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  const formatNumber = (value: number | null) => {
    if (value === null || value === undefined) return 'N/A'
    return value.toFixed(2)
  }

  const formatCurrency = (value: number | null) => {
    if (value === null || value === undefined) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value)
  }

  const isPositiveReturn = metrics.total_return >= 0

  return (
    <div className={cn('grid gap-4 md:grid-cols-2 lg:grid-cols-4', className)}>
      <Card className="border-l-4 border-l-green-500">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Total Return
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className={cn(
            'text-3xl font-bold',
            isPositiveReturn ? 'text-green-600' : 'text-red-600'
          )}>
            {formatPercent(metrics.total_return_percent)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {formatCurrency(metrics.total_return)}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Annualized Return
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className={cn(
            'text-3xl font-bold',
            metrics.annualized_return >= 0 ? 'text-green-600' : 'text-red-600'
          )}>
            {formatPercent(metrics.annualized_return)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            CAGR over {metrics.time_period}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Risk Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-xs text-muted-foreground">Volatility</span>
              <span className="text-sm font-medium">{formatPercent(metrics.volatility)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-muted-foreground">Sharpe Ratio</span>
              <span className={cn(
                'text-sm font-medium',
                (metrics.sharpe_ratio ?? 0) >= 1 ? 'text-green-600' : (metrics.sharpe_ratio ?? 0) >= 0 ? 'text-yellow-600' : 'text-red-600'
              )}>
                {formatNumber(metrics.sharpe_ratio)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-muted-foreground">Win Rate</span>
              <span className="text-sm font-medium">{formatPercent(metrics.win_rate)}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Target className="h-4 w-4" />
            Max Drawdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-red-600">
            {formatPercent(metrics.max_drawdown_percent)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Peak to trough decline
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Best Day
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xl font-bold text-green-600">
            {metrics.best_day ? formatCurrency(metrics.best_day.value) : 'N/A'}
          </p>
          {metrics.best_day && (
            <p className="text-xs text-muted-foreground mt-1">
              {new Date(metrics.best_day.date).toLocaleDateString()}
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <TrendingDown className="h-4 w-4" />
            Worst Day
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xl font-bold text-red-600">
            {metrics.worst_day ? formatCurrency(metrics.worst_day.value) : 'N/A'}
          </p>
          {metrics.worst_day && (
            <p className="text-xs text-muted-foreground mt-1">
              {new Date(metrics.worst_day.date).toLocaleDateString()}
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Percent className="h-4 w-4" />
            Alpha vs S&P 500
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className={cn(
            'text-xl font-bold',
            (metrics.alpha_vs_sp500 ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'
          )}>
            {formatPercent(metrics.alpha_vs_sp500)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Excess return vs benchmark
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Beta vs S&P 500
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xl font-bold">
            {formatNumber(metrics.beta_vs_sp500)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Market sensitivity
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
