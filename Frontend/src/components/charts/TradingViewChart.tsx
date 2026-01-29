'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import {
  createChart,
  IChartApi,
  ISeriesApi,
  ColorType,
  CrosshairMode,
  Time,
} from 'lightweight-charts'
import { useTheme } from 'next-themes'
import { Skeleton } from '@/components/ui/skeleton'
import { assetsApi } from '@/lib/api/assets'

export type ChartType = 'candlestick' | 'line' | 'area' | 'bar' | 'histogram'
export type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w' | '1M'

interface TradingViewChartProps {
  symbol: string
  chartType?: ChartType
  timeframe?: Timeframe
  height?: number
  showVolume?: boolean
  showIndicators?: string[]
  onTimeframeChange?: (tf: Timeframe) => void
  onSymbolChange?: (symbol: string) => void
}

interface OHLCVData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

export function TradingViewChart({
  symbol,
  chartType = 'candlestick',
  timeframe = '1d',
  height = 500,
  showVolume = true,
  showIndicators = [],
  onTimeframeChange,
  onSymbolChange,
}: TradingViewChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const { theme } = useTheme()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentData, setCurrentData] = useState<OHLCVData[]>([])

  const isDark = theme === 'dark'

  const chartColors = {
    background: isDark ? '#1a1a2e' : '#ffffff',
    text: isDark ? '#d1d5db' : '#374151',
    grid: isDark ? '#2d2d44' : '#e5e7eb',
    upColor: '#22c55e',
    downColor: '#ef4444',
    wickUpColor: '#22c55e',
    wickDownColor: '#ef4444',
    volumeColor: isDark ? 'rgba(34, 197, 94, 0.3)' : 'rgba(34, 197, 94, 0.2)',
  }

  const initializeChart = useCallback(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height,
      layout: {
        background: { type: ColorType.Solid, color: chartColors.background },
        textColor: chartColors.text,
      },
      grid: {
        vertLines: { color: chartColors.grid },
        horzLines: { color: chartColors.grid },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: chartColors.grid,
      },
      timeScale: {
        borderColor: chartColors.grid,
        timeVisible: true,
        secondsVisible: false,
        barSpacing: 8,
      },
      handleScroll: {
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    })

    chartRef.current = chart

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [height, chartColors])

  const loadData = useCallback(async () => {
    if (!chartContainerRef.current) return

    setLoading(true)
    setError(null)

    try {
      const interval = timeframe === '1d' ? '1d' : timeframe === '1w' ? '1wk' : timeframe === '1M' ? '1mo' : '1d'
      const history = await assetsApi.getHistorical(symbol, undefined, undefined, interval)

      if (!history || history.length === 0) {
        setError('No data available')
        setLoading(false)
        return
      }

      const ohlcvData: OHLCVData[] = history.map((d: any) => ({
        date: d.date,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
        volume: d.volume,
      }))

      setCurrentData(ohlcvData)

      if (chartRef.current) {
        chartRef.current.remove()
      }

      const chart = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height,
        layout: {
          background: { type: ColorType.Solid, color: chartColors.background },
          textColor: chartColors.text,
        },
        grid: {
          vertLines: { color: chartColors.grid },
          horzLines: { color: chartColors.grid },
        },
        crosshair: {
          mode: CrosshairMode.Normal,
        },
        rightPriceScale: {
          borderColor: chartColors.grid,
        },
        timeScale: {
          borderColor: chartColors.grid,
          timeVisible: true,
          secondsVisible: false,
          barSpacing: 8,
        },
      })

      const chartAny = chart as unknown as Record<string, (...args: any[]) => any>

      if (chartType === 'candlestick') {
        const candlestickSeries = chartAny.addCandlestickSeries({
          upColor: chartColors.upColor,
          downColor: chartColors.downColor,
          borderVisible: false,
          wickUpColor: chartColors.wickUpColor,
          wickDownColor: chartColors.wickDownColor,
        })

        candlestickSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close,
          }))
        )
      } else if (chartType === 'line') {
        const lineSeries = chartAny.addLineSeries({
          color: '#3b82f6',
          lineWidth: 2,
        })

        lineSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            value: d.close,
          }))
        )
      } else if (chartType === 'area') {
        const areaSeries = chartAny.addAreaSeries({
          topColor: 'rgba(59, 130, 246, 0.4)',
          bottomColor: 'rgba(59, 130, 246, 0.0)',
          lineColor: '#3b82f6',
          lineWidth: 2,
        })

        areaSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            value: d.close,
          }))
        )
      } else if (chartType === 'bar') {
        const barSeries = chartAny.addBarSeries({
          upColor: chartColors.upColor,
          downColor: chartColors.downColor,
        })

        barSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close,
          }))
        )
      }

      if (showVolume && ohlcvData.some((d) => d.volume !== undefined)) {
        const volumeSeries = chartAny.addHistogramSeries({
          priceFormat: {
            type: 'volume',
            precision: 0,
            separator: ',',
          },
          priceScaleId: '',
        })

        volumeSeries.priceScale().applyOptions({
          scaleMargins: {
            top: 0.85,
            bottom: 0,
          },
        })

        volumeSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            value: d.volume || 0,
            color: d.close >= d.open ? chartColors.upColor : chartColors.downColor,
          }))
        )
      }

      chartRef.current = chart
      chart.timeScale().fitContent()
      setLoading(false)
    } catch (err) {
      console.error('Failed to load chart data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load chart data')
      setLoading(false)
    }
  }, [symbol, chartType, timeframe, height, showVolume, chartColors])

  useEffect(() => {
    const cleanup = initializeChart()
    return () => {
      if (cleanup) cleanup()
    }
  }, [initializeChart])

  useEffect(() => {
    loadData()
  }, [loadData])

  if (loading) {
    return (
      <div className="w-full rounded-lg border" style={{ height }}>
        <Skeleton className="w-full h-full rounded-lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full rounded-lg border flex items-center justify-center" style={{ height }}>
        <p className="text-destructive">{error}</p>
      </div>
    )
  }

  return (
    <div className="relative w-full">
      <div ref={chartContainerRef} className="w-full rounded-lg" style={{ height }} />
    </div>
  )
}
