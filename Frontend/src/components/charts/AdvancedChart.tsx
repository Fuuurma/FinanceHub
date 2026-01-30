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
import {
  Download,
  RefreshCw,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Settings2,
  Undo,
  Minus,
  TrendingUp as TrendLineIcon,
  Square,
  Type,
  Activity,
  Camera,
  FileImage,
  FileText,
} from 'lucide-react'
import { TechnicalIndicatorsPanel } from './TechnicalIndicatorsPanel'
import { IndicatorConfig, calculateAllIndicators, INDICATOR_DESCRIPTIONS } from '@/lib/utils/technical-indicators'
import { useRealtimeStore } from '@/stores/realtimeStore'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { HelpCircle } from 'lucide-react'
import { useDownloadFile } from '@/hooks/useDownload'
import { cn } from '@/lib/utils'

export type ChartType = 'candlestick' | 'line' | 'area' | 'bar' | 'histogram'
export type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w' | '1M'
export type DrawingType = 'horizontal_line' | 'vertical_line' | 'trend_line' | 'fibonacci' | 'rectangle' | 'text'

export interface Drawing {
  id: string
  type: DrawingType
  startTime: Time
  startValue: number
  endTime?: Time
  endValue?: number
  color: string
  width: number
  text?: string
  visible: boolean
}

interface AdvancedChartProps {
  symbol: string
  chartType?: ChartType
  timeframe?: Timeframe
  height?: number
  showVolume?: boolean
  showIndicators?: string[]
  indicatorConfig?: IndicatorConfig
  enableDrawingTools?: boolean
  onTimeframeChange?: (tf: Timeframe) => void
  onSymbolChange?: (symbol: string) => void
  onIndicatorChange?: (indicator: string, enabled: boolean) => void
  onDrawingCreate?: (drawing: Drawing) => void
}

export interface OHLCVData {
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
  sma20?: number | null
  sma50?: number | null
  sma200?: number | null
  ema12?: number | null
  ema26?: number | null
  rsi?: number | null
  macd?: number | null
  macdSignal?: number | null
  bollingerUpper?: number | null
  bollingerMiddle?: number | null
  bollingerLower?: number | null
}

const TIMEFRAMES: { value: Timeframe; label: string; hotkey: string }[] = [
  { value: '1m', label: '1m', hotkey: '1' },
  { value: '5m', label: '5m', hotkey: '2' },
  { value: '15m', label: '15m', hotkey: '3' },
  { value: '1h', label: '1H', hotkey: '4' },
  { value: '4h', label: '4H', hotkey: '5' },
  { value: '1d', label: '1D', hotkey: '6' },
  { value: '1w', label: '1W', hotkey: '7' },
  { value: '1M', label: '1M', hotkey: '8' },
]

const CHART_TYPES: { value: ChartType; label: string; hotkey: string }[] = [
  { value: 'candlestick', label: 'Candlestick', hotkey: 'c' },
  { value: 'line', label: 'Line', hotkey: 'l' },
  { value: 'area', label: 'Area', hotkey: 'a' },
  { value: 'bar', label: 'Bar', hotkey: 'b' },
  { value: 'histogram', label: 'Histogram', hotkey: 'h' },
]

