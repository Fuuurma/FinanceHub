'use client'

import { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
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
  Download,
  ExternalLink,
  TrendingUp,
  TrendingDown,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatCurrency, formatNumber } from '@/lib/utils/formatters'
import { useScreenerStore } from '@/stores/screenerStore'
import type { ScreenerResult, SortField, SortDirection } from '@/lib/types/screener'

interface SortButtonProps {
  label: string
  field: SortField
  currentField: SortField
  direction: SortDirection
  onSort: (field: SortField, direction: SortDirection) => void
}

function SortButton({ label, field, currentField, direction, onSort }: SortButtonProps) {
  const isActive = currentField === field

  return (
    <Button
      variant="ghost"
      size="sm"
      className={cn('h-8 px-2 font-normal', isActive && 'bg-muted')}
      onClick={() => onSort(field, isActive && direction === 'asc' ? 'desc' : 'asc')}
    >
      {label}
      {isActive && direction === 'asc' && <ArrowUp className="ml-1 w-3 h-3" />}
      {isActive && direction === 'desc' && <ArrowDown className="ml-1 w-3 h-3" />}
      {!isActive && <ArrowUpDown className="ml-1 w-3 h-3 opacity-50" />}
    </Button>
  )
}

export function ScreenerResults() {
  const {
    results,
    loading,
    error,
    total_count,
    total_screened,
    elapsed_seconds,
    last_updated,
    sort_field,
    sort_direction,
    setSorting,
    exportResults,
    limit,
  } = useScreenerStore()

  const [selectedRow, setSelectedRow] = useState<string | null>(null)

  const sortedResults = useMemo(() => {
    if (!results || results.length === 0) return []

    return [...results].sort((a, b) => {
      const aValue = a[sort_field]
      const bValue = b[sort_field]

      if (aValue === undefined || aValue === null) return 1
      if (bValue === undefined || bValue === null) return -1

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return direction === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return direction === 'asc' ? aValue - bValue : bValue - aValue
      }

      return 0
    })
  }, [results, sort_field, sort_direction])

  const direction = sort_direction

  if (loading) {
    return (
      <Card className="h-full">
        <CardHeader>
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="h-full">
        <CardContent className="flex items-center justify-center h-full">
          <div className="text-center text-destructive">
            <p className="font-semibold">Error loading results</p>
            <p className="text-sm">{error}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (results.length === 0) {
    return (
      <Card className="h-full">
        <CardContent className="flex items-center justify-center h-full">
          <div className="text-center text-muted-foreground">
            <p className="font-semibold">No results found</p>
            <p className="text-sm">Try adjusting your filters</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Screener Results</CardTitle>
            <CardDescription>
              {total_count} results found from {total_screened} screened
              {elapsed_seconds > 0 && ` (${elapsed_seconds}s)`}
            </CardDescription>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => exportResults('csv')}>
                Export as CSV
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => exportResults('json')}>
                Export as JSON
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto">
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead className="w-[100px]">
                  <SortButton
                    label="Symbol"
                    field="symbol"
                    currentField={sort_field}
                    direction={direction}
                    onSort={setSorting}
                  />
                </TableHead>
                <TableHead>
                  <SortButton
                    label="Name"
                    field="name"
                    currentField={sort_field}
                    direction={direction}
                    onSort={setSorting}
                  />
                </TableHead>
                <TableHead className="text-right">
                  <SortButton
                    label="Price"
                    field="current_price"
                    currentField={sort_field}
                    direction={direction}
                    onSort={setSorting}
                  />
                </TableHead>
                <TableHead className="text-right">
                  <SortButton
                    label="Change"
                    field="change_percent"
                    currentField={sort_field}
                    direction={direction}
                    onSort={setSorting}
                  />
                </TableHead>
                <TableHead className="text-right">
                  <SortButton
                    label="Volume"
                    field="volume"
                    currentField={sort_field}
                    direction={direction}
                    onSort={setSorting}
                  />
                </TableHead>
                <TableHead className="text-right">
                  <SortButton
                    label="Market Cap"
                    field="market_cap"
                    currentField={sort_field}
                    direction={direction}
                    onSort={setSorting}
                  />
                </TableHead>
                <TableHead className="text-right">
                  <SortButton
                    label="P/E"
                    field="pe_ratio"
                    currentField={sort_field}
                    direction={direction}
                    onSort={setSorting}
                  />
                </TableHead>
                <TableHead className="text-right">
                  <SortButton
                    label="Div Yield"
                    field="dividend_yield"
                    currentField={sort_field}
                    direction={direction}
                    onSort={setSorting}
                  />
                </TableHead>
                <TableHead className="text-center">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedResults.map((result) => (
                <TableRow
                  key={result.id}
                  className={cn(
                    'cursor-pointer transition-colors',
                    selectedRow === result.id && 'bg-muted'
                  )}
                  onClick={() => setSelectedRow(selectedRow === result.id ? null : result.id)}
                >
                  <TableCell className="font-medium">
                    {result.symbol}
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate" title={result.name}>
                    {result.name}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(result.current_price)}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className={cn(
                      'flex items-center justify-end gap-1',
                      result.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                    )}>
                      {result.change_percent >= 0 ? (
                        <TrendingUp className="w-3 h-3" />
                      ) : (
                        <TrendingDown className="w-3 h-3" />
                      )}
                      {result.change_percent?.toFixed(2)}%
                    </div>
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">
                    {formatNumber(result.volume)}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(result.market_cap / 1000000, 0)}M
                  </TableCell>
                  <TableCell className="text-right">
                    {result.pe_ratio !== undefined && result.pe_ratio !== null
                      ? result.pe_ratio.toFixed(2)
                      : '-'}
                  </TableCell>
                  <TableCell className="text-right">
                    {result.dividend_yield !== undefined && result.dividend_yield !== null
                      ? `${result.dividend_yield.toFixed(2)}%`
                      : '-'}
                  </TableCell>
                  <TableCell className="text-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={(e) => {
                        e.stopPropagation()
                        window.open(`/assets/${result.symbol}`, '_blank')
                      }}
                    >
                      <ExternalLink className="w-3 h-3" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        
        {results.length >= limit && (
          <div className="mt-4 text-center text-sm text-muted-foreground">
            Showing {limit} of {total_count} results. Adjust filters to see more.
          </div>
        )}
      </CardContent>
    </Card>
  )
}
