'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Calendar,
  Download,
  FileSpreadsheet,
  FileJson,
  FileText,
  Clock,
  TrendingUp,
  Database,
  RefreshCw,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useDownloadFile } from '@/hooks/useDownload'
import { formatDate, subDays, subMonths, subYears } from 'date-fns'

interface HistoricalDataExportProps {
  symbol?: string
  className?: string
}

interface ExportConfig {
  symbol: string
  startDate: string
  endDate: string
  interval: '1d' | '1wk' | '1mo'
  adjustments: 'splits' | 'dividends' | 'unadjusted' | 'all'
  includeExtended: boolean
}

const INTERVALS = [
  { value: '1d', label: 'Daily', description: 'Trading days only' },
  { value: '1wk', label: 'Weekly', description: 'End of week prices' },
  { value: '1mo', label: 'Monthly', description: 'End of month prices' },
]

const ADJUSTMENTS = [
  { value: 'splits', label: 'Splits Only', description: 'Adjusted for splits' },
  { value: 'dividends', label: 'Dividends Only', description: 'Adjusted for dividends' },
  { value: 'unadjusted', label: 'Unadjusted', description: 'Raw prices' },
  { value: 'all', label: 'All Adjustments', description: 'Both splits & dividends' },
]

const PRESETS = [
  { label: 'Last 7 Days', days: 7 },
  { label: 'Last 30 Days', days: 30 },
  { label: 'Last 3 Months', months: 3 },
  { label: 'Last 6 Months', months: 6 },
  { label: 'Last Year', years: 1 },
  { label: 'Last 5 Years', years: 5 },
  { label: 'All Time', years: 10 },
]

function generateMockData(config: ExportConfig): Array<{
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  adjusted_close: number
}> {
  const start = new Date(config.startDate)
  const end = new Date(config.endDate)
  const data: Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
    adjusted_close: number
  }> = []

  let currentDate = new Date(start)
  let basePrice = 150 + Math.random() * 50

  while (currentDate <= end) {
    const dayData = {
      date: formatDate(currentDate),
      open: basePrice,
      high: basePrice * (1 + Math.random() * 0.04),
      low: basePrice * (1 - Math.random() * 0.04),
      close: basePrice * (0.98 + Math.random() * 0.04),
      volume: Math.floor(Math.random() * 50000000) + 10000000,
      adjusted_close: basePrice * (0.97 + Math.random() * 0.06),
    }
    data.push(dayData)
    basePrice = dayData.close
    currentDate.setDate(currentDate.getDate() + 1)
  }

  return data
}

