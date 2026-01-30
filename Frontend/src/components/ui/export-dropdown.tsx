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
import { Download, FileJson, FileSpreadsheet, FileText, Copy, Check, Loader2, FileSpreadsheetIcon } from 'lucide-react'
import * as XLSX from 'xlsx'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { useDownloadFile } from '@/hooks/useDownload'

export type ExportFormat = 'csv' | 'json' | 'xlsx' | 'pdf' | 'clipboard'

export interface ExportOptions {
  filename?: string
  datePrefix?: boolean
  includeMetadata?: boolean
  sheetName?: string
  title?: string
  columns?: string[]
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
  const [copied, setCopied] = useState(false)

  const {
    filename = 'export',
    datePrefix = true,
    includeMetadata = false,
    sheetName = 'Data',
    title,
  } = options

  const { downloadCSV, downloadJSON, downloadExcel, downloadText } = useDownloadFile()

  const getFilename = useCallback((format: ExportFormat, ext: string) => {
    const date = new Date().toISOString().split('T')[0]
    const base = datePrefix ? `${filename}-${date}` : filename
    return `${base}.${ext}`
  }, [filename, datePrefix])

  const getHeaders = useCallback(() => {
    return columns || (data.length > 0 ? Object.keys(data[0]) : [])
  }, [columns, data])

  const formatCellValue = useCallback((value: any): string => {
    if (value === null || value === undefined) return ''
    if (typeof value === 'object') {
      if (value instanceof Date) return value.toISOString()
      return JSON.stringify(value)
    }
    return String(value)
  }, [])

  const exportToCSV = useCallback(() => {
    setExporting('csv')
    try {
      const headers = getHeaders()
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
      const exportFilename = getFilename('csv', 'csv')
      onExport?.('csv', blob, exportFilename)

      downloadCSV(csvContent, exportFilename)
    } finally {
      setExporting(null)
    }
  }, [data, getHeaders, getFilename, onExport, downloadCSV])

  const exportToJSON = useCallback(() => {
    setExporting('json')
    try {
      const exportData = includeMetadata
        ? {
            metadata: {
              exportedAt: new Date().toISOString(),
              totalRecords: data.length,
              columns: getHeaders(),
            },
            data,
          }
        : data

      const jsonContent = JSON.stringify(exportData, null, 2)
      const exportFilename = getFilename('json', 'json')
      const blob = new Blob([jsonContent], { type: 'application/json' })
      onExport?.('json', blob, exportFilename)

      downloadJSON(exportData, exportFilename)
    } finally {
      setExporting(null)
    }
  }, [data, getHeaders, includeMetadata, getFilename, onExport, downloadJSON])

