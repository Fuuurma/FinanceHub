'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Search,
  Filter,
  Download,
  Calendar,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Clock,
  FileText,
  FileSpreadsheet,
  FileJson,
  MoreHorizontal,
  Eye,
} from 'lucide-react'
import { cn, formatCurrency, formatPercent, formatDate, formatDateTime } from '@/lib/utils'
import type { Trade, TradeFilters, TradeStats } from '@/lib/types/trading'
import { tradingApi } from '@/lib/api/trading'

interface TradeHistoryProps {
  portfolioId?: string
  initialFilters?: TradeFilters
  onTradeClick?: (trade: Trade) => void
  className?: string
}

const DEFAULT_PAGE_SIZE = 25

const SORT_FIELDS = [
  { key: 'created_at', label: 'Date' },
  { key: 'asset_symbol', label: 'Symbol' },
  { key: 'side', label: 'Side' },
  { key: 'quantity', label: 'Quantity' },
  { key: 'price', label: 'Price' },
  { key: 'total_value', label: 'Value' },
  { key: 'realized_pnl', label: 'P&L' },
] as const

type SortField = typeof SORT_FIELDS[number]['key']
type SortDirection = 'asc' | 'desc'

const TIMEFRAMES = [
  { value: '1d', label: 'Today' },
  { value: '1w', label: 'Last 7 Days' },
  { value: '1m', label: 'Last 30 Days' },
  { value: '3m', label: 'Last 3 Months' },
  { value: '1y', label: 'Last Year' },
  { value: 'all', label: 'All Time' },
] as const

type Timeframe = typeof TIMEFRAMES[number]['value']

function TradeSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-6 w-48" />
        <div className="flex gap-2">
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-10 w-24" />
        </div>
      </div>
      <div className="border rounded-lg">
        <div className="border-b">
          <Skeleton className="h-10 w-full" />
        </div>
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    </div>
  )
}

function formatTradeValue(value: number): string {
  if (Math.abs(value) >= 1e6) {
    return `$${(value / 1e6).toFixed(2)}M`
  }
  if (Math.abs(value) >= 1e3) {
    return `$${(value / 1e3).toFixed(2)}K`
  }
  return formatCurrency(value)
}

function getTimeframeDates(timeframe: Timeframe): { start_date: string; end_date: string } {
  const endDate = new Date()
  const startDate = new Date()

  switch (timeframe) {
    case '1d':
      startDate.setDate(startDate.getDate() - 1)
      break
    case '1w':
      startDate.setDate(startDate.getDate() - 7)
      break
    case '1m':
      startDate.setMonth(startDate.getMonth() - 1)
      break
    case '3m':
      startDate.setMonth(startDate.getMonth() - 3)
      break
    case '1y':
      startDate.setFullYear(startDate.getFullYear() - 1)
      break
    case 'all':
      startDate.setFullYear(2010)
      break
  }

  return {
    start_date: startDate.toISOString().split('T')[0],
    end_date: endDate.toISOString().split('T')[0],
  }
}

