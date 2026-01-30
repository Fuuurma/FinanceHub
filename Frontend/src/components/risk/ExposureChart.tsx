"use client"

import { useRef, useEffect, useState, useCallback } from 'react'
import { createChart, ColorType, IChartApi, ISeriesApi, Time } from 'lightweight-charts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useDownload } from '@/hooks/useDownload'
import { cn } from '@/lib/utils'

interface ExposureData {
  time: Time
  longExposure: number
  shortExposure: number
  netExposure: number
}

interface ExposureChartProps {
  data?: ExposureData[]
  title?: string
  className?: string
}

const CHART_COLORS = {
  background: 'transparent',
  text: '#94a3b8',
  grid: '#334155',
  long: '#22c55e',
  short: '#ef4444',
  net: '#3b82f6',
}

export function ExposureChart({
  data = [],
  title = 'Position Exposure',
  className,
}: ExposureChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const longSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const shortSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const netSeriesRef = useRef<ISeriesApi<'Line'> | null>(null)

  const [timeframe, setTimeframe] = useState('1M')
  const [chartType, setChartType] = useState<'stacked' | 'net'>('stacked')

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
    })

    chartRef.current = chart

    const chartAny = chart as unknown as { addLineSeries(options?: unknown): ISeriesApi<'Line'>; addHistogramSeries(options?: unknown): ISeriesApi<'Histogram'> }

    if (chartType === 'stacked') {
      const longSeries = chartAny.addHistogramSeries({
        priceFormat: { type: 'custom', formatter: (price: number) => `$${(price / 1000000).toFixed(1)}M` },
        priceScaleId: 'left',
      })
      longSeries.applyOptions({ color: CHART_COLORS.long, title: 'Long Exposure' })
      longSeriesRef.current = longSeries

      const shortSeries = chartAny.addHistogramSeries({
        priceFormat: { type: 'custom', formatter: (price: number) => `$${(price / 1000000).toFixed(1)}M` },
        priceScaleId: 'left',
      })
      shortSeries.applyOptions({ color: CHART_COLORS.short, title: 'Short Exposure' })
      shortSeriesRef.current = shortSeries

      chart.priceScale('left').applyOptions({ scaleMargins: { top: 0.1, bottom: 0.1 } })
    } else {
      const netSeries = chartAny.addLineSeries({
        priceFormat: { type: 'custom', formatter: (price: number) => `$${(price / 1000000).toFixed(1)}M` },
        priceScaleId: 'left',
      })
      netSeries.applyOptions({ color: CHART_COLORS.net, title: 'Net Exposure', lineWidth: 2 })
      netSeriesRef.current = netSeries

      chart.priceScale('left').applyOptions({ scaleMargins: { top: 0.1, bottom: 0.1 } })
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
  }, [chartType])

  useEffect(() => {
    const cleanup = initChart()
    return cleanup
  }, [initChart])

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return

    if (chartType === 'stacked' && longSeriesRef.current && shortSeriesRef.current) {
      longSeriesRef.current.setData(data.map(d => ({ time: d.time, value: d.longExposure, color: CHART_COLORS.long })))
      shortSeriesRef.current.setData(data.map(d => ({ time: d.time, value: d.shortExposure, color: CHART_COLORS.short })))
    } else if (chartType === 'net' && netSeriesRef.current) {
      netSeriesRef.current.setData(data.map(d => ({ time: d.time, value: d.netExposure })))
    }
  }, [data, chartType])

  const handleExport = useCallback(() => {
    if (data.length === 0) return
    const csvContent = ['Date,Long Exposure,Short Exposure,Net Exposure', ...data.map(d =>
      `${d.time},${d.longExposure.toFixed(2)},${d.shortExposure.toFixed(2)},${d.netExposure.toFixed(2)}`
    )].join('\n')
    download(csvContent, { filename: `exposure-chart-${new Date().toISOString().split('T')[0]}.csv`, mimeType: 'text/csv' })
  }, [data, download])

  const totalLong = data.reduce((sum, d) => sum + d.longExposure, 0)
  const totalShort = data.reduce((sum, d) => sum + d.shortExposure, 0)
  const totalNet = data.reduce((sum, d) => sum + d.netExposure, 0)

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">{title}</CardTitle>
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
            <Select value={chartType} onValueChange={(v) => setChartType(v as 'stacked' | 'net')}>
              <SelectTrigger className="w-28 h-8"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="stacked">Stacked</SelectItem>
                <SelectItem value="net">Net</SelectItem>
              </SelectContent>
            </Select>
            <button onClick={handleExport} className="px-3 py-1 text-sm bg-secondary hover:bg-secondary/80 rounded-md transition-colors">Export</button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="text-sm text-muted-foreground">Long Exposure</div>
            <div className="text-lg font-semibold text-green-500">${(totalLong / 1000000).toFixed(1)}M</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-muted-foreground">Short Exposure</div>
            <div className="text-lg font-semibold text-red-500">${(totalShort / 1000000).toFixed(1)}M</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-muted-foreground">Net Exposure</div>
            <div className="text-lg font-semibold text-blue-500">${(totalNet / 1000000).toFixed(1)}M</div>
          </div>
        </div>
        <div ref={chartContainerRef} className="w-full" />
      </CardContent>
    </Card>
  )
}
