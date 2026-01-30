'use client'

import { useState } from 'react'
import { TrendingUp, TrendingDown, Calendar, Users, Target, RefreshCw, Download, BarChart3, Minus } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { cn, formatCurrency, formatNumber, formatPercent, formatDate } from '@/lib/utils'
import type { AnalystEstimates } from '@/lib/types/iex-cloud'
import type { EarningsReport } from '@/lib/types/fundamentals'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ReferenceLine } from 'recharts'

export interface EarningsEstimate {
  fiscalYear: number
  fiscalPeriod: number
  periodLabel: string
  epsEstimate: number
  epsLow: number
  epsHigh: number
  epsCount: number
  revenueEstimate: number
  revenueLow: number
  revenueHigh: number
  revenueCount: number
  growthEstimate: number
}

export interface EarningsEstimatesSummary {
  avgEPSSurprise: number
  avgRevenueSurprise: number
  beatRate: number
  numberOfEstimates: number
  avgTargetPrice: number
  consensusRating: 'buy' | 'hold' | 'sell'
}

export interface EarningsData {
  symbol: string
  companyName: string
  estimates: AnalystEstimates[]
  historical: EarningsReport[]
  upcomingEarnings: string | null
  nextEarningsDate: string | null
  lastEarningsDate: string | null
  nextEarningsTime: 'before' | 'after' | 'during' | null
  summary: {
    avgEPSSurprise: number
    avgRevenueSurprise: number
    beatRate: number
    numberOfEstimates: number
    avgTargetPrice: number
    consensusRating: 'buy' | 'hold' | 'sell'
  }
  lastUpdated: string
}

interface EarningsEstimatesPanelProps {
  data: EarningsData
  isLoading?: boolean
  onRefresh?: () => void
  onExport?: () => void
  className?: string
}

const RATING_COLORS: Record<string, string> = {
  buy: 'bg-green-100 text-green-800 border-green-200',
  hold: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  sell: 'bg-red-100 text-red-800 border-red-200',
}

const RATING_LABELS: Record<string, string> = {
  buy: 'Buy',
  hold: 'Hold',
  sell: 'Sell',
}

function EstimateBar({ label, actual, estimate }: { label: string; actual: number | null; estimate: number | null }) {
  if (!actual && !estimate) return null
  const maxValue = Math.max(Math.abs(actual || 0), Math.abs(estimate || 0)) * 1.2
  const actualPercent = maxValue > 0 ? ((actual || 0) / maxValue) * 100 : 0
  const estimatePercent = maxValue > 0 ? ((estimate || 0) / maxValue) * 100 : 0
  const isBeat = actual !== null && estimate !== null && actual > estimate
  const isMiss = actual !== null && estimate !== null && actual < estimate

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium w-24">{label}</span>
        <div className="flex-1 relative h-2 bg-muted rounded-full overflow-hidden">
          {actual !== null && (
            <div
              className={cn('absolute top-0 h-full rounded-full', isBeat ? 'bg-green-500' : isMiss ? 'bg-red-500' : 'bg-gray-500')}
              style={{ width: `${Math.abs(actualPercent)}%`, left: actualPercent < 0 ? `${50 - Math.abs(actualPercent)}%` : '50%' }}
            />
          )}
          {estimate !== null && (
            <div
              className="absolute top-0 h-full bg-blue-500 rounded-full"
              style={{ width: `${Math.abs(estimatePercent)}%`, left: estimatePercent < 0 ? `${50 - Math.abs(estimatePercent)}%` : '50%' }}
            />
          )}
        </div>
        <div className="flex gap-4 text-xs ml-4">
          {actual !== null && (
            <span className={cn('font-medium', isBeat ? 'text-green-600' : isMiss ? 'text-red-600' : 'text-gray-600')}>
              {formatNumber(actual)}
            </span>
          )}
          {estimate !== null && <span className="font-medium text-blue-600">{formatNumber(estimate)}</span>}
        </div>
      </div>
    </div>
  )
}

function HistoricalEarningsCard({ report }: { report: EarningsReport }) {
  const isBeat = report.eps_surprise_pct !== null && report.eps_surprise_pct > 0
  const isMiss = report.eps_surprise_pct !== null && report.eps_surprise_pct < 0

  return (
    <div className="flex items-center justify-between p-3 border-b last:border-0 hover:bg-muted/50 transition-colors">
      <div className="flex items-center gap-3">
        <div className={cn('p-2 rounded-full', isBeat ? 'bg-green-100' : isMiss ? 'bg-red-100' : 'bg-gray-100')}>
          {isBeat ? <TrendingUp className="h-4 w-4 text-green-600" /> : isMiss ? <TrendingDown className="h-4 w-4 text-red-600" /> : <Minus className="h-4 w-4 text-gray-600" />}
        </div>
        <div>
          <p className="font-medium text-sm">Q{report.fiscal_period} {report.fiscal_year}</p>
          <p className="text-xs text-muted-foreground">{formatDate(report.report_date)}</p>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="text-right">
          <p className="font-medium text-sm">{report.eps_actual !== null ? formatCurrency(report.eps_actual) : 'N/A'}</p>
          <p className="text-xs text-muted-foreground">EPS</p>
        </div>
        <Badge variant={isBeat ? 'default' : isMiss ? 'destructive' : 'secondary'}>
          {report.eps_surprise_pct !== null ? `${report.eps_surprise_pct >= 0 ? '+' : ''}${formatPercent(report.eps_surprise_pct / 100)}` : 'N/A'}
        </Badge>
      </div>
    </div>
  )
}

