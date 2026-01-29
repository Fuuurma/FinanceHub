'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { createChart, ColorType, CrosshairMode, Time, IChartApi, ISeriesApi } from 'lightweight-charts'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, ZoomIn, ZoomOut, Maximize2, RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { ChartDataPoint, TimeFrame } from '@/lib/types/indicators'
import type { IndicatorConfig } from '@/lib/types/indicators'
import { calculateIndicator, type IndicatorResult } from '@/lib/utils/indicator-calculations'

export type ChartType = 'candlestick' | 'line' | 'area' | 'bar'

export type DrawingType =
  | 'horizontal_line'
  | 'vertical_line'
  | 'trend_line'
  | 'fibonacci'
  | 'rectangle'
  | 'text'

export interface Drawing {
  id: string
  type: DrawingType
  startTime: string
  startValue: number
  endTime?: string
  endValue?: number
  color: string
  text?: string
  visible: boolean
  createdAt: string
}

export interface AdvancedChartProps {
  symbol: string
  initialData?: ChartDataPoint[]
  chartType?: ChartType
  timeframe?: TimeFrame
  indicators?: IndicatorConfig[]
  showVolume?: boolean
  showIndicators?: boolean
  height?: number
  className?: string
  selectedDrawingTool?: DrawingType | null
  drawings?: Drawing[]
  onTimeframeChange?: (timeframe: TimeFrame) => void
  onChartTypeChange?: (chartType: ChartType) => void
  onIndicatorsChange?: (indicators: IndicatorConfig[]) => void
  onDrawingComplete?: (drawing: Drawing) => void
  onDrawingStart?: (point: { time: string; value: number }) => void
}

const CHART_CONFIG = {
  DEFAULT_HEIGHT: 500,
  VOLUME_HEIGHT: 150,
  CANDLE_UP_COLOR: '#22c55e',
  CANDLE_DOWN_COLOR: '#ef4444',
  GRID_COLOR: '#e1e1e1',
  TEXT_COLOR: '#666666',
  BACKGROUND_COLOR: '#ffffff',
} as const

const TIMEFRAMES: TimeFrame[] = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']

const CHART_TYPES: { value: ChartType; label: string }[] = [
  { value: 'candlestick', label: 'Candles' },
  { value: 'line', label: 'Line' },
  { value: 'area', label: 'Area' },
  { value: 'bar', label: 'Bar' },
]

