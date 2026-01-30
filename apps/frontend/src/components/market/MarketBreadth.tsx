'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  ArrowUp,
  ArrowDown,
  Minus,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Activity,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { format, subDays } from 'date-fns'

interface MarketBreadthData {
  date: string
  advances: number
  declines: number
  unchanged: number
  newHighs: number
  newLows: number
  trin: number
  aDLine: number
}

interface MarketBreadthProps {
  className?: string
}

const TIMEFRAMES = [
  { value: '1d', label: '1 Day' },
  { value: '5d', label: '5 Days' },
  { value: '1m', label: '1 Month' },
  { value: '3m', label: '3 Months' },
  { value: '6m', label: '6 Months' },
  { value: '1y', label: '1 Year' },
]

function generateMockData(days: number): MarketBreadthData[] {
  const data: MarketBreadthData[] = []
  let aDLine = 0

  for (let i = days; i >= 0; i--) {
    const date = subDays(new Date(), i)
    const advances = Math.floor(Math.random() * 1500) + 800
    const declines = Math.floor(Math.random() * 1200) + 600
    const unchanged = Math.floor(Math.random() * 300) + 100
    const netAdvances = advances - declines
    aDLine += netAdvances

    data.push({
      date: format(date, 'yyyy-MM-dd'),
      advances,
      declines,
      unchanged,
      newHighs: Math.floor(Math.random() * 50) + 5,
      newLows: Math.floor(Math.random() * 40) + 2,
      trin: parseFloat((Math.random() * 2 + 0.5).toFixed(2)),
      aDLine,
    })
  }

  return data
}

function formatNumber(value: number): string {
  if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return value.toString()
}

function formatTrin(value: number): string {
  return value.toFixed(2)
}

function getTrinColor(value: number): string {
  if (value < 0.8) return 'text-green-600'
  if (value > 1.2) return 'text-red-600'
  return 'text-yellow-600'
}

function getBreadthColor(advances: number, declines: number): string {
  const ratio = advances / (advances + declines)
  if (ratio > 0.6) return 'text-green-600'
  if (ratio < 0.4) return 'text-red-600'
  return 'text-yellow-600'
}

