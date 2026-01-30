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
  Activity,
} from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { cn, formatNumber, formatCurrency } from '@/lib/utils'
import { useDownloadFile } from '@/hooks/useDownload'

export interface DepthLevel {
  price: number
  bids: number
  asks: number
  bidVolume: number
  askVolume: number
  bidCumulative: number
  askCumulative: number
  spread: number
  spreadPercent: number
}

export interface DepthPoint {
  price: number
  bidDepth: number
  askDepth: number
  bidCumulative: number
  askCumulative: number
}

export interface OrderBookData {
  symbol: string
  bids: { price: number; size: number; total: number }[]
  asks: { price: number; size: number; total: number }[]
  spread: number
  spreadPercent: number
  midPrice: number
  timestamp: string
}

interface DepthChartProps {
  data?: OrderBookData
  depthLevels?: DepthLevel[]
  symbol?: string
  colorScheme?: 'classic' | 'blueRed' | 'greenRed'
  showCumulative?: boolean
  showMidPrice?: boolean
  className?: string
  onRefresh?: () => void
}

const TIMEFRAMES = [
  { value: 'realtime', label: 'Realtime' },
  { value: '1s', label: '1 Second' },
  { value: '5s', label: '5 Seconds' },
  { value: '1m', label: '1 Minute' },
]

