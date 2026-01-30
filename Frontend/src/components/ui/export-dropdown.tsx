'use client'

import { useCallback, useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Download, FileJson, FileSpreadsheet, Loader2 } from 'lucide-react'

export type ExportFormat = 'csv' | 'json'

export interface ExportOptions {
  filename?: string
  datePrefix?: boolean
  includeMetadata?: boolean
}

interface ExportDropdownProps {
  data: Record<string, any>[]
  columns?: string[]
  options?: ExportOptions
  children?: React.ReactNode
  disabled?: boolean
  onExport?: (format: ExportFormat, blob: Blob, filename: string) => void
}

export function ExportDropdown({
  data,
  columns,
  options = {},
  children,
  disabled = false,
  onExport,
}: ExportDropdownProps) {
  const [exporting, setExporting] = useState<ExportFormat | null>(null)

  const {
    filename = 'export',
    datePrefix = true,
    includeMetadata = false,
  } = options

  const getFilename = useCallback((format: ExportFormat) => {
    const date = new Date().toISOString().split('T')[0]
    const base = datePrefix ? `${filename}-${date}` : filename
    return `${base}.${format}`
  }, [filename, datePrefix])

  const exportToCSV = useCallback(() => {
    setExporting('csv')
    try {
      const headers = columns || (data.length > 0 ? Object.keys(data[0]) : [])
      const csvContent = [
        headers.join(','),
        ...data.map((row) =>
          headers.map((header) => {
            const value = row[header]
            if (value === null || value === undefined) return ''
            if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
              return `"${value.replace(/"/g, '""')}"`
            }
            return String(value)
          }).join(',')
        ),
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const exportFilename = getFilename('csv')
      onExport?.('csv', blob, exportFilename)

      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = exportFilename
      link.click()
      URL.revokeObjectURL(link.href)
    } finally {
      setExporting(null)
    }
  }, [data, columns, getFilename, onExport])

  const exportToJSON = useCallback(() => {
    setExporting('json')
    try {
      const exportData = includeMetadata
        ? {
            metadata: {
              exportedAt: new Date().toISOString(),
              totalRecords: data.length,
              columns: columns || (data.length > 0 ? Object.keys(data[0]) : []),
            },
            data,
          }
        : data

      const jsonContent = JSON.stringify(exportData, null, 2)
      const blob = new Blob([jsonContent], { type: 'application/json' })
      const exportFilename = getFilename('json')
      onExport?.('json', blob, exportFilename)

      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = exportFilename
      link.click()
      URL.revokeObjectURL(link.href)
    } finally {
      setExporting(null)
    }
  }, [data, columns, includeMetadata, getFilename, onExport])

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" disabled={disabled || data.length === 0}>
          {exporting ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Download className="w-4 h-4 mr-2" />
          )}
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {children}
        <DropdownMenuItem onClick={exportToCSV} disabled={exporting !== null}>
          <FileSpreadsheet className="w-4 h-4 mr-2" />
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportToJSON} disabled={exporting !== null}>
          <FileJson className="w-4 h-4 mr-2" />
          Export as JSON
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export function useExport<T extends Record<string, any>>() {
  const exportToCSV = useCallback((data: T[], filename: string) => {
    if (data.length === 0) return

    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map((row) =>
        headers.map((header) => {
          const value = row[header]
          if (value === null || value === undefined) return ''
          if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
            return `"${value.replace(/"/g, '""')}"`
          }
          return String(value)
        }).join(',')
      ),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${filename}-${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    URL.revokeObjectURL(link.href)
  }, [])

  const exportToJSON = useCallback((data: T[], filename: string, includeMetadata = false) => {
    if (data.length === 0) return

    const exportData = includeMetadata
      ? {
          metadata: {
            exportedAt: new Date().toISOString(),
            totalRecords: data.length,
          },
          data,
        }
      : data

    const jsonContent = JSON.stringify(exportData, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${filename}-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(link.href)
  }, [])

  return { exportToCSV, exportToJSON }
}
