'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { RefreshCw, TrendingUp, TrendingDown, DollarSign, Wallet, AlertTriangle } from 'lucide-react'
import { apiClient } from '@/lib/api/client'
import { OrderConfirmationDialog } from './OrderConfirmationDialog'

interface PaperTradeFormProps {
  onSuccess?: () => void
  className?: string
}

interface TradeResult {
  success: boolean
  error?: string
  trade_id?: string
  asset?: string
  quantity?: number
  price?: number
  total_value?: number
  profit_loss?: number
  remaining_cash?: number
}

type OrderSide = 'BUY' | 'SELL'
type OrderType = 'MARKET' | 'LIMIT' | 'STOP'

export function PaperTradeForm({ onSuccess, className }: PaperTradeFormProps) {
  const [asset, setAsset] = React.useState('')
  const [quantity, setQuantity] = React.useState('')
  const [tradeType, setTradeType] = React.useState<OrderSide>('BUY')
  const [orderType, setOrderType] = React.useState<OrderType>('MARKET')
  const [price, setPrice] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  const [result, setResult] = React.useState<TradeResult | null>(null)
  const [cashBalance, setCashBalance] = React.useState(100000)
  const [confirmationOpen, setConfirmationOpen] = React.useState(false)
  const [validationError, setValidationError] = React.useState<string | null>(null)

  const estimatedValue = React.useMemo(() => {
    const qty = parseFloat(quantity) || 0
    const prc = parseFloat(price) || 0
    return orderType === 'MARKET' ? 0 : qty * prc
  }, [quantity, price, orderType])

  const handleSubmit = async () => {
    const qty = parseFloat(quantity)
    const prc = parseFloat(price)

    if (!asset || !quantity) {
      setValidationError('Please enter symbol and quantity')
      return
    }

    if (qty <= 0) {
      setValidationError('Quantity must be greater than 0')
      return
    }

    if (orderType !== 'MARKET' && (!price || prc <= 0)) {
      setValidationError(`Please enter a valid ${orderType.toLowerCase()} price`)
      return
    }

    setValidationError(null)
    setConfirmationOpen(true)
  }

  const executeOrder = async () => {
    setLoading(true)
    setResult(null)
    setConfirmationOpen(false)

    const qty = parseFloat(quantity)
    const prc = parseFloat(price)

    const endpoint = tradeType === 'BUY'
      ? '/paper-trading/buy'
      : '/paper-trading/sell'

    try {
      const data = await apiClient.post<TradeResult>(endpoint, {
        asset,
        quantity: qty,
        ...(orderType !== 'MARKET' && { price: prc }),
      })
      setResult(data)

      if (data.success && data.remaining_cash) {
        setCashBalance(data.remaining_cash)
      }

      if (data.success && onSuccess) {
        onSuccess()
      }
    } catch {
      setResult({ success: false, error: 'Network error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className={cn('rounded-none border-2 border-foreground', className)}>
      <CardHeader className="border-b-2 border-foreground">
        <div className="flex items-center justify-between">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            {tradeType === 'BUY' ? (
              <TrendingUp className="h-5 w-5 text-green-600" />
            ) : (
              <TrendingDown className="h-5 w-5 text-red-600" />
            )}
            {tradeType} ORDER
          </CardTitle>
          <Badge variant="outline" className="font-mono text-xs">
            <Wallet className="h-3 w-3 mr-1" />
            ${cashBalance.toLocaleString()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div className="flex gap-2 mb-6">
          <Button
            type="button"
            variant={tradeType === 'BUY' ? 'default' : 'outline'}
            onClick={() => setTradeType('BUY')}
            className={cn(
              'flex-1 font-black uppercase rounded-none',
              tradeType === 'BUY' ? 'bg-green-600 hover:bg-green-700' : 'border-2'
            )}
          >
            <TrendingUp className="h-4 w-4 mr-2" />
            BUY
          </Button>
          <Button
            type="button"
            variant={tradeType === 'SELL' ? 'default' : 'outline'}
            onClick={() => setTradeType('SELL')}
            className={cn(
              'flex-1 font-black uppercase rounded-none',
              tradeType === 'SELL' ? 'bg-red-600 hover:bg-red-700' : 'border-2'
            )}
          >
            <TrendingDown className="h-4 w-4 mr-2" />
            SELL
          </Button>
        </div>

        <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="space-y-4">
          <div className="grid grid-cols-2 gap-2 mb-4">
            <Button
              type="button"
              variant={tradeType === 'BUY' ? 'default' : 'outline'}
              onClick={() => setTradeType('BUY')}
              className={cn(
                'flex-1 font-black uppercase rounded-none',
                tradeType === 'BUY' ? 'bg-green-600 hover:bg-green-700' : 'border-2'
              )}
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              BUY
            </Button>
            <Button
              type="button"
              variant={tradeType === 'SELL' ? 'default' : 'outline'}
              onClick={() => setTradeType('SELL')}
              className={cn(
                'flex-1 font-black uppercase rounded-none',
                tradeType === 'SELL' ? 'bg-red-600 hover:bg-red-700' : 'border-2'
              )}
            >
              <TrendingDown className="h-4 w-4 mr-2" />
              SELL
            </Button>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase mb-2">
              Order Type
            </label>
            <Select
              value={orderType}
              onValueChange={(v) => setOrderType(v as OrderType)}
            >
              <SelectTrigger className="rounded-none border-2 font-mono">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="MARKET">Market</SelectItem>
                <SelectItem value="LIMIT">Limit</SelectItem>
                <SelectItem value="STOP">Stop</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase mb-2">
              Asset Symbol
            </label>
            <Input
              type="text"
              value={asset}
              onChange={(e) => setAsset(e.target.value.toUpperCase())}
              placeholder="AAPL"
              className="rounded-none border-2 font-mono uppercase"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase mb-2">
              Quantity
            </label>
            <Input
              type="number"
              step="0.0001"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder="10"
              className="rounded-none border-2 font-mono"
              required
            />
          </div>

          {(orderType === 'LIMIT' || orderType === 'STOP') && (
            <div>
              <label className="block text-xs font-bold uppercase mb-2">
                {orderType === 'LIMIT' ? 'Limit Price' : 'Stop Price'}
              </label>
              <Input
                type="number"
                step="0.01"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="150.00"
                className="rounded-none border-2 font-mono"
                required
              />
            </div>
          )}

          {validationError && (
            <div className="bg-red-50 border border-red-500 p-3">
              <p className="text-red-700 font-mono text-xs">{validationError}</p>
            </div>
          )}

          <Button
            type="submit"
            disabled={loading}
            className={cn(
              'w-full font-black uppercase rounded-none',
              tradeType === 'BUY'
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-red-600 hover:bg-red-700'
            )}
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                EXECUTING...
              </>
            ) : (
              <>
                <DollarSign className="h-4 w-4 mr-2" />
                Review Order
              </>
            )}
          </Button>
        </form>

        {result && (
          <div className={cn(
            'mt-4 p-4 border-2',
            result.success ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
          )}>
            {result.success ? (
              <div className="space-y-1 text-sm">
                <p className="font-bold text-green-700 uppercase">
                  Order Executed Successfully
                </p>
                <p className="font-mono text-xs">
                  {result.asset} {result.quantity} @ ${result.price?.toFixed(2)}
                </p>
                <p className="font-mono text-xs">
                  Total: ${result.total_value?.toLocaleString()}
                </p>
                {result.profit_loss !== undefined && (
                  <p className={cn(
                    'font-mono text-xs font-bold',
                    result.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    P&L: ${result.profit_loss.toFixed(2)}
                  </p>
                )}
              </div>
            ) : (
              <p className="text-red-700 font-bold text-sm uppercase">
                {result.error}
              </p>
            )}
          </div>
        )}
      </CardContent>

      <OrderConfirmationDialog
        open={confirmationOpen}
        onOpenChange={setConfirmationOpen}
        order={asset && quantity ? {
          symbol: asset,
          side: tradeType,
          type: orderType,
          quantity: parseFloat(quantity),
          ...(orderType !== 'MARKET' && price && { price: parseFloat(price) }),
        } : null}
        onConfirm={executeOrder}
        isExecuting={loading}
        result={result}
        onResultClose={() => setResult(null)}
      />
    </Card>
  )
}
