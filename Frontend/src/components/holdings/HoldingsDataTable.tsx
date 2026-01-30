'use client'

import { useState, useMemo } from 'react'
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  useReactTable,
  SortingState,
  ColumnFiltersState,
  VisibilityState,
} from '@tanstack/react-table'
import { ChevronUp, ChevronDown, ArrowUpDown, Eye, Search, Filter, Download, MoreHorizontal, Plus, Edit2, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
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
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import type { Holding, AssetClass } from '@/lib/types/holdings'
import { ASSET_CLASS_LABELS, ASSET_CLASS_COLORS } from '@/lib/types/holdings'
import { cn } from '@/lib/utils'

interface HoldingsDataTableProps {
  holdings: Holding[]
  loading?: boolean
  onEdit?: (holding: Holding) => void
  onDelete?: (holding: Holding) => void
  onAdd?: () => void
  onExport?: () => void
}

const assetClassOptions: { value: AssetClass; label: string }[] = Object.entries(ASSET_CLASS_LABELS).map(([value, label]) => ({
  value: value as AssetClass,
  label,
}))

export function HoldingsDataTable({
  holdings,
  loading = false,
  onEdit,
  onDelete,
  onAdd,
  onExport,
}: HoldingsDataTableProps) {
  const [sorting, setSorting] = useState<SortingState>([{ id: 'current_value', desc: true }])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({
    symbol: true,
    name: true,
    asset_class: true,
    quantity: true,
    average_cost: true,
    current_price: true,
    current_value: true,
    unrealized_pnl: true,
    unrealized_pnl_percent: true,
    day_change: true,
    weight: true,
    actions: true,
  })
  const [globalFilter, setGlobalFilter] = useState('')

  const formatCurrency = (value: number, currency = 'USD') =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)

  const formatPercent = (value: number) =>
    `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`

  const columns = useMemo<ColumnDef<Holding>[]>(
    () => [
      {
        id: 'select',
        header: ({ table }) => (
          <Checkbox
            checked={table.getIsAllPageRowsSelected()}
            onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
            aria-label="Select all"
          />
        ),
        cell: ({ row }) => (
          <Checkbox
            checked={row.getIsSelected()}
            onCheckedChange={(value) => row.toggleSelected(!!value)}
            aria-label="Select row"
          />
        ),
        enableSorting: false,
        enableHiding: false,
        size: 40,
      },
      {
        accessorKey: 'symbol',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="p-0 hover:bg-transparent"
          >
            Symbol
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => (
          <div className="flex flex-col">
            <span className="font-semibold">{row.getValue('symbol')}</span>
            <span className="text-xs text-muted-foreground truncate max-w-[120px]">
              {row.original.name}
            </span>
          </div>
        ),
        size: 120,
      },
      {
        accessorKey: 'asset_class',
        header: 'Asset Class',
        cell: ({ row }) => {
          const assetClass = row.getValue('asset_class') as AssetClass
          return (
            <Badge
              variant="outline"
              style={{
                borderColor: ASSET_CLASS_COLORS[assetClass],
                color: ASSET_CLASS_COLORS[assetClass],
              }}
            >
              {ASSET_CLASS_LABELS[assetClass]}
            </Badge>
          )
        },
        filterFn: (row, id, value) => {
          if (Array.isArray(value)) return value.includes(row.getValue(id))
          return row.getValue(id) === value
        },
        size: 120,
      },
      {
        accessorKey: 'quantity',
        header: 'Quantity',
        cell: ({ row }) => (
          <span className="font-mono">{(row.getValue('quantity') as number).toLocaleString()}</span>
        ),
        size: 100,
      },
      {
        accessorKey: 'average_cost',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="p-0 hover:bg-transparent"
          >
            Avg Cost
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => formatCurrency(row.getValue('average_cost') as number),
        size: 120,
      },
      {
        accessorKey: 'current_price',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="p-0 hover:bg-transparent"
          >
            Price
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => formatCurrency(row.getValue('current_price')),
        size: 120,
      },
      {
        accessorKey: 'current_value',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="p-0 hover:bg-transparent"
          >
            Value
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => <span className="font-semibold">{formatCurrency(row.getValue('current_value'))}</span>,
        size: 140,
      },
      {
        accessorKey: 'unrealized_pnl',
        header: 'Unrealized P&L',
        cell: ({ row }) => {
          const pnl = row.getValue('unrealized_pnl') as number
          return (
            <div className="flex flex-col items-end">
              <span className={cn('font-semibold', pnl >= 0 ? 'text-green-600' : 'text-red-600')}>
                {pnl >= 0 ? '+' : ''}{formatCurrency(pnl)}
              </span>
              <span className={cn('text-xs', pnl >= 0 ? 'text-green-600' : 'text-red-600')}>
                {formatPercent(row.getValue('unrealized_pnl_percent'))}
              </span>
            </div>
          )
        },
        size: 150,
      },
      {
        accessorKey: 'day_change',
        header: 'Day Change',
        cell: ({ row }) => {
          const change = row.getValue('day_change') as number
          const changePercent = (row.original.day_change_percent) as number
          return (
            <div className="flex flex-col items-end">
              <span className={cn('font-semibold', change >= 0 ? 'text-green-600' : 'text-red-600')}>
                {change >= 0 ? '+' : ''}{formatCurrency(change)}
              </span>
              <span className={cn('text-xs', change >= 0 ? 'text-green-600' : 'text-red-600')}>
                {formatPercent(changePercent)}
              </span>
            </div>
          )
        },
        size: 150,
      },
      {
        accessorKey: 'weight',
        header: 'Weight',
        cell: ({ row }) => {
          const weight = row.getValue('weight') as number
          return (
            <div className="flex items-center gap-2">
              <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full"
                  style={{ width: `${Math.min(weight * 4, 100)}%` }}
                />
              </div>
              <span className="text-sm">{weight.toFixed(1)}%</span>
            </div>
          )
        },
        size: 140,
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => {
          const holding = row.original
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => onEdit?.(holding)}>
                  <Edit2 className="mr-2 h-4 w-4" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onDelete?.(holding)} className="text-red-600">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )
        },
        size: 60,
        enableHiding: false,
      },
    ],
    [onEdit, onDelete]
  )

  const table = useReactTable({
    data: holdings,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onGlobalFilterChange: setGlobalFilter,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      globalFilter,
    },
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  })

  const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0)
  const totalPnL = holdings.reduce((sum, h) => sum + h.unrealized_pnl, 0)
  const totalDayChange = holdings.reduce((sum, h) => sum + h.day_change, 0)

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-10 w-64 bg-muted animate-pulse rounded-md" />
            <div className="h-10 w-48 bg-muted animate-pulse rounded-md" />
          </div>
          <div className="h-10 w-32 bg-muted animate-pulse rounded-md" />
        </div>
        <div className="border rounded-lg">
          <div className="h-12 border-b bg-muted/50" />
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-16 border-b last:border-0">
              <div className="h-4 w-full bg-muted animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search holdings..."
              value={globalFilter ?? ''}
              onChange={(e) => setGlobalFilter(e.target.value)}
              className="pl-9"
            />
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Filter className="mr-2 h-4 w-4" />
                Filter
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-48">
              <div className="p-2">
                <p className="text-sm font-medium mb-2">Asset Class</p>
                <div className="space-y-1">
                  {assetClassOptions.map((option) => (
                    <label
                      key={option.value}
                      className="flex items-center gap-2 text-sm cursor-pointer"
                    >
                      <Checkbox
                        checked={(columnFilters.find(f => f.id === 'asset_class')?.value as AssetClass[] | undefined)?.includes(option.value)}
                        onCheckedChange={(checked) => {
                          const currentValues = (columnFilters.find(f => f.id === 'asset_class')?.value as AssetClass[] | undefined) || []
                          if (checked) {
                            setColumnFilters([...columnFilters.filter(f => f.id !== 'asset_class'), {
                              id: 'asset_class',
                              value: [...currentValues, option.value],
                            }])
                          } else {
                            setColumnFilters([...columnFilters.filter(f => f.id !== 'asset_class'), {
                              id: 'asset_class',
                              value: currentValues.filter(v => v !== option.value),
                            }])
                          }
                        }}
                      />
                      {option.label}
                    </label>
                  ))}
                </div>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Eye className="mr-2 h-4 w-4" />
                Columns
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              {table.getAllColumns().filter(col => col.getCanHide()).map(col => (
                <DropdownMenuItem key={col.id} className="capitalize">
                  <Checkbox
                    checked={col.getIsVisible()}
                    onCheckedChange={(value) => col.toggleVisibility(!!value)}
                    className="mr-2"
                  />
                  {typeof col.columnDef.header === 'string' ? col.columnDef.header : col.id}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <div className="flex items-center gap-2">
          {onAdd && (
            <Button onClick={onAdd} size="sm">
              <Plus className="mr-2 h-4 w-4" />
              Add Holding
            </Button>
          )}
          {onExport && (
            <Button variant="outline" onClick={onExport} size="sm">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          )}
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 p-4 bg-muted/50 rounded-lg">
        <div>
          <p className="text-sm text-muted-foreground">Total Value</p>
          <p className="text-2xl font-bold">{formatCurrency(totalValue)}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Total P&L</p>
          <p className={cn('text-2xl font-bold', totalPnL >= 0 ? 'text-green-600' : 'text-red-600')}>
            {totalPnL >= 0 ? '+' : ''}{formatCurrency(totalPnL)}
          </p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Day Change</p>
          <p className={cn('text-2xl font-bold', totalDayChange >= 0 ? 'text-green-600' : 'text-red-600')}>
            {totalDayChange >= 0 ? '+' : ''}{formatCurrency(totalDayChange)}
          </p>
        </div>
      </div>

      {/* Table */}
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} style={{ width: header.getSize() }}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id} data-state={row.getIsSelected() && 'selected'}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No holdings found. Add your first holding to get started.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{' '}
          {Math.min(
            (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
            holdings.length
          )}{' '}
          of {holdings.length} holdings
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