export function MarketBreadth({ className }: MarketBreadthProps) {
  const [timeframe, setTimeframe] = useState('1m')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<MarketBreadthData[]>([])
  const [chartType, setChartType] = useState<'adLine' | 'highsLows' | 'trin'>('adLine')

  const days = useMemo(() => {
    switch (timeframe) {
      case '1d': return 1
      case '5d': return 5
      case '1m': return 30
      case '3m': return 90
      case '6m': return 180
      case '1y': return 365
      default: return 30
    }
  }, [timeframe])

  useEffect(() => {
    setLoading(true)
    const timer = setTimeout(() => {
      const mockData = generateMockData(days)
      setData(mockData)
      setLoading(false)
    }, 800)

    return () => clearTimeout(timer)
  }, [timeframe, days])

  const latest = data[data.length - 1]

  const advancesPercent = latest
    ? ((latest.advances / (latest.advances + latest.declines + latest.unchanged)) * 100).toFixed(1)
    : '0'
  const declinesPercent = latest
    ? ((latest.declines / (latest.advances + latest.declines + latest.unchanged)) * 100).toFixed(1)
    : '0'

  if (loading) {
    return (
      <Card className={cn('h-full', className)}>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg">Market Breadth</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-[250px] w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('h-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Market Breadth
          </CardTitle>
          <div className="flex items-center gap-2">
            <Select value={timeframe} onValueChange={setTimeframe}>
              <SelectTrigger className="w-24 h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIMEFRAMES.map((tf) => (
                  <SelectItem key={tf.value} value={tf.value}>
                    {tf.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" className="h-8 w-8">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-green-50 dark:bg-green-950/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-green-700 dark:text-green-400">
              <ArrowUp className="h-4 w-4" />
              <span className="text-sm font-medium">Advancing</span>
            </div>
            <div className="text-2xl font-bold mt-1">
              {latest ? formatNumber(latest.advances) : '0'}
            </div>
            <div className="text-sm text-green-600 dark:text-green-500">
              {advancesPercent}%
            </div>
          </div>

          <div className="bg-red-50 dark:bg-red-950/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
              <ArrowDown className="h-4 w-4" />
              <span className="text-sm font-medium">Declining</span>
            </div>
            <div className="text-2xl font-bold mt-1">
              {latest ? formatNumber(latest.declines) : '0'}
            </div>
            <div className="text-sm text-red-600 dark:text-red-500">
              {declinesPercent}%
            </div>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-2 mb-4">
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-green-600">
              <TrendingUp className="h-3 w-3" />
              <span className="text-xs">Highs</span>
            </div>
            <div className="font-semibold">{latest ? latest.newHighs : 0}</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-red-600">
              <TrendingDown className="h-3 w-3" />
              <span className="text-xs">Lows</span>
            </div>
            <div className="font-semibold">{latest ? latest.newLows : 0}</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1">
              <Minus className="h-3 w-3" />
              <span className="text-xs">Unch</span>
            </div>
            <div className="font-semibold">{latest ? formatNumber(latest.unchanged) : 0}</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1">
              <Activity className="h-3 w-3" />
              <span className="text-xs">TRIN</span>
            </div>
            <div className={cn('font-semibold', latest && getTrinColor(latest.trin))}>
              {latest ? formatTrin(latest.trin) : '0'}
            </div>
          </div>
        </div>

        <div className="flex gap-2 mb-4">
          <Button
            variant={chartType === 'adLine' ? 'default' : 'outline'}
            size="sm"
            className="flex-1"
            onClick={() => setChartType('adLine')}
          >
            A/D Line
          </Button>
          <Button
            variant={chartType === 'highsLows' ? 'default' : 'outline'}
            size="sm"
            className="flex-1"
            onClick={() => setChartType('highsLows')}
          >
            Highs/Lows
          </Button>
          <Button
            variant={chartType === 'trin' ? 'default' : 'outline'}
            size="sm"
            className="flex-1"
            onClick={() => setChartType('trin')}
          >
            TRIN
          </Button>
        </div>

        <ResponsiveContainer width="100%" height={200}>
          {chartType === 'trin' ? (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => format(new Date(value), 'MMM d')}
                interval={Math.floor(data.length / 6)}
              />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => value.toFixed(1)}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: 'var(--radius)',
                }}
                labelFormatter={(label) => format(new Date(label), 'MMM d, yyyy')}
                formatter={(value: number) => [value.toFixed(2), 'TRIN']}
              />
              <ReferenceLine y={1} stroke="orange" strokeDasharray="5 5" />
              <Line
                type="monotone"
                dataKey="trin"
                stroke="#eab308"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          ) : chartType === 'highsLows' ? (
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => format(new Date(value), 'MMM d')}
                interval={Math.floor(data.length / 6)}
              />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: 'var(--radius)',
                }}
                labelFormatter={(label) => format(new Date(label), 'MMM d, yyyy')}
              />
              <Area
                type="monotone"
                dataKey="newHighs"
                stackId="1"
                stroke="#22c55e"
                fill="#22c55e"
                fillOpacity={0.6}
                name="New Highs"
              />
              <Area
                type="monotone"
                dataKey="newLows"
                stackId="2"
                stroke="#ef4444"
                fill="#ef4444"
                fillOpacity={0.6}
                name="New Lows"
              />
            </AreaChart>
          ) : (
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => format(new Date(value), 'MMM d')}
                interval={Math.floor(data.length / 6)}
              />
              <YAxis
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => {
                  if (Math.abs(value) >= 1000) return (value / 1000).toFixed(0) + 'K'
                  return value.toString()
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: 'var(--radius)',
                }}
                labelFormatter={(label) => format(new Date(label), 'MMM d, yyyy')}
                formatter={(value: number) => [value.toLocaleString(), 'A/D Line']}
              />
              <ReferenceLine y={0} stroke="gray" />
              <Area
                type="monotone"
                dataKey="aDLine"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
                name="A/D Line"
              />
            </AreaChart>
          )}
        </ResponsiveContainer>

        <div className="mt-2 text-xs text-center text-muted-foreground">
          {timeframe === '1d' ? 'Intraday' : `${days} day`} market breadth analysis
        </div>
      </CardContent>
    </Card>
  )
}
