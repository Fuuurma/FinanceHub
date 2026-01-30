"use client"

import { useState, useMemo } from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn, formatCurrency, formatDate } from '@/lib/utils'
import { Download, DollarSign, TrendingUp, TrendingDown, Calendar } from 'lucide-react'

export interface TaxLot {
  id: string
  symbol: string
  shares: number
  costBasis: number
  costPerShare: number
  purchaseDate: string
  currentPrice: number
  currentValue: number
  unrealizedGain: number
  unrealizedGainPercent: number
  term: 'short' | 'long'
  washSale: boolean
}

export interface TaxLotSummary {
  totalLots: number
  totalShares: number
  totalCostBasis: number
  totalCurrentValue: number
  totalUnrealizedGain: number
  shortTermGain: number
  longTermGain: number
}

export interface TaxLotTableProps {
  lots?: TaxLot[]
  summary?: TaxLotSummary
  symbol?: string
  loading?: boolean
  error?: string
  className?: string
}

type FilterType = 'all' | 'short' | 'long' | 'gainers' | 'losers' | 'wash'

function TaxLotRow({ lot }: { lot: TaxLot }) {
  const isGain = lot.unrealizedGain >= 0
  return (
    <TableRow className="hover:bg-muted/50">
      <TableCell className="py-3">
        <div className="flex flex-col">
          <span className="font-medium">{lot.symbol}</span>
          <span className="text-xs text-muted-foreground">{formatDate(lot.purchaseDate)}</span>
        </div>
      </TableCell>
      <TableCell className="py-3 text-right">{lot.shares.toLocaleString()}</TableCell>
      <TableCell className="py-3 text-right">{formatCurrency(lot.costPerShare)}</TableCell>
      <TableCell className="py-3 text-right">{formatCurrency(lot.costBasis)}</TableCell>
      <TableCell className="py-3 text-right">{formatCurrency(lot.currentValue)}</TableCell>
      <TableCell className="py-3">
        <div className="flex flex-col items-end">
          <span className={cn('font-medium', isGain ? 'text-green-500' : 'text-red-500')}>
            {isGain ? '+' : ''}{formatCurrency(lot.unrealizedGain)}
          </span>
          <span className={cn('text-xs', isGain ? 'text-green-600' : 'text-red-600')}>
            {isGain ? '+' : ''}{lot.unrealizedGainPercent.toFixed(2)}%
          </span>
        </div>
      </TableCell>
      <TableCell className="py-3">
        <Badge variant={lot.term === 'long' ? 'default' : 'secondary'}>
          {lot.term === 'long' ? 'Long' : 'Short'}
        </Badge>
        {lot.washSale && <Badge variant="destructive" className="ml-1">WS</Badge>}
      </TableCell>
    </TableRow>
  )
}

export function TaxLotTable({
  lots = [],
  summary,
  symbol,
  loading = false,
  error,
  className,
}: TaxLotTableProps) {
  const [filter, setFilter] = useState<FilterType>('all')
  const [search, setSearch] = useState('')

  const filteredLots = useMemo(() => {
    let result = [...lots]
    if (search) result = result.filter(l => l.symbol.toLowerCase().includes(search.toLowerCase()))
    switch (filter) {
      case 'short': return result.filter(l => l.term === 'short')
      case 'long': return result.filter(l => l.term === 'long')
      case 'gainers': return result.filter(l => l.unrealizedGain >= 0)
      case 'losers': return result.filter(l => l.unrealizedGain < 0)
      case 'wash': return result.filter(l => l.washSale)
    }
    return result
  }, [lots, filter, search])

  const handleExport = () => {
    const csv = ['Symbol,Shares,Cost/Share,Cost Basis,Current Value,Gain/Loss,Gain %,Term,Purchase Date',
      ...filteredLots.map(l => `${l.symbol},${l.shares},${l.costPerShare.toFixed(2)},${l.costBasis.toFixed(2)},${l.currentValue.toFixed(2)},${l.unrealizedGain.toFixed(2)},${l.unrealizedGainPercent.toFixed(2)},${l.term},${l.purchaseDate}`)].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${symbol || 'tax'}-lots.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader><Skeleton className="h-6 w-32" /><Skeleton className="h-4 w-48 mt-2" /></CardHeader>
        <CardContent><Skeleton className="h-24 w-full mb-4" /><Skeleton className="h-64 w-full" /></CardContent>
      </Card>
    )
  }

  if (error || (!lots.length && !summary)) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader><CardTitle>Tax Lots</CardTitle><CardDescription>Track cost basis and unrealized gains/losses</CardDescription></CardHeader>
        <CardContent><p className="text-sm text-red-500">{error || 'No tax lot data available'}</p></CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2"><DollarSign className="h-5 w-5" />Tax Lots{symbol && <Badge variant="outline">{symbol}</Badge>}</CardTitle>
            <CardDescription>Track cost basis and unrealized gains/losses</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Input placeholder="Search symbol..." value={search} onChange={(e) => setSearch(e.target.value)} className="w-32 h-8" />
            <Select value={filter} onValueChange={(v) => setFilter(v as FilterType)}>
              <SelectTrigger className="w-32 h-8"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="short">Short Term</SelectItem>
                <SelectItem value="long">Long Term</SelectItem>
                <SelectItem value="gainers">Gainers</SelectItem>
                <SelectItem value="losers">Losers</SelectItem>
                <SelectItem value="wash">Wash Sales</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" onClick={handleExport}><Download className="h-4 w-4" /></Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-32">Symbol</TableHead>
                <TableHead className="text-right">Shares</TableHead>
                <TableHead className="text-right">Cost/Share</TableHead>
                <TableHead className="text-right">Cost Basis</TableHead>
                <TableHead className="text-right">Value</TableHead>
                <TableHead className="text-right">G/L</TableHead>
                <TableHead>Term</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLots.map((lot) => <TaxLotRow key={lot.id} lot={lot} />)}
            </TableBody>
          </Table>
        </div>
        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">{filteredLots.length} lots</p>
        </div>
      </CardContent>
    </Card>
  )
}
