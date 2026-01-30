'use client'

import { useState, useMemo, useCallback, useRef, useEffect } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
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
  ZoomIn,
  ZoomOut,
  Download,
  RefreshCw,
  Settings2,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Maximize2,
  Minimize2,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts'
import { cn } from '@/lib/utils'
import { useDownloadFile } from '@/hooks/useDownload'

export interface VolumeProfileData {
  price: number
  volume: number
  volumePercent: number
  cumulativeVolume: number
  cumulativePercent: number
  avgTradedPrice: number
  tradingRange: {
    low: number
    high: number
    pointOfControl: number
    valueAreaHigh: number
    valueAreaLow: number
  }
}

export interface VolumeProfilePoint {
  price: number
  volume: number
  buys: number
  sells: number
  delta: number
}

interface VolumeProfileChartProps {
  data?: VolumeProfilePoint[]
  symbol?: string
  timeframe?: string
  profileWidth?: number
  showValueArea?: boolean
  showPOC?: boolean
  showVA?: boolean
  colorScheme?: 'classic' | 'greenRed' | 'heat'
  className?: string
  onPointClick?: (point: VolumeProfilePoint) => void
}

interface AxisTickProps {
  x: number
  y: number
  payload: {
    value: string | number
  }
}

const TIMEFRAMES = [
  { value: '1d', label: '1 Day' },
  { value: '5d', label: '5 Days' },
  { value: '1w', label: '1 Week' },
  { value: '1m', label: '1 Month' },
  { value: '3m', label: '3 Months' },
  { value: '6m', label: '6 Months' },
  { value: '1y', label: '1 Year' },
]

const COLOR_SCHEMES = {
  classic: {
    positive: '#22c55e',
    negative: '#ef4444',
    poc: '#f59e0b',
    va: 'rgba(59, 130, 246, 0.2)',
    background: 'rgba(255, 255, 255, 0.05)',
  },
  greenRed: {
    positive: '#16a34a',
    negative: '#dc2626',
    poc: '#ea580c',
    va: 'rgba(34, 197, 94, 0.15)',
    background: 'rgba(0, 0, 0, 0.3)',
  },
  heat: {
    positive: '#f97316',
    negative: '#8b5cf6',
    poc: '#eab308',
    va: 'rgba(251, 191, 36, 0.2)',
    background: 'rgba(139, 92, 246, 0.1)',
  },
}

const formatPrice = (price: number): string => {
  if (price >= 1000) return `$${(price / 1000).toFixed(2)}K`
  if (price >= 1) return `$${price.toFixed(2)}`
  return `$${price.toFixed(4)}`
}

