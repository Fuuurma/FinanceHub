'use client'

import { useState, useMemo, useCallback, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { ArrowUpDown, ArrowUp, ArrowDown, Search, Columns, ChevronLeft, ChevronRight, Copy, Download, FileJson, FileSpreadsheet, FileText, File, Rows, Maximize2, Minimize2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useDownload } from '@/hooks/useDownload'

export type SortDirection = 'asc' | 'desc'
export type Density = 'compact' | 'normal' | 'spacious'

export interface Column<T> {
  key: keyof T | string
  label: string
  sortable?: boolean
  searchable?: boolean
  render?: (value: any, item: T) => React.ReactNode
  className?: string
  headerClassName?: string
  frozen?: boolean
  width?: number
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
  showDensityToggle?: boolean
  showExport?: boolean
  showRowNumbers?: boolean
  exportFilename?: string
  frozenColumns?: number
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
  showDensityToggle = false,
  showExport = false,
  showRowNumbers = false,
  exportFilename = 'data-table',
  frozenColumns = 0,
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
  const [density, setDensity] = useState<Density>('normal')
  const tableRef = useRef<HTMLTableElement>(null)

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
  const frozenColumnsList = visibleColumnsList.filter((c) => c.frozen)
  const scrollableColumnsList = visibleColumnsList.filter((c) => !c.frozen)

  const densityClasses: Record<Density, string> = {
    compact: 'py-1',
    normal: 'py-3',
    spacious: 'py-4',
  }

  const { download, state } = useDownload()

  const copyToClipboard = useCallback(async () => {
    const headers = visibleColumnsList.map((c) => c.label).join('\t')
    const rows = filteredData.map((item) =>
      visibleColumnsList.map((col) => {
        const value = item[col.key]
        const rendered = col.render ? col.render(value, item) : value
        return typeof rendered === 'string' ? rendered : String(rendered ?? '')
      }).join('\t')
    ).join('\n')
    const text = `${headers}\n${rows}`
    await navigator.clipboard.writeText(text)
  }, [filteredData, visibleColumnsList])

  const exportToCSV = useCallback(() => {
    const headers = visibleColumnsList.map((c) => c.label).join(',')
    const rows = filteredData.map((item) =>
      visibleColumnsList.map((col) => {
        const value = item[col.key]
        const rendered = col.render ? col.render(value, item) : value
        const cellValue = typeof rendered === 'string' ? rendered : String(rendered ?? '')
        const escaped = cellValue.includes(',') || cellValue.includes('"') || cellValue.includes('\n')
          ? `"${cellValue.replace(/"/g, '""')}"`
          : cellValue
        return escaped
      }).join(',')
    ).join('\n')
    const csv = `${headers}\n${rows}`
    const timestamp = new Date().toISOString().split('T')[0]
    download(csv, { filename: `${exportFilename}_${timestamp}.csv`, mimeType: 'text/csv' })
  }, [filteredData, visibleColumnsList, exportFilename, download])

  const exportToJSON = useCallback(() => {
    const jsonData = filteredData.map((item) => {
      const row: Record<string, any> = {}
      visibleColumnsList.forEach((col) => {
        const value = item[col.key]
        row[col.label] = col.render ? col.render(value, item) : value
      })
      return row
    })
    const json = JSON.stringify(jsonData, null, 2)
    const timestamp = new Date().toISOString().split('T')[0]
    download(json, { filename: `${exportFilename}_${timestamp}.json`, mimeType: 'application/json' })
  }, [filteredData, visibleColumnsList, exportFilename, download])

  const exportToExcel = useCallback(() => {
    const headers = visibleColumnsList.map((c) => c.label).join('\t')
    const rows = filteredData.map((item) =>
      visibleColumnsList.map((col) => {
        const value = item[col.key]
        const rendered = col.render ? col.render(value, item) : value
        return typeof rendered === 'string' ? rendered : String(rendered ?? '')
      }).join('\t')
    ).join('\n')
    const tsv = `${headers}\n${rows}`
    const timestamp = new Date().toISOString().split('T')[0]
    download(tsv, { filename: `${exportFilename}_${timestamp}.xls`, mimeType: 'application/vnd.ms-excel' })
  }, [filteredData, visibleColumnsList, exportFilename, download])

  const exportToPDF = useCallback(() => {
    const headers = ['#', ...visibleColumnsList.map((c) => c.label)]
    const rows = filteredData.map((item, idx) => [
      String(idx + 1),
      ...visibleColumnsList.map((col) => {
        const value = item[col.key]
        const rendered = col.render ? col.render(value, item) : value
        return typeof rendered === 'string' ? rendered : String(rendered ?? '')
      }),
    ])

    let csv = headers.join(',') + '\n'
    csv += rows.map((row) => row.map((cell) => {
      const cellStr = String(cell)
      return cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')
        ? `"${cellStr.replace(/"/g, '""')}"`
        : cellStr
    }).join(',')).join('\n')

    const timestamp = new Date().toISOString().split('T')[0]
    download(csv, { filename: `${exportFilename}_${timestamp}.csv`, mimeType: 'text/csv' })
  }, [filteredData, visibleColumnsList, exportFilename, download])

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
      {(title || searchable || showColumnToggle || showDensityToggle || showExport) && (
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              {title && <CardTitle>{title}</CardTitle>}
              {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
            </div>
            <div className="flex items-center gap-2 flex-wrap">
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
              {showExport && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      <Download className="w-4 h-4 mr-2" />
                      Export
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={copyToClipboard}>
                      <Copy className="w-4 h-4 mr-2" />
                      Copy to Clipboard
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={exportToCSV}>
                      <FileText className="w-4 h-4 mr-2" />
                      Export as CSV
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={exportToExcel}>
                      <FileSpreadsheet className="w-4 h-4 mr-2" />
                      Export as Excel
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={exportToJSON}>
                      <FileJson className="w-4 h-4 mr-2" />
                      Export as JSON
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={exportToPDF}>
                      <File className="w-4 h-4 mr-2" />
                      Export as PDF
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
              {showDensityToggle && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      {density === 'compact' ? (
                        <Minimize2 className="w-4 h-4 mr-2" />
                      ) : density === 'spacious' ? (
                        <Maximize2 className="w-4 h-4 mr-2" />
                      ) : (
                        <Rows className="w-4 h-4 mr-2" />
                      )}
                      {density === 'compact' ? 'Compact' : density === 'spacious' ? 'Spacious' : 'Normal'}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuCheckboxItem
                      checked={density === 'compact'}
                      onCheckedChange={() => setDensity('compact')}
                    >
                      Compact
                    </DropdownMenuCheckboxItem>
                    <DropdownMenuCheckboxItem
                      checked={density === 'normal'}
                      onCheckedChange={() => setDensity('normal')}
                    >
                      Normal
                    </DropdownMenuCheckboxItem>
                    <DropdownMenuCheckboxItem
                      checked={density === 'spacious'}
                      onCheckedChange={() => setDensity('spacious')}
                    >
                      Spacious
                    </DropdownMenuCheckboxItem>
                  </DropdownMenuContent>
                </DropdownMenu>
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
          <table className="w-full" ref={tableRef}>
            <thead>
              <tr className="border-b text-left text-sm text-muted-foreground">
                {showRowNumbers && (
                  <th className="pb-3 font-medium w-12">#</th>
                )}
                {frozenColumns > 0 && frozenColumnsList.map((column) => (
                  <th
                    key={String(column.key)}
                    className={cn('pb-3 font-medium sticky left-0 bg-background z-10', column.headerClassName)}
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
                {scrollableColumnsList.map((column) => (
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
                  {showRowNumbers && (
                    <td className={cn('py-3 text-muted-foreground text-center w-12', densityClasses[density])}>
                      {currentPage * pageSize + index + 1}
                    </td>
                  )}
                  {frozenColumns > 0 && frozenColumnsList.map((column) => (
                    <td
                      key={String(column.key)}
                      className={cn('py-3 sticky left-0 bg-background z-10', densityClasses[density], column.className)}
                    >
                      {column.render
                        ? column.render(item[column.key], item)
                        : String(item[column.key] ?? '')}
                    </td>
                  ))}
                  {scrollableColumnsList.map((column) => (
                    <td key={String(column.key)} className={cn(densityClasses[density], column.className)}>
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
