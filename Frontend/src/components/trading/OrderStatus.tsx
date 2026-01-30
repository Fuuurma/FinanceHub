'use client'

import { useMemo } from 'react'
import { CheckCircle, XCircle, Clock, RotateCcw, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { cn, formatCurrency, formatDate, formatTime } from '@/lib/utils'

export type OrderStatusType = 'pending' | 'open' | 'filled' | 'partial' | 'cancelled' | 'rejected' | 'expired'

export interface OrderStatusData {
  orderId: string
  symbol: string
  side: 'buy' | 'sell'
  orderType: 'market' | 'limit' | 'stop' | 'stop_limit'
  quantity: number
  filledQuantity: number
  price: number | null
  stopPrice: number | null
  status: OrderStatusType
  statusMessage: string
  createdAt: string
  updatedAt: string
  expiresAt?: string
  commission: number
  fees: number
}

interface OrderStatusProps {
  order: OrderStatusData
  onCancel?: () => void
  onModify?: () => void
  onViewDetails?: () => void
  className?: string
}

const statusConfig: Record<OrderStatusType, { label: string; color: string; icon: typeof CheckCircle }> = {
  pending: { label: 'Pending', color: 'text-yellow-600 bg-yellow-100', icon: Clock },
  open: { label: 'Open', color: 'text-blue-600 bg-blue-100', icon: Clock },
  filled: { label: 'Filled', color: 'text-green-600 bg-green-100', icon: CheckCircle },
  partial: { label: 'Partial', color: 'text-orange-600 bg-orange-100', icon: RotateCcw },
  cancelled: { label: 'Cancelled', color: 'text-gray-600 bg-gray-100', icon: XCircle },
  rejected: { label: 'Rejected', color: 'text-red-600 bg-red-100', icon: XCircle },
  expired: { label: 'Expired', color: 'text-gray-600 bg-gray-100', icon: Clock }
}

export function OrderStatus({
  order,
  onCancel,
  onModify,
  onViewDetails,
  className
}: OrderStatusProps) {
  const status = statusConfig[order.status]
  const StatusIcon = status.icon
  const fillProgress = order.quantity > 0 ? (order.filledQuantity / order.quantity) * 100 : 0
  const isCancellable = order.status === 'pending' || order.status === 'open'

  const formatPrice = (price: number | null) => {
    if (price === null) return 'Market'
    return formatCurrency(price)
  }

  return (
    <Card className={cn('', className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn('p-2 rounded-full', status.color.replace('text-', 'bg-').replace('600', '200').replace('100', '100'))}>
              <StatusIcon className={cn('h-5 w-5', status.color)} />
            </div>
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                {order.symbol}
                <Badge variant="outline" className="text-xs">
                  {order.side.toUpperCase()}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {order.orderType.toUpperCase()}
                </Badge>
              </CardTitle>
              <p className="text-sm text-muted-foreground">Order #{order.orderId}</p>
            </div>
          </div>
          <Badge className={cn(status.color)}>
            {status.label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Quantity</p>
            <p className="font-medium">{order.quantity.toLocaleString()}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Filled</p>
            <p className="font-medium">{order.filledQuantity.toLocaleString()}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Price</p>
            <p className="font-medium">{formatPrice(order.price)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">{order.stopPrice ? 'Stop' : 'Limit'}</p>
            <p className="font-medium">{order.stopPrice ? formatCurrency(order.stopPrice) : formatPrice(order.price)}</p>
          </div>
        </div>

        {order.status !== 'filled' && order.status !== 'cancelled' && order.status !== 'rejected' && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Fill Progress</span>
              <span className="font-medium">{fillProgress.toFixed(1)}%</span>
            </div>
            <Progress value={fillProgress} className="h-2" />
          </div>
        )}

        <div className="p-3 rounded-lg bg-muted/50 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Commission</span>
            <span>{formatCurrency(order.commission)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Fees</span>
            <span>{formatCurrency(order.fees)}</span>
          </div>
          <div className="flex justify-between text-sm font-medium pt-2 border-t">
            <span>Total Cost</span>
            <span>{formatCurrency(order.filledQuantity * (order.price || 0) + order.commission + order.fees)}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
          <div>
            <span>Created: </span>
            <span className="font-medium">{formatDate(order.createdAt)} {formatTime(order.createdAt)}</span>
          </div>
          <div>
            <span>Updated: </span>
            <span className="font-medium">{formatDate(order.updatedAt)} {formatTime(order.updatedAt)}</span>
          </div>
        </div>

        {order.statusMessage && (
          <p className="text-sm p-2 rounded bg-muted">{order.statusMessage}</p>
        )}

        <div className="flex gap-2 pt-2">
          {isCancellable && onCancel && (
            <Button variant="outline" size="sm" onClick={onCancel} className="flex-1">
              <XCircle className="h-4 w-4 mr-2" />
              Cancel Order
            </Button>
          )}
          {isCancellable && onModify && (
            <Button variant="outline" size="sm" onClick={onModify} className="flex-1">
              <RotateCcw className="h-4 w-4 mr-2" />
              Modify
            </Button>
          )}
          {onViewDetails && (
            <Button variant="outline" size="sm" onClick={onViewDetails} className="flex-1">
              <ExternalLink className="h-4 w-4 mr-2" />
              Details
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default OrderStatus
