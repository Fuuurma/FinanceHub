'use client'

import { useState, useMemo } from 'react'
import { TrendingUp, TrendingDown, DollarSign, User, Download, Filter, ChevronDown, ChevronUp } from 'lucide-react'
import { cn, formatCurrency } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

export type InsiderTransactionType = 'buy' | 'sell' | 'all'

export interface InsiderTransaction {
  id: string
  insiderName: string
  insiderTitle: string
  symbol: string
  transactionType: 'buy' | 'sell'
  transactionDate: string
  filingDate: string
  sharesOwnedBefore: number
  sharesOwnedAfter: number
  sharesTransacted: number
  pricePerShare: number
  totalValue: number
  secFormType: string
  isIndirect: boolean
  relatedTo10b51: boolean
}

export interface InsiderTradingSummary {
  totalBuys: number
  totalSells: number
  totalBuyValue: number
  totalSellValue: number
  netBuying: number
  insiderBuyCount: number
  insiderSellCount: number
}

export interface InsiderTradingPanelProps {
  transactions?: InsiderTransaction[]
  summary?: InsiderTradingSummary
  symbol?: string
  loading?: boolean
  className?: string
}

type TimePeriod = '1w' | '1m' | '3m' | '6m' | '1y' | 'all'

const PERIOD_OPTIONS = [
  { value: '1w', label: '1 Week' },
  { value: '1m', label: '1 Month' },
  { value: '3m', label: '3 Months' },
  { value: '6m', label: '6 Months' },
  { value: '1y', label: '1 Year' },
  { value: 'all', label: 'All Time' },
]

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toLocaleString()
}

function formatValue(value: number): string {
  if (Math.abs(value) >= 1000000) return `$${(value / 1000000).toFixed(2)}M`
  if (Math.abs(value) >= 1000) return `$${(value / 1000).toFixed(1)}K`
  return formatCurrency(value)
}

function InsiderTransactionRow({ transaction }: { transaction: InsiderTransaction }) {
  const isBuy = transaction.transactionType === 'buy'
  return (
    <TableRow className="hover:bg-muted/50">
      <TableCell className="py-3">
        <div className="flex items-center gap-2">
          <div className={cn('w-8 h-8 rounded-full flex items-center justify-center', isBuy ? 'bg-green-100' : 'bg-red-100')}>
            {isBuy ? <TrendingUp className="h-4 w-4 text-green-600" /> : <TrendingDown className="h-4 w-4 text-red-600" />}
          </div>
          <div>
            <p className="font-semibold text-sm">{transaction.insiderName}</p>
            <p className="text-xs text-muted-foreground">{transaction.insiderTitle}</p>
          </div>
        </div>
      </TableCell>
      <TableCell className="py-3">
        <div className="flex items-center gap-1">
          <Badge variant={isBuy ? 'default' : 'destructive'} className="text-xs">{isBuy ? 'BUY' : 'SELL'}</Badge>
          {transaction.isIndirect && <Badge variant="outline" className="text-[10px]">Indirect</Badge>}
          {transaction.relatedTo10b51 && <Badge variant="outline" className="text-[10px]">10b5-1</Badge>}
        </div>
      </TableCell>
      <TableCell className="py-3">
        <p className="font-medium text-sm">{formatNumber(transaction.sharesTransacted)}</p>
        <p className="text-xs text-muted-foreground">@ {formatCurrency(transaction.pricePerShare)}</p>
      </TableCell>
      <TableCell className="py-3">
        <p className={cn('font-semibold text-sm', isBuy ? 'text-green-600' : 'text-red-600')}>{formatValue(transaction.totalValue)}</p>
      </TableCell>
      <TableCell className="py-3">
        <p className="text-sm">{transaction.sharesOwnedAfter.toLocaleString()}</p>
        <p className="text-xs text-muted-foreground">{transaction.sharesOwnedBefore > 0 ? `was ${formatNumber(transaction.sharesOwnedBefore)}` : 'New position'}</p>
      </TableCell>
      <TableCell className="py-3">
        <p className="text-xs font-medium">{new Date(transaction.transactionDate).toLocaleDateString()}</p>
        <p className="text-[10px] text-muted-foreground">Filed {new Date(transaction.filingDate).toLocaleDateString()}</p>
      </TableCell>
      <TableCell className="py-3">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge variant="outline" className="text-xs cursor-help">{transaction.secFormType}</Badge>
            </TooltipTrigger>
            <TooltipContent><p className="text-xs">SEC Form {transaction.secFormType}</p></TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </TableCell>
    </TableRow>
  )
}

function InsiderTradingPanelSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-32" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-20 w-full" />)}
          </div>
          <Skeleton className="h-64 w-full" />
        </div>
      </CardContent>
    </Card>
  )
}

