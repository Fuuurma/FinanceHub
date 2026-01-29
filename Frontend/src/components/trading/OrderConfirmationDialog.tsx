'use client'

import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import type { OrderCreateInput } from '@/lib/types'
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

interface OrderConfirmationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  orderData: OrderCreateInput | null
  estimatedCost: number
  fees: number
  totalValue: number
  onConfirm: () => void
  loading?: boolean
}

export function OrderConfirmationDialog({
  open,
  onOpenChange,
  orderData,
  estimatedCost,
  fees,
  totalValue,
  onConfirm,
  loading = false,
}: OrderConfirmationDialogProps) {
  if (!orderData) return null

  const isMarketOrder = orderData.order_type === 'market'
  const orderTypeLabels = {
    market: 'Market Order',
    limit: 'Limit Order',
    stop: 'Stop Order',
    stop_limit: 'Stop-Limit Order',
  }
  const sideColor = orderData.side === 'buy' ? 'text-green-600' : 'text-red-600'

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="border-2 border-foreground">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            Confirm Order
          </DialogTitle>
          <DialogDescription>
            Please review your order details before submitting
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-3">
              <div>
                <p className="text-sm text-muted-foreground">Order Type</p>
                <p className="font-semibold">{orderTypeLabels[orderData.order_type]}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Side</p>
                <Badge className={sideColor}>
                  {orderData.side.toUpperCase()}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Quantity</p>
                <p className="font-semibold font-mono">
                  {orderData.quantity}
                </p>
              </div>
              {orderData.time_in_force && (
                <div>
                  <p className="text-sm text-muted-foreground">Time in Force</p>
                  <p className="font-semibold">
                    {orderData.time_in_force.toUpperCase()}
                  </p>
                </div>
              )}
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-sm text-muted-foreground">Limit Price</p>
                <p className="font-semibold font-mono">
                  ${orderData.price?.toFixed(2) || 'Market'}
                </p>
              </div>
              {orderData.stop_price && (
                <div>
                  <p className="text-sm text-muted-foreground">Stop Price</p>
                  <p className="font-semibold font-mono">
                    ${orderData.stop_price.toFixed(2)}
                  </p>
                </div>
              )}
              <div>
                <p className="text-sm text-muted-foreground">Order Notes</p>
                <p className="font-semibold text-sm">
                  {orderData.notes || 'None'}
                </p>
              </div>
              {isMarketOrder && (
                <div>
                  <p className="text-sm text-muted-foreground">Estimated Fill Price</p>
                  <p className="font-semibold font-mono">
                    ${estimatedCost.toFixed(2)}
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-muted/30 border border-foreground/20 rounded-lg p-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Estimated Cost</span>
                <span className="font-mono font-semibold">
                  ${estimatedCost.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Estimated Fees (0.1%)</span>
                <span className="font-mono">
                  ${fees.toFixed(2)}
                </span>
              </div>
              <div className="border-t border-foreground/20 pt-2 flex justify-between">
                <span className="font-bold">Total</span>
                <span className="font-mono font-bold text-lg">
                  ${totalValue.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {isMarketOrder && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <strong>Market Order Risk:</strong> Your order will execute at the best available price in the market. Slippage may occur during periods of high volatility or low liquidity.
              </AlertDescription>
            </Alert>
          )}

          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Paper Trading Disclaimer:</strong> This is a simulated trading environment. No real money is at risk. All orders are executed using paper trading rules for demonstration purposes.
            </AlertDescription>
          </Alert>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              onConfirm()
              onOpenChange(false)
            }}
            disabled={loading}
            className={orderData.side === 'buy' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}
          >
            {loading ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Submitting...
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                {orderData.side === 'buy' ? 'Buy' : 'Sell'} {orderData.quantity} @{' '}
                {orderData.price ? `$${orderData.price.toFixed(2)}` : 'MARKET'}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
