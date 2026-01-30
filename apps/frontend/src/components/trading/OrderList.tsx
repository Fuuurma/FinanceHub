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
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Search,
  Filter,
  Download,
  Calendar,
  RefreshCw,
  Clock,
  FileText,
  FileJson,
  MoreHorizontal,
  Eye,
  XCircle,
  Edit,
  CheckCircle,
  AlertCircle,
} from 'lucide-react'
import { cn, formatCurrency, formatPercent, formatDate, formatDateTime } from '@/lib/utils'
import type { Order, OrderFilters, OrderStats, OrderStatusFilter, OrderTypeFilter } from '@/lib/types/trading'
import { tradingApi } from '@/lib/api/trading'

interface OrderListProps {
  portfolioId?: string
  initialStatus?: OrderFilters['status']
  onOrderClick?: (order: Order) => void
  onOrderCancel?: (orderId: string) => void
  className?: string
}

const DEFAULT_PAGE_SIZE = 25

const SORT_FIELDS = [
  { key: 'created_at', label: 'Date' },
  { key: 'asset_symbol', label: 'Symbol' },
  { key: 'side', label: 'Side' },
  { key: 'order_type', label: 'Type' },
  { key: 'quantity', label: 'Qty' },
  { key: 'price', label: 'Price' },
  { key: 'status', label: 'Status' },
  { key: 'filled_quantity', label: 'Filled' },
] as const

type SortField = typeof SORT_FIELDS[number]['key']
type SortDirection = 'asc' | 'desc'

const TIMEFRAMES = [
  { value: '1d', label: 'Today' },
  { value: '1w', label: 'Last 7 Days' },
  { value: '1m', label: 'Last 30 Days' },
  { value: '3m', label: 'Last 3 Months' },
  { value: 'all', label: 'All Time' },
] as const

type Timeframe = typeof TIMEFRAMES[number]['value']

const ORDER_STATUSES: { value: OrderStatusFilter; label: string; color: string }[] = [
  { value: 'all', label: 'All Orders', color: 'bg-gray-100' },
  { value: 'pending', label: 'Pending', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'partially_filled', label: 'Partially Filled', color: 'bg-blue-100 text-blue-800' },
  { value: 'filled', label: 'Filled', color: 'bg-green-100 text-green-800' },
  { value: 'cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-800' },
  { value: 'rejected', label: 'Rejected', color: 'bg-red-100 text-red-800' },
  { value: 'expired', label: 'Expired', color: 'bg-gray-100 text-gray-800' },
]

const ORDER_TYPES: { value: OrderTypeFilter; label: string }[] = [
  { value: 'all', label: 'All Types' },
  { value: 'market', label: 'Market' },
  { value: 'limit', label: 'Limit' },
  { value: 'stop', label: 'Stop' },
  { value: 'stop_limit', label: 'Stop Limit' },
  { value: 'oco', label: 'OCO' },
]

function OrderSkeleton() {
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
    case 'all':
      startDate.setFullYear(2010)
      break
  }

  return {
    start_date: startDate.toISOString().split('T')[0],
    end_date: endDate.toISOString().split('T')[0],
  }
}

function getStatusBadge(status: Order['status']) {
  const statusConfig = ORDER_STATUSES.find((s) => s.value === status)
  return (
    <Badge variant="outline" className={cn('text-xs', statusConfig?.color)}>
      {statusConfig?.label || status}
    </Badge>
  )
}

function getOrderTypeBadge(orderType: Order['order_type']) {
  const colors: Record<string, string> = {
    market: 'bg-blue-100 text-blue-800',
    limit: 'bg-purple-100 text-purple-800',
    stop: 'bg-orange-100 text-orange-800',
    stop_limit: 'bg-orange-100 text-orange-800',
    oco: 'bg-pink-100 text-pink-800',
  }
  return (
    <Badge variant="outline" className={cn('text-xs', colors[orderType] || 'bg-gray-100')}>
      {orderType.toUpperCase()}
    </Badge>
  )
}

