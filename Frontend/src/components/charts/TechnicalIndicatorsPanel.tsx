'use client'

import { useEffect, useRef, useMemo } from 'react'
import {
  createChart,
  IChartApi,
  ColorType,
  Time,
  LineSeries,
  HistogramSeries,
} from 'lightweight-charts'
import { useTheme } from 'next-themes'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { HelpCircle, TrendingUp, TrendingDown, Minus, Info } from 'lucide-react'
import type { OHLCVData } from '@/components/charts/TradingViewChart'
import {
  calculateRSI,
  calculateMACD,
  formatIndicatorValue,
  getRSISignal,
  getMACDSignal,
  INDICATOR_DESCRIPTIONS,
} from '@/lib/utils/technical-indicators'

interface TechnicalIndicatorsPanelProps {
  data: OHLCVData[]
  showRSI?: boolean
  showMACD?: boolean
  rsiPeriod?: number
  rsiOverbought?: number
  rsiOversold?: number
  macdFast?: number
  macdSlow?: number
  macdSignal?: number
  height?: number
  onIndicatorValueChange?: (indicator: string, value: number | null) => void
}

export function TechnicalIndicatorsPanel({
  data,
  showRSI = true,
  showMACD = true,
  rsiPeriod = 14,
  rsiOverbought = 70,
  rsiOversold = 30,
  macdFast = 12,
  macdSlow = 26,
  macdSignal = 9,
  height = 200,
  onIndicatorValueChange,
}: TechnicalIndicatorsPanelProps) {
  const rsiContainerRef = useRef<HTMLDivElement>(null)
  const macdContainerRef = useRef<HTMLDivElement>(null)
  const rsiChartRef = useRef<IChartApi | null>(null)
  const macdChartRef = useRef<IChartApi | null>(null)
  const { theme } = useTheme()

  const isDark = theme === 'dark'

  const chartColors = useMemo(() => ({
    background: isDark ? '#0f172a' : '#ffffff',
    text: isDark ? '#94a3b8' : '#64748b',
    grid: isDark ? '#1e293b' : '#e2e8f0',
    upColor: '#22c55e',
    downColor: '#ef4444',
    macdColor: '#3b82f6',
    signalColor: '#f59e0b',
    histogramUp: 'rgba(34, 197, 94, 0.5)',
    histogramDown: 'rgba(239, 68, 68, 0.5)',
    overbought: '#ef4444',
    oversold: '#22c55e',
    middle: isDark ? '#64748b' : '#9ca3af',
  }), [isDark])

  const closes = data.map(d => d.close)
  const times = data.map(d => d.date as Time)

  const rsiData = useMemo(() => calculateRSI(closes, rsiPeriod), [closes, rsiPeriod])
  const macdData = useMemo(
    () => calculateMACD(closes, macdFast, macdSlow, macdSignal),
    [closes, macdFast, macdSlow, macdSignal]
  )

  const latestRSI = rsiData[rsiData.length - 1]
  const latestMACD = macdData.macd[macdData.macd.length - 1]
  const latestSignal = macdData.signal[macdData.signal.length - 1]

  useEffect(() => {
    if (!showRSI || !rsiContainerRef.current || !data.length) return

    if (rsiChartRef.current) {
      rsiChartRef.current.remove()
    }

    const chart = createChart(rsiContainerRef.current, {
      width: rsiContainerRef.current.clientWidth,
      height: height - 40,
      layout: {
        background: { type: ColorType.Solid, color: chartColors.background },
        textColor: chartColors.text,
      },
      grid: {
        vertLines: { color: chartColors.grid, style: 2 },
        horzLines: { color: chartColors.grid, style: 2 },
      },
      rightPriceScale: {
        borderVisible: false,
        scaleMargins: { top: 0.1, bottom: 0.1 },
      },
      timeScale: {
        visible: false,
      },
      handleScroll: {
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: false,
        mouseWheel: false,
        pinch: false,
      },
    })

    rsiChartRef.current = chart

    const lineSeries = chart.addSeries(LineSeries, {
      color: '#8b5cf6',
      lineWidth: 2,
      priceFormat: {
        type: 'price',
        precision: 0,
        minMove: 1,
      },
    })

    const rsiValidData = rsiData
      .map((value, index) => (isNaN(value) ? null : { time: times[index], value }))
      .filter((item): item is { time: Time; value: number } => item !== null)

    lineSeries.setData(rsiValidData)

    chart.priceScale().applyOptions({
      autoScale: true,
    })

    const handleResize = () => {
      if (rsiContainerRef.current && rsiChartRef.current) {
        rsiChartRef.current.applyOptions({
          width: rsiContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [showRSI, data, rsiPeriod, chartColors, height, rsiData, times])

  useEffect(() => {
    if (!showMACD || !macdContainerRef.current || !data.length) return

    if (macdChartRef.current) {
      macdChartRef.current.remove()
    }

    const chart = createChart(macdContainerRef.current, {
      width: macdContainerRef.current.clientWidth,
      height: height - 40,
      layout: {
        background: { type: ColorType.Solid, color: chartColors.background },
        textColor: chartColors.text,
      },
      grid: {
        vertLines: { color: chartColors.grid, style: 2 },
        horzLines: { color: chartColors.grid, style: 2 },
      },
      rightPriceScale: {
        borderVisible: false,
        scaleMargins: { top: 0.1, bottom: 0.1 },
      },
      timeScale: {
        visible: false,
      },
      handleScroll: {
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: false,
        mouseWheel: false,
        pinch: false,
      },
    })

    macdChartRef.current = chart

    const macdLine = chart.addSeries(LineSeries, {
      color: chartColors.macdColor,
      lineWidth: 2,
    })

    const signalLine = chart.addSeries(LineSeries, {
      color: chartColors.signalColor,
      lineWidth: 2,
    })

    const histogramSeries = chart.addSeries(HistogramSeries, {
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
      priceScaleId: '',
    })

    const macdValidData = macdData.macd
      .map((value, index) => (isNaN(value) ? null : { time: times[index], value }))
      .filter((item): item is { time: Time; value: number } => item !== null)

    const signalValidData = macdData.signal
      .map((value, index) => (isNaN(value) ? null : { time: times[index], value }))
      .filter((item): item is { time: Time; value: number } => item !== null)

    const histogramValidData = macdData.histogram
      .map((value, index) => {
        if (isNaN(value)) return null
        return {
          time: times[index],
          value,
          color: value >= 0 ? chartColors.upColor : chartColors.downColor,
        }
      })
      .filter((item): item is { time: Time; value: number; color: string } => item !== null)

    macdLine.setData(macdValidData)
    signalLine.setData(signalValidData)
    histogramSeries.setData(histogramValidData)

    histogramSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.7, bottom: 0 },
      borderVisible: false,
    })

    const handleResize = () => {
      if (macdContainerRef.current && macdChartRef.current) {
        macdChartRef.current.applyOptions({
          width: macdContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [showMACD, data, macdFast, macdSlow, macdSignal, chartColors, height, macdData, times])

  const rsiSignal = getRSISignal(latestRSI, rsiOverbought, rsiOversold)
  const macdSignalType = getMACDSignal(latestMACD, latestSignal)

  if (!showRSI && !showMACD) {
    return null
  }

  return (
    <div className="space-y-4">
      <Tabs defaultValue={showRSI ? 'rsi' : 'macd'} className="w-full">
        <TabsList className="grid w-full grid-cols-2" style={{ maxWidth: 300 }}>
          {showRSI && (
            <TabsTrigger value="rsi" className="flex items-center gap-2">
              RSI
              {latestRSI && (
                <Badge
                  variant={rsiSignal === 'overbought' ? 'destructive' : rsiSignal === 'oversold' ? 'default' : 'secondary'}
                  className={rsiSignal === 'oversold' ? 'bg-green-500' : ''}
                >
                  {rsiSignal === 'overbought' ? 'OB' : rsiSignal === 'oversold' ? 'OS' : 'N'}
                </Badge>
              )}
            </TabsTrigger>
          )}
          {showMACD && (
            <TabsTrigger value="macd" className="flex items-center gap-2">
              MACD
              {latestMACD && latestSignal && (
                <Badge
                  variant={macdSignalType === 'bullish' ? 'default' : macdSignalType === 'bearish' ? 'destructive' : 'secondary'}
                  className={macdSignalType === 'bullish' ? 'bg-green-500' : ''}
                >
                  {macdSignalType === 'bullish' ? '↑' : macdSignalType === 'bearish' ? '↓' : '→'}
                </Badge>
              )}
            </TabsTrigger>
          )}
        </TabsList>

        {showRSI && (
          <TabsContent value="rsi" className="mt-4">
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-sm font-medium">
                      Relative Strength Index (RSI)
                    </CardTitle>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="h-4 w-4 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-sm">
                          <p className="font-medium mb-1">{INDICATOR_DESCRIPTIONS.rsi.fullName}</p>
                          <p className="text-sm text-muted-foreground mb-2">
                            {INDICATOR_DESCRIPTIONS.rsi.description}
                          </p>
                          <p className="text-sm">
                            <span className="text-red-500 font-medium">Overbought (≥{rsiOverbought}):</span> May indicate price is too high and could reverse down.
                          </p>
                          <p className="text-sm">
                            <span className="text-green-500 font-medium">Oversold (≤{rsiOversold}):</span> May indicate price is too low and could reverse up.
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <span className="text-muted-foreground">RSI({rsiPeriod}):</span>
                      {latestRSI !== undefined && !isNaN(latestRSI) ? (
                        <span className={`font-mono font-bold ${
                          rsiSignal === 'overbought' ? 'text-red-500' :
                          rsiSignal === 'oversold' ? 'text-green-500' : ''
                        }`}>
                          {formatIndicatorValue(latestRSI)}
                        </span>
                      ) : (
                        <span className="font-mono">--</span>
                      )}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 text-xs text-muted-foreground mb-2">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-red-500" />
                    Overbought ({rsiOverbought}+)
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-green-500" />
                    Oversold ({rsiOversold}-)
                  </span>
                </div>
                <div ref={rsiContainerRef} className="w-full" style={{ height: height - 40 }} />
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {showMACD && (
          <TabsContent value="macd" className="mt-4">
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-sm font-medium">
                      MACD ({macdFast},{macdSlow},{macdSignal})
                    </CardTitle>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="h-4 w-4 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-sm">
                          <p className="font-medium mb-1">{INDICATOR_DESCRIPTIONS.macd.fullName}</p>
                          <p className="text-sm text-muted-foreground mb-2">
                            {INDICATOR_DESCRIPTIONS.macd.description}
                          </p>
                          <div className="space-y-1 text-sm">
                            <p>
                              <span className="text-blue-500 font-medium">MACD Line:</span> {macdFast}-EMA minus {macdSlow}-EMA
                            </p>
                            <p>
                              <span className="text-amber-500 font-medium">Signal Line:</span> {macdSignal}-period EMA of MACD
                            </p>
                            <p>
                              <span className="font-medium">Histogram:</span> MACD minus Signal
                            </p>
                          </div>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <span className="w-3 h-0.5 bg-blue-500" />
                      <span className="text-muted-foreground">MACD:</span>
                      {latestMACD !== undefined && !isNaN(latestMACD) ? (
                        <span className={`font-mono ${
                          macdSignalType === 'bullish' ? 'text-green-500' :
                          macdSignalType === 'bearish' ? 'text-red-500' : ''
                        }`}>
                          {formatIndicatorValue(latestMACD)}
                        </span>
                      ) : (
                        <span className="font-mono">--</span>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="w-3 h-0.5 bg-amber-500" />
                      <span className="text-muted-foreground">Signal:</span>
                      {latestSignal !== undefined && !isNaN(latestSignal) ? (
                        <span className="font-mono">{formatIndicatorValue(latestSignal)}</span>
                      ) : (
                        <span className="font-mono">--</span>
                      )}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 text-xs text-muted-foreground mb-2">
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-0.5 bg-blue-500" />
                    MACD ({macdFast},{macdSlow})
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-0.5 bg-amber-500" />
                    Signal ({macdSignal})
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 bg-green-500/50" />
                    Histogram
                  </span>
                </div>
                <div ref={macdContainerRef} className="w-full" style={{ height: height - 40 }} />
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}