export function AdvancedChart({
  symbol,
  chartType = 'candlestick',
  timeframe = '1d',
  height = 500,
  showVolume = true,
  showIndicators = [],
  indicatorConfig = {},
  enableDrawingTools = false,
  onTimeframeChange,
  onSymbolChange,
  onIndicatorChange,
  onDrawingCreate,
}: AdvancedChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const { theme } = useTheme()
  const { prices } = useRealtimeStore()
  const { downloadCSV, downloadText } = useDownloadFile()
  
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
  const [selectedDrawingTool, setSelectedDrawingTool] = useState<DrawingType | null>(null)
  const [drawings, setDrawings] = useState<Drawing[]>([])
  const [isExporting, setIsExporting] = useState(false)

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
    sma20Color: '#3b82f6',
    sma50Color: '#22c55e',
    sma200Color: '#f59e0b',
    ema12Color: '#8b5cf6',
    ema26Color: '#ec4899',
    bollingerUpperColor: '#94a3b8',
    bollingerMiddleColor: '#64748b',
    bollingerLowerColor: '#94a3b8',
  }), [isDark])

  const showRSI = showIndicators.includes('rsi')
  const showMACD = showIndicators.includes('macd')
  const showSMA20 = showIndicators.includes('sma20')
  const showSMA50 = showIndicators.includes('sma50')
  const showSMA200 = showIndicators.includes('sma200')
  const showEMA12 = showIndicators.includes('ema12')
  const showEMA26 = showIndicators.includes('ema26')
  const showBollinger = showIndicators.includes('bollinger')

  const indicatorResults = useMemo(() => {
    if (currentData.length === 0) return null
    const config: IndicatorConfig = {
      sma20: showSMA20,
      sma50: showSMA50,
      sma200: showSMA200,
      ema12: showEMA12,
      ema26: showEMA26,
      rsi: showRSI,
      macd: showMACD,
      bollinger: showBollinger,
      rsiPeriod: indicatorConfig.rsiPeriod,
      rsiOverbought: indicatorConfig.rsiOverbought,
      rsiOversold: indicatorConfig.rsiOversold,
      macdFast: indicatorConfig.macdFast,
      macdSlow: indicatorConfig.macdSlow,
      macdSignal: indicatorConfig.macdSignal,
      bollingerPeriod: indicatorConfig.bollingerPeriod,
      bollingerStdDev: indicatorConfig.bollingerStdDev,
    }
    return calculateAllIndicators(currentData, config)
  }, [currentData, showSMA20, showSMA50, showSMA200, showEMA12, showEMA26, showRSI, showMACD, showBollinger, indicatorConfig])

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

      interface HistoryItem {
        date: string
        open: number
        high: number
        low: number
        close: number
        volume: number
      }

      const ohlcvData: OHLCVData[] = history.map((d: HistoryItem) => ({
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
        height: height - (showRSI || showMACD ? 250 : 0) - 60,
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

      const chartAny = chart as unknown as any

      let mainSeries: ISeriesApi<'Candlestick' | 'Line' | 'Area' | 'Bar'>

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

      if (indicatorResults) {
        const times = ohlcvData.map(d => d.date as Time)

        if (indicatorResults.sma20) {
          const sma20Series = chartAny.addLineSeries({
            color: chartColors.sma20Color,
            lineWidth: 1,
          })
          sma20Series.setData(
            indicatorResults.sma20.map((value, i) =>
              isNaN(value) ? null : { time: times[i], value }
            ).filter((v): v is { time: Time; value: number } => v !== null)
          )
        }

        if (indicatorResults.sma50) {
          const sma50Series = chartAny.addLineSeries({
            color: chartColors.sma50Color,
            lineWidth: 1,
          })
          sma50Series.setData(
            indicatorResults.sma50.map((value, i) =>
              isNaN(value) ? null : { time: times[i], value }
            ).filter((v): v is { time: Time; value: number } => v !== null)
          )
        }

        if (indicatorResults.sma200) {
          const sma200Series = chartAny.addLineSeries({
            color: chartColors.sma200Color,
            lineWidth: 1,
          })
          sma200Series.setData(
            indicatorResults.sma200.map((value, i) =>
              isNaN(value) ? null : { time: times[i], value }
            ).filter((v): v is { time: Time; value: number } => v !== null)
          )
        }

        if (indicatorResults.ema12) {
          const ema12Series = chartAny.addLineSeries({
            color: chartColors.ema12Color,
            lineWidth: 1,
          })
          ema12Series.setData(
            indicatorResults.ema12.map((value, i) =>
              isNaN(value) ? null : { time: times[i], value }
            ).filter((v): v is { time: Time; value: number } => v !== null)
          )
        }

        if (indicatorResults.ema26) {
          const ema26Series = chartAny.addLineSeries({
            color: chartColors.ema26Color,
            lineWidth: 1,
          })
          ema26Series.setData(
            indicatorResults.ema26.map((value, i) =>
              isNaN(value) ? null : { time: times[i], value }
            ).filter((v): v is { time: Time; value: number } => v !== null)
          )
        }

        if (indicatorResults.bollinger) {
          const bb = indicatorResults.bollinger
          const upperSeries = chartAny.addLineSeries({
            color: chartColors.bollingerUpperColor,
            lineWidth: 1,
          })
          upperSeries.setData(
            bb.upper.map((value, i) =>
              isNaN(value) ? null : { time: times[i], value }
            ).filter((v): v is { time: Time; value: number } => v !== null)
          )

          const middleSeries = chartAny.addLineSeries({
            color: chartColors.bollingerMiddleColor,
            lineWidth: 1,
          })
          middleSeries.setData(
            bb.middle.map((value, i) =>
              isNaN(value) ? null : { time: times[i], value }
            ).filter((v): v is { time: Time; value: number } => v !== null)
          )

          const lowerSeries = chartAny.addLineSeries({
            color: chartColors.bollingerLowerColor,
            lineWidth: 1,
          })
          lowerSeries.setData(
            bb.lower.map((value, i) =>
              isNaN(value) ? null : { time: times[i], value }
            ).filter((v): v is { time: Time; value: number } => v !== null)
          )
        }
      }

      chart.timeScale().fitContent()

      chart.subscribeCrosshairMove((param: MouseEventParams) => {
        if (param.time && param.seriesData.size > 0) {
          const time = param.time as string
          const ohlcv = ohlcvData.find((d) => d.date === time)
          if (ohlcv) {
            const idx = ohlcvData.findIndex(d => d.date === time)
            setCrosshairData({
              time,
              open: ohlcv.open,
              high: ohlcv.high,
              low: ohlcv.low,
              close: ohlcv.close,
              volume: ohlcv.volume || null,
              sma20: indicatorResults?.sma20?.[idx] ?? null,
              sma50: indicatorResults?.sma50?.[idx] ?? null,
              sma200: indicatorResults?.sma200?.[idx] ?? null,
              ema12: indicatorResults?.ema12?.[idx] ?? null,
              ema26: indicatorResults?.ema26?.[idx] ?? null,
              rsi: indicatorResults?.rsi?.[idx] ?? null,
              macd: indicatorResults?.macd?.macd?.[idx] ?? null,
              macdSignal: indicatorResults?.macd?.signal?.[idx] ?? null,
              bollingerUpper: indicatorResults?.bollinger?.upper?.[idx] ?? null,
              bollingerMiddle: indicatorResults?.bollinger?.middle?.[idx] ?? null,
              bollingerLower: indicatorResults?.bollinger?.lower?.[idx] ?? null,
            })
          }
        } else {
          const lastIdx = ohlcvData.length - 1
          if (lastIdx >= 0) {
            setCrosshairData({
              time: ohlcvData[lastIdx].date,
              open: ohlcvData[lastIdx].open,
              high: ohlcvData[lastIdx].high,
              low: ohlcvData[lastIdx].low,
              close: ohlcvData[lastIdx].close,
              volume: ohlcvData[lastIdx].volume || null,
              sma20: indicatorResults?.sma20?.[lastIdx] ?? null,
              sma50: indicatorResults?.sma50?.[lastIdx] ?? null,
              sma200: indicatorResults?.sma200?.[lastIdx] ?? null,
              ema12: indicatorResults?.ema12?.[lastIdx] ?? null,
              ema26: indicatorResults?.ema26?.[lastIdx] ?? null,
              rsi: indicatorResults?.rsi?.[lastIdx] ?? null,
              macd: indicatorResults?.macd?.macd?.[lastIdx] ?? null,
              macdSignal: indicatorResults?.macd?.signal?.[lastIdx] ?? null,
              bollingerUpper: indicatorResults?.bollinger?.upper?.[lastIdx] ?? null,
              bollingerMiddle: indicatorResults?.bollinger?.middle?.[lastIdx] ?? null,
              bollingerLower: indicatorResults?.bollinger?.lower?.[lastIdx] ?? null,
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
  }, [symbol, chartType, timeframe, height, showVolume, showIndicators, indicatorConfig, chartColors, indicatorResults])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleRetry = () => {
    setRetryCount((prev) => prev + 1)
    loadData()
  }

  const handleExportPNG = useCallback(async () => {
    if (!chartRef.current) return
    
    setIsExporting(true)
    try {
      const canvas = (chartRef.current as unknown as IChartApi).takeScreenshot()
      if (canvas) {
        const filename = `${symbol}-${chartType}-${timeframe}-${new Date().toISOString().slice(0, 10)}.png`
        const dataUrl = canvas.toDataURL('image/png')
        downloadText(dataUrl, filename, 'image/png')
      }
    } catch (err) {
      console.error('Failed to export chart:', err)
    } finally {
      setIsExporting(false)
    }
  }, [symbol, chartType, timeframe, downloadText])

  const handleExportCSV = useCallback(() => {
    if (currentData.length === 0) return
    
    const headers = 'Date,Open,High,Low,Close,Volume\n'
    const rows = currentData.map(d => 
      `${d.date},${d.open},${d.high},${d.low},${d.close},${d.volume || 0}`
    ).join('\n')
    
    const csv = headers + rows
    const filename = `${symbol}-${chartType}-${timeframe}-${new Date().toISOString().slice(0, 10)}.csv`
    downloadCSV(csv, filename)
  }, [currentData, symbol, chartType, timeframe, downloadCSV])

  const latestData = currentData[currentData.length - 1]
  const previousClose = currentData[currentData.length - 2]?.close
  const priceChange = latestData && previousClose ? latestData.close - previousClose : null
  const priceChangePercent = priceChange && previousClose ? (priceChange / previousClose) * 100 : null

  const formatValue = (value: number | null | undefined) => {
    if (value === null || value === undefined || isNaN(value)) return '--'
    return value.toFixed(2)
  }

  const activeIndicatorsCount = showIndicators.filter(ind =>
    ['sma20', 'sma50', 'sma200', 'ema12', 'ema26', 'rsi', 'macd', 'bollinger'].includes(ind)
  ).length

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
      <div className="p-3 border-b bg-muted/30 space-y-3">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg">{symbol}</span>
            <Badge variant={priceChangePercent !== null && priceChangePercent >= 0 ? 'default' : 'destructive'} className={priceChangePercent !== null && priceChangePercent >= 0 ? 'bg-green-500' : ''}>
              {priceChangePercent !== null ? (
                <>
                  {priceChangePercent >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                  {priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%
                </>
              ) : '--'}
            </Badge>
            {activeIndicatorsCount > 0 && (
              <Badge variant="outline" className="text-xs">
                {activeIndicatorsCount} indicator{activeIndicatorsCount > 1 ? 's' : ''}
              </Badge>
            )}
            {drawings.length > 0 && (
              <Badge variant="outline" className="text-xs">
                {drawings.length} drawing{drawings.length > 1 ? 's' : ''}
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center gap-0.5 bg-muted rounded-md p-0.5">
              {TIMEFRAMES.map((tf) => (
                <Button
                  key={tf.value}
                  variant={timeframe === tf.value ? 'default' : 'ghost'}
                  size="sm"
                  className="h-7 px-2 text-xs font-medium"
                  onClick={() => onTimeframeChange?.(tf.value)}
                  title={`Press ${tf.hotkey}`}
                >
                  {tf.label}
                </Button>
              ))}
            </div>

            <Select
              value={chartType}
              onValueChange={(value) => {
                const chartType = value as ChartType
                // Handle chart type change
              }}
            >
              <SelectTrigger className="h-8 w-36">
                <SelectValue>
                  <span className="text-xs">{CHART_TYPES.find((t) => t.value === chartType)?.label}</span>
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {CHART_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    <span>{type.label}</span>
                    <span className="text-xs text-muted-foreground ml-2">({type.hotkey})</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button
              variant={showVolume ? 'default' : 'outline'}
              size="sm"
              className="h-8 px-3"
            >
              Vol
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant={activeIndicatorsCount > 0 ? 'default' : 'outline'} size="sm" className="h-8">
                  <Settings2 className="h-4 w-4 mr-1" />
                  <span className="text-xs">Indicators</span>
                  {activeIndicatorsCount > 0 && (
                    <span className="ml-1 px-1.5 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
                      {activeIndicatorsCount}
                    </span>
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuLabel>Technical Indicators</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {['sma20', 'sma50', 'sma200', 'ema12', 'ema26', 'rsi', 'macd', 'bollinger'].map((indicator) => (
                  <DropdownMenuCheckboxItem
                    key={indicator}
                    checked={showIndicators.includes(indicator)}
                    onCheckedChange={(checked) => onIndicatorChange?.(indicator, checked as boolean)}
                  >
                    {(INDICATOR_DESCRIPTIONS as any)[indicator]?.name || indicator}
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {enableDrawingTools && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant={selectedDrawingTool ? 'default' : 'outline'} size="sm" className="h-8">
                    <Type className="h-4 w-4 mr-1" />
                    <span className="text-xs">Draw</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuLabel>Drawing Tools</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuCheckboxItem
                    checked={selectedDrawingTool === null}
                    onCheckedChange={() => setSelectedDrawingTool(null)}
                  >
                    Select/Move
                  </DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem
                    checked={selectedDrawingTool === 'horizontal_line'}
                    onCheckedChange={() => setSelectedDrawingTool('horizontal_line')}
                  >
                    <Minus className="h-4 w-4 mr-2" />
                    Horizontal Line
                  </DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem
                    checked={selectedDrawingTool === 'trend_line'}
                    onCheckedChange={() => setSelectedDrawingTool('trend_line')}
                  >
                    <TrendLineIcon className="h-4 w-4 mr-2" />
                    Trend Line
                  </DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem
                    checked={selectedDrawingTool === 'fibonacci'}
                    onCheckedChange={() => setSelectedDrawingTool('fibonacci')}
                  >
                    <Activity className="h-4 w-4 mr-2" />
                    Fibonacci
                  </DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem
                    checked={selectedDrawingTool === 'rectangle'}
                    onCheckedChange={() => setSelectedDrawingTool('rectangle')}
                  >
                    <Square className="h-4 w-4 mr-2" />
                    Rectangle
                  </DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem
                    checked={selectedDrawingTool === 'text'}
                    onCheckedChange={() => setSelectedDrawingTool('text')}
                  >
                    <Type className="h-4 w-4 mr-2" />
                    Text
                  </DropdownMenuCheckboxItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="h-8" disabled={isExporting}>
                  <Download className="h-4 w-4 mr-1" />
                  <span className="text-xs">Export</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Export Chart</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuCheckboxItem onClick={handleExportPNG} disabled={isExporting}>
                  <FileImage className="h-4 w-4 mr-2" />
                  Export as PNG
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem onClick={handleExportCSV} disabled={currentData.length === 0}>
                  <FileText className="h-4 w-4 mr-2" />
                  Export Data as CSV
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <div className="flex items-center gap-3 text-sm flex-wrap">
          <div className="flex items-center gap-1">
            <span className="text-muted-foreground">O:</span>
            <span className="font-mono">{formatValue(crosshairData.open)}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-muted-foreground">H:</span>
            <span className="font-mono text-green-500">{formatValue(crosshairData.high)}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-muted-foreground">L:</span>
            <span className="font-mono text-red-500">{formatValue(crosshairData.low)}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-muted-foreground">C:</span>
            <span className="font-mono">{formatValue(crosshairData.close)}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-muted-foreground">Vol:</span>
            <span className="font-mono">
              {crosshairData.volume ? (crosshairData.volume / 1000000).toFixed(2) + 'M' : '--'}
            </span>
          </div>

          {showSMA20 && crosshairData.sma20 !== null && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="flex items-center gap-1 cursor-help">
                    <span className="w-2 h-0.5 bg-blue-500" />
                    <span className="font-mono text-blue-500">{formatValue(crosshairData.sma20)}</span>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p className="font-medium">{INDICATOR_DESCRIPTIONS.sma20.name}</p>
                  <p className="text-xs text-muted-foreground">{INDICATOR_DESCRIPTIONS.sma20.description}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}

          {showSMA50 && crosshairData.sma50 !== null && (
            <div className="flex items-center gap-1">
              <span className="w-2 h-0.5 bg-green-500" />
              <span className="font-mono text-green-500">{formatValue(crosshairData.sma50)}</span>
            </div>
          )}

          {showBollinger && crosshairData.bollingerUpper !== null && (
            <div className="flex items-center gap-1">
              <span className="font-mono text-gray-400">{formatValue(crosshairData.bollingerLower)}</span>
              <span className="text-muted-foreground">-</span>
              <span className="font-mono text-gray-400">{formatValue(crosshairData.bollingerUpper)}</span>
            </div>
          )}
        </div>
      </div>
      
      <div ref={chartContainerRef} className="w-full" style={{ height: height - (showRSI || showMACD ? 250 : 0) - 60 }} />
      
      {(showRSI || showMACD) && indicatorResults && (
        <TechnicalIndicatorsPanel
          data={currentData}
          showRSI={showRSI}
          showMACD={showMACD}
          rsiPeriod={indicatorConfig.rsiPeriod}
          rsiOverbought={indicatorConfig.rsiOverbought}
          rsiOversold={indicatorConfig.rsiOversold}
          macdFast={indicatorConfig.macdFast}
          macdSlow={indicatorConfig.macdSlow}
          macdSignal={indicatorConfig.macdSignal}
          height={220}
        />
      )}
      
      <div className="p-2 border-t bg-muted/20 text-xs text-center text-muted-foreground">
        {currentData.length} data points • {timeframe} timeframe • Data by Polygon.io
        {activeIndicatorsCount > 0 && (
          <span className="ml-2">
            • Active: {showIndicators.filter(i => ['sma20', 'sma50', 'sma200', 'ema12', 'ema26', 'rsi', 'macd', 'bollinger'].includes(i)).join(', ')}
          </span>
        )}
        {drawings.length > 0 && (
          <span className="ml-2">
            • {drawings.length} drawing{drawings.length > 1 ? 's' : ''}
          </span>
        )}
      </div>
    </div>
  )
}
