"use client"

import { useState, useMemo } from 'react'
import { TrendingUp, TrendingDown, Minus, Calendar, DollarSign, BarChart3, Download, RefreshCw } from 'lucide-react'
import { cn, formatCurrency, formatNumber, formatPercent } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'

export interface EarningsEstimate {
  period: string
  periodType: 'Q1' | 'Q2' | 'Q3' | 'Q4' | 'FY' | 'H1' | 'H2'
  epsEstimate: number
  epsLow: number
  epsHigh: number
  revenueEstimate: number
  revenueLow: number
  revenueHigh: number
  epsCount: number
  revenueCount: number
  lastUpdated: string
}

export interface EarningsEstimatesSummary {
  symbol: string
  nextEarningsDate: string
  daysUntilEarnings: number
  currentQuarter: EarningsEstimate
  nextQuarter: EarningsEstimate
  fullYear: EarningsEstimate
  growthRate: number
  growthRateChange: number
  analystCount: number
}

export interface EarningsEstimatesPanelProps {
  estimates?: EarningsEstimate[]
  summary?: EarningsEstimatesSummary
  symbol?: string
  loading?: boolean
  error?: string
  className?: string
}

type EstimateType = 'eps' | 'revenue'

const PERIOD_LABELS: Record<string, string> = {
  Q1: 'Q1', Q2: 'Q2', Q3: 'Q3', Q4: 'Q4',
  FY: 'Full Year', H1: 'H1', H2: 'H2',
}

function EstimateRow({ estimate, type }: { estimate: EarningsEstimate; type: EstimateType }) {
  const isEps = type === 'eps'
  const estimateValue = isEps ? estimate.epsEstimate : estimate.revenueEstimate
  const lowValue = isEps ? estimate.epsLow : estimate.revenueLow
  const highValue = isEps ? estimate.epsHigh : estimate.revenueHigh
  const count = isEps ? estimate.epsCount : estimate.revenueCount

  const range = highValue - lowValue
  const position = range > 0 ? ((estimateValue - lowValue) / range) * 100 : 50

  return (
    <TableRow>
      <TableCell className="py-4">
        <div className="flex flex-col">
          <span className="font-medium">{estimate.period}</span>
          <span className="text-xs text-muted-foreground">{PERIOD_LABELS[estimate.periodType] || estimate.periodType}</span>
        </div>
      </TableCell>
      <TableCell className="text-right py-4">
        <div className="flex flex-col items-end">
          <span className="font-semibold text-lg">
            {isEps ? `$${estimateValue.toFixed(2)}` : formatNumber(estimateValue)}
          </span>
          <span className="text-xs text-muted-foreground">
            {count} analysts
          </span>
        </div>
      </TableCell>
      <TableCell className="py-4">
        <div className="w-full px-4">
          <div className="flex justify-between text-xs text-muted-foreground mb-1">
            <span>{isEps ? `$${lowValue.toFixed(2)}` : formatNumber(lowValue)}</span>
            <span>{isEps ? `$${highValue.toFixed(2)}` : formatNumber(highValue)}</span>
          </div>
          <div className="relative h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="absolute h-full bg-primary rounded-full"
              style={{ left: `${Math.max(0, Math.min(100, position))}%`, width: '4px' }}
            />
          </div>
        </div>
      </TableCell>
    </TableRow>
  )
}

