'use client'

import { useMemo, useRef, useEffect, useState } from 'react'
import { createChart, ColorType, IChartApi, ISeriesApi, Time } from 'lightweight-charts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'
import { RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'

export interface RenkoBrick {
  startTime: string
  endTime: string
  open: number
  close: number
  high: number
  low: number
  direction: 'up' | 'down'
  isReversal: boolean
}

interface RenkoDataPoint {
  time: string
  close: number
  volume?: number
}

interface RenkoChartProps {
  data: RenkoDataPoint[]
  className?: string
  height?: number
  brickSize?: number
  showVolume?: boolean
}

function calculateRenko(data: RenkoDataPoint[], brickSize: number): RenkoBrick[] {
  if (data.length < 2) return []

  const bricks: RenkoBrick[] = []
  let currentPrice = data[0].close
  let direction: 'up' | 'down' = data[1].close >= currentPrice ? 'up' : 'down'
  let brickOpen = currentPrice - (direction === 'up' ? 0 : brickSize)
  let brickClose = direction === 'up' ? brickOpen + brickSize : brickOpen - brickSize

  for (let i = 1; i < data.length; i++) {
    const price = data[i].close
    const time = data[i].time

    while (true) {
      if (direction === 'up') {
        if (price >= brickClose + brickSize) {
          bricks.push({
            startTime: time,
            endTime: time,
            open: brickOpen,
            close: brickClose,
            high: brickClose,
            low: brickOpen,
            direction: 'up',
            isReversal: false
          })
          brickOpen = brickClose
          brickClose += brickSize
        } else if (price <= brickOpen - brickSize) {
          bricks.push({
            startTime: time,
            endTime: time,
            open: brickOpen,
            close: brickOpen - brickSize,
            high: brickOpen,
            low: brickOpen - brickSize,
            direction: 'down',
            isReversal: true
          })
          brickClose = brickOpen
          brickOpen = brickClose - brickSize
          direction = 'down'
        } else {
          break
        }
      } else {
        if (price <= brickClose - brickSize) {
          bricks.push({
            startTime: time,
            endTime: time,
            open: brickOpen,
            close: brickClose,
            high: brickOpen,
            low: brickClose,
            direction: 'down',
            isReversal: false
          })
          brickOpen = brickClose
          brickClose -= brickSize
        } else if (price >= brickOpen + brickSize) {
          bricks.push({
            startTime: time,
            endTime: time,
            open: brickOpen,
            close: brickOpen + brickSize,
            high: brickOpen + brickSize,
            low: brickOpen,
            direction: 'up',
            isReversal: true
          })
          brickClose = brickOpen
          brickOpen = brickClose + brickSize
          direction = 'up'
        } else {
          break
        }
      }
    }
  }

  return bricks
}

export function RenkoChart({
  data,
  className,
  height = 400,
  brickSize: initialBrickSize,
  showVolume = true
}: RenkoChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Custom'> | null>(null)
  const [brickSize, setBrickSize] = useState(initialBrickSize || 10)
  const [brickCount, setBrickCount] = useState(20)

  const renkoData = useMemo(() => {
    if (data.length === 0) return []
    const priceRange = Math.max(...data.map(d => d.close)) - Math.min(...data.map(d => d.close))
    const calculatedBrickSize = initialBrickSize || Math.max(priceRange / 50, 1)
    return calculateRenko(data, calculatedBrickSize)
  }, [data, initialBrickSize])

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
    if (!chartRef.current || renkoData.length === 0) return

    const upBricks = renkoData.filter(b => b.direction === 'up')
    const downBricks = renkoData.filter(b => b.direction === 'down')

    const upData = upBricks.map((brick, i) => ({
      time: (i + 1) as Time,
      open: brick.open,
      high: brick.high,
      low: brick.low,
      close: brick.close,
    }))

    const downData = downBricks.map((brick, i) => ({
      time: (i + 1) as Time,
      open: brick.open,
      high: brick.high,
      low: brick.low,
      close: brick.close,
    }))

    chartRef.current.timeScale().fitContent()
  }, [renkoData])

  const upTrendCount = renkoData.filter(b => b.direction === 'up').length
  const downTrendCount = renkoData.filter(b => b.direction === 'down').length
  const reversalCount = renkoData.filter(b => b.isReversal).length

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle>Renko Chart</CardTitle>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <Label className="text-xs">Brick Size</Label>
              <Input
                type="number"
                value={brickSize}
                onChange={(e) => setBrickSize(parseFloat(e.target.value) || 10)}
                className="w-20 h-8"
                min={0.01}
                step={0.01}
              />
            </div>
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
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="text-xs text-green-600 font-medium">Up Bricks</span>
            </div>
            <p className="text-xl font-bold text-green-700">{upTrendCount}</p>
          </div>
          <div className="p-3 rounded-lg bg-red-50 border border-red-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <span className="text-xs text-red-600 font-medium">Down Bricks</span>
            </div>
            <p className="text-xl font-bold text-red-700">{downTrendCount}</p>
          </div>
          <div className="p-3 rounded-lg bg-muted">
            <div className="flex items-center gap-2 mb-1">
              <RefreshCw className="h-4 w-4" />
              <span className="text-xs font-medium">Reversals</span>
            </div>
            <p className="text-xl font-bold">{reversalCount}</p>
          </div>
          <div className="p-3 rounded-lg bg-muted">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium">Total</span>
            </div>
            <p className="text-xl font-bold">{renkoData.length}</p>
          </div>
        </div>
        <div className="mt-4 p-3 rounded-lg bg-muted text-sm">
          <p className="font-medium mb-2">Renko Chart Interpretation</p>
          <div className="grid grid-cols-2 gap-2 text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-sm bg-green-500" />
              <span>Green bricks = Up trend</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-sm bg-red-500" />
              <span>Red bricks = Down trend</span>
            </div>
            <div className="flex items-center gap-2">
              <span>•</span>
              <span>Equal brick sizes filter noise</span>
            </div>
            <div className="flex items-center gap-2">
              <span>•</span>
              <span>Reversals show trend changes</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default RenkoChart
