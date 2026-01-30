"use client"

import { useState, useMemo, useRef, EffectCallback, DependencyList } from 'react'
import { createChart, IChartApi, ColorType, Time, ISeriesApi } from 'lightweight-charts'
import { useTheme } from 'next-themes'
import { TrendingDown, TrendingUp, Calendar, Percent, AlertTriangle, Download, RefreshCw } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

export interface DrawdownData {
  date: string
  drawdown: number
  peak: number
  trough: number
  recovery: number | null
}

export interface DrawdownMetrics {
  maxDrawdown: number
  maxDrawdownDate: string
  currentDrawdown: number
  avgDrawdown: number
  maxRecovery: number
  timeInDrawdown: number
  avgTimeToRecovery: number
}

export interface DrawdownChartProps {
  data?: DrawdownData[]
  metrics?: DrawdownMetrics
  symbol?: string
  loading?: boolean
  error?: string
  className?: string
}

const CHART_COLORS = {
  background: 'transparent',
  text: '#94a3b8',
  grid: '#334155',
  drawdown: '#ef4444',
  zero: '#22c55e',
  area: 'rgba(239, 68, 68, 0.3)',
}

export function DrawdownChart({
  data = [],
  metrics,
  symbol,
  loading = false,
  error,
  className,
}: DrawdownChartProps) {
  const { theme } = useTheme()
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Area'> | null>(null)
  const [timeframe, setTimeframe] = useState('1Y')
  const [chartType, setChartType] = useState<'drawdown' | 'value'>('drawdown')

  const initChart = () => {
    if (!chartContainerRef.current) return
    chartContainerRef.current.style.width = '100%'
    chartContainerRef.current.style.height = '300px'

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: CHART_COLORS.background },
        textColor: theme === 'dark' ? '#94a3b8' : '#64748b',
      },
      grid: {
        vertLines: { color: theme === 'dark' ? '#334155' : '#e2e8f0' },
        horzLines: { color: theme === 'dark' ? '#334155' : '#e2e8f0' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 300,
      crosshair: { mode: 0 },
    })

    chartRef.current = chart

    const chartAny = chart as unknown as { addAreaSeries(options?: unknown): ISeriesApi<'Area'> }
    const series = chartAny.addAreaSeries({
      lineColor: CHART_COLORS.drawdown,
      topColor: CHART_COLORS.area,
      bottomColor: 'rgba(239, 68, 68, 0.0)',
      lineWidth: 2,
      priceFormat: {
        type: 'custom',
        formatter: (price: number) => `${(price * 100).toFixed(1)}%`,
      },
      priceScaleId: 'left',
    })

    seriesRef.current = series
    chart.priceScale('left').applyOptions({
      scaleMargins: { top: 0.1, bottom: 0.1 },
    })

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }

    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }

  const chartData = useMemo(() => {
    return data.map(d => ({
      time: d.date as Time,
      value: d.drawdown * 100,
    }))
  }, [data])

  const updateChart = () => {
    if (seriesRef.current && chartData.length > 0) {
      seriesRef.current.setData(chartData)
    }
  }

  if (typeof window !== 'undefined') {
    if (data.length > 0 && !seriesRef.current) {
      initChart()
    }
    if (seriesRef.current && chartData.length > 0) {
      updateChart()
    }
  }

  const handleExport = () => {
    const csv = ['Date,Drawdown,Peak,Trough,Recovery', ...data.map(d =>
      `${d.date},${(d.drawdown * 100).toFixed(2)}%,${d.peak},${d.trough},${d.recovery || 'N/A'}`
    )].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${symbol || 'drawdown'}-analysis.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-48 mt-2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-72 w-full" />
        </CardContent>
      </Card>
    )
  }

  if (error || (!data.length && !metrics)) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingDown className="h-5 w-5" />
            Drawdown Analysis
          </CardTitle>
          <CardDescription>Portfolio drawdown and recovery analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No drawdown data available'}</p>
        </CardContent>
      </Card>
    )
  }

  const maxDD = metrics?.maxDrawdown || 0
  const currentDD = metrics?.currentDrawdown || 0

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5" />
              Drawdown Analysis
              {symbol && <Badge variant="outline">{symbol}</Badge>}
            </CardTitle>
            <CardDescription>Portfolio drawdown and recovery analysis</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={timeframe} onValueChange={setTimeframe}>
              <SelectTrigger className="w-24 h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1M">1M</SelectItem>
                <SelectItem value="3M">3M</SelectItem>
                <SelectItem value="6M">6M</SelectItem>
                <SelectItem value="1Y">1Y</SelectItem>
                <SelectItem value="ALL">All</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" onClick={handleExport}>
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4 p-4 bg-muted/30 rounded-lg">
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
              <TrendingDown className="h-4 w-4" />
              <span className="text-xs">Max Drawdown</span>
            </div>
            <div className="text-lg font-semibold text-red-500">
              {formatPercent(maxDD)}
            </div>
            <div className="text-xs text-muted-foreground">{metrics?.maxDrawdownDate || 'N/A'}</div>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
              <TrendingDown className="h-4 w-4" />
              <span className="text-xs">Current DD</span>
            </div>
            <div className={cn('text-lg font-semibold', currentDD > 0 ? 'text-red-500' : 'text-green-500')}>
              {formatPercent(currentDD)}
            </div>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
              <Percent className="h-4 w-4" />
              <span className="text-xs">Avg Drawdown</span>
            </div>
            <div className="text-lg font-semibold">{formatPercent(metrics?.avgDrawdown || 0)}</div>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
              <Calendar className="h-4 w-4" />
              <span className="text-xs">Time in DD</span>
            </div>
            <div className="text-lg font-semibold">{metrics?.timeInDrawdown || 0}%</div>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
              <TrendingUp className="h-4 w-4" />
              <span className="text-xs">Max Recovery</span>
            </div>
            <div className="text-lg font-semibold text-green-500">
              {formatPercent(metrics?.maxRecovery || 0)}
            </div>
          </div>
        </div>

        <Tabs defaultValue="chart" className="mt-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="chart">Drawdown Chart</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
          </TabsList>

          <TabsContent value="chart" className="mt-4">
            <div ref={chartContainerRef} style={{ width: '100%', height: 300 }} />
          </TabsContent>

          <TabsContent value="analysis" className="mt-4">
            <div className="space-y-4">
              <div className="p-4 bg-muted/30 rounded-lg">
                <h4 className="font-medium mb-2">Drawdown Events</h4>
                <p className="text-sm text-muted-foreground">
                  Average time to recovery: {metrics?.avgTimeToRecovery || 'N/A'} days
                </p>
              </div>
              <div className="p-4 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 mb-2">
                  <AlertTriangle className="h-4 w-4" />
                  <span className="font-medium">Risk Warning</span>
                </div>
                <p className="text-sm text-amber-600 dark:text-amber-500">
                  {maxDD > 0.2 ? 'High drawdown detected. Consider reducing position sizes.' :
                   maxDD > 0.1 ? 'Moderate drawdown. Monitor positions closely.' :
                   'Drawdown is within normal ranges.'}
                </p>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">
            {data.length} data points · Drawdown calculated from portfolio peaks
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
