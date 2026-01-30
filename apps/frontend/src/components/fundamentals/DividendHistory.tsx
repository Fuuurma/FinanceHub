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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DollarSign,
  Calendar,
  Download,
  FileSpreadsheet,
  FileJson,
  TrendingUp,
  RefreshCw,
} from 'lucide-react'
import { cn, formatCurrency, formatDate } from '@/lib/utils'
import { useDownloadFile } from '@/hooks/useDownload'
import type { Dividend } from '@/lib/types/dividend'

interface DividendHistoryProps {
  symbol?: string
  className?: string
}

interface DividendData {
  exDate: string
  payDate: string
  recordDate: string
  amount: number
  frequency: string
  type: string
  declaredDate?: string
}

const FREQUENCY_LABELS: Record<string, string> = {
  quarterly: 'Quarterly',
  monthly: 'Monthly',
  annual: 'Annual',
  semi_annual: 'Semi-Annual',
  special: 'Special',
}

function generateMockDividends(): DividendData[] {
  const today = new Date()
  const dividends: DividendData[] = []

  const frequencies = ['quarterly', 'quarterly', 'quarterly', 'annual', 'special']
  const amounts = [0.88, 0.92, 0.95, 1.20, 3.50]

  for (let i = 0; i < 20; i++) {
    const exDate = new Date(today)
    exDate.setMonth(exDate.getMonth() - i * 3)

    const recordDate = new Date(exDate)
    recordDate.setDate(recordDate.getDate() - 2)

    const payDate = new Date(exDate)
    payDate.setDate(payDate.getDate() + 14)

    const freqIndex = Math.min(Math.floor(i / 4), frequencies.length - 1)
    const amountIndex = Math.min(i, amounts.length - 1)

    dividends.push({
      exDate: formatDate(exDate),
      payDate: formatDate(payDate),
      recordDate: formatDate(recordDate),
      amount: amounts[amountIndex] + (i * 0.01),
      frequency: frequencies[freqIndex],
      type: i === 15 ? 'special' : 'regular',
      declaredDate: formatDate(new Date(exDate.getTime() - 7 * 24 * 60 * 60 * 1000)),
    })
  }

  return dividends
}

export function DividendHistory({ symbol = 'AAPL', className }: DividendHistoryProps) {
  const [loading, setLoading] = useState(true)
  const [dividends, setDividends] = useState<DividendData[]>([])
  const [frequency, setFrequency] = useState<string>('all')
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc')
  const { downloadCSV, downloadJSON } = useDownloadFile()

  const loadDividends = () => {
    setLoading(true)
    setTimeout(() => {
      const data = generateMockDividends()
      setDividends(data)
      setLoading(false)
    }, 600)
  }

  const filteredDividends = dividends
    .filter((d) => frequency === 'all' || d.frequency === frequency)
    .sort((a, b) => {
      const dateA = new Date(a.exDate).getTime()
      const dateB = new Date(b.exDate).getTime()
      return sortOrder === 'desc' ? dateB - dateA : dateA - dateB
    })

  const totalDividends = dividends.reduce((sum, d) => sum + d.amount, 0)
  const avgAmount = dividends.length > 0 ? totalDividends / dividends.length : 0
  const annualYield = avgAmount * 4

  const handleExportCSV = () => {
    const headers = ['Ex-Date', 'Pay-Date', 'Record-Date', 'Amount', 'Frequency', 'Type', 'Declared']
    const rows = filteredDividends.map((d) => [
      d.exDate,
      d.payDate,
      d.recordDate,
      d.amount.toFixed(4),
      d.frequency,
      d.type,
      d.declaredDate || '',
    ])
    downloadCSV(rows, `${symbol}_dividend_history`, headers)
  }

  const handleExportJSON = () => {
    downloadJSON(filteredDividends, `${symbol}_dividend_history`)
  }

  if (loading) {
    return (
      <Card className={cn('', className)}>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Dividend History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-[300px] w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Dividend History
            {symbol && (
              <Badge variant="secondary" className="ml-2">
                {symbol}
              </Badge>
            )}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Select value={frequency} onValueChange={setFrequency}>
              <SelectTrigger className="w-32 h-8">
                <SelectValue placeholder="Frequency" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="regular">Regular</SelectItem>
                <SelectItem value="special">Special</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={loadDividends}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-4 gap-4 mb-4">
          <div className="bg-green-50 dark:bg-green-950/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-green-700 dark:text-green-400">
              <TrendingUp className="h-4 w-4" />
              <span className="text-xs font-medium">Total Paid</span>
            </div>
            <div className="text-xl font-bold mt-1">
              {formatCurrency(totalDividends)}
            </div>
            <div className="text-xs text-green-600 dark:text-green-500">
              Last 5 years
            </div>
          </div>

          <div className="bg-blue-50 dark:bg-blue-950/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-blue-700 dark:text-blue-400">
              <DollarSign className="h-4 w-4" />
              <span className="text-xs font-medium">Avg. Amount</span>
            </div>
            <div className="text-xl font-bold mt-1">
              {formatCurrency(avgAmount)}
            </div>
            <div className="text-xs text-blue-600 dark:text-blue-500">
              Per payment
            </div>
          </div>

          <div className="bg-purple-50 dark:bg-purple-950/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-purple-700 dark:text-purple-400">
              <Calendar className="h-4 w-4" />
              <span className="text-xs font-medium">Annual Yield</span>
            </div>
            <div className="text-xl font-bold mt-1">
              {annualYield.toFixed(2)}%
            </div>
            <div className="text-xs text-purple-600 dark:text-purple-500">
              Estimated
            </div>
          </div>

          <div className="bg-orange-50 dark:bg-orange-950/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-orange-700 dark:text-orange-400">
              <DollarSign className="h-4 w-4" />
              <span className="text-xs font-medium">Payments</span>
            </div>
            <div className="text-xl font-bold mt-1">
              {dividends.length}
            </div>
            <div className="text-xs text-orange-600 dark:text-orange-500">
              In history
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between mb-4">
          <div className="text-sm text-muted-foreground">
            Showing {filteredDividends.length} dividend payments
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleExportCSV}>
              <FileSpreadsheet className="h-4 w-4 mr-1" />
              CSV
            </Button>
            <Button variant="outline" size="sm" onClick={handleExportJSON}>
              <FileJson className="h-4 w-4 mr-1" />
              JSON
            </Button>
          </div>
        </div>

        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ex-Date</TableHead>
                <TableHead>Pay-Date</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Frequency</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Yield</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredDividends.map((dividend, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{dividend.exDate}</TableCell>
                  <TableCell>{dividend.payDate}</TableCell>
                  <TableCell className="font-semibold text-green-600 dark:text-green-400">
                    {formatCurrency(dividend.amount)}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {FREQUENCY_LABELS[dividend.frequency] || dividend.frequency}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={dividend.type === 'special' ? 'secondary' : 'default'}
                    >
                      {dividend.type}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {dividend.type === 'special' ? '-' : (
                      <span className="text-xs">
                        {((dividend.amount * 4) * 100).toFixed(2)}%
                      </span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
          <div>
            Data from {symbol} dividend history records
          </div>
          <div className="flex items-center gap-1">
            <span>Sorted by:</span>
            <Select value={sortOrder} onValueChange={(v) => setSortOrder(v as 'desc' | 'asc')}>
              <SelectTrigger className="h-7 w-28">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">Newest First</SelectItem>
                <SelectItem value="asc">Oldest First</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