export function OrderList({
  portfolioId,
  initialStatus = 'all',
  onOrderClick,
  onOrderCancel,
  className,
}: OrderListProps) {
  const [orders, setOrders] = useState<Order[]>([])
  const [stats, setStats] = useState<OrderStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [searchTerm, setSearchTerm] = useState('')
  const [timeframe, setTimeframe] = useState<Timeframe>('1m')
  const [statusFilter, setStatusFilter] = useState<OrderFilters['status']>(initialStatus)
  const [typeFilter, setTypeFilter] = useState<OrderFilters['order_type']>('all')
  const [sortField, setSortField] = useState<SortField>('created_at')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [page, setPage] = useState(0)
  const [totalCount, setTotalCount] = useState(0)
  const [isExporting, setIsExporting] = useState(false)
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false)
  const [orderToCancel, setOrderToCancel] = useState<Order | null>(null)
  const [cancelReason, setCancelReason] = useState('')
  const [isCancelling, setIsCancelling] = useState(false)

  const fetchOrders = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { start_date, end_date } = getTimeframeDates(timeframe)

      const filters: OrderFilters = {
        portfolio_id: portfolioId,
        start_date,
        end_date,
        status: statusFilter,
        order_type: typeFilter,
      }

      const [ordersData, statsData] = await Promise.all([
        tradingApi.orders.list({
          ...filters,
          limit: DEFAULT_PAGE_SIZE,
          offset: page * DEFAULT_PAGE_SIZE,
        }),
        tradingApi.orders.getStats({ portfolio_id: portfolioId }),
      ])

      setOrders(ordersData)
      setStats(statsData)
      setTotalCount(ordersData.length < DEFAULT_PAGE_SIZE ? page * DEFAULT_PAGE_SIZE + ordersData.length : (page + 1) * DEFAULT_PAGE_SIZE)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch orders')
    } finally {
      setLoading(false)
    }
  }, [portfolioId, timeframe, statusFilter, typeFilter, page])

  useEffect(() => {
    fetchOrders()
  }, [fetchOrders])

  const handleSort = useCallback((field: SortField) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }, [sortField])

  const filteredOrders = useMemo(() => {
    let result = [...orders]

    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      result = result.filter(
        (order) =>
          order.asset_symbol.toLowerCase().includes(search) ||
          order.asset_name.toLowerCase().includes(search) ||
          order.id.toLowerCase().includes(search)
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
  }, [orders, searchTerm, sortField, sortDirection])

  const totalPages = Math.ceil(totalCount / DEFAULT_PAGE_SIZE)

  const handleExportCSV = useCallback(() => {
    const headers = [
      'Date',
      'Symbol',
      'Type',
      'Side',
      'Quantity',
      'Price',
      'Stop Price',
      'Filled',
      'Status',
      'Time in Force',
    ]

    const rows = filteredOrders.map((order) => [
      formatDateTime(order.created_at),
      order.asset_symbol,
      order.order_type,
      order.side,
      order.quantity.toString(),
      order.price?.toString() || 'Market',
      order.stop_price?.toString() || '-',
      order.filled_quantity.toString(),
      order.status,
      order.time_in_force,
    ])

    const csv = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `orders-${timeframe}-${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }, [filteredOrders, timeframe])

  const handleExportJSON = useCallback(() => {
    const json = JSON.stringify(filteredOrders, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `orders-${timeframe}-${new Date().toISOString().slice(0, 10)}.json`
    link.click()
    URL.revokeObjectURL(url)
  }, [filteredOrders, timeframe])

  const handleCancelOrder = useCallback(async () => {
    if (!orderToCancel) return

    setIsCancelling(true)
    try {
      await tradingApi.orders.cancel(orderToCancel.id, cancelReason)
      setCancelDialogOpen(false)
      setOrderToCancel(null)
      setCancelReason('')
      onOrderCancel?.(orderToCancel.id)
      fetchOrders()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel order')
    } finally {
      setIsCancelling(false)
    }
  }, [orderToCancel, cancelReason, onOrderCancel, fetchOrders])

  if (loading) {
    return (
      <Card className={cn('', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Orders
          </CardTitle>
          <CardDescription>Your open and recent orders</CardDescription>
        </CardHeader>
        <CardContent>
          <OrderSkeleton />
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={cn('border-destructive', className)}>
        <CardHeader>
          <CardTitle className="text-destructive">Error Loading Orders</CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={fetchOrders} variant="outline">
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
              Orders
            </CardTitle>
            <CardDescription>
              {stats ? (
                <span className="flex items-center gap-2 mt-1">
                  <span>{stats.total_orders} orders</span>
                  <span className="text-muted-foreground">•</span>
                  <span>{stats.pending_orders} pending</span>
                  <span className="text-muted-foreground">•</span>
                  <span>{formatCurrency(stats.open_orders_value)} open value</span>
                </span>
              ) : (
                'Your open and recent orders'
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

            <Select
              value={statusFilter}
              onValueChange={(v) => setStatusFilter(v as OrderFilters['status'])}
            >
              <SelectTrigger className="w-36">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                {ORDER_STATUSES.map((status) => (
                  <SelectItem key={status.value} value={status.value}>
                    {status.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select
              value={typeFilter}
              onValueChange={(v) => setTypeFilter(v as OrderFilters['order_type'])}
            >
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                {ORDER_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
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

            <Button variant="ghost" size="icon" onClick={fetchOrders}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {filteredOrders.length === 0 ? (
          <div className="text-center py-12">
            <Clock className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
            <p className="text-muted-foreground font-medium">No orders found</p>
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
                  {filteredOrders.map((order) => (
                    <TableRow
                      key={order.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => onOrderClick?.(order)}
                    >
                      <TableCell className="whitespace-nowrap">
                        <span className="text-sm text-muted-foreground">
                          {formatDate(order.created_at)}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-medium">{order.asset_symbol}</span>
                          <span className="text-xs text-muted-foreground truncate max-w-[120px]">
                            {order.asset_name}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>{getOrderTypeBadge(order.order_type)}</TableCell>
                      <TableCell>
                        <Badge
                          variant={order.side === 'buy' ? 'default' : 'destructive'}
                          className={cn(order.side === 'buy' ? 'bg-green-500' : 'bg-red-500')}
                        >
                          {order.side.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {order.quantity.toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {order.price ? formatCurrency(order.price) : 'Market'}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {order.stop_price ? formatCurrency(order.stop_price) : '-'}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        <div className="flex flex-col items-end">
                          <span>{order.filled_quantity.toLocaleString()}</span>
                          {order.remaining_quantity > 0 && (
                            <span className="text-xs text-muted-foreground">
                              / {order.quantity.toLocaleString()}
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(order.status)}</TableCell>
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
                                onOrderClick?.(order)
                              }}
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                            {order.status === 'pending' && (
                              <>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    setOrderToCancel(order)
                                    setCancelDialogOpen(true)
                                  }}
                                  className="text-destructive"
                                >
                                  <XCircle className="h-4 w-4 mr-2" />
                                  Cancel Order
                                </DropdownMenuItem>
                              </>
                            )}
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

      <Dialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Order</DialogTitle>
            <DialogDescription>
              Are you sure you want to cancel this order for {orderToCancel?.asset_symbol}?
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium">Cancellation Reason (optional)</label>
              <Input
                placeholder="Enter reason for cancellation..."
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCancelDialogOpen(false)}>
              Keep Order
            </Button>
            <Button
              variant="destructive"
              onClick={handleCancelOrder}
              disabled={isCancelling}
            >
              {isCancelling ? 'Cancelling...' : 'Cancel Order'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
