'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Wallet, TrendingUp, TrendingDown, RefreshCw, Trophy, Target,
  DollarSign, PieChart, BarChart3, Wifi, WifiOff, XCircle
} from 'lucide-react'
import { usePaperTrading } from './usePaperTrading'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

interface PaperPortfolioSummaryProps {
  onRefresh?: () => void
  className?: string
}

export function PaperPortfolioSummary({ onRefresh, className }: PaperPortfolioSummaryProps) {
  const { portfolio, isLoading, isConnected, refreshPortfolio, closePosition } = usePaperTrading()
  const [closeDialogOpen, setCloseDialogOpen] = React.useState(false)
  const [positionToClose, setPositionToClose] = React.useState<{ symbol: string; quantity: number; marketValue: number } | null>(null)
  const [closing, setClosing] = React.useState(false)

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)

  const formatPercent = (value: number) =>
    `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`

  const handleClosePosition = async () => {
    if (!positionToClose) return
    setClosing(true)
    try {
      await closePosition(positionToClose.symbol)
      setCloseDialogOpen(false)
      setPositionToClose(null)
    } finally {
      setClosing(false)
    }
  }

  const openCloseDialog = (pos: { symbol: string; name?: string; quantity: number; market_value: number }) => {
    setPositionToClose({
      symbol: pos.symbol,
      quantity: pos.quantity,
      marketValue: pos.market_value,
    })
    setCloseDialogOpen(true)
  }

  if (isLoading) {
    return (
      <Card className={cn('rounded-none border-2 border-foreground', className)}>
        <CardHeader className="border-b-2 border-foreground">
          <Skeleton className="h-8 w-48" />
        </CardHeader>
        <CardContent className="p-6 space-y-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-48 w-full" />
        </CardContent>
      </Card>
    )
  }

  if (!portfolio) {
    return (
      <Card className={cn('rounded-none border-2 border-foreground', className)}>
        <CardContent className="p-12 text-center">
          <Wallet className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="font-black uppercase text-lg mb-2">No Portfolio Data</h3>
          <p className="text-muted-foreground font-mono text-xs mb-4">
            Your paper trading portfolio will appear here
          </p>
          {onRefresh && (
            <Button
              onClick={onRefresh}
              variant="outline"
              className="rounded-none border-2 font-bold uppercase"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Load Portfolio
            </Button>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('rounded-none border-2 border-foreground', className)}>
      <CardHeader className="border-b-2 border-foreground">
        <div className="flex items-center justify-between">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            <PieChart className="h-5 w-5" />
            Portfolio Summary
            <span className="ml-2" title={isConnected ? "Connected" : "Disconnected"}>
              {isConnected ? (
                <Wifi className="h-4 w-4 text-green-500" />
              ) : (
                <WifiOff className="h-4 w-4 text-red-500" />
              )}
            </span>
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={refreshPortfolio}
            className="rounded-none border-2 font-bold uppercase"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="rounded-none border-2 bg-transparent p-0 h-auto">
            <TabsTrigger
              value="overview"
              className="rounded-none border-2 border-b-0 data-[state=active]:bg-foreground data-[state=active]:text-background px-4 py-2 font-black uppercase"
            >
              Overview
            </TabsTrigger>
            <TabsTrigger
              value="positions"
              className="rounded-none border-2 border-b-0 data-[state=active]:bg-foreground data-[state=active]:text-background px-4 py-2 font-black uppercase"
            >
              Positions
            </TabsTrigger>
            <TabsTrigger
              value="performance"
              className="rounded-none border-2 border-b-0 data-[state=active]:bg-foreground data-[state=active]:text-background px-4 py-2 font-black uppercase"
            >
              Performance
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="border-2 border-foreground p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Wallet className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs font-bold uppercase text-muted-foreground">Cash</span>
                </div>
                <p className="font-mono text-xl font-black">{formatCurrency(portfolio.cash_balance)}</p>
              </div>
              <div className="border-2 border-foreground p-4">
                <div className="flex items-center gap-2 mb-2">
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs font-bold uppercase text-muted-foreground">Portfolio</span>
                </div>
                <p className="font-mono text-xl font-black">{formatCurrency(portfolio.portfolio_value)}</p>
              </div>
              <div className="border-2 border-foreground p-4">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs font-bold uppercase text-muted-foreground">Total Value</span>
                </div>
                <p className="font-mono text-xl font-black">{formatCurrency(portfolio.total_value)}</p>
              </div>
              <div className={cn(
                'border-2 border-foreground p-4',
                portfolio.total_return >= 0 ? 'bg-green-50' : 'bg-red-50'
              )}>
                <div className="flex items-center gap-2 mb-2">
                  {portfolio.total_return >= 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-600" />
                  )}
                  <span className="text-xs font-bold uppercase text-muted-foreground">Return</span>
                </div>
                <p className={cn(
                  'font-mono text-xl font-black',
                  portfolio.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                )}>
                  {formatPercent(portfolio.total_return)}
                </p>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="positions">
            {portfolio.positions.length === 0 ? (
              <div className="border-2 border-foreground p-8 text-center">
                <p className="font-mono text-sm text-muted-foreground">No positions yet</p>
              </div>
            ) : (
              <div className="border-2 border-foreground">
                <table className="w-full text-sm">
                  <thead className="border-b-2 border-foreground bg-muted/50">
                    <tr>
                      <th className="text-left p-3 font-black uppercase">Symbol</th>
                      <th className="text-right p-3 font-black uppercase">Qty</th>
                      <th className="text-right p-3 font-black uppercase">Avg Price</th>
                      <th className="text-right p-3 font-black uppercase">Current</th>
                      <th className="text-right p-3 font-black uppercase">Value</th>
                      <th className="text-right p-3 font-black uppercase">P/L</th>
                      <th className="text-center p-3 font-black uppercase">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {portfolio.positions.map((pos) => (
                      <tr key={pos.symbol} className="border-b border-border last:border-0">
                        <td className="p-3">
                          <div>
                            <p className="font-black uppercase">{pos.symbol}</p>
                            <p className="text-xs text-muted-foreground">{pos.name}</p>
                          </div>
                        </td>
                        <td className="p-3 text-right font-mono">{pos.quantity.toFixed(4)}</td>
                        <td className="p-3 text-right font-mono">{formatCurrency(pos.avg_price)}</td>
                        <td className="p-3 text-right font-mono">{formatCurrency(pos.current_price)}</td>
                        <td className="p-3 text-right font-mono">{formatCurrency(pos.market_value)}</td>
                        <td className={cn(
                          'p-3 text-right font-mono font-bold',
                          pos.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'
                        )}>
                          {formatCurrency(pos.profit_loss)}
                          <span className="block text-xs">
                            {formatPercent(pos.profit_loss_pct)}
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openCloseDialog(pos)}
                            className="rounded-none border-2 font-bold uppercase text-xs hover:bg-red-50 hover:border-red-500 hover:text-red-600"
                          >
                            <XCircle className="h-3 w-3 mr-1" />
                            Close
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </TabsContent>

          <TabsContent value="performance">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="border-2 border-foreground p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs font-bold uppercase text-muted-foreground">Day Change</span>
                </div>
                <p className={cn(
                  'font-mono text-2xl font-black',
                  (portfolio.day_change || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                )}>
                  {formatPercent(portfolio.day_change || 0)}
                </p>
              </div>
              <div className="border-2 border-foreground p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs font-bold uppercase text-muted-foreground">Positions</span>
                </div>
                <p className="font-mono text-2xl font-black">{portfolio.positions?.length || 0}</p>
              </div>
              <div className="border-2 border-foreground p-4">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs font-bold uppercase text-muted-foreground">Cash Balance</span>
                </div>
                <p className="font-mono text-2xl font-black">{formatCurrency(portfolio.cash_balance)}</p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>

      <Dialog open={closeDialogOpen} onOpenChange={setCloseDialogOpen}>
        <DialogContent className="rounded-none border-2 border-foreground max-w-md">
          <DialogHeader>
            <DialogTitle className="font-black uppercase flex items-center gap-2">
              <XCircle className="h-5 w-5 text-red-600" />
              Close Position
            </DialogTitle>
            <DialogDescription className="font-mono text-xs">
              This will sell all shares of this position at market price.
            </DialogDescription>
          </DialogHeader>

          {positionToClose && (
            <div className="space-y-4">
              <div className="border-2 border-foreground p-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground font-mono text-sm">Symbol</span>
                  <span className="font-black uppercase">{positionToClose.symbol}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground font-mono text-sm">Quantity</span>
                  <span className="font-mono">{positionToClose.quantity.toFixed(4)}</span>
                </div>
                <div className="flex justify-between border-t border-border pt-2">
                  <span className="text-muted-foreground font-mono text-sm font-bold">Market Value</span>
                  <span className="font-mono font-bold">{formatCurrency(positionToClose.marketValue)}</span>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-500 p-3">
                <p className="text-yellow-700 font-mono text-xs">
                  This action cannot be undone. The position will be sold at the current market price.
                </p>
              </div>
            </div>
          )}

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => setCloseDialogOpen(false)}
              className="rounded-none border-2 font-black uppercase"
              disabled={closing}
            >
              Cancel
            </Button>
            <Button
              onClick={handleClosePosition}
              className="rounded-none border-2 font-black uppercase bg-red-600 hover:bg-red-700 border-red-600"
              disabled={closing}
            >
              {closing ? (
                <>
                  <span className="animate-spin mr-2">⟳</span>
                  Closing...
                </>
              ) : (
                'Close Position'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
