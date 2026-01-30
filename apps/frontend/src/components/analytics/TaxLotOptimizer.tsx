'use client'

import { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn, formatCurrency, formatDate } from '@/lib/utils'
import { Calculator, Lightbulb, AlertTriangle, Info, TrendingUp, TrendingDown } from 'lucide-react'
import type { TaxLot } from './TaxLotTable'

interface TaxLotOptimizerProps {
  lots: TaxLot[]
  className?: string
}

type CostBasisMethod = 'fifo' | 'lifo' | 'hifo' | 'specific'

const TAX_RATES = {
  shortTerm: 0.37,
  longTerm: 0.20,
}

export function TaxLotOptimizer({ lots, className }: TaxLotOptimizerProps) {
  const [sharesToSell, setSharesToSell] = useState(10)
  const [targetMethod, setTargetMethod] = useState<CostBasisMethod>('hifo')

  const losingLots = useMemo(() => lots.filter(l => !l.washSale && (l.unrealizedGain ?? 0) < 0), [lots])

  const optimizedLots = useMemo(() => {
    const sorted = [...losingLots]
    switch (targetMethod) {
      case 'fifo': return sorted.sort((a, b) => new Date(a.purchaseDate).getTime() - new Date(b.purchaseDate).getTime())
      case 'lifo': return sorted.sort((a, b) => new Date(b.purchaseDate).getTime() - new Date(a.purchaseDate).getTime())
      case 'hifo': return sorted.sort((a, b) => (a.costPerShare ?? 0) - (b.costPerShare ?? 0))
      case 'specific': return sorted.sort((a, b) => (a.unrealizedGainPercent ?? 0) - (b.unrealizedGainPercent ?? 0))
      default: return sorted
    }
  }, [losingLots, targetMethod])

  const recommendation = useMemo(() => {
    let remaining = sharesToSell
    const selected: typeof lots = []
    let totalProceeds = 0
    let totalCostBasis = 0
    let realizedLoss = 0
    let shortTermCount = 0
    let longTermCount = 0

    for (const lot of optimizedLots) {
      if (remaining <= 0) break
      const shares = Math.min(lot.shares, remaining)
      selected.push({ ...lot, shares })
      totalProceeds += shares * (lot.currentPrice ?? 0)
      totalCostBasis += shares * (lot.costPerShare ?? 0)
      realizedLoss += shares * (lot.unrealizedGain ?? 0)
      if (lot.term === 'short') shortTermCount += shares
      else longTermCount += shares
      remaining -= shares
    }

    const avgTaxRate = shortTermCount > 0 ? TAX_RATES.shortTerm : longTermCount > 0 ? TAX_RATES.longTerm : TAX_RATES.shortTerm
    const taxSavings = Math.abs(realizedLoss) * avgTaxRate

    return { selected, totalProceeds, totalCostBasis, realizedLoss, taxSavings }
  }, [optimizedLots, sharesToSell])

  const taxImpact = useMemo(() => {
    const gains = lots.filter(l => (l.unrealizedGain ?? 0) > 0 && !l.washSale)
    const losses = lots.filter(l => (l.unrealizedGain ?? 0) < 0 && !l.washSale)
    const totalGains = gains.reduce((sum, l) => sum + (l.unrealizedGain ?? 0), 0)
    const totalLosses = Math.abs(losses.reduce((sum, l) => sum + (l.unrealizedGain ?? 0), 0))
    const netGain = totalGains - totalLosses
    return { totalGains, totalLosses, netGain }
  }, [lots])

  const currentPrice = lots[0]?.currentPrice || 0

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="h-5 w-5" />
          Tax Lot Optimizer
        </CardTitle>
        <CardDescription>Tax loss harvesting recommendations and optimization</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="optimize">
          <TabsList className="mb-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="optimize">Optimize</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span className="text-sm font-medium">Unrealized Gains</span>
                </div>
                <p className="text-2xl font-bold text-green-600">+{formatCurrency(taxImpact.totalGains)}</p>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingDown className="h-4 w-4 text-red-500" />
                  <span className="text-sm font-medium">Unrealized Losses</span>
                </div>
                <p className="text-2xl font-bold text-red-600">-{formatCurrency(taxImpact.totalLosses)}</p>
              </div>
              <div className="p-4 border rounded-lg bg-muted/50">
                <div className="flex items-center gap-2 mb-2">
                  <Calculator className="h-4 w-4" />
                  <span className="text-sm font-medium">Net Position</span>
                </div>
                <p className={cn('text-2xl font-bold', taxImpact.netGain >= 0 ? 'text-green-600' : 'text-red-600')}>
                  {taxImpact.netGain >= 0 ? '+' : ''}{formatCurrency(taxImpact.netGain)}
                </p>
              </div>
            </div>

            <div className="p-4 border rounded-lg bg-amber-50 dark:bg-amber-950/20">
              <div className="flex items-start gap-3">
                <Lightbulb className="h-5 w-5 text-amber-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-amber-800 dark:text-amber-200">Tax Loss Harvesting</h4>
                  <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                    You have {losingLots.length} lots with unrealized losses totaling {formatCurrency(taxImpact.totalLosses)}.
                    Consider selling to offset gains and reduce your tax liability.
                  </p>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="optimize" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Shares to Sell: {sharesToSell}</Label>
                  <Slider
                    value={[sharesToSell]}
                    min={1}
                    max={Math.min(100, losingLots.reduce((sum, l) => sum + l.shares, 0))}
                    step={1}
                    onValueChange={([v]) => setSharesToSell(v)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Cost Basis Method</Label>
                  <Select value={targetMethod} onValueChange={(v) => setTargetMethod(v as CostBasisMethod)}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fifo">FIFO - First In, First Out</SelectItem>
                      <SelectItem value="lifo">LIFO - Last In, First Out</SelectItem>
                      <SelectItem value="hifo">HIFO - Highest In, First Out (Best)</SelectItem>
                      <SelectItem value="specific">Specific Identification</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="p-4 border rounded-lg space-y-3">
                <h4 className="font-semibold">Optimization Result</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span className="text-muted-foreground">Sale Proceeds:</span>
                  <span className="font-medium">{formatCurrency(recommendation.totalProceeds)}</span>
                  <span className="text-muted-foreground">Cost Basis:</span>
                  <span className="font-medium">{formatCurrency(recommendation.totalCostBasis)}</span>
                  <span className="text-muted-foreground">Realized Loss:</span>
                  <span className="font-medium text-red-600">{formatCurrency(recommendation.realizedLoss)}</span>
                  <span className="text-muted-foreground">Est. Tax Savings:</span>
                  <span className="font-medium text-green-600">{formatCurrency(recommendation.taxSavings)}</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium flex items-center gap-2">
                <Info className="h-4 w-4" />
                Recommended Lots to Sell
              </h4>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Symbol</TableHead>
                      <TableHead>Purchase Date</TableHead>
                      <TableHead className="text-right">Shares</TableHead>
                      <TableHead className="text-right">Cost/Share</TableHead>
                      <TableHead className="text-right">Loss</TableHead>
                      <TableHead>Term</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {recommendation.selected.map((lot) => (
                      <TableRow key={lot.id} className="bg-green-50/50 dark:bg-green-950/20">
                        <TableCell className="font-medium">{lot.symbol}</TableCell>
                        <TableCell>{formatDate(lot.purchaseDate)}</TableCell>
                        <TableCell className="text-right">{lot.shares}</TableCell>
                        <TableCell className="text-right">{formatCurrency(lot.costPerShare ?? 0)}</TableCell>
                        <TableCell className="text-right text-red-600">{formatCurrency(lot.unrealizedGain ?? 0)}</TableCell>
                        <TableCell>
                          <Badge variant={lot.term === 'long' ? 'default' : 'secondary'}>
                            {lot.term}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>

            <div className="p-3 bg-muted rounded-lg text-xs text-muted-foreground">
              <p className="flex items-center gap-2">
                <AlertTriangle className="h-3 w-3" />
                Tax optimization suggestions are for informational purposes only. Consult a qualified tax professional for personalized advice.
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default TaxLotOptimizer