  const exportToExcel = useCallback(() => {
    setExporting('xlsx')
    try {
      const headers = getHeaders()
      const worksheetData = [
        headers,
        ...data.map((row) => headers.map((header) => formatCellValue(row[header]))),
      ]

      const worksheet = XLSX.utils.aoa_to_sheet(worksheetData)

      const workbook = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)

      if (title) {
        worksheet['!title'] = { t: title, font: { bold: true, sz: 16 } }
      }

      const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const exportFilename = getFilename('xlsx', 'xlsx')
      onExport?.('xlsx', blob, exportFilename)

      downloadExcel(blob, exportFilename)
    } finally {
      setExporting(null)
    }
  }, [data, getHeaders, getFilename, sheetName, title, formatCellValue, onExport, downloadExcel])

  const exportToPDF = useCallback(() => {
    setExporting('pdf')
    try {
      const headers = getHeaders()
      const pdf = new jsPDF({
        orientation: headers.length > 10 ? 'l' : 'p',
        unit: 'mm',
        format: 'a4',
      })

      if (title) {
        pdf.setFontSize(18)
        pdf.text(title, 14, 15)
      }

      const tableData = data.map((row) => headers.map((header) => formatCellValue(row[header])))

      autoTable(pdf, {
        head: [headers],
        body: tableData,
        startY: title ? 25 : 15,
        styles: {
          fontSize: 8,
          cellPadding: 2,
        },
        headStyles: {
          fillColor: [0, 0, 0],
          textColor: [255, 255, 255],
          fontStyle: 'bold',
        },
        alternateRowStyles: {
          fillColor: [245, 245, 245],
        },
        margin: { top: 15, left: 14, right: 14 },
        didDrawPage: (data) => {
          pdf.setFontSize(10)
          pdf.text(
            `Generated: ${new Date().toLocaleString()}`,
            data.settings.margin.left,
            pdf.internal.pageSize.height - 10
          )
        },
      })

      const pdfBlob = pdf.output('blob')
      const exportFilename = getFilename('pdf', 'pdf')
      onExport?.('pdf', pdfBlob, exportFilename)

      pdf.save(exportFilename)
    } finally {
      setExporting(null)
    }
  }, [data, getHeaders, getFilename, title, formatCellValue, onExport])

  const copyToClipboard = useCallback(async () => {
    setExporting('clipboard')
    try {
      const headers = getHeaders()
      const textContent = [
        headers.join('\t'),
        ...data.map((row) =>
          headers.map((header) => formatCellValue(row[header])).join('\t')
        ),
      ].join('\n')

      await navigator.clipboard.writeText(textContent)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    } finally {
      setExporting(null)
    }
  }, [data, getHeaders, formatCellValue])

  const isExporting = exporting !== null

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" disabled={disabled || data.length === 0}>
          {isExporting ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Download className="w-4 h-4 mr-2" />
          )}
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {children}
        <DropdownMenuItem onClick={exportToCSV} disabled={isExporting}>
          <FileSpreadsheetIcon className="w-4 h-4 mr-2" />
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportToExcel} disabled={isExporting}>
          <FileSpreadsheet className="w-4 h-4 mr-2" />
          Export as Excel
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportToPDF} disabled={isExporting}>
          <FileText className="w-4 h-4 mr-2" />
          Export as PDF
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportToJSON} disabled={isExporting}>
          <FileJson className="w-4 h-4 mr-2" />
          Export as JSON
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={copyToClipboard} disabled={isExporting}>
          {copied ? (
            <Check className="w-4 h-4 mr-2 text-green-500" />
          ) : (
            <Copy className="w-4 h-4 mr-2" />
          )}
          {copied ? 'Copied!' : 'Copy to Clipboard'}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export function useExport<T extends Record<string, any>>() {
  const { downloadCSV, downloadJSON, downloadExcel, downloadText } = useDownloadFile()

  const formatCellValue = useCallback((value: any): string => {
    if (value === null || value === undefined) return ''
    if (typeof value === 'object') {
      if (value instanceof Date) return value.toISOString()
      return JSON.stringify(value)
    }
    return String(value)
  }, [])

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

    const exportFilename = `${filename}-${new Date().toISOString().split('T')[0]}.csv`
    downloadCSV(csvContent, exportFilename)
  }, [downloadCSV])

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

    const exportFilename = `${filename}-${new Date().toISOString().split('T')[0]}.json`
    downloadJSON(exportData, exportFilename)
  }, [downloadJSON])

  const exportToExcel = useCallback((data: T[], filename: string, sheetName = 'Data') => {
    if (data.length === 0) return

    const headers = Object.keys(data[0])
    const worksheetData = [
      headers,
      ...data.map((row) => headers.map((header) => formatCellValue(row[header]))),
    ]

    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)

    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const exportFilename = `${filename}-${new Date().toISOString().split('T')[0]}.xlsx`
    downloadExcel(blob, exportFilename)
  }, [formatCellValue, downloadExcel])

  const exportToPDF = useCallback((data: T[], filename: string, title?: string) => {
    if (data.length === 0) return

    const headers = Object.keys(data[0])
    const pdf = new jsPDF({
      orientation: headers.length > 10 ? 'l' : 'p',
      unit: 'mm',
      format: 'a4',
    })

    if (title) {
      pdf.setFontSize(18)
      pdf.text(title, 14, 15)
    }

    const tableData = data.map((row) => headers.map((header) => formatCellValue(row[header])))

    autoTable(pdf, {
      head: [headers],
      body: tableData,
      startY: title ? 25 : 15,
      styles: {
        fontSize: 8,
        cellPadding: 2,
      },
      headStyles: {
        fillColor: [0, 0, 0],
        textColor: [255, 255, 255],
        fontStyle: 'bold',
      },
      alternateRowStyles: {
        fillColor: [245, 245, 245],
      },
      margin: { top: 15, left: 14, right: 14 },
      didDrawPage: (data) => {
        pdf.setFontSize(10)
        pdf.text(
          `Generated: ${new Date().toLocaleString()}`,
          data.settings.margin.left,
          pdf.internal.pageSize.height - 10
        )
      },
    })

    pdf.save(`${filename}-${new Date().toISOString().split('T')[0]}.pdf`)
  }, [formatCellValue])

  const copyToClipboard = useCallback(async (data: T[]) => {
    if (data.length === 0) return

    const headers = Object.keys(data[0])
    const textContent = [
      headers.join('\t'),
      ...data.map((row) =>
        headers.map((header) => formatCellValue(row[header])).join('\t')
      ),
    ].join('\n')

    await navigator.clipboard.writeText(textContent)
  }, [formatCellValue])

  return { exportToCSV, exportToJSON, exportToExcel, exportToPDF, copyToClipboard }
}
