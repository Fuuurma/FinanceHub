'use client'

import { useState, useMemo, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { ArrowUpDown, ArrowUp, ArrowDown, Search, Columns, ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

export type SortDirection = 'asc' | 'desc'

export interface Column<T> {
  key: keyof T | string
  label: string
  sortable?: boolean
  searchable?: boolean
  render?: (value: any, item: T) => React.ReactNode
  className?: string
  headerClassName?: string
}

interface DataTableProps<T> {
  title?: string
  description?: string
  data: T[]
  columns: Column<T>[]
  loading?: boolean
  searchable?: boolean
  searchKeys?: (keyof T)[]
  searchPlaceholder?: string
  pageSize?: number
  showColumnToggle?: boolean
  emptyMessage?: string
  onRowClick?: (item: T) => void
}

export function DataTable<T extends Record<string, any>>({
  title,
  description,
  data,
  columns,
  loading = false,
  searchable = true,
  searchKeys = [],
  searchPlaceholder = 'Search...',
  pageSize = 10,
  showColumnToggle = false,
  emptyMessage = 'No data available',
  onRowClick,
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortColumn, setSortColumn] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')
  const [visibleColumns, setVisibleColumns] = useState<Set<string>>(
    new Set(columns.map((c) => String(c.key)))
  )
  const [currentPage, setCurrentPage] = useState(0)

  const handleSort = useCallback((key: string) => {
    if (sortColumn === key) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortColumn(key)
      setSortDirection('asc')
    }
  }, [sortColumn])

  const filteredData = useMemo(() => {
    let result = [...data]

    if (searchTerm && searchable && searchKeys.length > 0) {
      const search = searchTerm.toLowerCase()
      result = result.filter((item) =>
        searchKeys.some((key) => {
          const value = item[key]
          return value && String(value).toLowerCase().includes(search)
        })
      )
    }

    if (sortColumn) {
      result.sort((a, b) => {
        const aVal = a[sortColumn]
        const bVal = b[sortColumn]
        if (aVal === bVal) return 0
        const comparison = aVal < bVal ? -1 : 1
        return sortDirection === 'asc' ? comparison : -comparison
      })
    }

    return result
  }, [data, searchTerm, searchable, searchKeys, sortColumn, sortDirection])

  const paginatedData = useMemo(() => {
    if (pageSize <= 0) return filteredData
    const start = currentPage * pageSize
    return filteredData.slice(start, start + pageSize)
  }, [filteredData, currentPage, pageSize])

  const totalPages = Math.ceil(filteredData.length / pageSize)

  const toggleColumn = (key: string) => {
    setVisibleColumns((prev) => {
      const next = new Set(prev)
      if (next.has(key)) {
        next.delete(key)
      } else {
        next.add(key)
      }
      return next
    })
  }

  const visibleColumnsList = columns.filter((c) => visibleColumns.has(String(c.key)))
  const sortableColumns = columns.filter((c) => c.sortable)

  const SortIcon = ({ column }: { column: Column<T> }) => {
    const key = String(column.key)
    if (!column.sortable) return null
    if (sortColumn !== key) return <ArrowUpDown className="w-4 h-4 ml-1 text-muted-foreground" />
    return sortDirection === 'asc' ? (
      <ArrowUp className="w-4 h-4 ml-1" />
    ) : (
      <ArrowDown className="w-4 h-4 ml-1" />
    )
  }

  if (loading) {
    return (
      <Card>
        {title && (
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
        )}
        <CardContent>
          {searchable && (
            <div className="mb-4">
              <Skeleton className="h-10 w-64" />
            </div>
          )}
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
      {(title || searchable || showColumnToggle) && (
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              {title && <CardTitle>{title}</CardTitle>}
              {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
            </div>
            <div className="flex items-center gap-2">
              {searchable && (
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder={searchPlaceholder}
                    value={searchTerm}
                    onChange={(e) => {
                      setSearchTerm(e.target.value)
                      setCurrentPage(0)
                    }}
                    className="pl-9 w-48 sm:w-64"
                  />
                </div>
              )}
              {showColumnToggle && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      <Columns className="w-4 h-4 mr-2" />
                      Columns
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    {columns.map((column) => (
                      <DropdownMenuCheckboxItem
                        key={String(column.key)}
                        checked={visibleColumns.has(String(column.key))}
                        onCheckedChange={() => toggleColumn(String(column.key))}
                      >
                        {column.label}
                      </DropdownMenuCheckboxItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>
          </div>
        </CardHeader>
      )}
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b text-left text-sm text-muted-foreground">
                {visibleColumnsList.map((column) => (
                  <th
                    key={String(column.key)}
                    className={cn('pb-3 font-medium', column.headerClassName)}
                  >
                    {column.sortable ? (
                      <Button
                        variant="ghost"
                        onClick={() => handleSort(String(column.key))}
                        className="p-0 hover:bg-transparent"
                      >
                        {column.label}
                        <SortIcon column={column} />
                      </Button>
                    ) : (
                      column.label
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((item, index) => (
                <tr
                  key={item.id || index}
                  className={cn(
                    'border-b last:border-0 hover:bg-muted/50',
                    onRowClick && 'cursor-pointer'
                  )}
                  onClick={() => onRowClick?.(item)}
                >
                  {visibleColumnsList.map((column) => (
                    <td key={String(column.key)} className={cn('py-3', column.className)}>
                      {column.render
                        ? column.render(item[column.key], item)
                        : String(item[column.key] ?? '')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredData.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            {emptyMessage}
          </div>
        )}

        {pageSize > 0 && totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 pt-4 border-t">
            <p className="text-sm text-muted-foreground">
              Showing {filteredData.length > 0 ? currentPage * pageSize + 1 : 0} to{' '}
              {Math.min((currentPage + 1) * pageSize, filteredData.length)} of {filteredData.length} results
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
                disabled={currentPage === 0}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="text-sm">
                Page {currentPage + 1} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={currentPage >= totalPages - 1}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
