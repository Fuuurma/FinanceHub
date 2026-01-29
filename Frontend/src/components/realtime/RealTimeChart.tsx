'use client'

import { useState, useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  CategoryScale,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js/auto'
import { Line, Bar } from 'react-chartjs-2'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useRealtimeStore } from '@/stores/realtimeStore'
import { CHART_CONFIG } from '@/lib/constants/realtime'
import type { ChartTimeframe, ChartDataPoint } from '@/lib/constants/realtime'
import type { IndicatorConfig } from '@/lib/types/indicators'
import { cn } from '@/lib/utils'

ChartJS.register(
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  CategoryScale,
  Tooltip,
  Legend,
  Filler
)

interface RealTimeChartProps {
  symbol: string
  timeframe?: ChartTimeframe
  indicators?: IndicatorConfig[]
  onIndicatorsChange?: (indicators: IndicatorConfig[]) => void
  showDrawingTools?: boolean
  showIndicatorsPanel?: boolean
}

export function RealTimeChart({
  symbol,
  timeframe = CHART_CONFIG.DEFAULT_TIMEFRAME,
  indicators = [],
  onIndicatorsChange,
  showDrawingTools = false,
  showIndicatorsPanel = false,
}: RealTimeChartProps) {
  const { prices, charts, setChartTimeframe } = useRealtimeStore()
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [isUpdating, setIsUpdating] = useState(false)
  const [showIndicators, setShowIndicators] = useState(showIndicatorsPanel || indicators.length > 0)
  const [selectedIndicators, setSelectedIndicators] = useState<IndicatorConfig[]>(indicators)
  const updateIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const chartRef = useRef<ChartJS<'line'> | null>(null)
  const [drawingMode, setDrawingMode] = useState<string | null>(null)

  useEffect(() => {
    setChartTimeframe(symbol, timeframe)
  }, [symbol, timeframe, setChartTimeframe])

  // Sync indicators with parent
  useEffect(() => {
    if (indicators.length > 0) {
      setSelectedIndicators(indicators)
      setShowIndicators(true)
    }
  }, [indicators])

  useEffect(() => {
    const bufferSize = CHART_CONFIG.BUFFER_SIZES[timeframe]
    const priceData = prices[symbol]

    if (priceData) {
      const newDataPoint: ChartDataPoint = {
        time: priceData.timestamp,
        price: priceData.price,
        volume: priceData.volume,
      }

      setChartData((prev) => {
        const updated = [...prev, newDataPoint].slice(-bufferSize)
        return updated
      })
    }

    setIsUpdating(true)
    updateIntervalRef.current = setTimeout(() => {
      setIsUpdating(false)
    }, CHART_CONFIG.UPDATE_INTERVAL)

    return () => {
      if (updateIntervalRef.current) {
        clearTimeout(updateIntervalRef.current)
      }
    }
  }, [symbol, prices, timeframe])

  const labels = chartData.map((d) => {
    const date = new Date(d.time)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  })

  const priceValues = chartData.map((d) => d.price)
  const volumeValues = chartData.map((d) => d.volume)

  const lineData = {
    labels,
    datasets: [
      {
        label: 'Price',
        data: priceValues,
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2,
        yAxisID: 'y',
      },
    ],
  }

  const volumeData = {
    labels,
    datasets: [
      {
        label: 'Volume',
        data: volumeValues,
        backgroundColor: 'rgba(148, 163, 184, 0.5)',
        borderColor: 'rgb(148, 163, 184)',
        borderWidth: 1,
        yAxisID: 'y1',
        borderRadius: 4,
      },
    ],
  }

  const timeframeOptions = Object.keys(CHART_CONFIG.BUFFER_SIZES) as ChartTimeframe[]

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || ''
            const value = context.parsed.y

            if (context.dataset.yAxisID === 'y1') {
              return `${label}: ${value?.toLocaleString()}`
            }

            return `${label}: $${value?.toFixed(2)}`
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: 'rgba(148, 163, 184, 0.5)',
          maxTicksLimit: 8,
        },
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        grid: {
          color: 'rgba(148, 163, 184, 0.1)',
        },
        ticks: {
          color: 'rgba(148, 163, 184, 0.5)',
          callback: (value: any) => `$${value.toFixed(2)}`,
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: 'rgba(148, 163, 184, 0.5)',
          callback: (value: any) => value?.toLocaleString(),
        },
      },
    },
  }

  if (chartData.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center border rounded-lg bg-background">
        <p className="text-muted-foreground">Waiting for real-time data...</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">{symbol} Price Chart</h3>
          {isUpdating && (
            <span className="text-xs text-muted-foreground animate-pulse">
              Updating...
            </span>
          )}
        </div>

        <div className="flex gap-1 flex-wrap">
          {timeframeOptions.map((tf) => (
            <Button
              key={tf}
              size="sm"
              variant={timeframe === tf ? 'default' : 'outline'}
              onClick={() => setChartTimeframe(symbol, tf)}
              className={cn(
                'text-xs font-mono',
                timeframe === tf && 'bg-primary text-primary-foreground'
              )}
            >
              {tf}
            </Button>
          ))}
          <Button
            size="sm"
            variant={showIndicators ? 'default' : 'outline'}
            onClick={() => {
              const newValue = !showIndicators
              setShowIndicators(newValue)
              if (!newValue && selectedIndicators.length === 0) {
                setSelectedIndicators([])
              }
            }}
            className="text-xs"
          >
            {showIndicators ? 'Hide Indicators' : 'Show Indicators'}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="chart" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="chart">Price & Volume</TabsTrigger>
          <TabsTrigger value="volume">Volume Only</TabsTrigger>
        </TabsList>

        <TabsContent value="chart" className="space-y-4">
          <div className="h-80">
            <Line data={lineData} options={commonOptions} />
          </div>
          <div className="h-32">
            <Bar data={volumeData} options={commonOptions} />
          </div>
        </TabsContent>
      </Tabs>
      {/* Technical Indicators Panel */}
      {showIndicators && (
        <div className="mt-4 border-t pt-4">
          <h4 className="text-sm font-semibold mb-3">Active Indicators</h4>
          {selectedIndicators.length === 0 ? (
            <p className="text-sm text-muted-foreground">No indicators applied. Add indicators from the panel above.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {selectedIndicators.map((ind) => (
                <Badge
                  key={ind.type}
                  variant="outline"
                  className="px-3 py-1"
                  style={{ borderColor: ind.color, color: ind.color }}
                >
                  {ind.type.toUpperCase()} ({ind.params.period || 'default'})
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
        </div>
      )}
    </div>
  )
}
