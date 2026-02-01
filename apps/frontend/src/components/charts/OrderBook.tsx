'use client'

import { useState, useMemo } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  ArrowUp,
  ArrowDown,
  Activity,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  DollarSign,
} from 'lucide-react'
import { cn, formatNumber, formatCurrency } from '@/lib/utils'

export interface OrderBookLevelData {
  price: number
  quantity: number
  total: number
}

export interface OrderBookMetrics {
  spread: number
  spread_pct: number
  total_bid_volume: number
  total_ask_volume: number
  top_5_bid_volume: number
  top_5_ask_volume: number
  vwap_bid: number | null
  vwap_ask: number | null
  order_imbalance: number | null
  timestamp: string
}

export interface OrderBookData {
  bids: OrderBookLevelData[]
  asks: OrderBookLevelData[]
  metrics: OrderBookMetrics
}

interface OrderBookProps {
  data?: OrderBookData
  symbol?: string
  depth?: number
  className?: string
  onRefresh?: () => void
}

export function OrderBook({
  data,
  symbol = '',
  depth = 15,
  className,
  onRefresh,
}: OrderBookProps) {
  const [activeTab, setActiveTab] = useState('book')
  const [showPercent, setShowPercent] = useState(true)

  const maxTotal = useMemo(() => {
    if (!data) return 1
    const maxBid = Math.max(...data.bids.map(b => b.total), 0)
    const maxAsk = Math.max(...data.asks.map(a => a.total), 0)
    return Math.max(maxBid, maxAsk)
  }, [data])

  const spread = data?.metrics.spread
  const spreadPct = data?.metrics.spread_pct
  const imbalance = data?.metrics.order_imbalance

  const getDepthBarWidth = (total: number) => {
    if (maxTotal === 0) return '0%'
    return `${(total / maxTotal) * 100}%`
  }

  const getImbalanceColor = (value: number | null) => {
    if (value === null) return 'bg-gray-500'
    if (value > 0.3) return 'bg-green-500'
    if (value > 0.1) return 'bg-green-400'
    if (value > -0.1) return 'bg-yellow-500'
    if (value > -0.3) return 'bg-orange-400'
    return 'bg-red-500'
  }

  const getImbalanceLabel = (value: number | null) => {
    if (value === null) return 'N/A'
    if (value > 0.3) return 'Strong Buy'
    if (value > 0.1) return 'Buy'
    if (value > -0.1) return 'Neutral'
    if (value > -0.3) return 'Sell'
    return 'Strong Sell'
  }

  if (!data) {
    return (
      <Card className={cn('border-2 border-foreground', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Order Book
            {symbol && <Badge variant="secondary">{symbol}</Badge>}
          </CardTitle>
          <CardDescription>Loading order book data...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <div className="animate-pulse flex flex-col items-center">
              <Activity className="h-8 w-8 text-muted-foreground mb-2" />
              <span className="text-sm text-muted-foreground">Waiting for market data</span>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('border-2 border-foreground', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Order Book
              {symbol && <Badge variant="secondary">{symbol}</Badge>}
            </CardTitle>
            <CardDescription className="flex items-center gap-3 mt-1">
                <span className="flex items-center gap-1">
                  Spread: <span className="font-mono font-medium">{spread ? formatCurrency(spread) : '-'}</span>
                  <span className="text-muted-foreground">({spreadPct?.toFixed(3)}%)</span>
                </span>
                <span className="flex items-center gap-1">
                  <DollarSign className="h-3 w-3" />
                  Imbalance:
                  <span className={cn('font-mono font-medium px-1 rounded', imbalance !== null && imbalance !== undefined ? getImbalanceColor(imbalance) : '')}>
                    {imbalance !== null && imbalance !== undefined ? imbalance.toFixed(3) : 'N/A'}
                  </span>
                  <span className="text-muted-foreground">({imbalance !== null && imbalance !== undefined ? getImbalanceLabel(imbalance) : 'N/A'})</span>
                </span>
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" onClick={onRefresh}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="book">Order Book</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="book" className="mt-0">
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-right">Price</TableHead>
                      <TableHead className="text-right">Size</TableHead>
                      {showPercent && <TableHead className="text-right">Total</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.asks.slice(0, depth).reverse().map((level, i) => (
                      <TableRow key={i}>
                        <TableCell className="text-right font-mono text-red-500">
                          {formatCurrency(level.price)}
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          <div className="flex items-center justify-end gap-2">
                            <span>{formatNumber(level.quantity)}</span>
                            <div
                              className="h-1 bg-red-500/30"
                              style={{ width: getDepthBarWidth(level.total) }}
                            />
                          </div>
                        </TableCell>
                        {showPercent && (
                          <TableCell className="text-right font-mono text-muted-foreground">
                            {formatCurrency(level.total)}
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      {showPercent && <TableHead className="text-left">Total</TableHead>}
                      <TableHead className="text-left">Size</TableHead>
                      <TableHead className="text-left text-green-500">Price</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.bids.slice(0, depth).map((level, i) => (
                      <TableRow key={i}>
                        {showPercent && (
                          <TableCell className="text-left font-mono text-muted-foreground">
                            <div className="flex items-center gap-2">
                              <div
                                className="h-1 bg-green-500/30"
                                style={{ width: getDepthBarWidth(level.total) }}
                              />
                              <span>{formatCurrency(level.total)}</span>
                            </div>
                          </TableCell>
                        )}
                        <TableCell className="text-left font-mono">
                          {formatNumber(level.quantity)}
                        </TableCell>
                        <TableCell className="text-left font-mono text-green-500">
                          {formatCurrency(level.price)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>

            <div className="flex items-center justify-between mt-4 pt-4 border-t-2 border-foreground/10">
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-red-500" />
                  <span className="text-muted-foreground">Asks (Sellers)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-green-500" />
                  <span className="text-muted-foreground">Bids (Buyers)</span>
                </div>
              </div>
              <div className="text-sm text-muted-foreground">
                Last update: {data.metrics.timestamp ? new Date(data.metrics.timestamp).toLocaleTimeString() : 'N/A'}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="mt-0">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-lg border bg-card">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  Total Bid Vol
                </div>
                <div className="text-2xl font-mono font-bold">
                  {formatNumber(data.metrics.total_bid_volume)}
                </div>
              </div>

              <div className="p-4 rounded-lg border bg-card">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                  <TrendingDown className="h-4 w-4 text-red-500" />
                  Total Ask Vol
                </div>
                <div className="text-2xl font-mono font-bold">
                  {formatNumber(data.metrics.total_ask_volume)}
                </div>
              </div>

              <div className="p-4 rounded-lg border bg-card">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                  <ArrowUp className="h-4 w-4 text-blue-500" />
                  VWAP Bid
                </div>
                <div className="text-2xl font-mono font-bold">
                  {data.metrics.vwap_bid ? formatCurrency(data.metrics.vwap_bid) : 'N/A'}
                </div>
              </div>

              <div className="p-4 rounded-lg border bg-card">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                  <ArrowDown className="h-4 w-4 text-blue-500" />
                  VWAP Ask
                </div>
                <div className="text-2xl font-mono font-bold">
                  {data.metrics.vwap_ask ? formatCurrency(data.metrics.vwap_ask) : 'N/A'}
                </div>
              </div>

              <div className="p-4 rounded-lg border bg-card">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                  Top 5 Bid Vol
                </div>
                <div className="text-2xl font-mono font-bold text-green-500">
                  {formatNumber(data.metrics.top_5_bid_volume)}
                </div>
              </div>

              <div className="p-4 rounded-lg border bg-card">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                  Top 5 Ask Vol
                </div>
                <div className="text-2xl font-mono font-bold text-red-500">
                  {formatNumber(data.metrics.top_5_ask_volume)}
                </div>
              </div>

              <div className="p-4 rounded-lg border bg-card col-span-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                  Order Imbalance
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex-1 h-4 rounded-full bg-gray-200 overflow-hidden">
                    <div
                      className={cn('h-full transition-all', imbalance !== null && imbalance !== undefined ? getImbalanceColor(imbalance) : '')}
                      style={{
                        width: `${((imbalance ?? 0) + 1) * 50}%`,
                      }}
                    />
                  </div>
                  <div className="text-lg font-mono font-bold">
                    {imbalance !== null && imbalance !== undefined ? imbalance.toFixed(3) : 'N/A'}
                  </div>
                  <Badge variant="secondary">
                    {imbalance !== null && imbalance !== undefined ? getImbalanceLabel(imbalance) : 'N/A'}
                  </Badge>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default OrderBook
