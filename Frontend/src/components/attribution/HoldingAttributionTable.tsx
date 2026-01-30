'use client'

import { useState, useMemo } from 'react'
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  SortingState,
} from '@tanstack/react-table'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Checkbox } from '@/components/ui/checkbox'
import type { HoldingAttribution } from '@/lib/types/attribution'
import { SECTOR_COLORS } from '@/lib/types/attribution'
import { cn } from '@/lib/utils'

interface HoldingAttributionTableProps {
  attribution: HoldingAttribution[]
  formatCurrency: (value: number) => string
  formatPercent: (value: number) => string
}

export function HoldingAttributionTable({
  attribution,
  formatCurrency,
  formatPercent,
}: HoldingAttributionTableProps) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'contribution', desc: true },
  ])
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set())

  const columns = useMemo<ColumnDef<HoldingAttribution>[]>(
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
        accessorKey: 'sector',
        header: 'Sector',
        cell: ({ row }) => {
          const sector = row.getValue('sector') as string
          return (
            <Badge
              variant="outline"
              style={{
                borderColor: SECTOR_COLORS[sector] || SECTOR_COLORS['Other'],
                color: SECTOR_COLORS[sector] || SECTOR_COLORS['Other'],
              }}
            >
              {sector}
            </Badge>
          )
        },
        size: 120,
      },
      {
        accessorKey: 'weight',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="p-0 hover:bg-transparent"
          >
            Weight
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
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
        accessorKey: 'return',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="p-0 hover:bg-transparent"
          >
            Return
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => {
          const returnValue = row.getValue('return') as number
          return (
            <span className={cn(
              'font-medium',
              returnValue >= 0 ? 'text-green-600' : 'text-red-600'
            )}>
              {formatPercent(returnValue)}
            </span>
          )
        },
        size: 100,
      },
      {
        accessorKey: 'contribution',
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="p-0 hover:bg-transparent"
          >
            Contribution
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => {
          const contribution = row.getValue('contribution') as number
          return (
            <div className="flex flex-col items-end">
              <span className={cn(
                'font-semibold',
                contribution >= 0 ? 'text-green-600' : 'text-red-600'
              )}>
                {formatPercent(contribution)}
              </span>
              <span className="text-xs text-muted-foreground">
                {formatCurrency(row.original.contribution * 1000)}
              </span>
            </div>
          )
        },
        size: 140,
      },
      {
        accessorKey: 'value_change',
        header: 'Value Change',
        cell: ({ row }) => {
          const valueChange = row.getValue('value_change') as number
          return (
            <span className={cn(
              'font-medium',
              valueChange >= 0 ? 'text-green-600' : 'text-red-600'
            )}>
              {formatCurrency(valueChange)}
            </span>
          )
        },
        size: 120,
      },
    ],
    [formatCurrency, formatPercent]
  )

  const table = useReactTable({
    data: attribution,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    },
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {attribution.length} holdings • Click column headers to sort
        </p>
      </div>

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
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && 'selected'}
                  className="cursor-pointer"
                  onClick={() => row.toggleSelected()}
                >
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
                  No attribution data available
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
            attribution.length
          )}{' '}
          of {attribution.length} holdings
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
