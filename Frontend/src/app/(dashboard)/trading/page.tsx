'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useTradingStore } from '@/stores/tradingStore'
import { OrderEntryForm } from '@/components/trading/OrderEntryForm'
import { PositionTracker } from '@/components/trading/PositionTracker'
import { AccountSummary } from '@/components/trading/AccountSummary'
import { OrderConfirmationDialog } from '@/components/trading/OrderConfirmationDialog'
import { ConnectionStatus } from '@/components/realtime/ConnectionStatus'
import { OrderBook } from '@/components/realtime/OrderBook'
import { TradeFeed } from '@/components/realtime/TradeFeed'
import { RealTimeChart } from '@/components/realtime/RealTimeChart'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  LayoutGrid,
  BarChart3,
  RefreshCw,
  ArrowLeft,
  Settings,
} from 'lucide-react'
import type { OrderCreateInput, Order } from '@/lib/types'
import { assetsApi } from '@/lib/api'

export default function TradingPage() {
  const router = useRouter()
  const { orders, loading, createOrder, fetchOrders, clearError, error } = useTradingStore()
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL')
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [pendingOrder, setPendingOrder] = useState<OrderCreateInput | null>(null)
  const [estimatedCost, setEstimatedCost] = useState(0)

  useEffect(() => {
    fetchOrders()
    return () => clearError()
  }, [fetchOrders, clearError])

  const handleOrderSubmit = async (orderData: OrderCreateInput) => {
    try {
      const asset = await assetsApi.get(orderData.asset_id)
      const cost = orderData.quantity * (asset.last_price || 0)
      setEstimatedCost(cost)
      setPendingOrder({ ...orderData, portfolio_id: 'default-portfolio' })
      setShowConfirmation(true)
    } catch (err) {
      console.error('Failed to fetch asset:', err)
    }
  }

  const handleConfirmOrder = async () => {
    if (!pendingOrder) return

    try {
      await createOrder(pendingOrder)
      setShowConfirmation(false)
      setPendingOrder(null)
      await fetchOrders()
    } catch (err) {
      console.error('Failed to create order:', err)
    }
  }

  const activeOrders = orders.filter(o => o.is_active).slice(0, 10)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold">Trading</h1>
            <ConnectionStatus />
          </div>
          <p className="text-muted-foreground mt-2">
            Execute trades and manage positions
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => router.push('/dashboard')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Trading Settings
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <AccountSummary />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1 space-y-6">
          <OrderEntryForm
            onSubmit={handleOrderSubmit}
            defaultSymbol={selectedSymbol}
          />

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LayoutGrid className="h-5 w-5" />
                Recent Orders
                <Badge variant="secondary">{activeOrders.length} active</Badge>
              </CardTitle>
              <CardDescription>Latest order activity</CardDescription>
            </CardHeader>
            <CardContent>
              {loading.orders ? (
                <div className="py-4 text-center text-muted-foreground">
                  <RefreshCw className="h-6 w-6 mx-auto animate-spin" />
                </div>
              ) : activeOrders.length === 0 ? (
                <div className="py-8 text-center text-muted-foreground">
                  No active orders
                </div>
              ) : (
                <div className="space-y-3">
                  {activeOrders.map((order) => (
                    <div key={order.id} className="border rounded-lg p-3 hover:bg-muted/50 transition-colors">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <p className="font-semibold">{order.asset_symbol}</p>
                          <p className="text-sm text-muted-foreground">
                            {order.order_type.toUpperCase()} • {order.side.toUpperCase()}
                          </p>
                        </div>
                        <Badge variant={order.status === 'pending' ? 'default' : 'secondary'}>
                          {order.status.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <p className="text-muted-foreground">Quantity</p>
                          <p className="font-mono font-semibold">
                            {order.quantity}
                          </p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Price</p>
                          <p className="font-mono font-semibold">
                            ${order.price || 'MKT'}
                          </p>
                        </div>
                      </div>
                      <div className="mt-2 text-sm text-muted-foreground">
                        {order.filled_quantity > 0 && (
                          <p>
                            Filled: {order.filled_quantity} / {order.quantity}
                          </p>
                        )}
                        <p className="text-xs">
                          {new Date(order.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <Tabs defaultValue="positions" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="positions">Positions</TabsTrigger>
              <TabsTrigger value="chart">Chart</TabsTrigger>
              <TabsTrigger value="orderbook">Order Book</TabsTrigger>
            </TabsList>

            <TabsContent value="positions" className="space-y-4">
              <PositionTracker />
            </TabsContent>

            <TabsContent value="chart" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="h-5 w-5" />
                        {selectedSymbol} Chart
                      </CardTitle>
                      <CardDescription>
                        Real-time price and volume
                      </CardDescription>
                    </div>
                    <Button variant="outline" size="sm">
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Refresh
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <RealTimeChart symbol={selectedSymbol} />
                </CardContent>
              </Card>

              <div className="grid gap-4 md:grid-cols-2">
                <TradeFeed symbol={selectedSymbol} limit={10} />
                <OrderBook symbol={selectedSymbol} depth={10} />
              </div>
            </TabsContent>

            <TabsContent value="orderbook" className="space-y-4">
              <OrderBook symbol={selectedSymbol} depth={20} />
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Trades</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <TradeFeed symbol={selectedSymbol} limit={20} />
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Order Statistics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Volume (24h)</p>
                        <p className="text-2xl font-bold">45.2M</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Trades (24h)</p>
                        <p className="text-2xl font-bold">284,392</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Avg Trade Size</p>
                        <p className="text-2xl font-bold">159</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Spread</p>
                        <p className="text-2xl font-bold text-green-600">$0.01</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      <OrderConfirmationDialog
        open={showConfirmation}
        onOpenChange={setShowConfirmation}
        orderData={pendingOrder}
        estimatedCost={estimatedCost}
        fees={estimatedCost * 0.001}
        totalValue={estimatedCost * 1.001}
        onConfirm={handleConfirmOrder}
        loading={loading.orders}
      />
    </div>
  )
}