const formatVolume = (volume: number): string => {
  if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`
  if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`
  if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`
  return volume.toString()
}

const generateMockVolumeProfile = (
  basePrice: number,
  volatility: number = 0.02,
  numRows: number = 30
): VolumeProfilePoint[] => {
  const data: VolumeProfilePoint[] = []
  const priceStep = basePrice * volatility / numRows

  for (let i = 0; i < numRows; i++) {
    const price = basePrice - (numRows * priceStep / 2) + (i * priceStep)
    const volume = Math.abs(Math.random() * 1000000 + Math.sin(i / 5) * 500000)
    const buySellRatio = 0.4 + Math.random() * 0.2
    const buys = volume * buySellRatio
    const sells = volume * (1 - buySellRatio)

    data.push({
      price,
      volume,
      buys,
      sells,
      delta: buys - sells,
    })
  }

  const pocIndex = data.findIndex(d => d.volume === Math.max(...data.map(x => x.volume)))
  if (pocIndex !== -1) {
    const pocVolume = data[pocIndex].volume
    data.forEach((d, i) => {
      const distance = Math.abs(i - pocIndex)
      const falloff = Math.exp(-distance / 8)
      d.volume += pocVolume * falloff * 0.3
      d.buys *= 1 + falloff * 0.2
      d.sells *= 1 - falloff * 0.1
      d.delta = d.buys - d.sells
    })
  }

  return data.sort((a, b) => b.price - a.price)
}

function PriceAxisTick({ x, y, payload }: AxisTickProps) {
  return (
    <g transform={`translate(${x},${y})`}>
      <text
        x={0}
        y={0}
        dy={4}
        textAnchor="end"
        fill="currentColor"
        fontSize={11}
        className="text-muted-foreground"
      >
        {formatPrice(payload.value as number)}
      </text>
    </g>
  )
}

function VolumeTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null

  const data = payload[0]?.payload as VolumeProfilePoint
  if (!data) return null

  return (
    <Card className="bg-background/95 backdrop-blur-sm border-2">
      <CardContent className="p-3 space-y-2">
        <div className="flex items-center justify-between">
          <span className="font-medium">Price:</span>
          <span>{formatPrice(data.price)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Total Volume:</span>
          <span>{formatVolume(data.volume)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-green-600">Buys:</span>
          <span>{formatVolume(data.buys)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-red-600">Sells:</span>
          <span>{formatVolume(data.sells)}</span>
        </div>
        <div className="flex items-center justify-between pt-2 border-t">
          <span className="text-muted-foreground">Delta:</span>
          <span className={cn(data.delta > 0 ? 'text-green-600' : 'text-red-600')}>
            {formatVolume(data.delta)}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}

function VolumeProfileCanvas({
  data,
  colors,
  showPOC,
  showVA,
  poc,
  valueAreaHigh,
  valueAreaLow,
  onPointClick,
  profileWidth = 200,
}: {
  data: VolumeProfilePoint[]
  colors: typeof COLOR_SCHEMES.classic
  showPOC: boolean
  showVA: boolean
  poc: number
  valueAreaHigh: number
  valueAreaLow: number
  onPointClick?: (point: VolumeProfilePoint) => void
  profileWidth?: number
}) {
  const maxVolume = Math.max(...data.map(d => d.volume))
  const maxDelta = Math.max(...data.map(d => Math.abs(d.delta)))

  return (
    <div className="relative h-full">
      {data.map((point, index) => {
        const barWidth = (point.volume / maxVolume) * profileWidth
        const isPOC = Math.abs(point.price - poc) < 0.001
        const inVA = point.price >= valueAreaLow && point.price <= valueAreaHigh

        const deltaPercent = Math.abs(point.delta) / maxDelta
        const deltaBarWidth = deltaPercent * 40

        return (
          <div
            key={index}
            className={cn(
              'absolute flex items-center h-5 transition-all hover:opacity-80 cursor-pointer',
              onPointClick && 'cursor-pointer'
            )}
            style={{
              top: `${(index / data.length) * 100}%`,
              left: 0,
              right: 0,
              transform: 'translateY(-50%)',
            }}
            onClick={() => onPointClick?.(point)}
          >
            {point.delta > 0 ? (
              <>
                <div
                  className="h-full bg-green-500/30 rounded-r"
                  style={{ width: `${deltaBarWidth}px` }}
                />
                <div
                  className={cn(
                    'h-full rounded-r',
                    isPOC ? 'bg-yellow-500' : inVA ? colors.positive : 'bg-green-500/50'
                  )}
                  style={{ width: `${barWidth}px`, marginLeft: `${deltaBarWidth + 2}px` }}
                />
              </>
            ) : (
              <>
                <div
                  className={cn(
                    'h-full rounded-l',
                    isPOC ? 'bg-yellow-500' : inVA ? colors.negative : 'bg-red-500/50'
                  )}
                  style={{ width: `${barWidth}px` }}
                />
                <div
                  className="h-full bg-red-500/30 rounded-l"
                  style={{ width: `${deltaBarWidth}px`, marginLeft: '2px' }}
                />
              </>
            )}

            <span
              className="ml-2 text-xs text-muted-foreground absolute left-full whitespace-nowrap"
              style={{ left: `${profileWidth + 50}px` }}
            >
              {formatVolume(point.volume)}
            </span>
          </div>
        )
      })}

      {showPOC && (
        <div
          className="absolute left-0 right-0 border-2 border-yellow-500 dashed opacity-60"
          style={{ top: `${(data.findIndex(d => Math.abs(d.price - poc) < 0.001) / data.length) * 100}%` }}
        />
      )}

      {showVA && (
        <>
          <div
            className="absolute left-0 right-0 border border-blue-400 opacity-30"
            style={{ top: `${(data.findIndex(d => Math.abs(d.price - valueAreaHigh) < 0.001) / data.length) * 100}%` }}
          />
          <div
            className="absolute left-0 right-0 border border-blue-400 opacity-30"
            style={{ top: `${(data.findIndex(d => Math.abs(d.price - valueAreaLow) < 0.001) / data.length) * 100}%` }}
          />
          <div
            className="absolute left-0 right-0 bg-blue-400/5"
            style={{
              top: `${(data.findIndex(d => Math.abs(d.price - valueAreaHigh) < 0.001) / data.length) * 100}%`,
              bottom: `${(1 - data.findIndex(d => Math.abs(d.price - valueAreaLow) / data.length) / data.length) * 100}%`,
            }}
          />
        </>
      )}
    </div>
  )
}

export function VolumeProfileChart({
  data: propData,
  symbol = 'AAPL',
  timeframe = '1d',
  showValueArea = true,
  showPOC = true,
  showVA = true,
  colorScheme = 'classic',
  className,
  onPointClick,
}: VolumeProfileChartProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [timeframeValue, setTimeframeValue] = useState(timeframe)
  const [colorSchemeValue, setColorSchemeValue] = useState(colorScheme)
  const [showPOCValue, setShowPOCValue] = useState(showPOC)
  const [showVAValue, setShowVAValue] = useState(showVA)
  const [profileWidth, setProfileWidth] = useState(200)
  const [isLoading, setIsLoading] = useState(false)

  const data = useMemo(() => {
    if (propData) return propData

    const basePrice = 150 + Math.random() * 50
    return generateMockVolumeProfile(basePrice)
  }, [propData, timeframeValue])

  const { downloadCSV } = useDownloadFile()

  const calculations = useMemo(() => {
    const totalVolume = data.reduce((sum, d) => sum + d.volume, 0)
    const totalDelta = data.reduce((sum, d) => sum + d.delta, 0)

    const poc = data.reduce((maxP, d) => (d.volume > maxP.volume ? d : maxP), data[0]).price
    const totalVolAtPOC = data.find(d => Math.abs(d.price - poc) < 0.001)?.volume || 0

    let volAccumulator = 0
    let valueAreaHigh = poc
    let valueAreaLow = poc

    const sortedData = [...data].sort((a, b) => b.price - a.price)
    const pocIndex = sortedData.findIndex(d => Math.abs(d.price - poc) < 0.001)

    for (let i = 0; i < sortedData.length; i++) {
      const currentPrice = sortedData[i].price
      const currentVol = sortedData[i].volume

      if (currentPrice >= poc) {
        if (volAccumulator + currentVol <= totalVolume * 0.68) {
          volAccumulator += currentVol
          valueAreaHigh = currentPrice
        }
      } else {
        if (volAccumulator + currentVol <= totalVolume * 0.68) {
          volAccumulator += currentVol
          valueAreaLow = currentPrice
        }
      }
    }

    const avgTradedPrice = data.reduce((sum, d) => sum + d.price * d.volume, 0) / totalVolume

    return {
      totalVolume,
      totalDelta,
      poc,
      totalVolAtPOC,
      valueAreaHigh,
      valueAreaLow,
      avgTradedPrice,
      longVolume: data.filter(d => d.delta > 0).reduce((sum, d) => sum + d.volume, 0),
      shortVolume: data.filter(d => d.delta < 0).reduce((sum, d) => sum + d.volume, 0),
    }
  }, [data])

  const colors = COLOR_SCHEMES[colorSchemeValue]

  const handleRefresh = useCallback(async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 500))
    setIsLoading(false)
  }, [])

  const handleExport = useCallback(() => {
    const exportData = data.map(d => ({
      price: d.price.toFixed(4),
      volume: d.volume.toFixed(0),
      buys: d.buys.toFixed(0),
      sells: d.sells.toFixed(0),
      delta: d.delta.toFixed(0),
    }))
    const csvContent = [
      'Price,Volume,Buys,Sells,Delta',
      ...data.map(d => `${d.price},${d.volume},${d.buys},${d.sells},${d.delta}`),
    ].join('\n')
    downloadCSV(csvContent, `${symbol}_volume_profile`)
  }, [data, symbol, downloadCSV])

  const handleDownload = useCallback(() => {
    const csvContent = [
      'Price,Volume,Buys,Sells,Delta',
      ...data.map(d => `${d.price},${d.volume},${d.buys},${d.sells},${d.delta}`),
    ].join('\n')
    downloadCSV(csvContent, `${symbol}_volume_profile`)
  }, [data, symbol, downloadCSV])

  return (
    <Card className={cn('relative', isFullscreen && 'fixed inset-0 z-50 m-0 rounded-none', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              <CardTitle className="text-lg">Volume Profile</CardTitle>
            </div>
            <Badge variant="outline">{symbol}</Badge>
            <Badge variant="secondary">{timeframeValue}</Badge>
          </div>

          <div className="flex items-center gap-2">
            <Select value={timeframeValue} onValueChange={setTimeframeValue}>
              <SelectTrigger className="w-28 h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIMEFRAMES.map(tf => (
                  <SelectItem key={tf.value} value={tf.value}>{tf.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={colorSchemeValue} onValueChange={(value: string) => setColorSchemeValue(value as "classic" | "greenRed" | "heat")}>
              <SelectTrigger className="w-28 h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="classic">Classic</SelectItem>
                <SelectItem value="greenRed">Green/Red</SelectItem>
                <SelectItem value="heat">Heat</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isLoading}>
              <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
            </Button>

            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="h-4 w-4" />
            </Button>

            <Button variant="outline" size="sm" onClick={() => setIsFullscreen(!isFullscreen)}>
              {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div className="p-3 bg-muted/50 rounded-lg">
            <div className="text-xs text-muted-foreground mb-1">Total Volume</div>
            <div className="text-lg font-bold">{formatVolume(calculations.totalVolume)}</div>
          </div>
          <div className="p-3 bg-muted/50 rounded-lg">
            <div className="text-xs text-muted-foreground mb-1">Point of Control</div>
            <div className="text-lg font-bold text-yellow-500">{formatPrice(calculations.poc)}</div>
          </div>
          <div className="p-3 bg-muted/50 rounded-lg">
            <div className="text-xs text-muted-foreground mb-1">Value Area (68%)</div>
            <div className="text-lg font-bold text-blue-500">
              {formatPrice(calculations.valueAreaLow)} - {formatPrice(calculations.valueAreaHigh)}
            </div>
          </div>
          <div className="p-3 bg-muted/50 rounded-lg">
            <div className="text-xs text-muted-foreground mb-1">Delta</div>
            <div className={cn('text-lg font-bold', calculations.totalDelta > 0 ? 'text-green-500' : 'text-red-500')}>
              {calculations.totalDelta > 0 ? '+' : ''}{formatVolume(calculations.totalDelta)}
            </div>
          </div>
        </div>

        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="profile">Profile View</TabsTrigger>
            <TabsTrigger value="bar">Bar Chart</TabsTrigger>
            <TabsTrigger value="delta">Delta View</TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="h-96">
            <div className="flex gap-4 h-full">
              <div className="flex-1 relative pl-20">
                <div className="absolute left-0 top-0 bottom-0 w-16 flex flex-col justify-between py-2">
                  <div className="text-xs text-muted-foreground text-center">
                    {formatPrice(data[0]?.price || 0)}
                  </div>
                  <div className="text-xs text-muted-foreground text-center">
                    {formatPrice(data[Math.floor(data.length / 2)]?.price || 0)}
                  </div>
                  <div className="text-xs text-muted-foreground text-center">
                    {formatPrice(data[data.length - 1]?.price || 0)}
                  </div>
                </div>

                <VolumeProfileCanvas
                  data={data}
                  colors={colors}
                  showPOC={showPOCValue}
                  showVA={showVAValue}
                  poc={calculations.poc}
                  valueAreaHigh={calculations.valueAreaHigh}
                  valueAreaLow={calculations.valueAreaLow}
                  onPointClick={onPointClick}
                  profileWidth={profileWidth}
                />

                <div className="absolute right-0 top-0 bottom-0 w-24 flex flex-col justify-center items-center border-l border-dashed border-muted-foreground/30">
                  <div className="text-xs text-muted-foreground mb-2">Profile</div>
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <div className="flex gap-1">
                  <Button
                    variant={showPOCValue ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setShowPOCValue(!showPOCValue)}
                    className="text-xs"
                  >
                    POC
                  </Button>
                  <Button
                    variant={showVAValue ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setShowVAValue(!showVAValue)}
                    className="text-xs"
                  >
                    VA
                  </Button>
                </div>
                <div className="flex-1" />
                <div className="flex gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setProfileWidth(Math.max(100, profileWidth - 25))}
                    className="h-6 w-6 p-0"
                  >
                    <ZoomOut className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setProfileWidth(Math.min(300, profileWidth + 25))}
                    className="h-6 w-6 p-0"
                  >
                    <ZoomIn className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="bar" className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 60, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  type="number"
                  tickFormatter={(v) => formatVolume(v as number)}
                  className="text-xs"
                />
                <YAxis
                  type="number"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(v) => formatPrice(v as number)}
                  className="text-xs"
                  width={60}
                />
                <Tooltip content={<VolumeTooltip />} />
                <Bar dataKey="volume" radius={[0, 4, 4, 0]}>
                  {data.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.delta > 0 ? colors.positive : colors.negative}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </TabsContent>

          <TabsContent value="delta" className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 60, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  type="number"
                  tickFormatter={(v) => formatVolume(Math.abs(v as number))}
                  className="text-xs"
                />
                <YAxis
                  type="number"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(v) => formatPrice(v as number)}
                  className="text-xs"
                  width={60}
                />
                <Tooltip content={<VolumeTooltip />} />
                <Bar dataKey="delta" radius={[0, 4, 4, 0]}>
                  {data.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.delta > 0 ? colors.positive : colors.negative}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </TabsContent>
        </Tabs>

        <div className="flex items-center justify-center gap-6 mt-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-green-500" />
            <span>Buying (Delta +)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-red-500" />
            <span>Selling (Delta -)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-yellow-500" />
            <span>Point of Control</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-blue-500/30" />
            <span>Value Area (68%)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default VolumeProfileChart
