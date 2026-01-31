'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  History, TrendingUp, TrendingDown, RefreshCw, Filter,
  ArrowUpDown, Calendar, DollarSign
} from 'lucide-react'

interface PaperTradeHistoryProps {
  onRefresh?: () => void
  className?: string
}

interface Trade {
  id: string
  asset: string
  type: string
  quantity: number
  price: number
  total_value: number
  executed_at: string
  profit_loss: number | null
}

export function PaperTradeHistory({ onRefresh, className }: PaperTradeHistoryProps) {
  const [loading, setLoading] = React.useState(true)
  const [trades, setTrades] = React.useState<Trade[]>([])
  const [filter, setFilter] = React.useState<string>('all')
  const [limit, setLimit] = React.useState<string>('50')

  const fetchTrades = React.useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/paper-trading/history?limit=${limit}`)
      const data = await response.json()
      setTrades(data.trades || [])
    } catch (error) {
      console.error('Failed to fetch trades:', error)
    } finally {
      setLoading(false)
    }
  }, [limit])

  React.useEffect(() => {
    fetchTrades()
  }, [fetchTrades])

  const filteredTrades = React.useMemo(() => {
    if (filter === 'all') return trades
    return trades.filter(trade => trade.type === filter)
  }, [trades, filter])

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleString()

  if (loading) {
    return (
      <Card className={cn('rounded-none border-2 border-foreground', className)}>
        <CardHeader className="border-b-2 border-foreground">
          <Skeleton className="h-8 w-48" />
        </CardHeader>
        <CardContent className="p-6">
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('rounded-none border-2 border-foreground', className)}>
      <CardHeader className="border-b-2 border-foreground">
        <div className="flex items-center justify-between">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            <History className="h-5 w-5" />
            Trade History
          </CardTitle>
          <div className="flex items-center gap-2">
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-24 rounded-none border-2 font-bold uppercase">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="BUY">Buy</SelectItem>
                <SelectItem value="SELL">Sell</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchTrades}
              className="rounded-none border-2 font-bold uppercase"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {filteredTrades.length === 0 ? (
          <div className="p-8 text-center">
            <History className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-black uppercase text-lg mb-2">No Trades Yet</h3>
            <p className="text-muted-foreground font-mono text-xs">
              Your paper trades will appear here
            </p>
          </div>
        ) : (
          <div className="border-2 border-foreground m-4">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 border-b-2 border-foreground">
                <tr>
                  <th className="text-left p-3 font-black uppercase">Date</th>
                  <th className="text-left p-3 font-black uppercase">Asset</th>
                  <th className="text-center p-3 font-black uppercase">Type</th>
                  <th className="text-right p-3 font-black uppercase">Qty</th>
                  <th className="text-right p-3 font-black uppercase">Price</th>
                  <th className="text-right p-3 font-black uppercase">Total</th>
                  <th className="text-right p-3 font-black uppercase">P&L</th>
                </tr>
              </thead>
              <tbody>
                {filteredTrades.map((trade, index) => (
                  <tr
                    key={trade.id}
                    className={cn(
                      'border-b border-border last:border-0',
                      index % 2 === 0 ? 'bg-muted/20' : ''
                    )}
                  >
                    <td className="p-3">
                      <span className="font-mono text-xs">
                        {formatDate(trade.executed_at)}
                      </span>
                    </td>
                    <td className="p-3">
                      <span className="font-black uppercase">{trade.asset}</span>
                    </td>
                    <td className="p-3 text-center">
                      <Badge
                        className={cn(
                          'rounded-none font-black uppercase',
                          trade.type === 'BUY'
                            ? 'bg-green-600'
                            : 'bg-red-600'
                        )}
                      >
                        {trade.type === 'BUY' ? (
                          <TrendingUp className="h-3 w-3 mr-1" />
                        ) : (
                          <TrendingDown className="h-3 w-3 mr-1" />
                        )}
                        {trade.type}
                      </Badge>
                    </td>
                    <td className="p-3 text-right font-mono">
                      {trade.quantity.toFixed(4)}
                    </td>
                    <td className="p-3 text-right font-mono">
                      {formatCurrency(trade.price)}
                    </td>
                    <td className="p-3 text-right font-mono">
                      {formatCurrency(trade.total_value)}
                    </td>
                    <td className="p-3 text-right">
                      {trade.profit_loss !== null && trade.profit_loss !== undefined ? (
                        <span
                          className={cn(
                            'font-mono font-bold',
                            trade.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'
                          )}
                        >
                          {trade.profit_loss >= 0 ? '+' : ''}
                          {formatCurrency(trade.profit_loss)}
                        </span>
                      ) : (
                        <span className="text-muted-foreground font-mono text-xs">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="p-4 border-t-2 border-foreground flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase text-muted-foreground">
              Show
            </span>
            <Select value={limit} onValueChange={setLimit}>
              <SelectTrigger className="w-20 rounded-none border-2 font-mono">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="25">25</SelectItem>
                <SelectItem value="50">50</SelectItem>
                <SelectItem value="100">100</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <p className="text-xs font-mono text-muted-foreground">
            Showing {filteredTrades.length} trades
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
