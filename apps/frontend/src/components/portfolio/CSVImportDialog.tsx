'use client'

import React, { useState, useCallback } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Progress } from '@/components/ui/progress'
import { AlertCircle, CheckCircle2, Upload, Download, FileText, RefreshCw } from 'lucide-react'

interface CSVImportDialogProps {
  open: boolean
  onClose: () => void
  portfolioId: string
  onImportComplete: () => void
}

type ImportStep = 'upload' | 'preview' | 'importing' | 'success' | 'error'

interface PreviewData {
  valid_count: number
  error_count: number
  rows: ParsedRow[]
  errors: ParseError[]
}

interface ParsedRow {
  transaction_date: string
  asset_symbol: string
  transaction_type: string
  quantity: number
  price_per_share: number
  total_value: number
  notes?: string
  commission?: number
}

interface ParseError {
  row: number
  message: string
}

const IMPORT_FORMATS = [
  { id: 'generic', name: 'Generic Format', description: 'Standard format with date, symbol, type, quantity, price' },
  { id: 'schwab', name: 'Charles Schwab', description: ' Schwab brokerage export format' },
  { id: 'fidelity', name: 'Fidelity', description: 'Fidelity brokerage export format' },
  { id: 'etrade', name: 'E*TRADE', description: 'E*TRADE brokerage export format' },
  { id: 'robinhood', name: 'Robinhood', description: 'Robinhood app export format' },
  { id: 'vanguard', name: 'Vanguard', description: 'Vanguard brokerage export format' },
  { id: 'interactive_brokers', name: 'Interactive Brokers', description: 'IBKR export format' },
]