export function DepthChart({
  data,
  depthLevels = [],
  symbol = '',
  colorScheme = 'blueRed',
  showCumulative = false,
  showMidPrice = true,
  className,
  onRefresh,
}: DepthChartProps) {
  const [activeTab, setActiveTab] = useState('depth')
  const [selectedTimeframe, setSelectedTimeframe] = useState('realtime')
  const [showMid, setShowMid] = useState(showMidPrice)
  const [showCum, setShowCum] = useState(showCumulative)
  const [isExporting, setIsExporting] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const chartRef = useRef<HTMLDivElement>(null)
  const { downloadCSV, downloadText } = useDownloadFile()

  const colors = useMemo(() => {
    switch (colorScheme) {
      case 'greenRed':
        return { bid: '#22c55e', ask: '#ef4444', bidFill: '#22c55e20', askFill: '#ef444420' }
      case 'blueRed':
        return { bid: '#3b82f6', ask: '#ef4444', bidFill: '#3b82f620', askFill: '#ef444420' }
      default:
        return { bid: '#22c55e', ask: '#ef4444', bidFill: '#22c55e20', askFill: '#ef444420' }
    }
  }, [colorScheme])

  const chartData = useMemo(() => {
    if (depthLevels.length > 0) {
      return depthLevels.map(level => ({
        price: level.price,
        bidDepth: level.bids,
        askDepth: level.asks,
        bidCumulative: level.bidCumulative,
        askCumulative: level.askCumulative,
        spread: level.spread,
      }))
    }

    if (data) {
      const maxPrice = Math.max(...data.asks.map(a => a.price))
      const minPrice = Math.min(...data.bids.map(b => b.price))
      const priceStep = (maxPrice - minPrice) / 50

      const levels: DepthPoint[] = []
      for (let price = minPrice; price <= maxPrice; price += priceStep) {
        const bidDepth = data.bids
          .filter(b => b.price >= price && b.price < price + priceStep)
          .reduce((sum, b) => sum + b.size, 0)
        const askDepth = data.asks
          .filter(a => a.price >= price && a.price < price + priceStep)
          .reduce((sum, a) => sum + a.size, 0)

        levels.push({
          price: parseFloat(price.toFixed(2)),
          bidDepth,
          askDepth,
          bidCumulative: 0,
          askCumulative: 0,
        })
      }

      let bidCum = 0
      let askCum = 0
      for (let i = levels.length - 1; i >= 0; i--) {
        bidCum += levels[i].bidDepth
        levels[i].bidCumulative = bidCum
      }
      for (let i = 0; i < levels.length; i++) {
        askCum += levels[i].askDepth
        levels[i].askCumulative = askCum
      }

      return levels
    }

    return []
  }, [data, depthLevels])

  const maxDepth = useMemo(() => {
    return Math.max(
      ...chartData.map(d => Math.max(showCum ? d.bidCumulative : d.bidDepth, showCum ? d.askCumulative : d.askDepth))
    )
  }, [chartData, showCum])

  const midPrice = useMemo(() => {
    if (data) return data.midPrice
    if (chartData.length > 0) {
      const bids = chartData.filter(d => d.bidDepth > 0)
      const asks = chartData.filter(d => d.askDepth > 0)
      if (bids.length > 0 && asks.length > 0) {
        const bidHigh = Math.max(...bids.map(b => b.price))
        const askLow = Math.min(...asks.map(a => a.price))
        return (bidHigh + askLow) / 2
      }
    }
    return 0
  }, [data, chartData])

  const handleExportCSV = useCallback(() => {
    if (chartData.length === 0) return

    const headers = ['Price', 'Bid Depth', 'Ask Depth', 'Bid Cumulative', 'Ask Cumulative']
    const rows = chartData.map(row => [
      row.price.toFixed(2),
      row.bidDepth.toFixed(4),
      row.askDepth.toFixed(4),
      row.bidCumulative.toFixed(4),
      row.askCumulative.toFixed(4),
    ])

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
    const filename = `depth-${symbol || 'chart'}-${new Date().toISOString().slice(0, 10)}.csv`
    downloadCSV(csvContent, filename)
  }, [chartData, symbol, downloadCSV])

  const handleExportPNG = useCallback(async () => {
    if (!chartRef.current) return
    setIsExporting(true)

    try {
      const html2canvas = (await import('html2canvas')).default
      const canvas = await html2canvas(chartRef.current, { scale: 2 })
      const dataUrl = canvas.toDataURL('image/png')
      const filename = `depth-${symbol || 'chart'}-${new Date().toISOString().slice(0, 10)}.png`
      downloadText(dataUrl, filename, 'image/png')
    } catch (err) {
      console.error('Failed to export PNG:', err)
    } finally {
      setIsExporting(false)
    }
  }, [symbol, downloadText])

  if (!data && depthLevels.length === 0) {
    return (
      <Card className={cn('border-2 border-foreground', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Order Book Depth
          </CardTitle>
          <CardDescription>Loading depth data...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center">
            <div className="animate-pulse flex flex-col items-center">
              <BarChart3 className="h-8 w-8 text-muted-foreground mb-2" />
              <span className="text-sm text-muted-foreground">Waiting for market data</span>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('border-2 border-foreground', isFullscreen && 'fixed inset-4 z-50', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Order Book Depth
              {symbol && <Badge variant="secondary">{symbol}</Badge>}
            </CardTitle>
            <CardDescription>
              {data && (
                <span>
                  Spread: {formatCurrency(data.spread)} ({data.spreadPercent.toFixed(3)}%) • Mid: {formatCurrency(data.midPrice)}
                </span>
              )}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={selectedTimeframe} onValueChange={setSelectedTimeframe}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIMEFRAMES.map(tf => (
                  <SelectItem key={tf.value} value={tf.value}>{tf.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" onClick={onRefresh}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={() => setIsFullscreen(!isFullscreen)}>
              {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                  <Settings2 className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setShowMid(!showMid)}>
                  <CheckCircle className={cn('h-4 w-4 mr-2', showMid ? 'opacity-100' : 'opacity-0')} />
                  Show Mid Price
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setShowCum(!showCum)}>
                  <CheckCircle className={cn('h-4 w-4 mr-2', showCum ? 'opacity-100' : 'opacity-0')} />
                  Show Cumulative
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => {}}>
                  Color Scheme
                  <Select defaultValue={colorScheme} onValueChange={(v) => {}}>
                    <SelectTrigger className="w-24 ml-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="blueRed">Blue/Red</SelectItem>
                      <SelectItem value="greenRed">Green/Red</SelectItem>
                      <SelectItem value="classic">Classic</SelectItem>
                    </SelectContent>
                  </Select>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardHeader>
      <CardContent ref={chartRef}>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="depth">Depth Chart</TabsTrigger>
            <TabsTrigger value="levels">Order Levels</TabsTrigger>
          </TabsList>

          <TabsContent value="depth" className="mt-0">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="bidGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={colors.bid} stopOpacity={0.8} />
                      <stop offset="95%" stopColor={colors.bid} stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="askGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={colors.ask} stopOpacity={0.8} />
                      <stop offset="95%" stopColor={colors.ask} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} />
                  <XAxis
                    dataKey="price"
                    tick={{ fontSize: 11, fontFamily: 'monospace' }}
                    tickFormatter={(v) => formatCurrency(v)}
                  />
                  <YAxis
                    tick={{ fontSize: 11, fontFamily: 'monospace' }}
                    tickFormatter={(v) => formatNumber(v)}
                    domain={[0, maxDepth * 1.1]}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--background)',
                      border: '2px solid var(--foreground)',
                      borderRadius: 0,
                      boxShadow: '4px 4px 0px 0px var(--foreground)',
                    }}
                    formatter={(value: number, name: string) => [
                      formatNumber(value),
                      name === 'bidDepth' || name === 'bidCumulative' ? 'Bid' : 'Ask'
                    ]}
                    labelFormatter={(label) => `Price: ${formatCurrency(label)}`}
                  />
                  {showMid && midPrice > 0 && (
                    <ReferenceLine
                      x={midPrice}
                      stroke="var(--muted-foreground)"
                      strokeDasharray="5 5"
                      label={{ value: 'Mid', position: 'top', fill: 'var(--muted-foreground)', fontSize: 10 }}
                    />
                  )}
                  <Area
                    type="monotone"
                    dataKey={showCum ? 'bidCumulative' : 'bidDepth'}
                    stroke={colors.bid}
                    fill="url(#bidGradient)"
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey={showCum ? 'askCumulative' : 'askDepth'}
                    stroke={colors.ask}
                    fill="url(#askGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </TabsContent>

          <TabsContent value="levels" className="mt-0">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-right">Price</TableHead>
                    <TableHead className="text-right text-green-500">Bid Size</TableHead>
                    <TableHead className="text-right text-red-500">Ask Size</TableHead>
                    <TableHead className="text-right">Price</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {depthLevels.slice(0, 20).map((level, i) => (
                    <TableRow key={i}>
                      <TableCell className="text-right font-mono text-green-500">
                        {formatCurrency(level.price)}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {formatNumber(level.bids)}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {formatNumber(level.asks)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-red-500">
                        {formatCurrency(level.price + level.spread)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>
        </Tabs>

        <div className="flex items-center justify-between mt-4 pt-4 border-t-2 border-foreground/10">
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-green-500" />
              <span className="text-muted-foreground">Bids</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-red-500" />
              <span className="text-muted-foreground">Asks</span>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleExportCSV}>
              <Download className="h-4 w-4 mr-2" />
              CSV
            </Button>
            <Button variant="outline" size="sm" onClick={handleExportPNG} disabled={isExporting}>
              <BarChart3 className="h-4 w-4 mr-2" />
              PNG
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Table } from '@/components/ui/table'

export default DepthChart
