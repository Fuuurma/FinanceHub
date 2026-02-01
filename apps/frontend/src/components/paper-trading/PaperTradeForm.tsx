'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { RefreshCw, TrendingUp, TrendingDown, DollarSign, Wallet } from 'lucide-react'
import { apiClient } from '@/lib/api/client'

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

export function PaperTradeForm({ onSuccess, className }: PaperTradeFormProps) {
  const [asset, setAsset] = React.useState('')
  const [quantity, setQuantity] = React.useState('')
  const [tradeType, setTradeType] = React.useState<'BUY' | 'SELL'>('BUY')
  const [loading, setLoading] = React.useState(false)
  const [result, setResult] = React.useState<TradeResult | null>(null)
  const [cashBalance, setCashBalance] = React.useState(100000)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)

    const endpoint = tradeType === 'BUY'
      ? '/paper-trading/buy'
      : '/paper-trading/sell'

    try {
      const data = await apiClient.post<TradeResult>(endpoint, { asset, quantity: parseFloat(quantity) })
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

        <form onSubmit={handleSubmit} className="space-y-4">
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
                {tradeType} {asset || 'ASSET'}
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
    </Card>
  )
}