function EstimatesSummaryCard({ summary }: { summary: EarningsData['summary'] }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-blue-600" />
            <span className="text-xs text-muted-foreground">Beat Rate</span>
          </div>
          <p className="text-2xl font-bold mt-2">{formatPercent(summary.beatRate / 100)}</p>
          <p className="text-xs text-muted-foreground">of earnings beats</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-green-600" />
            <span className="text-xs text-muted-foreground">Avg EPS Surprise</span>
          </div>
          <p className={cn('text-2xl font-bold mt-2', summary.avgEPSSurprise >= 0 ? 'text-green-600' : 'text-red-600')}>
            {summary.avgEPSSurprise >= 0 ? '+' : ''}{formatPercent(summary.avgEPSSurprise / 100)}
          </p>
          <p className="text-xs text-muted-foreground">historical surprise</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-purple-600" />
            <span className="text-xs text-muted-foreground">Analysts</span>
          </div>
          <p className="text-2xl font-bold mt-2">{summary.numberOfEstimates}</p>
          <p className="text-xs text-muted-foreground">active estimates</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-orange-600" />
            <span className="text-xs text-muted-foreground">Avg Target</span>
          </div>
          <p className="text-2xl font-bold mt-2">{formatCurrency(summary.avgTargetPrice)}</p>
          <Badge variant="outline" className={cn('mt-1', RATING_COLORS[summary.consensusRating])}>
            {RATING_LABELS[summary.consensusRating]}
          </Badge>
        </CardContent>
      </Card>
    </div>
  )
}

function EarningsChart({ estimates }: { estimates: { epsEstimate: number; epsLow: number; epsHigh: number; periodLabel: string }[] }) {
  const chartData = estimates.map(est => ({
    period: est.periodLabel,
    Low: est.epsLow,
    Estimate: est.epsEstimate,
    High: est.epsHigh,
  }))

  if (chartData.length === 0) {
    return <div className="h-64 flex items-center justify-center text-muted-foreground">No estimate data available</div>
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={chartData} barSize={40}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis dataKey="period" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} tickFormatter={(value) => `$${value.toFixed(2)}`} />
        <RechartsTooltip formatter={(value: number) => formatCurrency(value)} contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
        <ReferenceLine y={0} stroke="#000" />
        <Bar dataKey="Low" fill="#94a3b8" radius={[2, 2, 0, 0]} />
        <Bar dataKey="Estimate" fill="#3b82f6" radius={[2, 2, 0, 0]} />
        <Bar dataKey="High" fill="#94a3b8" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

function UpcomingEarningsCard({ data }: { data: EarningsData }) {
  if (!data.nextEarningsDate) {
    return (
      <Card className="bg-muted/50">
        <CardContent className="pt-6">
          <div className="flex items-center justify-center text-muted-foreground">
            <Calendar className="h-5 w-5 mr-2" />
            No upcoming earnings date announced
          </div>
        </CardContent>
      </Card>
    )
  }

  const timeLabel = data.nextEarningsTime === 'before' ? 'Before Open' : data.nextEarningsTime === 'after' ? 'After Close' : data.nextEarningsTime === 'during' ? 'During Trading' : ''

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          Upcoming Earnings
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="text-2xl font-bold">{formatDate(data.nextEarningsDate)}</div>
          {timeLabel && <Badge variant="outline">{timeLabel}</Badge>}
        </div>
      </CardContent>
    </Card>
  )
}

export function EarningsEstimatesPanel({ data, isLoading = false, onRefresh, onExport, className }: EarningsEstimatesPanelProps) {
  const [activeTab, setActiveTab] = useState('estimates')

  if (isLoading) {
    return (
      <Card className={cn('', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24" />)}
          </div>
          <Skeleton className="h-64" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Earnings Estimates
            </CardTitle>
            <CardDescription>{data.companyName} ({data.symbol}) - Analyst forecasts and historical performance</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline" size="sm" onClick={() => onRefresh?.()}>
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Refresh data</TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline" size="sm" onClick={() => onExport?.()}>
                    <Download className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Export data</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <EstimatesSummaryCard summary={data.summary} />

        <div className="mt-6">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="estimates">Current Estimates</TabsTrigger>
              <TabsTrigger value="chart">Estimate Trend</TabsTrigger>
              <TabsTrigger value="history">Historical</TabsTrigger>
            </TabsList>

            <TabsContent value="estimates" className="mt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <UpcomingEarningsCard data={data} />
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">Latest Quarter Estimates</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {data.estimates.slice(0, 3).map((estimate, index) => (
                      <div key={index} className="space-y-2 pb-3 border-b last:border-0">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-sm">Q{estimate.fiscalPeriod} {estimate.fiscalYear}</span>
                          <Badge variant="outline">{estimate.estimateCount || 0} analysts</Badge>
                        </div>
                        <EstimateBar label="EPS" actual={null} estimate={estimate.estimatedEPS} />
                        {estimate.estimatedRevenue && <EstimateBar label="Revenue" actual={null} estimate={estimate.estimatedRevenue / 1000000} />}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="chart" className="mt-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    EPS Estimate Range
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <EarningsChart estimates={[]} />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="mt-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Historical Earnings</CardTitle>
                </CardHeader>
                <CardContent>
                  {data.historical.length === 0 ? (
                    <div className="p-8 text-center text-muted-foreground">No historical earnings data available</div>
                  ) : (
                    data.historical.slice(0, 10).map((report, index) => <HistoricalEarningsCard key={index} report={report} />)
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </CardContent>
    </Card>
  )
}
