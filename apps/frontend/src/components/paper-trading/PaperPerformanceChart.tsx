'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { RefreshCw, TrendingUp, TrendingDown, LineChart as LineChartIcon } from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { apiClient } from '@/lib/api/client'

interface PaperPerformanceChartProps {
  className?: string
}

interface PerformanceDataPoint {
  timestamp: string
  portfolio_value: number
  benchmark: number
}

interface PerformanceResponse {
  data: PerformanceDataPoint[]
  total_return: number
  benchmark_return: number
  period: string
}

export function PaperPerformanceChart({ className }: PaperPerformanceChartProps) {
  const [loading, setLoading] = React.useState(true)
  const [data, setData] = React.useState<PerformanceDataPoint[]>([])
  const [period, setPeriod] = React.useState<string>('7d')
  const [stats, setStats] = React.useState<{
    total_return: number
    benchmark_return: number
  }>({ total_return: 0, benchmark_return: 0 })

  const fetchPerformance = React.useCallback(async () => {
    setLoading(true)
    try {
      const response = await apiClient.get<PerformanceResponse>(
        `/paper-trading/performance?period=${period}`
      )
      setData(response.data || [])
      setStats({
        total_return: response.total_return || 0,
        benchmark_return: response.benchmark_return || 0,
      })
    } catch (error) {
      console.error('Failed to fetch performance:', error)
    } finally {
      setLoading(false)
    }
  }, [period])

  React.useEffect(() => {
    fetchPerformance()
  }, [fetchPerformance])

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    if (period === '1d') {
      return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
      })
    }
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })
  }

  const formatPercent = (value: number) =>
    `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`

  if (loading) {
    return (
      <Card className={cn('rounded-none border-2 border-foreground', className)}>
        <CardHeader className="border-b-2 border-foreground">
          <Skeleton className="h-8 w-48" />
        </CardHeader>
        <CardContent className="p-6">
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('rounded-none border-2 border-foreground', className)}>
      <CardHeader className="border-b-2 border-foreground">
        <div className="flex items-center justify-between">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            <LineChartIcon className="h-5 w-5" />
            Performance
          </CardTitle>
          <div className="flex items-center gap-2">
            <Select value={period} onValueChange={setPeriod}>
              <SelectTrigger className="w-24 rounded-none border-2 font-bold uppercase text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1d">1D</SelectItem>
                <SelectItem value="7d">7D</SelectItem>
                <SelectItem value="30d">30D</SelectItem>
                <SelectItem value="90d">90D</SelectItem>
                <SelectItem value="1y">1Y</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchPerformance}
              className="rounded-none border-2 font-bold uppercase"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div
            className={cn(
              'border-2 border-foreground p-4',
              stats.total_return >= 0 ? 'bg-green-50' : 'bg-red-50'
            )}
          >
            <div className="flex items-center gap-2 mb-2">
              {stats.total_return >= 0 ? (
                <TrendingUp className="h-4 w-4 text-green-600" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-600" />
              )}
              <span className="text-xs font-bold uppercase text-muted-foreground">
                Your Return
              </span>
            </div>
            <p
              className={cn(
                'font-mono text-2xl font-black',
                stats.total_return >= 0 ? 'text-green-600' : 'text-red-600'
              )}
            >
              {formatPercent(stats.total_return)}
            </p>
          </div>
          <div className="border-2 border-foreground p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs font-bold uppercase text-muted-foreground">
                S&P 500
              </span>
            </div>
            <p
              className={cn(
                'font-mono text-2xl font-black',
                stats.benchmark_return >= 0 ? 'text-green-600' : 'text-red-600'
              )}
            >
              {formatPercent(stats.benchmark_return)}
            </p>
          </div>
        </div>

        {data.length === 0 ? (
          <div className="border-2 border-foreground p-12 text-center">
            <LineChartIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-black uppercase text-lg mb-2">
              No Performance Data
            </h3>
            <p className="text-muted-foreground font-mono text-xs">
              Start trading to see your performance over time
            </p>
          </div>
        ) : (
          <div className="border-2 border-foreground p-4">
            <ResponsiveContainer width="100%" height={256}>
              <LineChart data={data}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="hsl(var(--border))"
                />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatTime}
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tickFormatter={(value) => formatCurrency(value as number)}
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  width={80}
                />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="border-2 border-foreground bg-background p-3 shadow-lg">
                          <p className="font-mono text-xs font-bold mb-2">
                            {formatTime(label)}
                          </p>
                          {payload.map((entry, index) => (
                            <p
                              key={index}
                              className="font-mono text-xs"
                              style={{ color: entry.color }}
                            >
                              {entry.name}: {formatCurrency(entry.value as number)}
                            </p>
                          ))}
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="portfolio_value"
                  stroke="#8884d8"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                  name="Portfolio"
                />
                <Line
                  type="monotone"
                  dataKey="benchmark"
                  stroke="#82ca9d"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  activeDot={{ r: 6 }}
                  name="S&P 500"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
