'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  TrendingUp,
  Plus,
  X,
  RefreshCw,
  Minus,
  Activity,
} from 'lucide-react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js/auto'
import { Line } from 'react-chartjs-2'
import { cn } from '@/lib/utils'
import type { TimeFrame } from '@/lib/types/indicators'

interface ComparisonData {
  symbol: string
  name: string
  data: Array<{
    timestamp: string
    price: number
    normalized: number
    change: number
  }>
  currentPrice: number
  change: number
  changePercent: number
  color: string
}

interface ComparisonChartProps {
  symbols: string[]
  timeframe?: TimeFrame
  normalize?: boolean
  startDate?: Date
  endDate?: Date
  className?: string
}

const TIMEFRAME_OPTIONS = [
  { value: '1d', label: '1 Day' },
  { value: '1w', label: '1 Week' },
  { value: '1m', label: '1 Month' },
  { value: '3m', label: '3 Months' },
  { value: '6m', label: '6 Months' },
  { value: '1y', label: '1 Year' },
] as const

const PRESET_COMPARISONS = [
  {
    name: 'Tech Giants',
    symbols: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
  },
  {
    name: 'Major Indices',
    symbols: ['SPY', 'QQQ', 'IWM', 'DIA'],
  },
  {
    name: 'Auto Makers',
    symbols: ['TSLA', 'F', 'GM', 'RIVN', 'LCID'],
  },
  {
    name: 'Banks',
    symbols: ['JPM', 'BAC', 'WFC', 'C', 'GS'],
  },
]

const COLOR_PALETTE = [
  '#3b82f6', // blue
  '#22c55e', // green
  '#f59e0b', // orange
  '#ef4444', // red
  '#8b5cf6', // purple
  '#06b6d4', // cyan
  '#ec4899', // pink
  '#14b8a6', // teal
]

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
)

