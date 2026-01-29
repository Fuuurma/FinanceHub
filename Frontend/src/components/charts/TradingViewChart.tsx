'use client'

import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import {
  createChart,
  IChartApi,
  ISeriesApi,
  ColorType,
  CrosshairMode,
  Time,
  MouseEventParams,
} from 'lightweight-charts'
import { useTheme } from 'next-themes'
import { Skeleton } from '@/components/ui/skeleton'
import { assetsApi } from '@/lib/api/assets'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { RefreshCw, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react'

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

interface CrosshairData {
  time: string | null
  open: number | null
  high: number | null
  low: number | null
  close: number | null
  volume: number | null
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
  const [crosshairData, setCrosshairData] = useState<CrosshairData>({
    time: null,
    open: null,
    high: null,
    low: null,
    close: null,
    volume: null,
  })
  const [retryCount, setRetryCount] = useState(0)

  const isDark = theme === 'dark'

  const chartColors = useMemo(() => ({
    background: isDark ? '#0f172a' : '#ffffff',
    text: isDark ? '#94a3b8' : '#64748b',
    grid: isDark ? '#1e293b' : '#e2e8f0',
    upColor: '#22c55e',
    downColor: '#ef4444',
    wickUpColor: '#22c55e',
    wickDownColor: '#ef4444',
    volumeUp: isDark ? 'rgba(34, 197, 94, 0.3)' : 'rgba(34, 197, 94, 0.2)',
    volumeDown: isDark ? 'rgba(239, 68, 68, 0.3)' : 'rgba(239, 68, 68, 0.2)',
    crosshairLine: isDark ? 'rgba(148, 163, 184, 0.3)' : 'rgba(100, 116, 139, 0.3)',
  }), [isDark])

  const loadData = useCallback(async () => {
    if (!chartContainerRef.current) return

    setLoading(true)
    setError(null)

    try {
      const interval = timeframe === '1d' ? '1d' : timeframe === '1w' ? '1wk' : timeframe === '1M' ? '1mo' : '1d'
      const history = await assetsApi.getHistorical(symbol, undefined, undefined, interval)

      if (!history || history.length === 0) {
        setError('No data available for this symbol')
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
      setRetryCount(0)

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
          vertLines: { color: chartColors.grid, style: 2 },
          horzLines: { color: chartColors.grid, style: 2 },
        },
        crosshair: {
          mode: CrosshairMode.Normal,
          vertLine: {
            width: 1,
            color: chartColors.crosshairLine,
            style: 2,
          },
          horzLine: {
            width: 1,
            color: chartColors.crosshairLine,
            style: 2,
          },
        },
        rightPriceScale: {
          borderColor: chartColors.grid,
          borderVisible: true,
          scaleMargins: {
            top: showVolume ? 0.1 : 0,
            bottom: showVolume ? 0.15 : 0,
          },
        },
        timeScale: {
          borderColor: chartColors.grid,
          timeVisible: true,
          secondsVisible: false,
          barSpacing: 6,
          minBarSpacing: 2,
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

      const chartAny = chart as unknown as Record<string, (...args: any[]) => any>

      let mainSeries: ISeriesApi<any>

      if (chartType === 'candlestick') {
        mainSeries = chartAny.addCandlestickSeries({
          upColor: chartColors.upColor,
          downColor: chartColors.downColor,
          borderVisible: false,
          wickUpColor: chartColors.wickUpColor,
          wickDownColor: chartColors.wickDownColor,
        })

        mainSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close,
          }))
        )
      } else if (chartType === 'line') {
        mainSeries = chartAny.addLineSeries({
          color: '#3b82f6',
          lineWidth: 2,
          priceFormat: {
            type: 'price',
            precision: 2,
            minMove: 0.01,
          },
        })

        mainSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            value: d.close,
          }))
        )
      } else if (chartType === 'area') {
        mainSeries = chartAny.addAreaSeries({
          topColor: 'rgba(59, 130, 246, 0.5)',
          bottomColor: 'rgba(59, 130, 246, 0.0)',
          lineColor: '#3b82f6',
          lineWidth: 2,
        })

        mainSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            value: d.close,
          }))
        )
      } else if (chartType === 'bar') {
        mainSeries = chartAny.addBarSeries({
          upColor: chartColors.upColor,
          downColor: chartColors.downColor,
        })

        mainSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close,
          }))
        )
      } else {
        mainSeries = chartAny.addHistogramSeries({
          priceFormat: {
            type: 'volume',
            precision: 0,
            separator: ',',
          },
          priceScaleId: '',
        })

        mainSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            value: d.volume || 0,
            color: d.close >= d.open ? chartColors.upColor : chartColors.downColor,
          }))
        )
      }

      if (showVolume && chartType !== 'histogram' && ohlcvData.some((d) => d.volume !== undefined)) {
        const volumeSeries = chartAny.addHistogramSeries({
          priceFormat: {
            type: 'volume',
            precision: 0,
            separator: ',',
          },
          priceScaleId: 'volume',
        })

        volumeSeries.priceScale().applyOptions({
          scaleMargins: {
            top: 0.85,
            bottom: 0,
          },
          borderVisible: false,
        })

        volumeSeries.setData(
          ohlcvData.map((d) => ({
            time: d.date as Time,
            value: d.volume || 0,
            color: d.close >= d.open ? chartColors.volumeUp : chartColors.volumeDown,
          }))
        )
      }

      chart.timeScale().fitContent()

      chart.subscribeCrosshairMove((param: MouseEventParams) => {
        if (param.time && param.seriesData.size > 0) {
          const time = param.time as string
          const ohlcv = ohlcvData.find((d) => d.date === time)
          if (ohlcv) {
            setCrosshairData({
              time,
              open: ohlcv.open,
              high: ohlcv.high,
              low: ohlcv.low,
              close: ohlcv.close,
              volume: ohlcv.volume || null,
            })
          }
        } else {
          const lastData = ohlcvData[ohlcvData.length - 1]
          if (lastData) {
            setCrosshairData({
              time: lastData.date,
              open: lastData.open,
              high: lastData.high,
              low: lastData.low,
              close: lastData.close,
              volume: lastData.volume || null,
            })
          }
        }
      })

      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({
            width: chartContainerRef.current.clientWidth,
          })
        }
      }

      window.addEventListener('resize', handleResize)

      setLoading(false)
    } catch (err) {
      console.error('Failed to load chart data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load chart data')
      setLoading(false)
    }
  }, [symbol, chartType, timeframe, height, showVolume, chartColors])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleRetry = () => {
    setRetryCount((prev) => prev + 1)
    loadData()
  }

  const latestData = currentData[currentData.length - 1]
  const previousClose = currentData[currentData.length - 2]?.close
  const priceChange = latestData && previousClose ? latestData.close - previousClose : null
  const priceChangePercent = priceChange && previousClose ? (priceChange / previousClose) * 100 : null

  if (loading) {
    return (
      <div className="w-full rounded-lg border bg-card" style={{ height }}>
        <div className="p-4 border-b space-y-3">
          <Skeleton className="h-6 w-32" />
          <div className="flex gap-4">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-20" />
          </div>
        </div>
        <Skeleton className="w-full h-[calc(100%-80px)] rounded-none" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full rounded-lg border bg-card flex flex-col items-center justify-center" style={{ height }}>
        <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
        <p className="text-destructive font-medium mb-2">Failed to load chart data</p>
        <p className="text-sm text-muted-foreground mb-4">{error}</p>
        <Button onClick={handleRetry} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div className="w-full rounded-lg border bg-card overflow-hidden">
      <div className="p-3 border-b bg-muted/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-bold text-lg">{symbol}</span>
            <Badge variant={priceChangePercent !== null && priceChangePercent >= 0 ? 'default' : 'destructive'} className={priceChangePercent !== null && priceChangePercent >= 0 ? 'bg-green-500' : ''}>
              {priceChangePercent !== null ? (
                <>
                  {priceChangePercent >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                  {priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%
                </>
              ) : '--'}
            </Badge>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground">O:</span>
              <span className="font-mono">{crosshairData.open?.toFixed(2) || '--'}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground">H:</span>
              <span className="font-mono text-green-500">{crosshairData.high?.toFixed(2) || '--'}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground">L:</span>
              <span className="font-mono text-red-500">{crosshairData.low?.toFixed(2) || '--'}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground">C:</span>
              <span className="font-mono">{crosshairData.close?.toFixed(2) || '--'}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground">Vol:</span>
              <span className="font-mono">
                {crosshairData.volume ? (crosshairData.volume / 1000000).toFixed(2) + 'M' : '--'}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full" style={{ height: height - 60 }} />
      <div className="p-2 border-t bg-muted/20 text-xs text-center text-muted-foreground">
        {currentData.length} data points • {timeframe} timeframe • Data by Polygon.io
      </div>
    </div>
  )
}
