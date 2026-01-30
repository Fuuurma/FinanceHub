'use client'

import { useState, useCallback } from 'react'
import { Download, FileSpreadsheet, FileJson, FileText, ChevronDown, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

export type ExportFormat = 'csv' | 'json' | 'xlsx' | 'txt'

export interface ExportOption {
  format: ExportFormat
  label: string
  icon: React.ElementType
  mimeType: string
  extension: string
}

export const EXPORT_OPTIONS: ExportOption[] = [
  { format: 'csv', label: 'CSV', icon: FileSpreadsheet, mimeType: 'text/csv', extension: 'csv' },
  { format: 'json', label: 'JSON', icon: FileJson, mimeType: 'application/json', extension: 'json' },
  { format: 'xlsx', label: 'Excel', icon: FileSpreadsheet, mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', extension: 'xlsx' },
  { format: 'txt', label: 'Text', icon: FileText, mimeType: 'text/plain', extension: 'txt' }
]

interface DataExportButtonProps {
  data: unknown[] | object
  filename?: string
  disabled?: boolean
  loading?: boolean
  onExport?: (format: ExportFormat) => void
  className?: string
  buttonLabel?: string
  showLabels?: boolean
  maxRows?: number
}

function convertToCSV(data: unknown[]): string {
  if (data.length === 0) return ''

  const headers = Object.keys(data[0] as object)
  const rows = data.map(row =>
    headers.map(header => {
      const value = (row as Record<string, unknown>)[header]
      const stringValue = String(value ?? '')
      const escaped = stringValue.replace(/"/g, '""')
      return `"${escaped}"`
    }).join(',')
  )
  return [headers.join(','), ...rows].join('\n')
}

function convertToText(data: unknown[]): string {
  if (data.length === 0) return ''

  const headers = Object.keys(data[0] as object)
  const maxWidths = headers.map((h, i) => {
    const colWidth = Math.max(
      h.length,
      ...data.map(row => String((row as Record<string, unknown>)[h] ?? '').length)
    )
    return colWidth
  })

  const formatRow = (row: object) =>
    headers.map((h, i) => String((row as Record<string, unknown>)[h] ?? '').padEnd(maxWidths[i])).join('  ')

  const separator = maxWidths.map(w => '-'.repeat(w)).join('  ')

  return [formatRow({} as object), separator, ...data.map(formatRow)].join('\n')
}

function downloadFile(content: string | Blob, filename: string, mimeType: string) {
  const blob = typeof content === 'string' ? new Blob([content], { type: mimeType }) : content
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function DataExportButton({
  data,
  filename = 'export',
  disabled = false,
  loading = false,
  onExport,
  className,
  buttonLabel = 'Export',
  showLabels = true,
  maxRows
}: DataExportButtonProps) {
  const [exporting, setExporting] = useState<ExportFormat | null>(null)

  const handleExport = useCallback(async (format: ExportFormat) => {
    if (loading || disabled) return

    setExporting(format)
    try {
      const exportData = maxRows ? (Array.isArray(data) ? data.slice(0, maxRows) : data) : data
      let content: string | Blob
      const option = EXPORT_OPTIONS.find(o => o.format === format)!

      switch (format) {
        case 'csv':
          content = convertToCSV(exportData as unknown[])
          break
        case 'json':
          content = JSON.stringify(exportData, null, 2)
          break
        case 'txt':
          content = convertToText(exportData as unknown[])
          break
        case 'xlsx':
          content = new Blob([exportData as BlobPart], { type: option.mimeType })
          break
        default:
          content = JSON.stringify(exportData)
      }

      const finalFilename = filename.endsWith(`.${option.extension}`)
        ? filename
        : `${filename}.${option.extension}`

      downloadFile(content, finalFilename, option.mimeType)
      onExport?.(format)
    } finally {
      setExporting(null)
    }
  }, [data, filename, disabled, loading, maxRows, onExport])

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button disabled={disabled || loading} className={cn('gap-2', className)}>
          {loading || exporting ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Download className="h-4 w-4" />
          )}
          {showLabels && buttonLabel}
          <ChevronDown className="h-4 w-4 ml-1" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {EXPORT_OPTIONS.map((option, index) => (
          <DropdownMenuItem
            key={option.format}
            onClick={() => handleExport(option.format)}
            disabled={exporting !== null}
            className="gap-2"
          >
            {exporting === option.format ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <option.icon className="h-4 w-4" />
            )}
            {option.label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default DataExportButton
