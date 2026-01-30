'use client'

import { useState } from 'react'
import { CheckCircle, AlertTriangle, ArrowRight, Printer, Share2, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { cn, formatCurrency, formatDate, formatTime } from '@/lib/utils'

export type TradeConfirmationStatus = 'success' | 'pending' | 'error'

export interface TradeConfirmationData {
  tradeId: string
  symbol: string
  side: 'buy' | 'sell'
  quantity: number
  executionPrice: number
  orderType: 'market' | 'limit' | 'stop' | 'stop_limit'
  limitPrice?: number
  stopPrice?: number
  commission: number
  fees: number
  totalValue: number
  netValue: number
  timestamp: string
  exchange: string
  status: TradeConfirmationStatus
  message?: string
}

interface TradeConfirmationProps {
  trade: TradeConfirmationData
  onViewTrade?: () => void
  onViewPortfolio?: () => void
  onPrint?: () => void
  onShare?: () => void
  onNewTrade?: () => void
  className?: string
}

export function TradeConfirmation({
  trade,
  onViewTrade,
  onViewPortfolio,
  onPrint,
  onShare,
  onNewTrade,
  className
}: TradeConfirmationProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const statusConfig = {
    success: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100', label: 'Trade Executed' },
    pending: { icon: AlertTriangle, color: 'text-yellow-600', bg: 'bg-yellow-100', label: 'Order Pending' },
    error: { icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-100', label: 'Trade Failed' }
  }

  const status = statusConfig[trade.status]
  const StatusIcon = status.icon

  return (
    <Card className={cn('max-w-md mx-auto', className)}>
      <CardHeader className="text-center pb-2">
        <div className={cn('mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4', status.bg)}>
          <StatusIcon className={cn('h-8 w-8', status.color)} />
        </div>
        <Badge variant={trade.status === 'success' ? 'default' : trade.status === 'error' ? 'destructive' : 'secondary'}>
          {status.label}
        </Badge>
        <CardTitle className="text-xl mt-2">
          {trade.side === 'buy' ? 'Bought' : 'Sold'} {trade.quantity} {trade.symbol}
        </CardTitle>
        <CardDescription>Trade ID: #{trade.tradeId}</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="text-center">
          <p className="text-3xl font-bold">{formatCurrency(trade.executionPrice)}</p>
          <p className="text-sm text-muted-foreground">per share</p>
        </div>

        <Separator />

        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Order Type</span>
            <span className="font-medium">{trade.orderType.toUpperCase()}</span>
          </div>
          {trade.limitPrice && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Limit Price</span>
              <span className="font-medium">{formatCurrency(trade.limitPrice)}</span>
            </div>
          )}
          {trade.stopPrice && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Stop Price</span>
              <span className="font-medium">{formatCurrency(trade.stopPrice)}</span>
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-muted-foreground">Quantity</span>
            <span className="font-medium">{trade.quantity.toLocaleString()}</span>
          </div>
          <Separator />
          <div className="flex justify-between font-medium">
            <span>Gross Value</span>
            <span>{formatCurrency(trade.totalValue)}</span>
          </div>
          <div className="flex justify-between text-muted-foreground">
            <span>Commission</span>
            <span>{formatCurrency(trade.commission)}</span>
          </div>
          <div className="flex justify-between text-muted-foreground">
            <span>Fees</span>
            <span>{formatCurrency(trade.fees)}</span>
          </div>
          <Separator />
          <div className="flex justify-between font-semibold text-lg">
            <span>Net {trade.side === 'buy' ? 'Debit' : 'Credit'}</span>
            <span className={cn(trade.side === 'buy' ? 'text-red-600' : 'text-green-600')}>
              {formatCurrency(trade.netValue)}
            </span>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-muted text-xs text-muted-foreground space-y-1">
          <div className="flex justify-between">
            <span>Exchange</span>
            <span className="font-medium">{trade.exchange}</span>
          </div>
          <div className="flex justify-between">
            <span>Time</span>
            <span className="font-medium">{formatDate(trade.timestamp)} {formatTime(trade.timestamp)}</span>
          </div>
        </div>

        {trade.message && (
          <div className={cn('p-3 rounded-lg text-sm', trade.status === 'error' ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700')}>
            {trade.message}
          </div>
        )}

        <div className="flex gap-2">
          {onViewTrade && (
            <Button variant="outline" size="sm" onClick={onViewTrade} className="flex-1">
              <FileText className="h-4 w-4 mr-2" />
              View Trade
            </Button>
          )}
          {onViewPortfolio && (
            <Button variant="outline" size="sm" onClick={onViewPortfolio} className="flex-1">
              <ArrowRight className="h-4 w-4 mr-2" />
              Portfolio
            </Button>
          )}
        </div>

        <div className="flex gap-2">
          {onPrint && (
            <Button variant="ghost" size="sm" onClick={onPrint} className="flex-1">
              <Printer className="h-4 w-4 mr-2" />
              Print
            </Button>
          )}
          {onShare && (
            <Button variant="ghost" size="sm" onClick={onShare} className="flex-1">
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          )}
          {onNewTrade && (
            <Button size="sm" onClick={onNewTrade} className="flex-1">
              New Trade
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default TradeConfirmation
