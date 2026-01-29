'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import type { PortfolioHolding } from '@/lib/types'
import { ArrowUpDown, ArrowUp, ArrowDown, Search } from 'lucide-react'

interface HoldingsTableProps {
  holdings: PortfolioHolding[]
  loading: boolean
}

type SortField = 'symbol' | 'quantity' | 'current_value' | 'unrealized_pnl' | 'unrealized_pnl_percent' | 'day_change_percent' | 'weight'
type SortDirection = 'asc' | 'desc'

export default function HoldingsTable({ holdings, loading }: HoldingsTableProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortField, setSortField] = useState<SortField>('current_value')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const filteredHoldings = holdings
    .filter(
      (h) =>
        h.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        h.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      const aVal = a[sortField] as number
      const bVal = b[sortField] as number
      return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
    })

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <ArrowUpDown className="w-4 h-4 ml-1 text-muted-foreground" />
    return sortDirection === 'asc' ? (
      <ArrowUp className="w-4 h-4 ml-1" />
    ) : (
      <ArrowDown className="w-4 h-4 ml-1" />
    )
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-12" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Holdings ({holdings.length})</CardTitle>
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search by symbol or name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b text-left text-sm text-muted-foreground">
                <th className="pb-3 font-medium">
                  <Button variant="ghost" onClick={() => handleSort('symbol')} className="p-0 hover:bg-transparent">
                    Symbol
                    <SortIcon field="symbol" />
                  </Button>
                </th>
                <th className="pb-3 font-medium">Name</th>
                <th className="pb-3 font-medium text-right">
                  <Button variant="ghost" onClick={() => handleSort('quantity')} className="p-0 hover:bg-transparent">
                    Quantity
                  </Button>
                </th>
                <th className="pb-3 font-medium text-right">
                  <Button variant="ghost" onClick={() => handleSort('current_value')} className="p-0 hover:bg-transparent">
                    Value
                    <SortIcon field="current_value" />
                  </Button>
                </th>
                <th className="pb-3 font-medium text-right">Avg Cost</th>
                <th className="pb-3 font-medium text-right">
                  <Button variant="ghost" onClick={() => handleSort('unrealized_pnl')} className="p-0 hover:bg-transparent">
                    P&L
                    <SortIcon field="unrealized_pnl" />
                  </Button>
                </th>
                <th className="pb-3 font-medium text-right">
                  <Button variant="ghost" onClick={() => handleSort('unrealized_pnl_percent')} className="p-0 hover:bg-transparent">
                    Return
                    <SortIcon field="unrealized_pnl_percent" />
                  </Button>
                </th>
                <th className="pb-3 font-medium text-right">
                  <Button variant="ghost" onClick={() => handleSort('day_change_percent')} className="p-0 hover:bg-transparent">
                    Day
                    <SortIcon field="day_change_percent" />
                  </Button>
                </th>
                <th className="pb-3 font-medium text-right">
                  <Button variant="ghost" onClick={() => handleSort('weight')} className="p-0 hover:bg-transparent">
                    Weight
                    <SortIcon field="weight" />
                  </Button>
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredHoldings.map((holding) => (
                <tr key={holding.id} className="border-b last:border-0 hover:bg-muted/50">
                  <td className="py-3 font-medium">{holding.symbol}</td>
                  <td className="py-3 text-muted-foreground max-w-[200px] truncate">{holding.name}</td>
                  <td className="py-3 text-right">{holding.quantity.toLocaleString()}</td>
                  <td className="py-3 text-right font-medium">{formatCurrency(holding.current_value)}</td>
                  <td className="py-3 text-right text-muted-foreground">{formatCurrency(holding.average_cost)}</td>
                  <td className={cn('py-3 text-right font-medium', holding.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600')}>
                    {formatCurrency(holding.unrealized_pnl)}
                  </td>
                  <td className={cn('py-3 text-right font-medium', holding.unrealized_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600')}>
                    {formatPercent(holding.unrealized_pnl_percent)}
                  </td>
                  <td className={cn('py-3 text-right font-medium', holding.day_change_percent >= 0 ? 'text-green-600' : 'text-red-600')}>
                    {formatPercent(holding.day_change_percent)}
                  </td>
                  <td className="py-3 text-right text-muted-foreground">
                    {(holding.weight * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredHoldings.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            {holdings.length === 0 ? 'No holdings in this portfolio' : 'No holdings match your search'}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
