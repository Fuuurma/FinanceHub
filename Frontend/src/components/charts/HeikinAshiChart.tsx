'use client'

import { useMemo, useRef, useEffect, useState } from 'react'
import { createChart, ColorType, IChartApi, ISeriesApi, CandlestickData, Time } from 'lightweight-charts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn } from '@/lib/utils'
import { RefreshCw } from 'lucide-react'

export interface HeikinAshiData {
  time: string
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

interface HeikinAshiChartProps {
  data: HeikinAshiData[]
  className?: string
  height?: number
  showVolume?: boolean
  onSymbolChange?: (symbol: string) => void
}

function calculateHeikinAshi(data: { time: string; open: number; high: number; low: number; close: number; volume?: number }[]): HeikinAshiData[] {
  if (data.length === 0) return []

  const result: HeikinAshiData[] = []
  let prevHaOpen = data[0].open
  let prevHaClose = data[0].close

  for (let i = 0; i < data.length; i++) {
    const candle = data[i]
    const haClose = (candle.open + candle.high + candle.low + candle.close) / 4
    const haOpen = (prevHaOpen + prevHaClose) / 2
    const haHigh = Math.max(candle.high, Math.max(haOpen, haClose))
    const haLow = Math.min(candle.low, Math.min(haOpen, haClose))

    result.push({
      time: candle.time,
      open: haOpen,
      high: haHigh,
      low: haLow,
      close: haClose,
      volume: candle.volume
    })

    prevHaOpen = haOpen
    prevHaClose = haClose
  }

  return result
}

export function HeikinAshiChart({
  data,
  className,
  height = 400,
  showVolume = true,
  onSymbolChange
}: HeikinAshiChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const [chartType, setChartType] = useState<'heikin-ashi' | 'traditional'>('heikin-ashi')

  const processedData = useMemo(() => {
    if (chartType === 'heikin-ashi') {
      return calculateHeikinAshi(data)
    }
    return data.map(d => ({
      time: d.time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
      volume: d.volume
    }))
  }, [data, chartType])

  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: 'hsl(var(--muted-foreground))'
      },
      grid: {
        vertLines: { color: 'hsl(var(--border))' },
        horzLines: { color: 'hsl(var(--border))' }
      },
      width: chartContainerRef.current.clientWidth,
      height: height,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      }
    })

    chartRef.current = chart

    const candlestickSeries = (chart as any).addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    })
    seriesRef.current = candlestickSeries

    if (showVolume) {
      const volumeSeries = (chart as any).addHistogramSeries({
        color: '#64748b',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
      })
      volumeSeries.priceScale().applyOptions({
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      })
      volumeSeriesRef.current = volumeSeries
    }

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [height, showVolume])

  useEffect(() => {
    if (!seriesRef.current) return

    const candleData: CandlestickData<Time>[] = processedData.map(d => ({
      time: d.time as Time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }))

    seriesRef.current.setData(candleData)

    if (volumeSeriesRef.current && showVolume) {
      const volumeData = processedData.map(d => ({
        time: d.time as Time,
        value: d.volume || 0,
        color: d.close >= d.open ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)',
      }))
      volumeSeriesRef.current.setData(volumeData)
    }

    chartRef.current?.timeScale().fitContent()
  }, [processedData, showVolume])

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle>Heikin Ashi Chart</CardTitle>
          <div className="flex items-center gap-2">
            <Select value={chartType} onValueChange={(v) => setChartType(v as 'heikin-ashi' | 'traditional')}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="heikin-ashi">Heikin Ashi</SelectItem>
                <SelectItem value="traditional">Traditional</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" onClick={() => chartRef.current?.timeScale().fitContent()}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div ref={chartContainerRef} className="w-full" />
        {chartType === 'heikin-ashi' && (
          <div className="mt-4 p-3 rounded-lg bg-muted text-sm">
            <p className="font-medium mb-2">Heikin Ashi Interpretation</p>
            <div className="grid grid-cols-2 gap-2 text-muted-foreground">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm bg-green-500" />
                <span>Green candles = Uptrend</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm bg-red-500" />
                <span>Red candles = Downtrend</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm bg-green-500" />
                <span>Large bodies = Strong momentum</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm bg-red-500" />
                <span>Small bodies = Weak trend</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default HeikinAshiChart
