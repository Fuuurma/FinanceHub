'use client'

import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import {
  createChart,
  IChartApi,
  ISeriesApi,
  ColorType,
  CrosshairMode,
  Time,
} from 'lightweight-charts'
import { useTheme } from 'next-themes'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Download,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Maximize2,
  Minimize2,
} from 'lucide-react'
import { useDownloadFile } from '@/hooks/useDownload'
import { cn } from '@/lib/utils'

export type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w' | '1M'

export interface AreaData {
  time: Time
  value: number
}

interface AreaChartProps {
  data?: AreaData[]
  symbol?: string
  timeframe?: Timeframe
  height?: number
  showToolbar?: boolean
  lineColor?: string
  topColor?: string
  bottomColor?: string
  lineWidth?: number
  className?: string
}

export function AreaChart({
  data: externalData,
  symbol = 'BTC/USD',
  timeframe: initialTimeframe = '1h',
  height = 400,
  showToolbar = true,
  lineColor,
  topColor,
  bottomColor,
  lineWidth = 2,
  className,
}: AreaChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const areaSeriesRef = useRef<ISeriesApi<'Area'> | null>(null)
  
  const { theme } = useTheme()
  const downloadFile = useDownloadFile()
  
  const [timeframe, setTimeframe] = useState<Timeframe>(initialTimeframe)
  const [isLoading, setIsLoading] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const colors = useMemo(() => {
    const defaultLineColor = theme === 'dark' ? '#26a69a' : '#0ea5e9'
    const defaultTopColor = theme === 'dark' ? 'rgba(38, 166, 154, 0.4)' : 'rgba(14, 165, 233, 0.4)'
    const defaultBottomColor = theme === 'dark' ? 'rgba(38, 166, 154, 0.0)' : 'rgba(14, 165, 233, 0.0)'
    
    return {
      background: theme === 'dark' ? '#0a0a0a' : '#ffffff',
      grid: theme === 'dark' ? '#1a1a1a' : '#e5e5e5',
      text: theme === 'dark' ? '#a0a0a0' : '#666666',
      line: lineColor || defaultLineColor,
      top: topColor || defaultTopColor,
      bottom: bottomColor || defaultBottomColor,
    }
  }, [theme, lineColor, topColor, bottomColor])

  const data = useMemo(() => {
    if (externalData) return externalData
    
    const mockData: AreaData[] = []
    let value = 50000 + Math.random() * 5000
    const now = Date.now()
    const interval = 60000
    
    for (let i = 0; i < 200; i++) {
      const time = Math.floor((now - (200 - i) * interval) / 1000) as Time
      const change = (Math.random() - 0.5) * 500
      value = Math.max(value + change, 1000)
      
      mockData.push({
        time,
        value,
      })
    }
    
    return mockData
  }, [externalData, symbol, timeframe])

  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: isFullscreen ? window.innerHeight - 100 : height,
      layout: {
        background: { type: ColorType.Solid, color: colors.background },
        textColor: colors.text,
      },
      grid: {
        vertLines: { color: colors.grid },
        horzLines: { color: colors.grid },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: colors.grid,
      },
      timeScale: {
        borderColor: colors.grid,
        timeVisible: true,
        secondsVisible: false,
      },
    })

    chartRef.current = chart

    const areaSeries = chart.addAreaSeries({
      lineColor: colors.line,
      topColor: colors.top,
      bottomColor: colors.bottom,
      lineWidth,
      priceLineVisible: false,
    })

    areaSeriesRef.current = areaSeries

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: isFullscreen ? window.innerHeight - 100 : height,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      if (chartRef.current) {
        chartRef.current.remove()
        chartRef.current = null
      }
    }
  }, [colors, height, lineWidth, isFullscreen])

  useEffect(() => {
    if (areaSeriesRef.current) {
      areaSeriesRef.current.setData(data)
    }
  }, [data])

  const handleRefresh = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000))
    } catch (err) {
      setError('Failed to refresh data')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const handleDownloadImage = useCallback(() => {
    if (chartRef.current) {
      const canvas = chartContainerRef.current?.querySelector('canvas')
      if (canvas) {
        canvas.toBlob((blob) => {
          if (blob) {
            downloadFile(blob, `${symbol.replace('/', '-')}-area-${timeframe}.png`)
          }
        })
      }
    }
  }, [chartRef, downloadFile, symbol, timeframe])

  const currentValue = data[data.length - 1]
  const previousValue = data[data.length - 2]
  const priceChange = currentValue && previousValue ? ((currentValue.value - previousValue.value) / previousValue.value) * 100 : 0

  return (
    <Card className={cn('relative', className)}>
      {showToolbar && (
        <div className="absolute top-2 right-2 z-10 flex items-center gap-2">
          <Badge variant={priceChange >= 0 ? 'default' : 'destructive'}>
            {priceChange >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
            {priceChange.toFixed(2)}%
          </Badge>
          
          <Select value={timeframe} onValueChange={(value) => setTimeframe(value as Timeframe)}>
            <SelectTrigger className="h-8 w-[80px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1m">1m</SelectItem>
              <SelectItem value="5m">5m</SelectItem>
              <SelectItem value="15m">15m</SelectItem>
              <SelectItem value="1h">1H</SelectItem>
              <SelectItem value="4h">4H</SelectItem>
              <SelectItem value="1d">1D</SelectItem>
              <SelectItem value="1w">1W</SelectItem>
              <SelectItem value="1M">1M</SelectItem>
            </SelectContent>
          </Select>

          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefresh}
            disabled={isLoading}
            className="h-8 w-8"
          >
            <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
          </Button>

          <Button
            variant="ghost"
            size="icon"
            onClick={handleDownloadImage}
            className="h-8 w-8"
          >
            <Download className="h-4 w-4" />
          </Button>

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="h-8 w-8"
          >
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
        </div>
      )}

      <div ref={chartContainerRef} className="w-full" />
      
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/80">
          <div className="text-center">
            <p className="text-destructive font-medium">{error}</p>
            <Button variant="outline" size="sm" className="mt-2" onClick={handleRefresh}>
              Retry
            </Button>
          </div>
        </div>
      )}
    </Card>
  )
}
