'use client'

import { useMemo, useState } from 'react'
import { Area, AreaChart, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import { TrendingUp, TrendingDown, Activity, Target, Calendar, BarChart3 } from 'lucide-react'

export interface PerformanceDataPoint {
  date: string
  value: number
  benchmark?: number
  return?: number
  benchmarkReturn?: number
}

export interface PerformanceMetrics {
  totalReturn: number
  totalReturnPercent: number
  annualizedReturn: number
  volatility: number
  sharpeRatio: number
  maxDrawdown: number
  maxDrawdownPercent: number
  alpha: number
  beta: number
  sortinoRatio: number
  informationRatio: number
  trackingError: number
  winRate: number
  avgWin: number
  avgLoss: number
  profitFactor: number
}

interface PerformanceChartProps {
  data: PerformanceDataPoint[]
  metrics: PerformanceMetrics | null
  benchmarkData?: { name: string; data: PerformanceDataPoint[] }
  className?: string
}

const periods = [
  { value: '1W', label: '1W', days: 7 },
  { value: '1M', label: '1M', days: 30 },
  { value: '3M', label: '3M', days: 90 },
  { value: '6M', label: '6M', days: 180 },
  { value: '1Y', label: '1Y', days: 365 },
  { value: 'YTD', label: 'YTD', days: -1 },
  { value: 'ALL', label: 'All', days: -2 },
] as const

type Period = typeof periods[number]['value']

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function formatLargeNumber(value: number): string {
  if (Math.abs(value) >= 1000000) return `$${(value / 1000000).toFixed(2)}M`
  if (Math.abs(value) >= 1000) return `$${(value / 1000).toFixed(1)}K`
  return formatCurrency(value)
}

function CustomTooltip({ active, payload, label, data }: { active?: boolean; payload?: Array<{ value: number; dataKey: string; color: string }>; label?: string; data: PerformanceDataPoint[] }) {
  if (!active || !payload || !label) return null

  const point = data.find(d => d.date === label)
  if (!point) return null

  return (
    <div className="bg-background border rounded-lg shadow-lg p-3">
      <p className="text-sm font-medium text-muted-foreground mb-2">{formatDate(label)}</p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-muted-foreground">{entry.dataKey === 'value' ? 'Portfolio' : entry.dataKey}:</span>
          <span className="font-medium">{formatLargeNumber(entry.value)}</span>
        </div>
      ))}
      {point.return !== undefined && (
        <p className={cn('text-sm font-medium mt-2', point.return >= 0 ? 'text-green-600' : 'text-red-600')}>
          {point.return >= 0 ? '+' : ''}{formatPercent(point.return / 100)}
        </p>
      )}
    </div>
  )
}

function MetricCard({ title, value, subValue, icon: Icon, trend }: { title: string; value: string; subValue?: string; icon: typeof TrendingUp; trend?: 'up' | 'down' | 'neutral' }) {
  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-muted-foreground'
  }

  return (
    <div className="p-4 rounded-lg border bg-card">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-muted-foreground">{title}</span>
        <Icon className={cn('h-4 w-4', trendColors[trend || 'neutral'])} />
      </div>
      <p className="text-2xl font-bold">{value}</p>
      {subValue && <p className="text-xs text-muted-foreground mt-1">{subValue}</p>}
    </div>
  )
}

function getFilteredData(data: PerformanceDataPoint[], period: Period): PerformanceDataPoint[] {
  const now = new Date()
  let cutoffDate: Date

  const periodConfig = periods.find(p => p.value === period)
  if (!periodConfig) return data

  if (periodConfig.days === -1) {
    cutoffDate = new Date(now.getFullYear(), 0, 1)
  } else if (periodConfig.days === -2) {
    return data
  } else {
    cutoffDate = new Date(now.getTime() - periodConfig.days * 24 * 60 * 60 * 1000)
  }

  return data.filter(d => new Date(d.date) >= cutoffDate)
}

