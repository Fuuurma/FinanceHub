'use client'

import { useState, useMemo, useCallback } from 'react'
import { RefreshCw, CheckCircle, TrendingUp, TrendingDown, DollarSign, Target, PieChart } from 'lucide-react'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Slider } from '@/components/ui/slider'
import { Progress } from '@/components/ui/progress'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

export interface RebalanceHolding {
  symbol: string
  name: string
  currentQuantity: number
  currentPrice: number
  currentValue: number
  currentWeight: number
  targetWeight: number
  category?: string
}

export interface RebalanceTrade {
  symbol: string
  action: 'buy' | 'sell'
  quantity: number
  price: number
  totalValue: number
  currentWeight: number
  targetWeight: number
}

export interface RebalancingToolProps {
  holdings?: RebalanceHolding[]
  totalPortfolioValue?: number
  onExecuteTrades?: (trades: RebalanceTrade[]) => void
  className?: string
}

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toLocaleString()
}

export function RebalancingTool({
  holdings = [],
  totalPortfolioValue = 0,
  onExecuteTrades,
  className,
}: RebalancingToolProps) {
  const [targetWeights, setTargetWeights] = useState<Record<string, number>>(() => {
    const initial: Record<string, number> = {}
    holdings.forEach(h => {
      initial[h.symbol] = h.targetWeight > 0 ? h.targetWeight : h.currentWeight
    })
    return initial
  })

  const handleUpdateTarget = useCallback((symbol: string, weight: number) => {
    setTargetWeights(prev => ({ ...prev, [symbol]: weight }))
  }, [])

  const trades = useMemo<RebalanceTrade[]>(() => {
    if (totalPortfolioValue === 0) return []

    return holdings.map(holding => {
      const targetValue = totalPortfolioValue * (targetWeights[holding.symbol] / 100)
      const valueDiff = targetValue - holding.currentValue
      const action: 'buy' | 'sell' = valueDiff >= 0 ? 'buy' : 'sell'
      const absValue = Math.abs(valueDiff)
      const quantity = Math.floor(absValue / holding.currentPrice)

      return {
        symbol: holding.symbol,
        action,
        quantity,
        price: holding.currentPrice,
        totalValue: quantity * holding.currentPrice,
        currentWeight: holding.currentWeight,
        targetWeight: targetWeights[holding.symbol],
      } as RebalanceTrade
    }).filter(t => t.quantity > 0)
  }, [holdings, targetWeights, totalPortfolioValue])

  const totalBuy = trades.filter(t => t.action === 'buy').reduce((sum, t) => sum + t.totalValue, 0)
  const totalSell = trades.filter(t => t.action === 'sell').reduce((sum, t) => sum + t.totalValue, 0)
  const totalTargetWeight = Object.values(targetWeights).reduce((sum, w) => sum + w, 0)

  const handleExecute = useCallback(() => {
    onExecuteTrades?.(trades)
  }, [trades, onExecuteTrades])

  if (holdings.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <Target className="h-5 w-5" />
            Portfolio Rebalancing
          </CardTitle>
          <CardDescription>Set target allocations and rebalance your portfolio</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <PieChart className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
            <p className="text-muted-foreground">No holdings available for rebalancing</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <Target className="h-5 w-5" />
              Portfolio Rebalancing
            </CardTitle>
            <CardDescription>Set target allocations and rebalance your portfolio</CardDescription>
          </div>
          <div className={cn(
            'px-3 py-1 rounded-full text-sm font-bold',
            Math.abs(totalTargetWeight - 100) < 0.1 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          )}>
            Total: {totalTargetWeight.toFixed(1)}%
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="targets" className="space-y-4">
          <TabsList>
            <TabsTrigger value="targets">Set Targets</TabsTrigger>
            <TabsTrigger value="trades">Trade Preview</TabsTrigger>
            <TabsTrigger value="summary">Summary</TabsTrigger>
          </TabsList>

          <TabsContent value="targets" className="space-y-4">
            <div className="border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Asset</TableHead>
                    <TableHead className="text-right">Value</TableHead>
                    <TableHead className="text-right">Current</TableHead>
                    <TableHead className="w-32">Target</TableHead>
                    <TableHead className="text-right">Diff</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {holdings.map((holding) => {
                    const diff = targetWeights[holding.symbol] - holding.currentWeight
                    return (
                      <TableRow key={holding.symbol}>
                        <TableCell>
                          <p className="font-semibold">{holding.symbol}</p>
                          <p className="text-xs text-muted-foreground truncate max-w-[200px]">{holding.name}</p>
                        </TableCell>
                        <TableCell className="text-right font-medium">{formatCurrency(holding.currentValue)}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Progress value={holding.currentWeight * 100} className="h-2 w-16" />
                            <span className="text-sm w-14 text-right">{formatPercent(holding.currentWeight)}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Slider
                            value={[targetWeights[holding.symbol]]}
                            onValueChange={([v]) => handleUpdateTarget(holding.symbol, v)}
                            max={100}
                            step={0.5}
                          />
                          <span className="text-xs text-muted-foreground">{targetWeights[holding.symbol].toFixed(1)}%</span>
                        </TableCell>
                        <TableCell className="text-right">
                          <Badge variant={diff >= 0 ? 'default' : 'destructive'} className="gap-1">
                            {diff >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                            {diff >= 0 ? '+' : ''}{diff.toFixed(1)}%
                          </Badge>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="trades" className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span className="text-sm text-green-700 font-medium">Total Buy</span>
                </div>
                <p className="text-2xl font-bold text-green-700">{formatCurrency(totalBuy)}</p>
              </div>
              <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingDown className="h-4 w-4 text-red-600" />
                  <span className="text-sm text-red-700 font-medium">Total Sell</span>
                </div>
                <p className="text-2xl font-bold text-red-700">{formatCurrency(totalSell)}</p>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground font-medium">Net Flow</span>
                </div>
                <p className={cn('text-2xl font-bold', totalSell - totalBuy >= 0 ? 'text-green-600' : 'text-red-600')}>
                  {totalSell >= totalBuy ? '+' : ''}{formatCurrency(totalSell - totalBuy)}
                </p>
              </div>
            </div>

            <div className="border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead className="text-right">Quantity</TableHead>
                    <TableHead className="text-right">Value</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {trades.map((trade, index) => (
                    <TableRow key={`${trade.symbol}-${index}`}>
                      <TableCell className="font-semibold">{trade.symbol}</TableCell>
                      <TableCell>
                        <Badge variant={trade.action === 'buy' ? 'default' : 'destructive'}>
                          {trade.action.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">{formatNumber(trade.quantity)}</TableCell>
                      <TableCell className={cn('text-right font-semibold', trade.action === 'buy' ? 'text-green-600' : 'text-red-600')}>
                        {formatCurrency(trade.totalValue)}
                      </TableCell>
                    </TableRow>
                  ))}
                  {trades.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                        No trades needed - portfolio is balanced
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>

            {trades.length > 0 && (
              <div className="flex justify-end">
                <Button size="lg" onClick={handleExecute}>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Execute {trades.length} Trade{trades.length !== 1 ? 's' : ''}
                </Button>
              </div>
            )}
          </TabsContent>

          <TabsContent value="summary" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-6 border rounded-lg text-center">
                <PieChart className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground mb-1">Portfolio Value</p>
                <p className="text-3xl font-bold">{formatCurrency(totalPortfolioValue)}</p>
              </div>
              <div className="p-6 border rounded-lg text-center">
                <RefreshCw className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground mb-1">Turnover</p>
                <p className="text-3xl font-bold">{totalPortfolioValue > 0 ? ((totalBuy + totalSell) / 2 / totalPortfolioValue * 100).toFixed(1) : 0}%</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <TrendingDown className="h-4 w-4 text-red-600" />
                  Overweight (Sell)
                </h4>
                <div className="space-y-2">
                  {holdings.filter(h => targetWeights[h.symbol] < h.currentWeight).map(h => (
                    <div key={h.symbol} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                      <div>
                        <p className="font-semibold">{h.symbol}</p>
                        <p className="text-xs text-muted-foreground">Sell to reduce</p>
                      </div>
                      <Badge variant="destructive">-{(h.currentWeight - targetWeights[h.symbol]).toFixed(1)}%</Badge>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  Underweight (Buy)
                </h4>
                <div className="space-y-2">
                  {holdings.filter(h => targetWeights[h.symbol] > h.currentWeight).map(h => (
                    <div key={h.symbol} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div>
                        <p className="font-semibold">{h.symbol}</p>
                        <p className="text-xs text-muted-foreground">Buy to increase</p>
                      </div>
                      <Badge variant="default">+{(targetWeights[h.symbol] - h.currentWeight).toFixed(1)}%</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default RebalancingTool
