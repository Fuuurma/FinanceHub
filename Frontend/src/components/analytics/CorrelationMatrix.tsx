'use client'

import { useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { Copy, Download, FileJson, FileSpreadsheet, Maximize2, Minimize2, RefreshCw } from 'lucide-react'
import type { CorrelationMatrix } from '@/lib/types/portfolio-analytics'
import { cn } from '@/lib/utils'

interface CorrelationMatrixProps {
  data?: CorrelationMatrix | null
  loading?: boolean
  title?: string
  className?: string
}

const TIMEFRAMES = [
  { value: '1m', label: '1 Month' },
  { value: '3m', label: '3 Months' },
  { value: '6m', label: '6 Months' },
  { value: '1y', label: '1 Year' },
  { value: 'all', label: 'All Time' },
]

const getCorrelationColor = (value: number): string => {
  if (value >= 0.8) return 'bg-green-700 text-white'
  if (value >= 0.6) return 'bg-green-500 text-white'
  if (value >= 0.4) return 'bg-green-300 text-green-950'
  if (value >= 0.2) return 'bg-green-100 text-green-900'
  if (value >= 0) return 'bg-gray-100 text-gray-900'
  if (value >= -0.2) return 'bg-red-100 text-red-900'
  if (value >= -0.4) return 'bg-red-300 text-red-950'
  if (value >= -0.6) return 'bg-red-500 text-white'
  if (value >= -0.8) return 'bg-red-700 text-white'
  return 'bg-red-800 text-white'
}

const getCorrelationLabel = (value: number): string => {
  if (value >= 0.8) return 'Very Strong Positive'
  if (value >= 0.6) return 'Strong Positive'
  if (value >= 0.4) return 'Moderate Positive'
  if (value >= 0.2) return 'Weak Positive'
  if (value >= 0) return 'Very Weak / None'
  if (value >= -0.2) return 'Very Weak Negative'
  if (value >= -0.4) return 'Weak Negative'
  if (value >= -0.6) return 'Moderate Negative'
  if (value >= -0.8) return 'Strong Negative'
  return 'Very Strong Negative'
}

const formatCorrelation = (value: number): string => {
  return value.toFixed(2)
}

export function CorrelationMatrix({
  data,
  loading = false,
  title = 'Correlation Matrix',
  className,
}: CorrelationMatrixProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [selectedTimeframe, setSelectedTimeframe] = useState('1m')

  const handleCopy = useCallback(() => {
    if (!data) return
    const text = data.labels.map((label, i) =>
      data.labels.map((col, j) => `${label}-${col}: ${formatCorrelation(data.matrix[i][j])}`).join('\t')
    ).join('\n')
    navigator.clipboard.writeText(text)
  }, [data])

  const exportToCSV = useCallback(() => {
    if (!data) return
    const headers = ['', ...data.labels].join(',')
    const rows = data.labels.map((label, i) =>
      [label, ...data.matrix[i].map(formatCorrelation)].join(',')
    ).join('\n')
    const csv = `${headers}\n${rows}`
    downloadFile(csv, 'correlation-matrix.csv', 'text/csv')
  }, [data])

  const exportToJSON = useCallback(() => {
    if (!data) return
    const jsonData = {
      labels: data.labels,
      matrix: data.matrix,
      timeframe: selectedTimeframe,
      exportedAt: new Date().toISOString(),
    }
    downloadFile(JSON.stringify(jsonData, null, 2), 'correlation-matrix.json', 'application/json')
  }, [data, selectedTimeframe])

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <Skeleton className="h-64 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!data || !data.labels.length || !data.matrix.length) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            No correlation data available
          </div>
        </CardContent>
      </Card>
    )
  }

  const maxValue = Math.max(...data.matrix.flat().map(Math.abs))

  return (
    <Card className={cn('w-full', isFullscreen && 'fixed inset-0 z-50 overflow-auto bg-background p-6', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <CardTitle>{title}</CardTitle>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  {TIMEFRAMES.find(t => t.value === selectedTimeframe)?.label || 'Timeframe'}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {TIMEFRAMES.map((tf) => (
                  <DropdownMenuItem
                    key={tf.value}
                    onClick={() => setSelectedTimeframe(tf.value)}
                  >
                    {tf.label}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleCopy}>
              <Copy className="w-4 h-4 mr-1" />
              Copy
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-1" />
                  Export
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={exportToCSV}>
                  <FileSpreadsheet className="w-4 h-4 mr-2" />
                  Export as CSV
                </DropdownMenuItem>
                <DropdownMenuItem onClick={exportToJSON}>
                  <FileJson className="w-4 h-4 mr-2" />
                  Export as JSON
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button variant="outline" size="sm" onClick={() => setIsFullscreen(!isFullscreen)}>
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <TooltipProvider>
          <div className="overflow-auto">
            <div
              className="inline-block min-w-full"
              style={{
                gridTemplateColumns: `auto.length}, minmax(60 repeat(${data.labelspx, 1fr))`,
              }}
            >
              <div className="flex items-center justify-center p-2 font-medium text-sm text-muted-foreground">
                -
              </div>
              {data.labels.map((label, i) => (
                <div
                  key={i}
                  className="flex items-center justify-center p-2 font-medium text-sm truncate"
                  style={{ minWidth: '60px' }}
                  title={label}
                >
                  {label.length > 6 ? label.substring(0, 6) + '...' : label}
                </div>
              ))}

              {data.labels.map((rowLabel, i) => (
                <>
                  <div
                    key={`row-${i}`}
                    className="flex items-center justify-end pr-3 py-2 font-medium text-sm truncate"
                    title={rowLabel}
                  >
                    {rowLabel.length > 6 ? rowLabel.substring(0, 6) + '...' : rowLabel}
                  </div>
                  {data.labels.map((colLabel, j) => {
                    const value = data.matrix[i][j]
                    const colorIntensity = Math.abs(value) / maxValue
                    const bgOpacity = colorIntensity * 0.8 + 0.1
                    const isPositive = value >= 0
                    const bgColor = isPositive
                      ? `rgba(34, 197, 94, ${bgOpacity})`
                      : `rgba(239, 68, 68, ${bgOpacity})`
                    const textColor = colorIntensity > 0.5 ? 'white' : 'inherit'

                    return (
                      <Tooltip key={`${i}-${j}`}>
                        <TooltipTrigger asChild>
                          <div
                            className="flex items-center justify-center p-2 text-sm font-medium cursor-help transition-all hover:scale-105"
                            style={{
                              backgroundColor: bgColor,
                              color: textColor,
                              minWidth: '60px',
                              minHeight: '40px',
                            }}
                          >
                            {formatCorrelation(value)}
                          </div>
                        </TooltipTrigger>
                        <TooltipContent>
                          <div className="text-center">
                            <p className="font-medium">{rowLabel} / {colLabel}</p>
                            <p className="text-lg font-bold">{formatCorrelation(value)}</p>
                            <p className="text-xs text-muted-foreground">
                              {getCorrelationLabel(value)}
                            </p>
                          </div>
                        </TooltipContent>
                      </Tooltip>
                    )
                  })}
                </>
              ))}
            </div>
          </div>

          <div className="mt-4 flex items-center justify-center gap-4">
            <span className="text-sm text-muted-foreground">Legend:</span>
            <div className="flex items-center gap-1">
              <div className="w-6 h-4 bg-red-800 rounded" />
              <span className="text-xs">-1.0</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-6 h-4 bg-red-500 rounded" />
              <span className="text-xs">-0.6</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-6 h-4 bg-gray-200 rounded" />
              <span className="text-xs">0.0</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-6 h-4 bg-green-500 rounded" />
              <span className="text-xs">+0.6</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-6 h-4 bg-green-700 rounded" />
              <span className="text-xs">+1.0</span>
            </div>
          </div>
        </TooltipProvider>
      </CardContent>
    </Card>
  )
}

export default CorrelationMatrix