export function PerformanceChart({ data, metrics, benchmarkData, className }: PerformanceChartProps) {
  const [period, setPeriod] = useState<Period>('1Y')
  const [showBenchmark, setShowBenchmark] = useState(true)
  const [chartType, setChartType] = useState<'value' | 'return'>('value')

  const filteredData = useMemo(() => getFilteredData(data, period), [data, period])

  const chartData = useMemo(() => {
    return filteredData.map(point => {
      const result: Record<string, number | string> = { date: point.date }
      result['Portfolio'] = point.value
      if (showBenchmark && benchmarkData && point.benchmark !== undefined) {
        result['Benchmark'] = point.benchmark
      }
      if (chartType === 'return' && point.return !== undefined) {
        result['Portfolio'] = point.return
        if (showBenchmark && benchmarkData && point.benchmarkReturn !== undefined) {
          result['Benchmark'] = point.benchmarkReturn
        }
      }
      return result
    })
  }, [filteredData, showBenchmark, benchmarkData, chartType])

  const latestValue = filteredData.length > 0 ? filteredData[filteredData.length - 1]?.value || 0 : 0
  const firstValue = filteredData.length > 0 ? filteredData[0]?.value || 0 : 0
  const periodReturn = firstValue > 0 ? ((latestValue - firstValue) / firstValue) * 100 : 0

  const yAxisDomain = useMemo(() => {
    if (chartType === 'return') {
      const returns = filteredData.map(d => d.return || 0)
      const minReturn = Math.min(...returns)
      const maxReturn = Math.max(...returns)
      const padding = (maxReturn - minReturn) * 0.1 || 5
      return [minReturn - padding, maxReturn + padding]
    }
    const values = filteredData.map(d => d.value)
    const minValue = Math.min(...values)
    const maxValue = Math.max(...values)
    const padding = (maxValue - minValue) * 0.1 || 1000
    return [minValue - padding, maxValue + padding]
  }, [filteredData, chartType])

  const chartColors = {
    portfolio: '#22c55e',
    benchmark: '#3b82f6'
  }

  if (data.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Performance</CardTitle>
          <CardDescription>Portfolio performance over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80 flex items-center justify-center text-muted-foreground">
            No historical data available
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Performance
            </CardTitle>
            <CardDescription>Track your portfolio performance over time</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={period} onValueChange={(v) => setPeriod(v as Period)}>
              <SelectTrigger className="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {periods.map(p => (
                  <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={chartType} onValueChange={(v) => setChartType(v as 'value' | 'return')} className="space-y-4">
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="value">Value</TabsTrigger>
              <TabsTrigger value="return">Return</TabsTrigger>
            </TabsList>
            {benchmarkData && (
              <button
                onClick={() => setShowBenchmark(!showBenchmark)}
                className={cn(
                  'text-sm px-3 py-1 rounded-md transition-colors',
                  showBenchmark ? 'bg-primary text-primary-foreground' : 'bg-muted hover:bg-muted/80'
                )}
              >
                {showBenchmark ? 'Hide' : 'Show'} Benchmark
              </button>
            )}
          </div>

          <TabsContent value="value" className="space-y-4">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={chartColors.portfolio} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={chartColors.portfolio} stopOpacity={0} />
                    </linearGradient>
                    {showBenchmark && benchmarkData && (
                      <linearGradient id="benchmarkGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={chartColors.benchmark} stopOpacity={0.3} />
                        <stop offset="95%" stopColor={chartColors.benchmark} stopOpacity={0} />
                      </linearGradient>
                    )}
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={formatDate}
                    tick={{ fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    domain={yAxisDomain as [number, number]}
                    tickFormatter={formatLargeNumber}
                    tick={{ fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip content={<CustomTooltip data={filteredData} />} />
                  <Area
                    type="monotone"
                    dataKey="Portfolio"
                    stroke={chartColors.portfolio}
                    fill="url(#portfolioGradient)"
                    strokeWidth={2}
                  />
                  {showBenchmark && benchmarkData && (
                    <Area
                      type="monotone"
                      dataKey="Benchmark"
                      stroke={chartColors.benchmark}
                      fill="url(#benchmarkGradient)"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                    />
                  )}
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {metrics && (
              <div className="grid gap-4 md:grid-cols-4">
                <MetricCard
                  title="Total Return"
                  value={formatPercent(metrics.totalReturnPercent / 100)}
                  subValue={formatCurrency(metrics.totalReturn)}
                  icon={TrendingUp}
                  trend={metrics.totalReturnPercent >= 0 ? 'up' : 'down'}
                />
                <MetricCard
                  title="Sharpe Ratio"
                  value={metrics.sharpeRatio.toFixed(2)}
                  subValue={`Vol: ${formatPercent(metrics.volatility / 100)}`}
                  icon={Activity}
                />
                <MetricCard
                  title="Max Drawdown"
                  value={`-${formatPercent(metrics.maxDrawdownPercent / 100)}`}
                  subValue={formatCurrency(metrics.maxDrawdown)}
                  icon={TrendingDown}
                />
                <MetricCard
                  title="Alpha"
                  value={metrics.alpha >= 0 ? `+${metrics.alpha.toFixed(2)}` : metrics.alpha.toFixed(2)}
                  subValue={`Beta: ${metrics.beta.toFixed(2)}`}
                  icon={Target}
                  trend={metrics.alpha >= 0 ? 'up' : 'down'}
                />
              </div>
            )}
          </TabsContent>

          <TabsContent value="return" className="space-y-4">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="returnGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={periodReturn >= 0 ? '#22c55e' : '#ef4444'} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={periodReturn >= 0 ? '#22c55e' : '#ef4444'} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={formatDate}
                    tick={{ fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    domain={yAxisDomain as [number, number]}
                    tickFormatter={(v) => `${v.toFixed(1)}%`}
                    tick={{ fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <ReferenceLine y={0} stroke="hsl(var(--muted-foreground))" strokeDasharray="3 3" />
                  <Tooltip content={<CustomTooltip data={filteredData} />} />
                  <Area
                    type="monotone"
                    dataKey="Portfolio"
                    stroke={periodReturn >= 0 ? '#22c55e' : '#ef4444'}
                    fill="url(#returnGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="p-4 rounded-lg bg-muted/50">
              <p className="text-sm text-muted-foreground">Period Return</p>
              <p className={cn('text-3xl font-bold', periodReturn >= 0 ? 'text-green-600' : 'text-red-600')}>
                {periodReturn >= 0 ? '+' : ''}{formatPercent(periodReturn / 100)}
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default PerformanceChart
