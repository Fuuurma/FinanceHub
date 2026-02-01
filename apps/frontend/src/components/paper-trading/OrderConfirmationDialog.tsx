'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, XCircle, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react'

interface OrderConfirmationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  order: {
    symbol: string
    side: 'BUY' | 'SELL'
    type: 'MARKET' | 'LIMIT' | 'STOP'
    quantity: number
    price?: number
  } | null
  onConfirm: () => void
  isExecuting: boolean
  result: {
    success: boolean
    error?: string
    asset?: string
    quantity?: number
    price?: number
    total_value?: number
    remaining_cash?: number
  } | null
  onResultClose: () => void
}

export function OrderConfirmationDialog({
  open,
  onOpenChange,
  order,
  onConfirm,
  isExecuting,
  result,
  onResultClose,
}: OrderConfirmationDialogProps) {
  const handleConfirm = () => {
    onConfirm()
    onOpenChange(false)
  }

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value)

  if (!order) return null

  if (result) {
    return (
      <Dialog open={open} onOpenChange={onResultClose}>
        <DialogContent className="rounded-none border-2 border-foreground max-w-md">
          <DialogHeader>
            <div className="flex items-center gap-3 mb-4">
              {result.success ? (
                <CheckCircle className="h-8 w-8 text-green-600" />
              ) : (
                <XCircle className="h-8 w-8 text-red-600" />
              )}
              <DialogTitle
                className={cn(
                  'font-black uppercase text-xl',
                  result.success ? 'text-green-600' : 'text-red-600'
                )}
              >
                {result.success ? 'Order Executed' : 'Order Failed'}
              </DialogTitle>
            </div>
          </DialogHeader>

          {result.success ? (
            <div className="space-y-4">
              <div className="border-2 border-foreground p-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground font-mono text-sm">Symbol</span>
                  <span className="font-black uppercase">{result.asset}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground font-mono text-sm">Quantity</span>
                  <span className="font-mono">{result.quantity?.toFixed(4)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground font-mono text-sm">Price</span>
                  <span className="font-mono">{formatCurrency(result.price || 0)}</span>
                </div>
                <div className="flex justify-between border-t border-border pt-2">
                  <span className="text-muted-foreground font-mono text-sm font-bold">
                    Total Value
                  </span>
                  <span className="font-mono font-bold">
                    {formatCurrency(result.total_value || 0)}
                  </span>
                </div>
              </div>

              {result.remaining_cash !== undefined && (
                <div className="flex justify-between border-2 border-foreground p-3 bg-muted/30">
                  <span className="font-bold uppercase text-sm">Remaining Cash</span>
                  <span className="font-mono font-bold">
                    {formatCurrency(result.remaining_cash)}
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-start gap-3 border-2 border-red-500 bg-red-50 p-4">
                <AlertTriangle className="h-6 w-6 text-red-600 shrink-0" />
                <div>
                  <p className="font-bold text-red-700 uppercase text-sm">Order Failed</p>
                  <p className="text-red-600 font-mono text-sm">{result.error}</p>
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              onClick={onResultClose}
              className="rounded-none border-2 font-black uppercase"
            >
              {result.success ? 'Done' : 'Try Again'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="rounded-none border-2 border-foreground max-w-md">
        <DialogHeader>
          <DialogTitle className="font-black uppercase flex items-center gap-2">
            {order.side === 'BUY' ? (
              <TrendingUp className="h-5 w-5 text-green-600" />
            ) : (
              <TrendingDown className="h-5 w-5 text-red-600" />
            )}
            Confirm Order
          </DialogTitle>
          <DialogDescription className="font-mono text-xs">
            Please review your order before executing
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Badge
              className={cn(
                'rounded-none font-black uppercase text-sm px-3 py-1',
                order.side === 'BUY' ? 'bg-green-600' : 'bg-red-600'
              )}
            >
              {order.side} {order.symbol}
            </Badge>
          </div>

          <div className="border-2 border-foreground p-4 space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-bold uppercase text-muted-foreground">Type</p>
                <p className="font-mono">{order.type}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase text-muted-foreground">Quantity</p>
                <p className="font-mono">{order.quantity.toFixed(4)}</p>
              </div>
            </div>

            {order.price && (
              <div>
                <p className="text-xs font-bold uppercase text-muted-foreground">
                  {order.type === 'STOP' ? 'Stop Price' : 'Limit Price'}
                </p>
                <p className="font-mono">{formatCurrency(order.price)}</p>
              </div>
            )}

            <div className="border-t border-border pt-3">
              <p className="text-xs font-bold uppercase text-muted-foreground">
                Estimated {order.side === 'BUY' ? 'Cost' : 'Credit'}
              </p>
              <p className="font-mono text-2xl font-black">
                {formatCurrency(order.quantity * (order.price || 0))}
              </p>
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-500 p-3">
            <p className="text-yellow-700 font-mono text-xs">
              This is a paper trading simulation. No real money will be used.
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="rounded-none border-2 font-black uppercase"
            disabled={isExecuting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            className={cn(
              'rounded-none border-2 font-black uppercase',
              order.side === 'BUY'
                ? 'bg-green-600 hover:bg-green-700 border-green-600'
                : 'bg-red-600 hover:bg-red-700 border-red-600'
            )}
            disabled={isExecuting}
          >
            {isExecuting ? (
              <>
                <span className="animate-spin mr-2">⟳</span>
                Executing...
              </>
            ) : (
              `Execute ${order.side} Order`
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
