'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import {
  createChart,
  IChartApi,
  ISeriesApi,
  ColorType,
  CrosshairMode,
  Time,
} from 'lightweight-charts'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useRealtimeStore } from '@/stores/realtimeStore'
import { CHART_CONFIG, WS_CONFIG } from '@/lib/constants/realtime'
import type { ChartTimeframe, ChartDataPoint } from '@/lib/constants/realtime'
import type { IndicatorConfig } from '@/lib/types/indicators'
import { cn, formatCurrency } from '@/lib/utils'
import {
  LineChart,
  BarChart3,
  CandlestickChart,
  AreaChart,
  Settings2,
  Activity,
  TrendingUp,
} from 'lucide-react'

export type ChartType = 'candlestick' | 'line' | 'area' | 'bar'

interface RealTimeChartProps {
  symbol: string
  initialTimeframe?: ChartTimeframe
  initialChartType?: ChartType
  indicators?: IndicatorConfig[]
  onIndicatorsChange?: (indicators: IndicatorConfig[]) => void
  height?: number
}

const TIMEFRAMES: { value: ChartTimeframe; label: string }[] = [
  { value: '1m', label: '1m' },
  { value: '5m', label: '5m' },
  { value: '15m', label: '15m' },
  { value: '30m', label: '30m' },
  { value: '1h', label: '1H' },
  { value: '4h', label: '4H' },
  { value: '1d', label: '1D' },
  { value: '1w', label: '1W' },
]

const CHART_TYPES: { value: ChartType; label: string; icon: React.ReactNode }[] = [
  { value: 'candlestick', label: 'Candlestick', icon: <CandlestickChart className="h-4 w-4" /> },
  { value: 'line', label: 'Line', icon: <LineChart className="h-4 w-4" /> },
  { value: 'area', label: 'Area', icon: <AreaChart className="h-4 w-4" /> },
  { value: 'bar', label: 'Bar', icon: <BarChart3 className="h-4 w-4" /> },
]