function EstimatesSummary({ summary }: { summary: EarningsEstimatesSummary }) {
  const isUpcoming = summary.daysUntilEarnings <= 14
  const isUrgent = summary.daysUntilEarnings <= 7

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-muted/30 rounded-lg">
      <div className="flex flex-col">
        <span className="text-xs text-muted-foreground">Next Earnings</span>
        <span className="font-semibold">{summary.nextEarningsDate}</span>
        <Badge
          variant={isUrgent ? 'destructive' : isUpcoming ? 'default' : 'secondary'}
          className="mt-1 w-fit"
        >
          {summary.daysUntilEarnings <= 0 ? 'Today' : `${summary.daysUntilEarnings} days`}
        </Badge>
      </div>

      <div className="flex flex-col">
        <span className="text-xs text-muted-foreground">Analysts</span>
        <span className="font-semibold text-lg">{summary.analystCount}</span>
        <span className="text-xs text-muted-foreground">covering stock</span>
      </div>

      <div className="flex flex-col">
        <span className="text-xs text-muted-foreground">Growth Rate</span>
        <span className={cn('font-semibold text-lg', summary.growthRate > 0 ? 'text-green-500' : 'text-red-500')}>
          {formatPercent(summary.growthRate)}
        </span>
        <span className="text-xs text-muted-foreground">
          {summary.growthRateChange > 0 ? '+' : ''}{formatPercent(summary.growthRateChange)} YoY
        </span>
      </div>

      <div className="flex flex-col">
        <span className="text-xs text-muted-foreground">Current Est.</span>
        <span className="font-semibold text-lg">
          ${summary.currentQuarter.epsEstimate.toFixed(2)}
        </span>
        <span className="text-xs text-muted-foreground">EPS for {summary.currentQuarter.period}</span>
      </div>
    </div>
  )
}

export function EarningsEstimatesPanel({
  estimates = [],
  summary,
  symbol,
  loading = false,
  error,
  className,
}: EarningsEstimatesPanelProps) {
  const [estimateType, setEstimateType] = useState<EstimateType>('eps')
  const [showConsensus, setShowConsensus] = useState(true)

  const epsEstimates = useMemo(() =>
    estimates.filter(e => e.epsCount > 0),
    [estimates]
  )

  const revenueEstimates = useMemo(() =>
    estimates.filter(e => e.revenueCount > 0),
    [estimates]
  )

  const handleRefresh = () => {
    console.log('Refresh earnings estimates')
  }

  const handleExport = () => {
    const data = estimates.map(e => ({
      period: e.period,
      type: e.periodType,
      epsEstimate: e.epsEstimate,
      epsLow: e.epsLow,
      epsHigh: e.epsHigh,
      revenueEstimate: e.revenueEstimate,
      revenueLow: e.revenueLow,
      revenueHigh: e.revenueHigh,
    }))
    const csv = [
      Object.keys(data[0] || {}).join(','),
      ...data.map(row => Object.values(row).join(',')),
    ].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${symbol || 'earnings'}-estimates.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || (!estimates.length && !summary)) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <CardTitle>Earnings Estimates</CardTitle>
          <CardDescription>Analyst consensus for upcoming earnings</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No estimates data available'}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              Earnings Estimates
              {symbol && <Badge variant="outline">{symbol}</Badge>}
            </CardTitle>
            <CardDescription>Analyst consensus for upcoming earnings periods</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={estimateType} onValueChange={(v) => setEstimateType(v as EstimateType)}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="eps">EPS Estimates</SelectItem>
                <SelectItem value="revenue">Revenue Estimates</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" onClick={handleRefresh}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleExport}>
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {summary && <EstimatesSummary summary={summary} />}

        <Tabs defaultValue="estimates" className="mt-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="estimates">Consensus Estimates</TabsTrigger>
            <TabsTrigger value="history">Estimate History</TabsTrigger>
          </TabsList>

          <TabsContent value="estimates" className="mt-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Period</TableHead>
                  <TableHead className="text-right">
                    {estimateType === 'eps' ? 'EPS Estimate' : 'Revenue Estimate'}
                  </TableHead>
                  <TableHead>Range</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(estimateType === 'eps' ? epsEstimates : revenueEstimates).map((estimate, index) => (
                  <EstimateRow key={index} estimate={estimate} type={estimateType} />
                ))}
              </TableBody>
            </Table>
          </TabsContent>

          <TabsContent value="history" className="mt-4">
            <div className="text-center py-8 text-muted-foreground">
              <BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>Historical estimate revisions chart would go here</p>
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">
            Last updated: {estimates[0]?.lastUpdated || 'N/A'} · Data from {summary?.analystCount || 0} analysts
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
