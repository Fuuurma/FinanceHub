'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useTradingStore } from '@/stores/tradingStore'
import type { OrderCreateInput } from '@/lib/types'
import { TrendingUp, TrendingDown, DollarSign, Calculator } from 'lucide-react'

interface OrderEntryFormProps {
  onSubmit?: (order: OrderCreateInput) => void
  defaultSymbol?: string
}

export function OrderEntryForm({ onSubmit, defaultSymbol = '' }: OrderEntryFormProps) {
  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [orderType, setOrderType] = useState<'market' | 'limit' | 'stop' | 'stop_limit'>('market')
  const [symbol, setSymbol] = useState(defaultSymbol)
  const [quantity, setQuantity] = useState('1')
  const [price, setPrice] = useState('')
  const [stopPrice, setStopPrice] = useState('')
  const [timeInForce, setTimeInForce] = useState<'day' | 'gtc' | 'ioc' | 'fok'>('day')
  const [notes, setNotes] = useState('')
  const [showConfirmation, setShowConfirmation] = useState(false)

  const { accountSummary, loading } = useTradingStore()

  useEffect(() => {
    if (defaultSymbol) setSymbol(defaultSymbol)
  }, [defaultSymbol])

  const calculateEstimatedCost = () => {
    const qty = parseFloat(quantity) || 0
    const priceValue = parseFloat(price) || 0
    const stopPriceValue = parseFloat(stopPrice) || 0

    let cost = 0
    if (orderType === 'market') {
      cost = 0 // Market orders don't have a known price until execution
    } else if (orderType === 'limit') {
      cost = qty * priceValue
    } else if (orderType === 'stop') {
      cost = qty * stopPriceValue
    } else if (orderType === 'stop_limit') {
      cost = qty * priceValue
    }

    return cost
  }

  const estimatedCost = calculateEstimatedCost()
  const fees = estimatedCost * 0.001
  const totalCost = estimatedCost + fees

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const orderData: OrderCreateInput = {
      portfolio_id: '', // Will be set by parent
      asset_id: '', // Will be set by parent after symbol lookup
      order_type: orderType,
      side,
      quantity: parseFloat(quantity),
      price: orderType !== 'market' ? parseFloat(price) : undefined,
      stop_price: (orderType === 'stop' || orderType === 'stop_limit') ? parseFloat(stopPrice) : undefined,
      time_in_force: timeInForce,
      notes: notes || undefined,
    }

    if (onSubmit) {
      onSubmit(orderData)
    }
    setShowConfirmation(false)
  }

  return (
    <Card className="border-2 border-foreground">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="h-5 w-5" />
          Order Entry
        </CardTitle>
        <CardDescription>Place new buy or sell orders</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex gap-2">
            <Button
              type="button"
              variant={side === 'buy' ? 'default' : 'outline'}
              className={`flex-1 ${side === 'buy' ? 'bg-green-600 hover:bg-green-700' : ''}`}
              onClick={() => setSide('buy')}
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              BUY
            </Button>
            <Button
              type="button"
              variant={side === 'sell' ? 'default' : 'outline'}
              className={`flex-1 ${side === 'sell' ? 'bg-red-600 hover:bg-red-700' : ''}`}
              onClick={() => setSide('sell')}
            >
              <TrendingDown className="h-4 w-4 mr-2" />
              SELL
            </Button>
          </div>

          <div className="space-y-2">
            <Label htmlFor="symbol">Symbol</Label>
            <Input
              id="symbol"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="AAPL"
              className="font-mono uppercase"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="orderType">Order Type</Label>
            <Select value={orderType} onValueChange={(v: any) => setOrderType(v)}>
              <SelectTrigger id="orderType">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="market">Market Order</SelectItem>
                <SelectItem value="limit">Limit Order</SelectItem>
                <SelectItem value="stop">Stop Order</SelectItem>
                <SelectItem value="stop_limit">Stop-Limit Order</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="quantity">Quantity</Label>
            <div className="flex gap-2">
              <Input
                id="quantity"
                type="number"
                step="0.0001"
                min="0"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="0.00"
                className="flex-1"
                required
              />
              <div className="flex gap-1">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setQuantity('100')}
                >
                  25%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setQuantity('250')}
                >
                  50%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setQuantity('500')}
                >
                  75%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setQuantity('1000')}
                >
                  100%
                </Button>
              </div>
            </div>
          </div>

          {orderType === 'limit' || orderType === 'stop_limit' ? (
            <div className="space-y-2">
              <Label htmlFor="price">Limit Price</Label>
              <Input
                id="price"
                type="number"
                step="0.01"
                min="0"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="0.00"
                className="font-mono"
                required
              />
            </div>
          ) : null}

          {orderType === 'stop' || orderType === 'stop_limit' ? (
            <div className="space-y-2">
              <Label htmlFor="stopPrice">Stop Price</Label>
              <Input
                id="stopPrice"
                type="number"
                step="0.01"
                min="0"
                value={stopPrice}
                onChange={(e) => setStopPrice(e.target.value)}
                placeholder="0.00"
                className="font-mono"
                required
              />
            </div>
          ) : null}

          <div className="space-y-2">
            <Label htmlFor="timeInForce">Time in Force</Label>
            <Select value={timeInForce} onValueChange={(v: any) => setTimeInForce(v)}>
              <SelectTrigger id="timeInForce">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="day">Day Order</SelectItem>
                <SelectItem value="gtc">Good Till Cancelled</SelectItem>
                <SelectItem value="ioc">Immediate or Cancel</SelectItem>
                <SelectItem value="fok">Fill or Kill</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Input
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Order notes..."
            />
          </div>

          <Card className="bg-muted/30">
            <CardContent className="pt-6 space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Estimated Cost</span>
                <span className="font-mono font-semibold">
                  ${estimatedCost.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Est. Fees (0.1%)</span>
                <span className="font-mono">
                  ${fees.toFixed(2)}
                </span>
              </div>
              <div className="border-t pt-2 flex justify-between">
                <span className="font-semibold">Total</span>
                <span className="font-mono font-bold text-lg">
                  ${totalCost.toFixed(2)}
                </span>
              </div>
            </CardContent>
          </Card>

          {orderType === 'market' && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
              <p className="text-xs text-yellow-600 dark:text-yellow-500">
                <strong>Market Order:</strong> Will execute at the best available price.
                Slippage may occur during periods of high volatility.
              </p>
            </div>
          )}

          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={() => {
                setQuantity('1')
                setPrice('')
                setStopPrice('')
                setNotes('')
              }}
            >
              Reset
            </Button>
            <Button
              type="button"
              className={side === 'buy' ? 'flex-2 bg-green-600 hover:bg-green-700' : 'flex-2 bg-red-600 hover:bg-red-700'}
              onClick={() => setShowConfirmation(true)}
              disabled={loading.orders}
            >
              <DollarSign className="h-4 w-4 mr-2" />
              Review Order
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
