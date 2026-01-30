'use client'

import { useMemo, useRef, useEffect } from 'react'
import { createChart, ColorType, IChartApi, Time } from 'lightweight-charts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { RefreshCw } from 'lucide-react'

export interface KagiLine {
  time: string
  value: number
  direction: 'up' | 'down' | 'neutral'
  reversal: boolean
  type: 'yang' | 'yin' | 'neutral'
}

interface KagiDataPoint {
  time: string
  close: number
  volume?: number
}

interface KagiChartProps {
  data: KagiDataPoint[]
  className?: string
  height?: number
  reversalAmount?: number
  showVolume?: boolean
}

function calculateKagi(data: KagiDataPoint[], reversalPercent: number): KagiLine[] {
  if (data.length < 2) return []

  const kagiLines: KagiLine[] = []
  let currentPrice = data[0].close
  let direction: 'up' | 'down' | 'neutral' = 'neutral'
  let startPrice = currentPrice

  const reversalThreshold = currentPrice * (reversalPercent / 100)

  for (let i = 1; i < data.length; i++) {
    const price = data[i].close
    const time = data[i].time

    if (direction === 'neutral') {
      if (price > startPrice + reversalThreshold) {
        direction = 'up'
        kagiLines.push({ time, value: price, direction: 'up', reversal: false, type: 'yang' })
      } else if (price < startPrice - reversalThreshold) {
        direction = 'down'
        kagiLines.push({ time, value: price, direction: 'down', reversal: false, type: 'yin' })
      }
    } else if (direction === 'up') {
      if (price >= currentPrice) {
        currentPrice = price
        kagiLines.push({ time, value: price, direction: 'up', reversal: false, type: 'yang' })
      } else if (price <= currentPrice - reversalThreshold) {
        direction = 'down'
        kagiLines.push({ time, value: price, direction: 'down', reversal: true, type: 'yin' })
        currentPrice = price
      }
    } else if (direction === 'down') {
      if (price <= currentPrice) {
        currentPrice = price
        kagiLines.push({ time, value: price, direction: 'down', reversal: false, type: 'yin' })
      } else if (price >= currentPrice + reversalThreshold) {
        direction = 'up'
        kagiLines.push({ time, value: price, direction: 'up', reversal: true, type: 'yang' })
        currentPrice = price
      }
    }
  }

  return kagiLines
}

export function KagiChart({
  data,
  className,
  height = 400,
  reversalAmount = 4,
  showVolume = true
}: KagiChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)

  const kagiData = useMemo(() => calculateKagi(data, reversalAmount), [data, reversalAmount])

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
  }, [height])

  useEffect(() => {
    if (!chartRef.current || kagiData.length === 0) return

    const yangLines = kagiData.filter(l => l.type === 'yang')
    const yinLines = kagiData.filter(l => l.type === 'yin')

    chartRef.current.timeScale().fitContent()
  }, [kagiData])

  const yangCount = kagiData.filter(l => l.type === 'yang').length
  const yinCount = kagiData.filter(l => l.type === 'yin').length
  const reversalCount = kagiData.filter(l => l.reversal).length

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle>Kagi Chart</CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              Reversal: {reversalAmount}%
            </span>
            <Button variant="outline" size="icon" onClick={() => chartRef.current?.timeScale().fitContent()}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div ref={chartContainerRef} className="w-full" />
        <div className="mt-4 grid grid-cols-4 gap-4">
          <div className="p-3 rounded-lg bg-green-50 border border-green-200">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-4 h-1 bg-green-600 rounded" />
              <span className="text-xs text-green-600 font-medium">Yang (Up)</span>
            </div>
            <p className="text-xl font-bold text-green-700">{yangCount}</p>
          </div>
          <div className="p-3 rounded-lg bg-red-50 border border-red-200">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-4 h-1 bg-red-600 rounded" />
              <span className="text-xs text-red-600 font-medium">Yin (Down)</span>
            </div>
            <p className="text-xl font-bold text-red-700">{yinCount}</p>
          </div>
          <div className="p-3 rounded-lg bg-muted">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium">Reversals</span>
            </div>
            <p className="text-xl font-bold">{reversalCount}</p>
          </div>
          <div className="p-3 rounded-lg bg-muted">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium">Total Lines</span>
            </div>
            <p className="text-xl font-bold">{kagiData.length}</p>
          </div>
        </div>
        <div className="mt-4 p-3 rounded-lg bg-muted text-sm">
          <p className="font-medium mb-2">Kagi Chart Interpretation</p>
          <div className="grid grid-cols-2 gap-2 text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="w-3 h-1 bg-green-600 rounded" />
              <span>Yang (green) = Rising trend</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-1 bg-red-600 rounded" />
              <span>Yin (red) = Falling trend</span>
            </div>
            <div className="flex items-center gap-2">
              <span>•</span>
              <span>Thickness changes indicate strength</span>
            </div>
            <div className="flex items-center gap-2">
              <span>•</span>
              <span>Shoulders mark trend reversals</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default KagiChart