export function HistoricalDataExport({ symbol = 'AAPL', className }: HistoricalDataExportProps) {
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState<ExportConfig>({
    symbol,
    startDate: formatDate(subYears(new Date(), 1)),
    endDate: formatDate(new Date()),
    interval: '1d',
    adjustments: 'all',
    includeExtended: false,
  })
  const [preview, setPreview] = useState<Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
  }> | null>(null)
  const { downloadCSV, downloadJSON } = useDownloadFile()

  const applyPreset = (preset: typeof PRESETS[0]) => {
    const endDate = new Date()
    let startDate: Date

    if (preset.days) {
      startDate = subDays(endDate, preset.days)
    } else if (preset.months) {
      startDate = subMonths(endDate, preset.months)
    } else {
      startDate = subYears(endDate, preset.years)
    }

    setConfig((prev) => ({
      ...prev,
      startDate: formatDate(startDate),
      endDate: formatDate(endDate),
    }))
  }

  const handlePreview = () => {
    setLoading(true)
    setTimeout(() => {
      const data = generateMockData(config).slice(0, 5)
      setPreview(data.map(({ adjusted_close, ...rest }) => rest))
      setLoading(false)
    }, 800)
  }

  const handleExportCSV = () => {
    const data = generateMockData(config)
    const headers = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adjusted_Close']
    const rows = data.map((d) => [
      d.date,
      d.open.toFixed(4),
      d.high.toFixed(4),
      d.low.toFixed(4),
      d.close.toFixed(4),
      d.volume.toString(),
      d.adjusted_close.toFixed(4),
    ])
    downloadCSV(rows, `${symbol}_historical_data`, headers)
  }

  const handleExportJSON = () => {
    const data = generateMockData(config)
    downloadJSON(data, `${symbol}_historical_data`)
  }

  const handleExportYAML = () => {
    const data = generateMockData(config)
    const yaml = `symbol: ${symbol}
start_date: ${config.startDate}
end_date: ${config.endDate}
interval: ${config.interval}
adjustments: ${config.adjustments}
data:\n${data.map((d) => `  - date: ${d.date}
    open: ${d.open.toFixed(4)}
    high: ${d.high.toFixed(4)}
    low: ${d.low.toFixed(4)}
    close: ${d.close.toFixed(4)}
    volume: ${d.volume}
    adjusted_close: ${d.adjusted_close.toFixed(4)}`).join('\n')}`
    const blob = new Blob([yaml], { type: 'text/yaml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${symbol}_historical_data.yaml`
    a.click()
    URL.revokeObjectURL(url)
  }

  const dataPoints = preview?.length || 0

  return (
    <Card className={cn('', className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <Database className="h-5 w-5" />
          Historical Data Export
          {symbol && (
            <Badge variant="secondary" className="ml-2">
              {symbol}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Start Date</Label>
                <Input
                  type="date"
                  value={config.startDate}
                  onChange={(e) => setConfig((prev) => ({ ...prev, startDate: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label>End Date</Label>
                <Input
                  type="date"
                  value={config.endDate}
                  onChange={(e) => setConfig((prev) => ({ ...prev, endDate: e.target.value }))}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Quick Select</Label>
              <div className="flex flex-wrap gap-2">
                {PRESETS.map((preset) => (
                  <Button
                    key={preset.label}
                    variant="outline"
                    size="sm"
                    onClick={() => applyPreset(preset)}
                  >
                    {preset.label}
                  </Button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Interval</Label>
                <Select
                  value={config.interval}
                  onValueChange={(v) => setConfig((prev) => ({ ...prev, interval: v as ExportConfig['interval'] }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {INTERVALS.map((interval) => (
                      <SelectItem key={interval.value} value={interval.value}>
                        <div>
                          <div className="font-medium">{interval.label}</div>
                          <div className="text-xs text-muted-foreground">{interval.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Adjustments</Label>
                <Select
                  value={config.adjustments}
                  onValueChange={(v) => setConfig((prev) => ({ ...prev, adjustments: v as ExportConfig['adjustments'] }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {ADJUSTMENTS.map((adj) => (
                      <SelectItem key={adj.value} value={adj.value}>
                        <div>
                          <div className="font-medium">{adj.label}</div>
                          <div className="text-xs text-muted-foreground">{adj.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button onClick={handlePreview} disabled={loading} className="w-full">
              {loading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Generating Preview...
                </>
              ) : (
                <>
                  <Clock className="h-4 w-4 mr-2" />
                  Preview Data
                </>
              )}
            </Button>
          </div>

          <div className="space-y-4">
            <div className="bg-muted/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">Export Options</h4>
              </div>

              <div className="grid grid-cols-3 gap-2 mb-4">
                <Button variant="outline" onClick={handleExportCSV}>
                  <FileSpreadsheet className="h-4 w-4 mr-2" />
                  CSV
                </Button>
                <Button variant="outline" onClick={handleExportJSON}>
                  <FileJson className="h-4 w-4 mr-2" />
                  JSON
                </Button>
                <Button variant="outline" onClick={handleExportYAML}>
                  <FileText className="h-4 w-4 mr-2" />
                  YAML
                </Button>
              </div>

              <div className="text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" />
                  <span>Includes: OHLCV + Adjusted Close</span>
                </div>
              </div>
            </div>

            {preview && (
              <div className="bg-muted/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">Preview ({dataPoints} rows)</h4>
                  <Badge variant="outline">{config.interval.toUpperCase()}</Badge>
                </div>

                <div className="space-y-1">
                  <div className="grid grid-cols-6 gap-2 text-xs font-medium">
                    <div>Date</div>
                    <div>Open</div>
                    <div>High</div>
                    <div>Low</div>
                    <div>Close</div>
                    <div>Volume</div>
                  </div>
                  {preview.map((row, i) => (
                    <div key={i} className="grid grid-cols-6 gap-2 text-xs">
                      <div className="truncate">{row.date}</div>
                      <div>${row.open.toFixed(2)}</div>
                      <div>${row.high.toFixed(2)}</div>
                      <div>${row.low.toFixed(2)}</div>
                      <div className="font-medium">${row.close.toFixed(2)}</div>
                      <div className="text-muted-foreground">{(row.volume / 1000000).toFixed(1)}M</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!preview && !loading && (
              <div className="bg-muted/50 rounded-lg p-8 text-center text-muted-foreground">
                <Calendar className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Click "Preview Data" to see sample</p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
