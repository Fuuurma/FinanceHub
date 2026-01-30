'use client'

import { useState, useMemo } from 'react'
import { TrendingUp, TrendingDown, Activity, PieChart, BarChart3, Settings } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

export type OrderSide = 'buy' | 'sell'
export type OrderType = 'market' | 'limit' | 'stop' | 'stop_limit'

export interface TradingPanelProps {
  symbol: string
  currentPrice: number
  bid?: number
  ask?: number
  dayHigh?: number
  dayLow?: number
  volume?: number
  onSubmitOrder?: (order: { side: OrderSide; type: OrderType; quantity: number; price?: number; stopPrice?: number }) => void
  className?: string
}

export function TradingPanel({
  symbol,
  currentPrice,
  bid,
  ask,
  dayHigh,
  dayLow,
  volume,
  onSubmitOrder,
  className
}: TradingPanelProps) {
  const [side, setSide] = useState<OrderSide>('buy')
  const [orderType, setOrderType] = useState<OrderType>('limit')
  const [quantity, setQuantity] = useState(1)
  const [price, setPrice] = useState(currentPrice)
  const [stopPrice, setStopPrice] = useState(currentPrice * 0.95)

  const estimatedValue = useMemo(() => quantity * (orderType === 'market' ? currentPrice : price), [quantity, orderType, currentPrice, price])

  const spread = useMemo(() => {
    if (bid && ask) return ask - bid
    return null
  }, [bid, ask])

  const dayChange = useMemo(() => {
    if (dayHigh && dayLow) return currentPrice - dayLow
    return null
  }, [currentPrice, dayHigh, dayLow])

  const handleSubmit = () => {
    onSubmitOrder?.({
      side,
      type: orderType,
      quantity,
      price: orderType === 'market' ? undefined : price,
      stopPrice: (orderType === 'stop' || orderType === 'stop_limit') ? stopPrice : undefined
    })
  }

  const presetQuantities = [1, 10, 25, 50, 100]

  return (
    <Card className={cn('', className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">{symbol}</CardTitle>
            <CardDescription>Trading Panel</CardDescription>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">{formatCurrency(currentPrice)}</p>
            {bid && ask && (
              <p className="text-xs text-muted-foreground">
                Bid: {formatCurrency(bid)} | Ask: {formatCurrency(ask)}
              </p>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={side} onValueChange={(v) => setSide(v as OrderSide)} className="space-y-4">
          <TabsList className="grid grid-cols-2">
            <TabsTrigger value="buy" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">
              <TrendingUp className="h-4 w-4 mr-2" />
              Buy
            </TabsTrigger>
            <TabsTrigger value="sell" className="data-[state=active]:bg-red-600 data-[state=active]:text-white">
              <TrendingDown className="h-4 w-4 mr-2" />
              Sell
            </TabsTrigger>
          </TabsList>

          <TabsContent value={side} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Order Type</Label>
                <Select value={orderType} onValueChange={(v) => setOrderType(v as OrderType)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="market">Market</SelectItem>
                    <SelectItem value="limit">Limit</SelectItem>
                    <SelectItem value="stop">Stop</SelectItem>
                    <SelectItem value="stop_limit">Stop Limit</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Quantity</Label>
                <div className="flex gap-2">
                  <Input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                    min={1}
                    className="flex-1"
                  />
                </div>
                <div className="flex gap-1">
                  {presetQuantities.map((q) => (
                    <Button
                      key={q}
                      variant="outline"
                      size="sm"
                      className="text-xs flex-1"
                      onClick={() => setQuantity(q)}
                    >
                      {q}
                    </Button>
                  ))}
                </div>
              </div>
            </div>

            {(orderType === 'limit' || orderType === 'stop_limit') && (
              <div className="space-y-2">
                <Label>Limit Price</Label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={price}
                    onChange={(e) => setPrice(parseFloat(e.target.value) || 0)}
                    step={0.01}
                    min={0}
                  />
                  <Button variant="outline" size="sm" onClick={() => setPrice(currentPrice)}>
                    Current
                  </Button>
                </div>
              </div>
            )}

            {(orderType === 'stop' || orderType === 'stop_limit') && (
              <div className="space-y-2">
                <Label>Stop Price</Label>
                <Input
                  type="number"
                  value={stopPrice}
                  onChange={(e) => setStopPrice(parseFloat(e.target.value) || 0)}
                  step={0.01}
                  min={0}
                />
              </div>
            )}

            <div className="p-4 rounded-lg bg-muted space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Estimated {side === 'buy' ? 'Cost' : 'Credit'}</span>
                <span className="font-semibold">{formatCurrency(estimatedValue)}</span>
              </div>
              {spread && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Spread</span>
                  <span>{formatCurrency(spread)}</span>
                </div>
              )}
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Commission</span>
                <span>$0.00</span>
              </div>
            </div>

            <Button
              className={cn('w-full', side === 'buy' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700')}
              size="lg"
              onClick={handleSubmit}
            >
              {side === 'buy' ? 'Buy' : 'Sell'} {quantity} {symbol}
            </Button>
          </TabsContent>
        </Tabs>

        <div className="mt-4 pt-4 border-t space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Day Range</span>
            <span>{dayLow ? formatCurrency(dayLow) : '-'} - {dayHigh ? formatCurrency(dayHigh) : '-'}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Volume</span>
            <span>{volume ? volume.toLocaleString() : '-'}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default TradingPanel
