"use client"

import { useRef, useEffect, useState, useCallback } from 'react'
import { createChart, ColorType, IChartApi, ISeriesApi, Time } from 'lightweight-charts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { useDownload } from '@/hooks/useDownload'
import { cn } from '@/lib/utils'

interface IVData {
  time: Time
  iv: number
  ivPercentile: number
  ivRank: number
}

export type { IVData as IVData }

interface ImpliedVolatilityChartProps {
  data?: IVData[]
  symbol?: string
  title?: string
  className?: string
}

const CHART_COLORS = {
  background: 'transparent',
  text: '#94a3b8',
  grid: '#334155',
  iv: '#8b5cf6',
  ivFill: 'rgba(139, 92, 246, 0.1)',
  percentile: '#06b6d4',
  rank: '#f59e0b',
}

export function ImpliedVolatilityChart({
  data = [],
  symbol = '',
  title = 'Implied Volatility',
  className,
}: ImpliedVolatilityChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const ivSeriesRef = useRef<ISeriesApi<'Area'> | null>(null)
  const percentileSeriesRef = useRef<ISeriesApi<'Line'> | null>(null)

  const [timeframe, setTimeframe] = useState('1M')
  const [showPercentile, setShowPercentile] = useState(true)

  const { download } = useDownload()

  const initChart = useCallback(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: CHART_COLORS.background },
        textColor: CHART_COLORS.text,
      },
      grid: {
        vertLines: { color: CHART_COLORS.grid },
        horzLines: { color: CHART_COLORS.grid },
      },
      width: chartContainerRef.current.clientWidth,
      height: 300,
      crosshair: { mode: 0 },
      rightPriceScale: { invertScale: false },
    })

    chartRef.current = chart

    const chartAny = chart as unknown as { addLineSeries(options?: unknown): ISeriesApi<'Line'>; addAreaSeries(options?: unknown): ISeriesApi<'Area'> }

    const ivSeries = chartAny.addAreaSeries({
      lineColor: CHART_COLORS.iv,
      topColor: CHART_COLORS.iv,
      bottomColor: CHART_COLORS.ivFill,
      lineWidth: 2,
      priceFormat: { type: 'custom', formatter: (price: number) => `${price.toFixed(1)}%` },
      priceScaleId: 'left',
    })
    ivSeries.applyOptions({ title: 'IV' })
    ivSeriesRef.current = ivSeries

    chart.priceScale('left').applyOptions({ scaleMargins: { top: 0.1, bottom: 0.1 } })

    if (showPercentile) {
      const percentileSeries = chartAny.addLineSeries({
        color: CHART_COLORS.percentile,
        lineWidth: 2,
        priceFormat: { type: 'custom', formatter: (price: number) => `${price.toFixed(0)}%` },
        priceScaleId: 'right',
      })
      percentileSeries.applyOptions({ title: 'Percentile' })
      percentileSeriesRef.current = percentileSeries
      chart.priceScale('right').applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } })
    }

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
  }, [showPercentile])

  useEffect(() => {
    const cleanup = initChart()
    return cleanup
  }, [initChart])

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return

    if (ivSeriesRef.current) {
      ivSeriesRef.current.setData(data.map(d => ({ time: d.time, value: d.iv })))
    }

    if (showPercentile && percentileSeriesRef.current) {
      percentileSeriesRef.current.setData(data.map(d => ({ time: d.time, value: d.ivPercentile })))
    }
  }, [data, showPercentile])

  const handleExport = useCallback(() => {
    if (data.length === 0) return
    const csvContent = ['Date,IV,IV Percentile,IV Rank', ...data.map(d =>
      `${d.time},${d.iv.toFixed(2)},${d.ivPercentile.toFixed(2)},${d.ivRank.toFixed(2)}`
    )].join('\n')
    download(csvContent, { filename: `iv-chart-${symbol}-${new Date().toISOString().split('T')[0]}.csv`, mimeType: 'text/csv' })
  }, [data, download, symbol])

  const currentIV = data.length > 0 ? data[data.length - 1].iv : 0
  const currentPercentile = data.length > 0 ? data[data.length - 1].ivPercentile : 0
  const currentRank = data.length > 0 ? data[data.length - 1].ivRank : 0

  const ivLevel = currentIV < 20 ? 'Low' : currentIV < 40 ? 'Moderate' : currentIV < 60 ? 'Elevated' : currentIV < 80 ? 'High' : 'Extreme'

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg font-semibold">{title}</CardTitle>
            {symbol && <Badge variant="outline">{symbol}</Badge>}
          </div>
          <div className="flex items-center gap-2">
            <Select value={timeframe} onValueChange={setTimeframe}>
              <SelectTrigger className="w-24 h-8"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="1W">1W</SelectItem>
                <SelectItem value="1M">1M</SelectItem>
                <SelectItem value="3M">3M</SelectItem>
                <SelectItem value="6M">6M</SelectItem>
                <SelectItem value="1Y">1Y</SelectItem>
              </SelectContent>
            </Select>
            <button onClick={handleExport} className="px-3 py-1 text-sm bg-secondary hover:bg-secondary/80 rounded-md transition-colors">Export</button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-4 gap-4 mb-4">
          <div className="text-center">
            <div className="text-sm text-muted-foreground">Current IV</div>
            <div className="text-lg font-semibold text-violet-500">{currentIV.toFixed(1)}%</div>
            <Badge variant={ivLevel === 'Low' ? 'secondary' : ivLevel === 'Moderate' ? 'outline' : ivLevel === 'Elevated' ? 'default' : 'destructive'} className="mt-1">{ivLevel}</Badge>
          </div>
          <div className="text-center">
            <div className="text-sm text-muted-foreground">IV Percentile</div>
            <div className="text-lg font-semibold text-cyan-500">{currentPercentile.toFixed(0)}%</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-muted-foreground">IV Rank</div>
            <div className="text-lg font-semibold text-amber-500">{currentRank.toFixed(0)}%</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-muted-foreground">Data Points</div>
            <div className="text-lg font-semibold">{data.length}</div>
          </div>
        </div>
        <div ref={chartContainerRef} className="w-full" />
      </CardContent>
    </Card>
  )
}