export function TradeHistory({
  portfolioId,
  initialFilters,
  onTradeClick,
  className,
}: TradeHistoryProps) {
  const [trades, setTrades] = useState<Trade[]>([])
  const [stats, setStats] = useState<TradeStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [searchTerm, setSearchTerm] = useState('')
  const [timeframe, setTimeframe] = useState<Timeframe>('1m')
  const [sideFilter, setSideFilter] = useState<'all' | 'buy' | 'sell'>('all')
  const [sortField, setSortField] = useState<SortField>('created_at')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [page, setPage] = useState(0)
  const [totalCount, setTotalCount] = useState(0)
  const [isExporting, setIsExporting] = useState(false)

  const fetchTrades = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { start_date, end_date } = getTimeframeDates(timeframe)

      const filters: TradeFilters = {
        portfolio_id: portfolioId,
        start_date,
        end_date,
        side: sideFilter === 'all' ? undefined : sideFilter,
      }

      const [tradesData, statsData] = await Promise.all([
        tradingApi.trades.list({
          ...filters,
          limit: DEFAULT_PAGE_SIZE,
          offset: page * DEFAULT_PAGE_SIZE,
        }),
        tradingApi.trades.getStats({ portfolio_id: portfolioId, start_date, end_date }),
      ])

      setTrades(tradesData)
      setStats(statsData)
      setTotalCount(tradesData.length < DEFAULT_PAGE_SIZE ? page * DEFAULT_PAGE_SIZE + tradesData.length : (page + 1) * DEFAULT_PAGE_SIZE)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch trade history')
    } finally {
      setLoading(false)
    }
  }, [portfolioId, timeframe, sideFilter, page])

  useEffect(() => {
    fetchTrades()
  }, [fetchTrades])

  const handleSort = useCallback((field: SortField) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }, [sortField])

  const filteredTrades = useMemo(() => {
    let result = [...trades]

    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      result = result.filter(
        (trade) =>
          trade.asset_symbol.toLowerCase().includes(search) ||
          trade.asset_name.toLowerCase().includes(search) ||
          trade.id.toLowerCase().includes(search)
      )
    }

    result.sort((a, b) => {
      let aVal = a[sortField]
      let bVal = b[sortField]

      if (sortField === 'created_at') {
        aVal = new Date(aVal as string).getTime()
        bVal = new Date(bVal as string).getTime()
      }

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
      }

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal)
      }

      return 0
    })

    return result
  }, [trades, searchTerm, sortField, sortDirection])

  const totalPages = Math.ceil(totalCount / DEFAULT_PAGE_SIZE)

  const handleExportCSV = useCallback(() => {
    const headers = [
      'Date',
      'Symbol',
      'Side',
      'Quantity',
      'Price',
      'Total Value',
      'Fees',
      'Realized P&L',
      'Exchange',
      'Execution Time',
    ]

    const rows = filteredTrades.map((trade) => [
      formatDateTime(trade.created_at),
      trade.asset_symbol,
      trade.side,
      trade.quantity.toString(),
      trade.price.toString(),
      trade.total_value.toString(),
      trade.fees.toString(),
      trade.realized_pnl.toString(),
      trade.exchange,
      trade.execution_time,
    ])

    const csv = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `trade-history-${timeframe}-${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }, [filteredTrades, timeframe])

  const handleExportJSON = useCallback(() => {
    const json = JSON.stringify(filteredTrades, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `trade-history-${timeframe}-${new Date().toISOString().slice(0, 10)}.json`
    link.click()
    URL.revokeObjectURL(url)
  }, [filteredTrades, timeframe])

  if (loading) {
    return (
      <Card className={cn('', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Trade History
          </CardTitle>
          <CardDescription>Your executed trades and transactions</CardDescription>
        </CardHeader>
        <CardContent>
          <TradeSkeleton />
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={cn('border-destructive', className)}>
        <CardHeader>
          <CardTitle className="text-destructive">Error Loading Trade History</CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={fetchTrades} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('', className)}>
      <CardHeader>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Trade History
            </CardTitle>
            <CardDescription>
              {stats ? (
                <span className="flex items-center gap-2 mt-1">
                  <span>{stats.total_trades} trades</span>
                  <span className="text-muted-foreground">•</span>
                  <span className={stats.total_realized_pnl >= 0 ? 'text-green-500' : 'text-red-500'}>
                    {formatCurrency(stats.total_realized_pnl)} realized P&L
                  </span>
                </span>
              ) : (
                'Your executed trades and transactions'
              )}
            </CardDescription>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search symbol..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 w-40 sm:w-48"
              />
            </div>

            <Select value={timeframe} onValueChange={(v) => setTimeframe(v as Timeframe)}>
              <SelectTrigger className="w-36">
                <Calendar className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIMEFRAMES.map((tf) => (
                  <SelectItem key={tf.value} value={tf.value}>
                    {tf.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={sideFilter} onValueChange={(v) => setSideFilter(v as 'all' | 'buy' | 'sell')}>
              <SelectTrigger className="w-28">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="buy">Buy</SelectItem>
                <SelectItem value="sell">Sell</SelectItem>
              </SelectContent>
            </Select>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" disabled={isExporting}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleExportCSV}>
                  <FileText className="h-4 w-4 mr-2" />
                  Export as CSV
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleExportJSON}>
                  <FileJson className="h-4 w-4 mr-2" />
                  Export as JSON
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button variant="ghost" size="icon" onClick={fetchTrades}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {filteredTrades.length === 0 ? (
          <div className="text-center py-12">
            <Clock className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
            <p className="text-muted-foreground font-medium">No trades found</p>
            <p className="text-sm text-muted-foreground mt-1">
              Try adjusting your filters or timeframe
            </p>
          </div>
        ) : (
          <>
            <div className="border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    {SORT_FIELDS.map((field) => (
                      <TableHead
                        key={field.key}
                        className="cursor-pointer hover:bg-muted/50"
                        onClick={() => handleSort(field.key)}
                      >
                        <div className="flex items-center gap-1">
                          {field.label}
                          {sortField === field.key ? (
                            sortDirection === 'asc' ? (
                              <ArrowUp className="h-4 w-4" />
                            ) : (
                              <ArrowDown className="h-4 w-4" />
                            )
                          ) : (
                            <ArrowUpDown className="h-4 w-4 text-muted-foreground/50" />
                          )}
                        </div>
                      </TableHead>
                    ))}
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTrades.map((trade) => (
                    <TableRow
                      key={trade.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => onTradeClick?.(trade)}
                    >
                      <TableCell className="whitespace-nowrap">
                        <span className="text-sm text-muted-foreground">
                          {formatDate(trade.created_at)}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-medium">{trade.asset_symbol}</span>
                          <span className="text-xs text-muted-foreground truncate max-w-[120px]">
                            {trade.asset_name}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={trade.side === 'buy' ? 'default' : 'destructive'}
                          className={cn(
                            trade.side === 'buy' ? 'bg-green-500' : 'bg-red-500'
                          )}
                        >
                          {trade.side === 'buy' ? (
                            <TrendingUp className="h-3 w-3 mr-1" />
                          ) : (
                            <TrendingDown className="h-3 w-3 mr-1" />
                          )}
                          {trade.side.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {trade.quantity.toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {formatCurrency(trade.price)}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {formatTradeValue(trade.total_value)}
                      </TableCell>
                      <TableCell>
                        <div
                          className={cn(
                            'font-mono font-medium text-right',
                            trade.realized_pnl >= 0 ? 'text-green-500' : 'text-red-500'
                          )}
                        >
                          {trade.realized_pnl >= 0 ? '+' : ''}
                          {formatCurrency(trade.realized_pnl)}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              onClick={(e) => {
                                e.stopPropagation()
                                onTradeClick?.(trade)
                              }}
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-muted-foreground">
                  Showing {page * DEFAULT_PAGE_SIZE + 1} - {Math.min((page + 1) * DEFAULT_PAGE_SIZE, totalCount)} of {totalCount}
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                    disabled={page === 0}
                  >
                    Previous
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    Page {page + 1} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page >= totalPages - 1}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