export function RealTimeChart({
  symbol,
  initialTimeframe = '1h',
  initialChartType = 'candlestick',
  indicators = [],
  onIndicatorsChange,
  height = 500,
}: RealTimeChartProps) {
  const { prices, charts, setChartTimeframe } = useRealtimeStore()
  const [chartType, setChartType] = useState<ChartType>(initialChartType)
  const [timeframe, setTimeframe] = useState<ChartTimeframe>(initialTimeframe)
  const [showVolume, setShowVolume] = useState(true)
  const [showIndicators, setShowIndicators] = useState(indicators.length > 0)
  const [selectedIndicators, setSelectedIndicators] = useState<IndicatorConfig[]>(indicators)
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [isConnected, setIsConnected] = useState(false)

  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<any>(null)
  const seriesRef = useRef<any>(null)
  const volumeSeriesRef = useRef<any>(null)
  const resizeObserverRef = useRef<ResizeObserver | null>(null)

  useEffect(() => {
    setChartTimeframe(symbol, timeframe)
  }, [symbol, timeframe, setChartTimeframe])

  useEffect(() => {
    if (indicators.length > 0) {
      setSelectedIndicators(indicators)
      setShowIndicators(true)
    }
  }, [indicators])

  useEffect(() => {
    const priceData = prices[symbol]
    if (priceData) {
      const newDataPoint: ChartDataPoint = {
        time: priceData.timestamp,
        price: priceData.price,
        volume: priceData.volume,
      }
      setChartData((prev) => {
        const updated = [...prev, newDataPoint].slice(-CHART_CONFIG.BUFFER_SIZES[timeframe])
        return updated
      })
    }
  }, [prices, symbol, timeframe])

  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height,
      layout: {
        background: { type: ColorType.Solid, color: '#0a0a0a' },
        textColor: '#a0a0a0',
      },
      grid: {
        vertLines: { color: '#1a1a1a' },
        horzLines: { color: '#1a1a1a' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: '#1a1a1a',
      },
      timeScale: {
        borderColor: '#1a1a1a',
        timeVisible: true,
        secondsVisible: false,
      },
    })

    chartRef.current = chart as unknown as any
    const chartAny = chart as unknown as any

    let series: ISeriesApi<'Candlestick' | 'Line' | 'Area'> | null = null
    let volumeSeries: ISeriesApi<'Histogram'> | null = null

    switch (chartType) {
      case 'candlestick':
        series = chartAny.addCandlestickSeries({
          upColor: '#22C55E',
          downColor: '#EF4444',
          borderDownColor: '#EF4444',
          borderUpColor: '#22C55E',
          wickDownColor: '#EF4444',
          wickUpColor: '#22C55E',
        })
        break
      case 'line':
        series = chartAny.addLineSeries({
          color: '#3B82F6',
          lineWidth: 2,
        })
        break
      case 'area':
        series = chartAny.addAreaSeries({
          topColor: 'rgba(59, 130, 246, 0.4)',
          bottomColor: 'rgba(59, 130, 246, 0.0)',
          lineColor: '#3B82F6',
          lineWidth: 2,
        })
        break
      case 'bar':
        series = chartAny.addHistogramSeries({
          color: '#6B7280',
        })
        break
    }

    seriesRef.current = series

    if (showVolume) {
      volumeSeries = chartAny.addHistogramSeries({
        color: 'rgba(148, 163, 184, 0.3)',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
      })
      if (volumeSeries) {
        volumeSeries.priceScale().applyOptions({
          scaleMargins: {
            top: 0.8,
            bottom: 0,
          },
        })
      }
      volumeSeriesRef.current = volumeSeries
    }

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: height,
        })
      }
    }

    resizeObserverRef.current = new ResizeObserver(handleResize)
    resizeObserverRef.current.observe(chartContainerRef.current)

    return () => {
      resizeObserverRef.current?.disconnect()
      chart.remove()
    }
  }, [chartType, showVolume, height])

  useEffect(() => {
    if (!seriesRef.current || chartData.length === 0) return

    const ohlcData = chartData.map((point) => ({
      time: (Number(point.time) / 1000) as Time,
      open: point.price,
      high: point.price * (1 + Math.random() * 0.002),
      low: point.price * (1 - Math.random() * 0.002),
      close: point.price,
    }))

    const lastPoint = chartData[chartData.length - 1]
    const updatedOhlc = {
      ...ohlcData[ohlcData.length - 1],
      high: Math.max(lastPoint.price, ohlcData[ohlcData.length - 1].high),
      low: Math.min(lastPoint.price, ohlcData[ohlcData.length - 1].low),
      close: lastPoint.price,
    }
    ohlcData[ohlcData.length - 1] = updatedOhlc

    if (chartType === 'candlestick') {
      seriesRef.current.setData(ohlcData)
    } else if (chartType === 'line' || chartType === 'area') {
      seriesRef.current.setData(
        chartData.map((point) => ({
          time: (Number(point.time) / 1000) as any,
          value: point.price,
        }))
      )
    } else if (chartType === 'bar') {
      seriesRef.current.setData(
        chartData.map((point) => ({
          time: (Number(point.time) / 1000) as any,
          value: point.volume,
          color: point.price >= (chartData[chartData.indexOf(point) - 1]?.price || point.price) ? '#22C55E' : '#EF4444',
        }))
      )
    }

    if (volumeSeriesRef.current && showVolume) {
      volumeSeriesRef.current.setData(
        chartData.map((point) => ({
          time: (point.time as number) / 1000 as any,
          value: point.volume,
          color: point.price >= (chartData[Math.max(0, chartData.indexOf(point) - 1)]?.price || point.price) ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)',
        }))
      )
    }

    chartRef.current?.timeScale().fitContent()
  }, [chartData, chartType, showVolume])

  const formatPrice = (value: number) => formatCurrency(value)

  if (chartData.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">{symbol}</h3>
            <Badge variant={isConnected ? 'default' : 'destructive'}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </Badge>
          </div>
        </div>
        <div
          className="flex items-center justify-center border rounded-lg bg-background"
          style={{ height }}
        >
          <div className="text-center">
            <Activity className="h-8 w-8 mx-auto text-muted-foreground mb-2 animate-pulse" />
            <p className="text-muted-foreground">
              {isConnected ? 'Waiting for data...' : 'Connect to see real-time data'}
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">{symbol}</h3>
          <Badge variant={isConnected ? 'default' : 'destructive'}>
            {isConnected ? 'Live' : 'Offline'}
          </Badge>
          {chartData.length > 0 && (
            <span className="text-sm text-muted-foreground">
              {formatPrice(chartData[chartData.length - 1]?.price || 0)}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Select value={timeframe} onValueChange={(v) => setTimeframe(v as ChartTimeframe)}>
            <SelectTrigger className="w-20">
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

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                {CHART_TYPES.find((t) => t.value === chartType)?.icon}
                <span className="ml-2 hidden sm:inline">{CHART_TYPES.find((t) => t.value === chartType)?.label}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Chart Type</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {CHART_TYPES.map((type) => (
                <DropdownMenuCheckboxItem
                  key={type.value}
                  checked={chartType === type.value}
                  onCheckedChange={() => setChartType(type.value)}
                >
                  {type.icon}
                  <span className="ml-2">{type.label}</span>
                </DropdownMenuCheckboxItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            variant={showVolume ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowVolume(!showVolume)}
          >
            <Activity className="h-4 w-4" />
          </Button>

          <Button
            variant={showIndicators ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowIndicators(!showIndicators)}
          >
            <TrendingUp className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div
        ref={chartContainerRef}
        className="border rounded-lg bg-background"
        style={{ height }}
      />

      {showIndicators && selectedIndicators.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedIndicators.map((ind) => (
            <Badge
              key={ind.type}
              variant="outline"
              className="px-3 py-1"
              style={{ borderColor: ind.color, color: ind.color }}
            >
              {ind.type.toUpperCase()}
              <button
                onClick={() => {
                  const newIndicators = selectedIndicators.filter((i) => i.type !== ind.type)
                  setSelectedIndicators(newIndicators)
                  onIndicatorsChange?.(newIndicators)
                }}
                className="ml-2 hover:text-destructive"
              >
                ×
              </button>
            </Badge>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>Last update: {new Date().toLocaleTimeString()}</span>
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          Real-time data
        </span>
      </div>
    </div>
  )
}