export function ComparisonChart({
  symbols: initialSymbols,
  timeframe = '1m',
  normalize = true,
  startDate,
  endDate,
  className,
}: ComparisonChartProps) {
  const [symbols, setSymbols] = useState<string[]>(initialSymbols.slice(0, 4))
  const [selectedTimeframe, setSelectedTimeframe] = useState<TimeFrame>(timeframe)
  const [comparisonData, setComparisonData] = useState<ComparisonData[]>([])
  const [loading, setLoading] = useState(false)
  const [newSymbol, setNewSymbol] = useState('')
  const [normalized, setNormalized] = useState(normalize)

  const symbolColors = symbols.reduce((acc, symbol, index) => {
    acc[symbol] = COLOR_PALETTE[index % COLOR_PALETTE.length]
    return acc
  }, {} as Record<string, string>)

  useEffect(() => {
    fetchComparisonData()
  }, [symbols, selectedTimeframe, normalized])

  const fetchComparisonData = async () => {
    setLoading(true)
    try {
      // Mock data for now - in production, fetch from API
      const now = new Date()
      const days = getTimeframeDays(selectedTimeframe)
      
      const data: ComparisonData[] = await Promise.all(
        symbols.map(async (symbol) => {
          // Generate mock historical data
          const basePrice = Math.random() * 1000 + 50
          const dataPoints = []
          let cumulativeChange = 0
          
          for (let i = days; i >= 0; i--) {
            const date = new Date(now)
            date.setDate(date.getDate() - i)
            
            const dailyChange = (Math.random() - 0.5) * 0.05
            cumulativeChange += dailyChange
            
            const price = basePrice * (1 + cumulativeChange)
            dataPoints.push({
              timestamp: date.toISOString(),
              price,
              normalized: 0, // Will be calculated
              change: cumulativeChange * 100,
            })
          }
          
          // Normalize to first data point
          const firstPrice = dataPoints[0].price
          dataPoints.forEach(point => {
            point.normalized = ((point.price - firstPrice) / firstPrice) * 100
          })
          
          const currentPrice = dataPoints[dataPoints.length - 1].price
          const totalChange = dataPoints[dataPoints.length - 1].change
          
          return {
            symbol,
            name: symbol,
            data: dataPoints,
            currentPrice,
            change: totalChange,
            changePercent: totalChange,
            color: symbolColors[symbol],
          }
        })
      )
      
      setComparisonData(data)
    } catch (error) {
      console.error('Failed to fetch comparison data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getTimeframeDays = (tf: TimeFrame): number => {
    switch (tf) {
      case '1d': return 1
      case '1w': return 7
      case '1m': return 30
      case '3m': return 90
      case '6m': return 180
      case '1y': return 365
      default: return 30
    }
  }

  const handleAddSymbol = () => {
    const symbol = newSymbol.toUpperCase().trim()
    if (symbol && !symbols.includes(symbol) && symbols.length < 4) {
      setSymbols([...symbols, symbol])
      setNewSymbol('')
    }
  }

  const handleRemoveSymbol = (symbol: string) => {
    const newSymbols = symbols.filter((s) => s !== symbol)
    setSymbols(newSymbols)
  }

  const handleApplyPreset = (presetSymbols: string[]) => {
    setSymbols(presetSymbols.slice(0, 4))
  }

  const labels = comparisonData[0]?.data.map((point) => {
    const date = new Date(point.timestamp)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }) || []

  const datasets = comparisonData.flatMap((data) => [
    {
      label: `${data.symbol} (Price)`,
      data: data.data.map((point) =>
        normalized ? point.normalized : point.price
      ),
      borderColor: data.color,
      backgroundColor: data.color + '20',
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 4,
      borderWidth: 2,
      fill: false,
      yAxisID: 'y',
    },
  ])

  const chartOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          boxWidth: 12,
          padding: 15,
          font: {
            size: 11,
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: (context: { datasetIndex: number; dataIndex: number }) => {
            const dataset = comparisonData[context.datasetIndex]
            const dataPoint = dataset?.data[context.dataIndex]
            if (!dataset || !dataPoint) return ''
            
            const value = normalized
              ? `${dataPoint.normalized.toFixed(2)}%`
              : `$${dataPoint.price.toFixed(2)}`
            
            return `${dataset.symbol}: ${value} (${dataPoint.change >= 0 ? '+' : ''}${dataPoint.change.toFixed(2)}%)`
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
          callback: (value: number) =>
            normalized ? `${value.toFixed(0)}%` : `$${value.toFixed(2)}`,
        },
      },
    },
  }

  const calculateCorrelation = (data1: number[], data2: number[]): number => {
    const n = Math.min(data1.length, data2.length)
    let sumX = 0,
      sumY = 0,
      sumXY = 0,
      sumX2 = 0,
      sumY2 = 0
    
    for (let i = 0; i < n; i++) {
      sumX += data1[i]
      sumY += data2[i]
      sumXY += data1[i] * data2[i]
      sumX2 += data1[i] * data1[i]
      sumY2 += data2[i] * data2[i]
    }
    
    const numerator = n * sumXY - sumX * sumY
    const denominator = Math.sqrt(
      (n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY)
    )
    
    return denominator === 0 ? 0 : numerator / denominator
  }

  const correlations = comparisonData.flatMap((data1, i) =>
    comparisonData.slice(i + 1).map((data2) => ({
      pair: `${data1.symbol}-${data2.symbol}`,
      value: calculateCorrelation(
        data1.data.map((d) => d.price),
        data2.data.map((d) => d.price)
      ),
    }))
  )

  return (
    <div className={cn('space-y-4', className)}>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Comparison Chart
                <Badge variant="secondary">{symbols.length} symbols</Badge>
              </CardTitle>
              <CardDescription>
                Compare multiple symbols performance
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={fetchComparisonData} disabled={loading}>
              <RefreshCw className={cn('h-4 w-4 mr-2', loading && 'animate-spin')} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-4 flex-wrap">
              <div className="flex-1 min-w-[200px]">
                <Label htmlFor="symbol">Add Symbol</Label>
                <div className="flex gap-2">
                  <Input
                    id="symbol"
                    value={newSymbol}
                    onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
                    placeholder="AAPL"
                    className="flex-1 font-mono uppercase"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleAddSymbol()
                    }}
                  />
                  <Button
                    size="sm"
                    onClick={handleAddSymbol}
                    disabled={symbols.length >= 4 || !newSymbol.trim()}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="flex-1 min-w-[200px]">
                <Label>Normalization</Label>
                <Select value={normalized ? 'true' : 'false'} onValueChange={(v) => setNormalized(v === 'true')}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="true">Normalized (%)</SelectItem>
                    <SelectItem value="false">Absolute ($)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex-1 min-w-[200px]">
                <Label>Timeframe</Label>
                <Select value={selectedTimeframe} onValueChange={(v) => setSelectedTimeframe(v as TimeFrame)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TIMEFRAME_OPTIONS.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Quick Presets</Label>
              <div className="flex gap-2 flex-wrap mt-2">
                {PRESET_COMPARISONS.map((preset) => (
                  <Button
                    key={preset.name}
                    variant="outline"
                    size="sm"
                    onClick={() => handleApplyPreset(preset.symbols)}
                  >
                    {preset.name}
                  </Button>
                ))}
              </div>
            </div>

            <div className="flex gap-2 flex-wrap">
              {symbols.map((symbol) => {
                const data = comparisonData.find((d) => d.symbol === symbol)
                return (
                  <Badge
                    key={symbol}
                    variant="outline"
                    className={cn(
                      'px-3 py-1 text-sm cursor-pointer',
                      data && data.change >= 0 ? 'border-green-500 text-green-700' : 'border-red-500 text-red-700'
                    )}
                    style={{
                      borderColor: data?.color,
                      backgroundColor: data?.color + '10',
                    }}
                  >
                    <span className="font-mono font-semibold mr-2">{symbol}</span>
                    {data && (
                      <span className="text-xs">
                        {data.change >= 0 ? '+' : ''}
                        {data.changePercent.toFixed(2)}%
                      </span>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleRemoveSymbol(symbol)
                      }}
                      className="ml-2 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )
              })}
            </div>

            {comparisonData.length > 0 && (
              <>
                <div className="h-80">
                  <Line data={{ labels, datasets }} options={chartOptions} />
                </div>

                {correlations.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Correlation Matrix</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {correlations.slice(0, 5).map((corr) => (
                          <div
                            key={corr.pair}
                            className="flex items-center justify-between text-sm"
                          >
                            <span className="font-mono">{corr.pair.replace('-', ' vs ')}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                                <div
                                  className={cn(
                                    'h-full transition-all',
                                    Math.abs(corr.value) > 0.7
                                      ? 'bg-green-500'
                                      : Math.abs(corr.value) > 0.4
                                      ? 'bg-yellow-500'
                                      : 'bg-red-500'
                                  )}
                                  style={{
                                    width: `${Math.abs(corr.value) * 100}%`,
                                    marginLeft: corr.value < 0 ? 'auto' : '0',
                                  }}
                                />
                              </div>
                              <span className="font-mono w-12 text-right">
                                {corr.value.toFixed(2)}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}

            {comparisonData.length === 0 && !loading && (
              <div className="text-center py-12 text-muted-foreground">
                <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No symbols to compare</p>
                <p className="text-sm">Add symbols above or select a preset</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
