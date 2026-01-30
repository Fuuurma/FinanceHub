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
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
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

export interface CandlestickData {
  time: Time
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

interface CandlestickChartProps {
  data?: CandlestickData[]
  symbol?: string
  timeframe?: Timeframe
  height?: number
  showVolume?: boolean
  showToolbar?: boolean
  className?: string
}

export function CandlestickChart({
  data: externalData,
  symbol = 'BTC/USD',
  timeframe: initialTimeframe = '1h',
  height = 400,
  showVolume = true,
  showToolbar = true,
  className,
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  
  const { theme } = useTheme()
  const downloadFile = useDownloadFile()
  
  const [timeframe, setTimeframe] = useState<Timeframe>(initialTimeframe)
  const [isLoading, setIsLoading] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const colors = useMemo(() => ({
    background: theme === 'dark' ? '#0a0a0a' : '#ffffff',
    grid: theme === 'dark' ? '#1a1a1a' : '#e5e5e5',
    text: theme === 'dark' ? '#a0a0a0' : '#666666',
    upColor: '#26a69a',
    downColor: '#ef5350',
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350',
    volumeUpColor: 'rgba(38, 166, 154, 0.5)',
    volumeDownColor: 'rgba(239, 83, 80, 0.5)',
  }), [theme])

  const data = useMemo(() => {
    if (externalData) return externalData
    
    const mockData: CandlestickData[] = []
    let price = 50000 + Math.random() * 5000
    const now = Date.now()
    const interval = 60000
    
    for (let i = 0; i < 200; i++) {
      const time = Math.floor((now - (200 - i) * interval) / 1000) as Time
      const volatility = 0.02
      
      const open = price
      const change = (Math.random() - 0.5) * volatility * price
      const close = open + change
      const high = Math.max(open, close) + Math.random() * volatility * price * 0.5
      const low = Math.min(open, close) - Math.random() * volatility * price * 0.5
      const volume = Math.floor(Math.random() * 1000000) + 100000
      
      mockData.push({
        time,
        open,
        high,
        low,
        close,
        volume,
      })
      
      price = close
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

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: colors.upColor,
      downColor: colors.downColor,
      borderDownColor: colors.downColor,
      borderUpColor: colors.upColor,
      wickDownColor: colors.wickDownColor,
      wickUpColor: colors.wickUpColor,
    })

    candlestickSeriesRef.current = candlestickSeries

    if (showVolume) {
      const volumeSeries = chart.addHistogramSeries({
        color: colors.volumeDownColor,
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: 'volume',
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
  }, [colors, height, showVolume, isFullscreen])

  useEffect(() => {
    if (candlestickSeriesRef.current) {
      candlestickSeriesRef.current.setData(data)
    }

    if (volumeSeriesRef.current && showVolume) {
      const volumeData = data.map((d) => ({
        time: d.time,
        value: d.volume || 0,
        color: d.close >= d.open ? colors.volumeUpColor : colors.volumeDownColor,
      }))
      volumeSeriesRef.current.setData(volumeData)
    }
  }, [data, showVolume, colors.volumeUpColor, colors.volumeDownColor])

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
            downloadFile(blob, `${symbol.replace('/', '-')}-candlestick-${timeframe}.png`)
          }
        })
      }
    }
  }, [chartRef, downloadFile, symbol, timeframe])

  const currentPrice = data[data.length - 1]
  const previousPrice = data[data.length - 2]
  const priceChange = currentPrice ? ((currentPrice.close - previousPrice.close) / previousPrice.close) * 100 : 0

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