export function InsiderTradingPanel({ transactions = [], summary, symbol, loading = false, className }: InsiderTradingPanelProps) {
  const [period, setPeriod] = useState<TimePeriod>('3m')
  const [transactionType, setTransactionType] = useState<InsiderTransactionType>('all')

  const filteredTransactions = useMemo(() => {
    return transactions.filter(t => transactionType === 'all' || t.transactionType === transactionType)
  }, [transactions, transactionType])

  const insiderGroups = useMemo(() => {
    const groups: Record<string, InsiderTransaction[]> = {}
    filteredTransactions.forEach(t => {
      if (!groups[t.insiderName]) groups[t.insiderName] = []
      groups[t.insiderName].push(t)
    })
    return groups
  }, [filteredTransactions])

  const topInsiders = useMemo(() => {
    return Object.entries(insiderGroups)
      .map(([name, txs]) => ({ name, totalValue: txs.reduce((sum, t) => sum + t.totalValue, 0), transactionCount: txs.length, type: txs[0].transactionType }))
      .sort((a, b) => Math.abs(b.totalValue) - Math.abs(a.totalValue))
      .slice(0, 10)
  }, [insiderGroups])

  if (loading) return <InsiderTradingPanelSkeleton />

  return (
    <Card className={cn('', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold flex items-center gap-2"><User className="h-5 w-5" />Insider Trading Activity</CardTitle>
            <CardDescription>{symbol ? `${symbol} - ` : ''}Track insider buying and selling patterns</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={period} onValueChange={(v: TimePeriod) => setPeriod(v)}>
              <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
              <SelectContent>
                {PERIOD_OPTIONS.map(opt => <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>)}
              </SelectContent>
            </Select>
            <Button size="sm" variant="outline"><Download className="h-4 w-4 mr-1" />Export</Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {summary && (
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center gap-2 mb-2"><TrendingUp className="h-4 w-4 text-green-600" /><span className="text-sm text-green-700 font-medium">Total Buys</span></div>
              <p className="text-2xl font-bold text-green-700">{formatValue(summary.totalBuyValue)}</p>
              <p className="text-xs text-green-600">{summary.totalBuys} transactions</p>
            </div>
            <div className="p-4 bg-red-50 rounded-lg border border-red-200">
              <div className="flex items-center gap-2 mb-2"><TrendingDown className="h-4 w-4 text-red-600" /><span className="text-sm text-red-700 font-medium">Total Sells</span></div>
              <p className="text-2xl font-bold text-red-700">{formatValue(summary.totalSellValue)}</p>
              <p className="text-xs text-red-600">{summary.totalSells} transactions</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <div className="flex items-center gap-2 mb-2"><DollarSign className="h-4 w-4 text-muted-foreground" /><span className="text-sm text-muted-foreground font-medium">Net Activity</span></div>
              <p className={cn('text-2xl font-bold', summary.netBuying >= 0 ? 'text-green-600' : 'text-red-600')}>{formatValue(summary.netBuying)}</p>
              <p className="text-xs text-muted-foreground">{summary.netBuying >= 0 ? 'Net buying' : 'Net selling'}</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <div className="flex items-center gap-2 mb-2"><User className="h-4 w-4 text-muted-foreground" /><span className="text-sm text-muted-foreground font-medium">Insiders Active</span></div>
              <p className="text-2xl font-bold">{summary.insiderBuyCount + summary.insiderSellCount}</p>
              <p className="text-xs text-muted-foreground">{summary.insiderBuyCount} buying, {summary.insiderSellCount} selling</p>
            </div>
          </div>
        )}
        <Tabs defaultValue="transactions" className="space-y-4">
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="transactions">Transactions</TabsTrigger>
              <TabsTrigger value="insiders">Top Insiders</TabsTrigger>
              <TabsTrigger value="summary">Summary</TabsTrigger>
            </TabsList>
            <Select value={transactionType} onValueChange={(v: InsiderTransactionType) => setTransactionType(v)}>
              <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="buy">Buys Only</SelectItem>
                <SelectItem value="sell">Sells Only</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <TabsContent value="transactions" className="space-y-4">
            {filteredTransactions.length === 0 ? (
              <div className="text-center py-12"><User className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" /><p className="text-muted-foreground">No insider transactions found</p></div>
            ) : (
              <div className="border rounded-lg">
                <Table>
                  <TableHeader>
                    <TableRow><TableHead>Insider</TableHead><TableHead>Type</TableHead><TableHead>Shares</TableHead><TableHead>Value</TableHead><TableHead>Owned After</TableHead><TableHead>Date</TableHead><TableHead>Form</TableHead></TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredTransactions.map(tx => <InsiderTransactionRow key={tx.id} transaction={tx} />)}
                  </TableBody>
                </Table>
              </div>
            )}
          </TabsContent>
          <TabsContent value="insiders" className="space-y-4">
            {topInsiders.length === 0 ? (
              <div className="text-center py-12"><User className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" /><p className="text-muted-foreground">No insider activity found</p></div>
            ) : (
              <div className="grid gap-4">
                {topInsiders.map((insider, index) => (
                  <div key={insider.name} className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <span className="text-lg font-bold text-muted-foreground w-6">{index + 1}</span>
                        <div>
                          <p className="font-semibold">{insider.name}</p>
                          <p className="text-xs text-muted-foreground">{insider.transactionCount} transaction(s)</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={cn('font-bold', insider.type === 'buy' ? 'text-green-600' : 'text-red-600')}>{formatValue(insider.totalValue)}</p>
                        <Badge variant={insider.type === 'buy' ? 'default' : 'destructive'} className="text-xs">{insider.type.toUpperCase()}</Badge>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>
          <TabsContent value="summary" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-6 border rounded-lg text-center">
                <p className="text-sm text-muted-foreground mb-2">Buy/Sell Ratio</p>
                <div className="flex h-4 rounded-full overflow-hidden mb-2">
                  <div className="bg-green-500" style={{ width: '50%' }} />
                  <div className="bg-red-500" style={{ width: '50%' }} />
                </div>
                <p className="text-2xl font-bold">1:1</p>
              </div>
              <div className="p-6 border rounded-lg text-center">
                <p className="text-sm text-muted-foreground mb-2">Average Transaction Size</p>
                <p className="text-2xl font-bold">{formatValue((summary?.totalBuyValue || 0) / Math.max(1, summary?.totalBuys || 1))}</p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default InsiderTradingPanel