export const CSVImportDialog: React.FC<CSVImportDialogProps> = ({
  open,
  onClose,
  portfolioId,
  onImportComplete
}) => {
  const [step, setStep] = useState<ImportStep>('upload')
  const [format, setFormat] = useState('generic')
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<PreviewData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [importProgress, setImportProgress] = useState(0)
  const [importMessage, setImportMessage] = useState('')

  const handleDownloadTemplate = useCallback(async () => {
    try {
      const response = await fetch(`/api/import/template/${format}`)
      if (!response.ok) throw new Error('Failed to download template')
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `portfolio_import_${format}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download template')
    }
  }, [format])

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0]
    if (selected) {
      if (selected.type === 'text/csv' || selected.name.endsWith('.csv')) {
        setFile(selected)
        setError(null)
      } else {
        setError('Please select a CSV file')
      }
    }
  }, [])

  const handlePreview = useCallback(async () => {
    if (!file) return

    setStep('importing')
    setError(null)
    setImportProgress(10)

    const formData = new FormData()
    formData.append('csv_file', file)
    formData.append('format', format)
    formData.append('portfolio_id', portfolioId)

    try {
      setImportProgress(30)
      const response = await fetch('/api/import/preview', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Preview failed')
      }

      const data = await response.json()
      setPreview(data)
      setImportProgress(100)

      if (data.error_count > 0 && data.valid_count === 0) {
        setStep('error')
        setError(`All rows have errors. Please fix your CSV file.`)
      } else {
        setStep('preview')
      }
    } catch (err) {
      setStep('error')
      setError(err instanceof Error ? err.message : 'Preview failed')
    }
  }, [file, format, portfolioId])

  const handleConfirmImport = useCallback(async () => {
    if (!file) return

    setStep('importing')
    setError(null)
    setImportProgress(10)
    setImportMessage('Parsing CSV file...')

    const formData = new FormData()
    formData.append('csv_file', file)
    formData.append('format', format)
    formData.append('portfolio_id', portfolioId)

    try {
      setImportProgress(30)
      const response = await fetch('/api/import/confirm', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Import failed')
      }

      const data = await response.json()
      setImportProgress(100)
      setImportMessage(data.message)

      if (data.success) {
        setStep('success')
        setTimeout(() => {
          onImportComplete()
          onClose()
          resetDialog()
        }, 3000)
      } else {
        setStep('error')
        setError(data.message || 'Import failed')
      }
    } catch (err) {
      setStep('error')
      setError(err instanceof Error ? err.message : 'Import failed')
    }
  }, [file, format, portfolioId, onImportComplete, onClose])

  const resetDialog = useCallback(() => {
    setStep('upload')
    setFile(null)
    setPreview(null)
    setError(null)
    setImportProgress(0)
    setImportMessage('')
  }, [])

  const handleClose = useCallback(() => {
    resetDialog()
    onClose()
  }, [onClose, resetDialog])

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString()
    } catch {
      return dateStr
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-5xl max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Import Transactions from CSV
          </DialogTitle>
        </DialogHeader>

        {step === 'upload' && (
          <div className="space-y-6 overflow-y-auto flex-1 pr-2">
            <div className="bg-muted/50 rounded-lg p-4">
              <h4 className="font-medium mb-2">Supported Formats</h4>
              <div className="grid grid-cols-2 gap-2">
                {IMPORT_FORMATS.map((fmt) => (
                  <div
                    key={fmt.id}
                    className={`text-sm p-2 rounded cursor-pointer transition-colors ${
                      format === fmt.id
                        ? 'bg-primary/10 text-primary border border-primary/20'
                        : 'hover:bg-muted'
                    }`}
                    onClick={() => setFormat(fmt.id)}
                  >
                    <div className="font-medium">{fmt.name}</div>
                    <div className="text-muted-foreground text-xs">{fmt.description}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <Button variant="outline" onClick={handleDownloadTemplate} className="flex-1">
                <Download className="mr-2 h-4 w-4" />
                Download Template
              </Button>
            </div>

            <div>
              <Label htmlFor="csv-file">Upload CSV File</Label>
              <Input
                id="csv-file"
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="mt-1"
              />
              {file && (
                <p className="text-sm text-muted-foreground mt-2 flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Selected: {file.name} ({formatBytes(file.size)})
                </p>
              )}
            </div>

            {error && (
              <div className="flex items-center gap-2 text-destructive bg-destructive/10 p-3 rounded-lg">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            )}

            <DialogFooter>
              <Button variant="ghost" onClick={handleClose}>Cancel</Button>
              <Button
                onClick={handlePreview}
                disabled={!file}
              >
                <Upload className="mr-2 h-4 w-4" />
                Preview Import
              </Button>
            </DialogFooter>
          </div>
        )}

        {step === 'preview' && preview && (
          <div className="space-y-4 overflow-y-auto flex-1 pr-2">
            <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                <span className="font-medium">{preview.valid_count} valid transactions</span>
              </div>
              {preview.error_count > 0 && (
                <div className="flex items-center gap-2 text-destructive">
                  <AlertCircle className="h-5 w-5" />
                  <span className="font-medium">{preview.error_count} errors</span>
                </div>
              )}
            </div>

            {preview.errors.length > 0 && (
              <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Errors Found
                </h4>
                <div className="max-h-32 overflow-y-auto space-y-1">
                  {preview.errors.slice(0, 10).map((err, i) => (
                    <div key={i} className="text-sm text-destructive">
                      Row {err.row}: {err.message}
                    </div>
                  ))}
                  {preview.errors.length > 10 && (
                    <div className="text-sm text-muted-foreground">
                      ...and {preview.errors.length - 10} more errors
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="border rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="whitespace-nowrap">Date</TableHead>
                      <TableHead className="whitespace-nowrap">Symbol</TableHead>
                      <TableHead className="whitespace-nowrap">Type</TableHead>
                      <TableHead className="whitespace-nowrap text-right">Qty</TableHead>
                      <TableHead className="whitespace-nowrap text-right">Price</TableHead>
                      <TableHead className="whitespace-nowrap text-right">Total</TableHead>
                      <TableHead className="whitespace-nowrap">Notes</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {preview.rows.slice(0, 50).map((row, i) => (
                      <TableRow key={i}>
                        <TableCell className="whitespace-nowrap">{formatDate(row.transaction_date)}</TableCell>
                        <TableCell className="font-medium">{row.asset_symbol}</TableCell>
                        <TableCell>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            row.transaction_type === 'buy' ? 'bg-green-100 text-green-700' :
                            row.transaction_type === 'sell' ? 'bg-red-100 text-red-700' :
                            row.transaction_type === 'dividend' ? 'bg-blue-100 text-blue-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {row.transaction_type}
                          </span>
                        </TableCell>
                        <TableCell className="text-right">{row.quantity}</TableCell>
                        <TableCell className="text-right">{formatCurrency(row.price_per_share)}</TableCell>
                        <TableCell className="text-right font-medium">{formatCurrency(row.total_value)}</TableCell>
                        <TableCell className="max-w-xs truncate">{row.notes || '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              {preview.rows.length > 50 && (
                <div className="text-center text-sm text-muted-foreground p-2">
                  Showing 50 of {preview.rows.length} transactions
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="ghost" onClick={() => setStep('upload')}>
                Back
              </Button>
              <Button
                onClick={handleConfirmImport}
                disabled={preview.valid_count === 0}
              >
                <Upload className="mr-2 h-4 w-4" />
                Import {preview.valid_count} Transactions
              </Button>
            </DialogFooter>
          </div>
        )}

        {step === 'importing' && (
          <div className="space-y-6 py-12">
            <div className="text-center">
              <RefreshCw className="h-12 w-12 mx-auto animate-spin text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">Importing Transactions</h3>
              <p className="text-muted-foreground">{importMessage}</p>
            </div>
            <Progress value={importProgress} className="max-w-md mx-auto" />
          </div>
        )}

        {step === 'success' && (
          <div className="text-center py-12">
            <CheckCircle2 className="h-16 w-16 mx-auto text-green-500 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Import Successful!</h3>
            <p className="text-muted-foreground mb-4">{importMessage}</p>
            <p className="text-sm text-muted-foreground">Redirecting to portfolio...</p>
          </div>
        )}

        {step === 'error' && (
          <div className="space-y-4 py-8">
            <div className="flex items-center justify-center gap-2 text-destructive">
              <AlertCircle className="h-8 w-8" />
              <span className="text-lg font-medium">Import Failed</span>
            </div>
            <p className="text-center text-muted-foreground">{error}</p>
            <div className="flex justify-center gap-3">
              <Button variant="outline" onClick={() => setStep('upload')}>
                Try Again
              </Button>
              <Button variant="ghost" onClick={handleClose}>Cancel</Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export default CSVImportDialog