export function AdvancedChart({
  symbol,
  initialData = [],
  chartType = 'candlestick',
  timeframe = '1h',
  indicators = [],
  showVolume = true,
  showIndicators = false,
  height = CHART_CONFIG.DEFAULT_HEIGHT,
  className,
  selectedDrawingTool = null,
  drawings = [],
  onTimeframeChange,
  onChartTypeChange,
  onIndicatorsChange,
  onDrawingComplete,
  onDrawingStart,
}: AdvancedChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<any> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const indicatorSeriesRef = useRef<Map<string, ISeriesApi<any>>>(new Map())

  const [loading, setLoading] = useState(false)
  const [currentChartType, setCurrentChartType] = useState<ChartType>(chartType)
  const [currentTimeframe, setCurrentTimeframe] = useState<TimeFrame>(timeframe)
  const [activeIndicators, setActiveIndicators] = useState<IndicatorConfig[]>(indicators)
  const [chartData, setChartData] = useState<ChartDataPoint[]>(initialData)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [drawingInProgress, setDrawingInProgress] = useState(false)
  const [drawingStartPoint, setDrawingStartPoint] = useState<{ time: string; value: number } | null>(null)

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: isFullscreen ? window.innerHeight - 200 : height,
      layout: {
        background: { type: ColorType.Solid, color: CHART_CONFIG.BACKGROUND_COLOR },
        textColor: CHART_CONFIG.TEXT_COLOR,
      },
      grid: {
        vertLines: { color: CHART_CONFIG.GRID_COLOR, visible: true },
        horzLines: { color: CHART_CONFIG.GRID_COLOR, visible: true },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          width: 1,
          color: CHART_CONFIG.GRID_COLOR,
          style: 2,
          visible: true,
          labelVisible: true,
        },
        horzLine: {
          width: 1,
          color: CHART_CONFIG.GRID_COLOR,
          style: 2,
          visible: true,
          labelVisible: true,
        },
      },
      rightPriceScale: {
        borderColor: CHART_CONFIG.GRID_COLOR,
      },
      leftPriceScale: {
        visible: false,
        borderColor: CHART_CONFIG.GRID_COLOR,
      },
      timeScale: {
        borderColor: CHART_CONFIG.GRID_COLOR,
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 5,
        barSpacing: 6,
        minBarSpacing: 2,
      },
      handleScale: true,
      handleScroll: true,
      kineticScroll: {
        mouse: true,
        touch: true,
      },
    })

    chart.addPriceScale('indicator', {
      visible: false,
      autoScale: true,
      scaleMargins: { top: 0.1, bottom: 0.1 },
    })

    chart.addPriceScale('macd', {
      visible: false,
      autoScale: true,
      scaleMargins: { top: 0.8, bottom: 0 },
    })

    chart.addPriceScale('stochastic', {
      visible: false,
      autoScale: true,
      scaleMargins: { top: 0.1, bottom: 0.1 },
    })

    chartRef.current = chart

    // Click handler for drawing tools
    const handleClick = (param: any) => {
      if (!selectedDrawingTool || !param.point || !param.time) return

      const time = param.time as string
      const price = param.point.y

      if (!drawingInProgress) {
        setDrawingInProgress(true)
        setDrawingStartPoint({ time, value: price })
        onDrawingStart?.({ time, value: price })
      } else {
        setDrawingInProgress(false)
        const newDrawing: Drawing = {
          id: `drawing-${Date.now()}`,
          type: selectedDrawingTool,
          startTime: drawingStartPoint!.time,
          startValue: drawingStartPoint!.value,
          endTime: time,
          endValue: price,
          color: '#3b82f6',
          visible: true,
          createdAt: new Date().toISOString(),
        }
        onDrawingComplete?.(newDrawing)
        setDrawingStartPoint(null)
      }
    }

    chart.subscribeClick(handleClick)

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: isFullscreen ? window.innerHeight - 200 : height,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.unsubscribeClick(handleClick)
      chart.remove()
    }
  }, [height, isFullscreen, selectedDrawingTool, drawingInProgress, drawingStartPoint, onDrawingStart, onDrawingComplete])

  // Update chart type
  useEffect(() => {
    if (!chartRef.current) return

    if (seriesRef.current) {
      chartRef.current.removeSeries(seriesRef.current)
      seriesRef.current = null
    }

    let newSeries: ISeriesApi<any> | null = null

    switch (currentChartType) {
      case 'candlestick':
        newSeries = chartRef.current.addCandlestickSeries({
          upColor: CHART_CONFIG.CANDLE_UP_COLOR,
          downColor: CHART_CONFIG.CANDLE_DOWN_COLOR,
          borderUpColor: CHART_CONFIG.CANDLE_UP_COLOR,
          borderDownColor: CHART_CONFIG.CANDLE_DOWN_COLOR,
          wickUpColor: CHART_CONFIG.CANDLE_UP_COLOR,
          wickDownColor: CHART_CONFIG.CANDLE_DOWN_COLOR,
        })
        break
      case 'line':
        newSeries = chartRef.current.addLineSeries({
          color: CHART_CONFIG.CANDLE_UP_COLOR,
          lineWidth: 2,
          crosshairMarkerVisible: true,
          crosshairMarkerRadius: 5,
        })
        break
      case 'area':
        newSeries = chartRef.current.addAreaSeries({
          topColor: 'rgba(34, 197, 94, 0.5)',
          bottomColor: 'rgba(34, 197, 94, 0.0)',
          lineColor: CHART_CONFIG.CANDLE_UP_COLOR,
          lineWidth: 2,
        })
        break
      case 'bar':
        newSeries = chartRef.current.addBarSeries({
          upColor: CHART_CONFIG.CANDLE_UP_COLOR,
          downColor: CHART_CONFIG.CANDLE_DOWN_COLOR,
        })
        break
    }

    if (newSeries) {
      seriesRef.current = newSeries
    }
  }, [currentChartType])

  // Update data
  useEffect(() => {
    if (!chartRef.current || !seriesRef.current || chartData.length === 0) return

    const data = chartData.map((d) => ({
      time: d.timestamp as Time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }))

    seriesRef.current.setData(data)
    chartRef.current.timeScale().fitContent()
  }, [chartData, currentChartType])

  // Update volume
  useEffect(() => {
    if (!chartRef.current || !showVolume) return

    if (volumeSeriesRef.current) {
      chartRef.current.removeSeries(volumeSeriesRef.current)
    }

    const volumeSeries = chartRef.current.addHistogramSeries({
      color: '#94a3b8',
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    })

    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    })

    const volumeData = chartData.map((d) => ({
      time: d.timestamp as Time,
      value: d.volume,
      color: d.close >= d.open ? CHART_CONFIG.CANDLE_UP_COLOR + '80' : CHART_CONFIG.CANDLE_DOWN_COLOR + '80',
    }))

    volumeSeries.setData(volumeData)
    volumeSeriesRef.current = volumeSeries
  }, [chartData, showVolume])

  // Update indicators
  useEffect(() => {
    if (!chartRef.current || chartData.length === 0) return

    indicatorSeriesRef.current.forEach((series) => {
      chartRef.current?.removeSeries(series)
    })
    indicatorSeriesRef.current.clear()

    activeIndicators.forEach((indicator) => {
      if (!indicator.visible) return

      const results = calculateIndicator(chartData, indicator)
      
      switch (indicator.type) {
        case 'sma':
        case 'ema':
        case 'wma':
        case 'atr':
        case 'rsi':
        case 'cci':
        case 'williams_r':
        case 'mfi': {
          const series = chartRef.current?.addLineSeries({
            color: indicator.color,
            lineWidth: 2,
            priceScaleId: indicator.secondary_yaxis ? 'indicator' : 'right',
          })
          if (series) {
            const data = results.filter((r) => !isNaN(r.value)).map((r) => ({
              time: r.timestamp as Time,
              value: r.value,
            }))
            series.setData(data)
            indicatorSeriesRef.current.set(indicator.type, series)
          }
          break
        }
        case 'bollinger': {
          const middleSeries = chartRef.current?.addLineSeries({
            color: indicator.color,
            lineWidth: 1,
            lineStyle: 2,
            priceScaleId: indicator.secondary_yaxis ? 'indicator' : 'right',
          })
          if (middleSeries) {
            const data = results.filter((r) => !isNaN(r.value)).map((r) => ({
              time: r.timestamp as Time,
              value: r.value,
            }))
            middleSeries.setData(data)
            indicatorSeriesRef.current.set('bollinger-middle', middleSeries)
          }

          const upperSeries = chartRef.current?.addLineSeries({
            color: indicator.color,
            lineWidth: 1,
            lineStyle: 2,
            priceScaleId: indicator.secondary_yaxis ? 'indicator' : 'right',
          })
          if (upperSeries) {
            const data = results.filter((r) => !isNaN(r.upper)).map((r) => ({
              time: r.timestamp as Time,
              value: r.upper!,
            }))
            upperSeries.setData(data)
            indicatorSeriesRef.current.set('bollinger-upper', upperSeries)
          }

          const lowerSeries = chartRef.current?.addLineSeries({
            color: indicator.color,
            lineWidth: 1,
            lineStyle: 2,
            priceScaleId: indicator.secondary_yaxis ? 'indicator' : 'right',
          })
          if (lowerSeries) {
            const data = results.filter((r) => !isNaN(r.lower)).map((r) => ({
              time: r.timestamp as Time,
              value: r.lower!,
            }))
            lowerSeries.setData(data)
            indicatorSeriesRef.current.set('bollinger-lower', lowerSeries)
          }
          break
        }
        case 'macd': {
          const macdSeries = chartRef.current?.addLineSeries({
            color: indicator.color,
            lineWidth: 2,
            priceScaleId: 'macd',
          })
          if (macdSeries) {
            const data = results.filter((r) => !isNaN(r.value)).map((r) => ({
              time: r.timestamp as Time,
              value: r.value,
            }))
            macdSeries.setData(data)
            indicatorSeriesRef.current.set('macd-line', macdSeries)
          }

          const signalSeries = chartRef.current?.addLineSeries({
            color: '#f59e0b',
            lineWidth: 2,
            priceScaleId: 'macd',
          })
          if (signalSeries) {
            const data = results.filter((r) => !isNaN(r.signal)).map((r) => ({
              time: r.timestamp as Time,
              value: r.signal!,
            }))
            signalSeries.setData(data)
            indicatorSeriesRef.current.set('macd-signal', signalSeries)
          }

          const histogramSeries = chartRef.current?.addHistogramSeries({
            color: '#94a3b8',
            priceScaleId: 'macd',
          })
          if (histogramSeries) {
            histogramSeries.priceScale().applyOptions({
              scaleMargins: { top: 0.8, bottom: 0 },
            })
            const data = results.filter((r) => !isNaN(r.histogram)).map((r) => ({
              time: r.timestamp as Time,
              value: r.histogram!,
              color: (r.histogram! >= 0 ? CHART_CONFIG.CANDLE_UP_COLOR : CHART_CONFIG.CANDLE_DOWN_COLOR) + '80',
            }))
            histogramSeries.setData(data)
            indicatorSeriesRef.current.set('macd-histogram', histogramSeries)
          }
          break
        }
        case 'stochastic': {
          const kSeries = chartRef.current?.addLineSeries({
            color: indicator.color,
            lineWidth: 2,
            priceScaleId: 'stochastic',
          })
          if (kSeries) {
            const data = results.filter((r) => !isNaN(r.value)).map((r) => ({
              time: r.timestamp as Time,
              value: r.value,
            }))
            kSeries.setData(data)
            indicatorSeriesRef.current.set('stochastic-k', kSeries)
          }

          const dSeries = chartRef.current?.addLineSeries({
            color: '#f59e0b',
            lineWidth: 2,
            priceScaleId: 'stochastic',
          })
          if (dSeries) {
            const data = results.filter((r) => !isNaN(r.signal)).map((r) => ({
              time: r.timestamp as Time,
              value: r.signal!,
            }))
            dSeries.setData(data)
            indicatorSeriesRef.current.set('stochastic-d', dSeries)
          }
          break
        }
      }
    })
  }, [chartData, activeIndicators])

  const handleTimeframeChange = useCallback((tf: TimeFrame) => {
    setCurrentTimeframe(tf)
    onTimeframeChange?.(tf)
    setLoading(true)
    setTimeout(() => setLoading(false), 1000)
  }, [onTimeframeChange])

  const handleChartTypeChange = useCallback((ct: ChartType) => {
    setCurrentChartType(ct)
    onChartTypeChange?.(ct)
  }, [onChartTypeChange])

  const handleZoomIn = useCallback(() => {
    chartRef.current?.applyOptions({
      timeScale: {
        barSpacing: (chartRef.current?.options().timeScale?.barSpacing || 6) * 1.2,
      },
    })
  }, [])

  const handleZoomOut = useCallback(() => {
    chartRef.current?.applyOptions({
      timeScale: {
        barSpacing: (chartRef.current?.options().timeScale?.barSpacing || 6) / 1.2,
      },
    })
  }, [])

  const handleResetZoom = useCallback(() => {
    chartRef.current?.timeScale().fitContent()
  }, [])

  const toggleFullscreen = useCallback(() => {
    setIsFullscreen(prev => !prev)
  }, [])

  const handleIndicatorToggle = useCallback((indicator: IndicatorConfig) => {
    const exists = activeIndicators.find(ind => ind.type === indicator.type)
    let newIndicators: IndicatorConfig[]

    if (exists) {
      newIndicators = activeIndicators.filter(ind => ind.type !== indicator.type)
    } else {
      newIndicators = [...activeIndicators, { ...indicator, visible: true }]
    }

    setActiveIndicators(newIndicators)
    onIndicatorsChange?.(newIndicators)
  }, [activeIndicators, onIndicatorsChange])

  const lastCandle = chartData[chartData.length - 1]
  const prevCandle = chartData[chartData.length - 2]
  const priceChange = prevCandle ? ((lastCandle.close - prevCandle.close) / prevCandle.close * 100) : 0

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                {symbol}
                {loading && <Loader2 className="h-4 w-4 animate-spin" />}
                {selectedDrawingTool && (
                  <Badge variant="outline" className="text-xs">
                    Drawing: {selectedDrawingTool.replace('_', ' ')}
                  </Badge>
                )}
              </CardTitle>
              <CardDescription>
                {currentChartType.charAt(0).toUpperCase() + currentChartType.slice(1)} Chart
              </CardDescription>
            </div>
          </div>

          <div className="flex items-center gap-2" role="toolbar" aria-label="Chart controls">
            <div className="flex items-center gap-1 bg-muted rounded-md p-1" role="group" aria-label="Timeframe selection">
              {TIMEFRAMES.map((tf) => (
                <Button
                  key={tf}
                  variant={currentTimeframe === tf ? 'default' : 'ghost'}
                  size="sm"
                  className={cn(
                    'h-7 px-2 text-xs font-mono',
                    currentTimeframe === tf && 'bg-primary text-primary-foreground'
                  )}
                  onClick={() => handleTimeframeChange(tf)}
                  aria-label={`${tf} timeframe`}
                  aria-pressed={currentTimeframe === tf}
                >
                  {tf}
                </Button>
              ))}
            </div>

            <Select value={currentChartType} onValueChange={(v) => handleChartTypeChange(v as ChartType)}>
              <SelectTrigger className="w-32 h-8" aria-label="Chart type">
                <SelectValue placeholder="Chart type" />
              </SelectTrigger>
              <SelectContent>
                {CHART_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="flex items-center gap-1 border rounded-md" role="group" aria-label="Zoom controls">
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleZoomIn} aria-label="Zoom in">
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleZoomOut} aria-label="Zoom out">
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleResetZoom} aria-label="Reset zoom">
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>

            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={toggleFullscreen} aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}>
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {activeIndicators.length > 0 && (
          <div className="flex items-center gap-2 mt-2" role="list" aria-label="Active indicators">
            <span className="text-sm text-muted-foreground">Indicators:</span>
            {activeIndicators.map((indicator) => (
              <Badge key={indicator.type} variant="outline" className="text-xs" style={{ borderColor: indicator.color, color: indicator.color }}>
                {indicator.type.toUpperCase()}
              </Badge>
            ))}
          </div>
        )}
      </CardHeader>

      <CardContent>
        <div ref={chartContainerRef} className="w-full rounded-lg border overflow-hidden" style={{ height: isFullscreen ? window.innerHeight - 200 : height }} role="img" aria-label={`${symbol} price chart`}>
          {chartData.length === 0 && !loading && (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              <p>No data available for {symbol}</p>
            </div>
          )}
        </div>

        {chartData.length > 0 && (
          <div className="flex items-center justify-between mt-2 pt-2 border-t">
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-full bg-green-500" />
                <span>Open: ${lastCandle?.open.toFixed(2)}</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-full bg-red-500" />
                <span>Close: ${lastCandle?.close.toFixed(2)}</span>
              </div>
              <div className="flex items-center gap-1">
                <span>High: ${lastCandle?.high.toFixed(2)}</span>
              </div>
              <div className="flex items-center gap-1">
                <span>Low: ${lastCandle?.low.toFixed(2)}</span>
              </div>
              <div className="flex items-center gap-1">
                {priceChange >= 0 ? <TrendingUp className="h-4 w-4 text-green-500" /> : <TrendingDown className="h-4 w-4 text-red-500" />}
                <span className="font-medium">{priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%</span>
              </div>
            </div>
            <div className="text-sm text-muted-foreground">{chartData.length} candles</div>
          </div>
        )}

        {activeIndicators.length > 0 && chartData.length > 0 && (
          <div className="flex items-center gap-4 mt-2 pt-2 border-t text-xs">
            <span className="text-muted-foreground">Indicators:</span>
            {activeIndicators.slice(0, 3).map((indicator) => {
              const results = calculateIndicator(chartData, indicator)
              const lastValue = results[results.length - 1]?.value
              if (isNaN(lastValue)) return null
              return (
                <div key={indicator.type} className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: indicator.color }} />
                  <span className="capitalize">{indicator.type}:</span>
                  <span className="font-mono">{lastValue.toFixed(2)}</span>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
