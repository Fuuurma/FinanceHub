'use client'

import { useState, useEffect } from 'react'
import { useTradingStore } from '@/stores/tradingStore'
import type { Position } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  TrendingUp,
  TrendingDown,
  X,
  RefreshCw,
  Filter,
  Download,
  Star,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useDownloadFile } from '@/hooks/useDownload'

export function PositionTracker() {
  const { positions, loading, closePosition, fetchPositions } = useTradingStore()
  const [filter, setFilter] = useState('')
  const [sortField, setSortField] = useState<keyof Position>('unrealized_pnl')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null)
  const { downloadCSV } = useDownloadFile()

  useEffect(() => {
    fetchPositions()
    const interval = setInterval(() => fetchPositions(), 5000)
    return () => clearInterval(interval)
  }, [fetchPositions])

  const filteredPositions = positions
    .filter((pos) => 
      pos.asset_symbol.toLowerCase().includes(filter.toLowerCase()) ||
      pos.asset_name.toLowerCase().includes(filter.toLowerCase())
    )
    .sort((a, b) => {
      const aVal = a[sortField] as number
      const bVal = b[sortField] as number
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
      }
      return 0
    })

  const handleSort = (field: keyof Position) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const handleClosePosition = async (positionId: string) => {
    if (confirm('Are you sure you want to close this position?')) {
      await closePosition(positionId)
    }
  }

  const exportToCSV = () => {
    const headers = ['Symbol', 'Side', 'Quantity', 'Avg Price', 'Current Price', 'Market Value', 'P&L', 'P&L %', 'Days Open']
    const rows = filteredPositions.map(pos => [
      pos.asset_symbol,
      pos.side,
      pos.quantity,
      pos.avg_entry_price,
      pos.current_price || 'N/A',
      pos.market_value || 'N/A',
      pos.unrealized_pnl.toFixed(2),
      pos.unrealized_pnl_percent.toFixed(2),
      pos.days_open,
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(',')),
    ].join('\n')

    const filename = `positions-${new Date().toISOString().split('T')[0]}.csv`
    downloadCSV(csvContent, filename)
  }

  if (loading.positions) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-2 border-foreground">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Position Tracker
              <Badge variant="secondary">{filteredPositions.length} positions</Badge>
            </CardTitle>
            <CardDescription>
              Real-time P&L tracking for open positions
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={exportToCSV}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" size="sm" onClick={fetchPositions} disabled={loading.positions}>
              <RefreshCw className={cn('h-4 w-4 mr-2', loading.positions && 'animate-spin')} />
              Refresh
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex gap-4">
          <div className="flex-1">
            <div className="relative">
              <Filter className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search positions..."
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="pl-8"
              />
            </div>
          </div>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead
                  className="cursor-pointer hover:bg-muted"
                  onClick={() => handleSort('asset_symbol')}
                >
                  Symbol
                  {sortField === 'asset_symbol' && (
                    <span className="ml-2">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted"
                  onClick={() => handleSort('side')}
                >
                  Side
                  {sortField === 'side' && (
                    <span className="ml-2">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted text-right"
                  onClick={() => handleSort('quantity')}
                >
                  Quantity
                  {sortField === 'quantity' && (
                    <span className="ml-2">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted text-right"
                  onClick={() => handleSort('avg_entry_price')}
                >
                  Avg Price
                  {sortField === 'avg_entry_price' && (
                    <span className="ml-2">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted text-right"
                  onClick={() => handleSort('current_price')}
                >
                  Current Price
                  {sortField === 'current_price' && (
                    <span className="ml-2">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted text-right"
                  onClick={() => handleSort('market_value')}
                >
                  Market Value
                  {sortField === 'market_value' && (
                    <span className="ml-2">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted text-right"
                  onClick={() => handleSort('unrealized_pnl')}
                >
                  P&L
                  {sortField === 'unrealized_pnl' && (
                    <span className="ml-2">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted text-right"
                  onClick={() => handleSort('unrealized_pnl_percent')}
                >
                  P&L %
                  {sortField === 'unrealized_pnl_percent' && (
                    <span className="ml-2">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted text-right"
                  onClick={() => handleSort('days_open')}
                >
                  Days
                  {sortField === 'days_open' && (
                    <span className="ml-2">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredPositions.map((position) => (
                <TableRow key={position.id}>
                  <TableCell className="font-medium">
                    <a
                      href={`/dashboard/assets/${position.asset_id}`}
                      className="hover:underline"
                    >
                      {position.asset_symbol}
                    </a>
                  </TableCell>
                  <TableCell>
                    <Badge variant={position.side === 'long' ? 'default' : 'secondary'}>
                      {position.side === 'long' ? (
                        <TrendingUp className="h-3 w-3 mr-1" />
                      ) : (
                        <TrendingDown className="h-3 w-3 mr-1" />
                      )}
                      {position.side.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {position.quantity.toFixed(4)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    ${position.avg_entry_price.toFixed(2)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    ${position.current_price?.toFixed(2) || 'N/A'}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    ${position.market_value?.toFixed(2) || 'N/A'}
                  </TableCell>
                  <TableCell
                    className={cn(
                      'text-right font-mono font-semibold',
                      position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                    )}
                  >
                    {position.unrealized_pnl >= 0 ? '+' : ''}
                    ${position.unrealized_pnl.toFixed(2)}
                  </TableCell>
                  <TableCell
                    className={cn(
                      'text-right font-mono',
                      position.unrealized_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'
                    )}
                  >
                    {position.unrealized_pnl_percent >= 0 ? '+' : ''}
                    {position.unrealized_pnl_percent.toFixed(2)}%
                  </TableCell>
                  <TableCell className="text-right font-mono text-muted-foreground">
                    {position.days_open}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedPosition(position)}
                      >
                        <Star className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleClosePosition(position.id)}
                        className="hover:bg-destructive hover:text-destructive-foreground"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {filteredPositions.length === 0 && (
          <div className="py-12 text-center text-muted-foreground">
            No positions found
          </div>
        )}
      </CardContent>
    </Card>
  )
}
