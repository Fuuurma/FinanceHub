'use client'

import { useState, useMemo, useCallback } from 'react'
import { TrendingUp, TrendingDown, Target, Calendar, Building, Download, Filter, BarChart3 } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Progress } from '@/components/ui/progress'
import { cn, formatCurrency } from '@/lib/utils'

export interface PriceTarget {
  id: string
  analystName: string
  firmName: string
  rating: 'buy' | 'hold' | 'sell' | 'outperform' | 'underweight'
  currentPrice: number
  targetPrice: number
  previousTarget?: number
  date: string
  confidence: number
}

export interface PriceTargetSummary {
  currentPrice: number
  highTarget: number
  lowTarget: number
  meanTarget: number
  medianTarget: number
  standardDeviation: number
  numberOfAnalysts: number
  upsidePotential: number
}

export interface PriceTargetChartProps {
  symbol: string
  targets?: PriceTarget[]
  summary?: PriceTargetSummary
  loading?: boolean
  className?: string
}

function generateMockTargets(symbol: string, count: number = 15): PriceTarget[] {
  const firms = ['Goldman Sachs', 'Morgan Stanley', 'JP Morgan', 'Bank of America', 'Citigroup', 'Deutsche Bank', 'UBS', 'Credit Suisse', 'Wells Fargo', 'Raymond James']
  const analysts = ['John Smith', 'Jane Doe', 'Mike Johnson', 'Sarah Williams', 'David Brown', 'Emily Davis', 'Chris Wilson', 'Amanda Taylor', 'Ryan Martinez', 'Lisa Anderson']
  const ratings: Array<'buy' | 'hold' | 'sell' | 'outperform' | 'underweight'> = ['buy', 'hold', 'sell', 'outperform', 'underweight']
  const currentPrice = 150 + Math.random() * 50

  return Array.from({ length: count }, (_, i) => {
    const targetPrice = currentPrice * (0.8 + Math.random() * 0.6)
    const previousTarget = Math.random() > 0.5 ? targetPrice * (0.9 + Math.random() * 0.2) : undefined
    return {
      id: `target-${i}`,
      analystName: analysts[i % analysts.length],
      firmName: firms[i % firms.length],
      rating: ratings[i % ratings.length],
      currentPrice,
      targetPrice,
      previousTarget,
      date: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      confidence: 50 + Math.random() * 50,
    }
  })
}

function generateMockSummary(currentPrice: number): PriceTargetSummary {
  const targets = Array.from({ length: 15 }, () => currentPrice * (0.8 + Math.random() * 0.6))
  return {
    currentPrice,
    highTarget: Math.max(...targets),
    lowTarget: Math.min(...targets),
    meanTarget: targets.reduce((a, b) => a + b, 0) / targets.length,
    medianTarget: targets.sort((a, b) => a - b)[Math.floor(targets.length / 2)],
    standardDeviation: Math.sqrt(targets.reduce((sum, t) => sum + Math.pow(t - targets.reduce((a, b) => a + b, 0) / targets.length, 2), 0) / targets.length),
    numberOfAnalysts: targets.length,
    upsidePotential: ((targets.reduce((a, b) => a + b, 0) / targets.length - currentPrice) / currentPrice) * 100,
  }
}

function PriceTargetChartSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-32" />
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-20 w-full" />)}
        </div>
        <Skeleton className="h-64 w-full" />
      </CardContent>
    </Card>
  )
}

function RatingBadge({ rating }: { rating: string }) {
  const colors: Record<string, string> = {
    buy: 'bg-green-100 text-green-700 border-green-200',
    outperform: 'bg-green-50 text-green-600 border-green-200',
    hold: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    underweight: 'bg-orange-100 text-orange-700 border-orange-200',
    sell: 'bg-red-100 text-red-700 border-red-200',
  }
  return (
    <Badge variant="outline" className={cn('text-xs', colors[rating] || 'bg-gray-100')}>
      {rating.charAt(0).toUpperCase() + rating.slice(1)}
    </Badge>
  )
}

export function PriceTargetChart({ symbol, targets: propTargets, summary: propSummary, loading = false, className }: PriceTargetChartProps) {
  const [timeframe, setTimeframe] = useState<'1m' | '3m' | '6m' | '1y' | 'all'>('6m')
  const [sortBy, setSortBy] = useState<'date' | 'target' | 'upside'>('date')

  const targets = useMemo(() => propTargets || generateMockTargets(symbol, 15), [propTargets, symbol])
  const summary = useMemo(() => propSummary || generateMockSummary(targets[0]?.currentPrice || 150), [propSummary, targets])

  const sortedTargets = useMemo(() => {
    return [...targets].sort((a, b) => {
      if (sortBy === 'date') return new Date(b.date).getTime() - new Date(a.date).getTime()
      if (sortBy === 'target') return b.targetPrice - a.targetPrice
      return (b.targetPrice - b.currentPrice) / b.currentPrice - (a.targetPrice - a.currentPrice) / a.currentPrice
    })
  }, [targets, sortBy])

  const handleExport = useCallback(() => {
    const csvData = sortedTargets.map(t => ({
      Analyst: t.analystName,
      Firm: t.firmName,
      Rating: t.rating,
      'Current Price': t.currentPrice,
      'Target Price': t.targetPrice,
      Upside: `${((t.targetPrice - t.currentPrice) / t.currentPrice * 100).toFixed(1)}%`,
      Date: t.date,
    }))
    const csv = ['Analyst,Firm,Rating,Current Price,Target Price,Upside,Date', ...csvData.map(row => Object.values(row).join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${symbol}_price_targets.csv`
    a.click()
  }, [sortedTargets, symbol])

  if (loading) return <PriceTargetChartSkeleton />

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <Target className="h-5 w-5" />
              Price Targets
            </CardTitle>
            <CardDescription>{symbol} - Analyst price targets and forecasts</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={timeframe} onValueChange={(v: any) => setTimeframe(v)}>
              <SelectTrigger className="w-28"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="1m">1 Month</SelectItem>
                <SelectItem value="3m">3 Months</SelectItem>
                <SelectItem value="6m">6 Months</SelectItem>
                <SelectItem value="1y">1 Year</SelectItem>
                <SelectItem value="all">All Time</SelectItem>
              </SelectContent>
            </Select>
            <Button size="sm" variant="outline" onClick={handleExport}>
              <Download className="h-4 w-4 mr-1" />Export
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Target className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Mean Target</span>
            </div>
            <p className="text-xl font-bold">{formatCurrency(summary.meanTarget)}</p>
            <p className={cn('text-xs', summary.upsidePotential >= 0 ? 'text-green-600' : 'text-red-600')}>
              {summary.upsidePotential >= 0 ? '+' : ''}{summary.upsidePotential.toFixed(1)}% upside
            </p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="text-xs text-green-700">High Target</span>
            </div>
            <p className="text-xl font-bold text-green-700">{formatCurrency(summary.highTarget)}</p>
            <p className="text-xs text-green-600">{((summary.highTarget - summary.currentPrice) / summary.currentPrice * 100).toFixed(1)}% upside</p>
          </div>
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <span className="text-xs text-red-700">Low Target</span>
            </div>
            <p className="text-xl font-bold text-red-700">{formatCurrency(summary.lowTarget)}</p>
            <p className="text-xs text-red-600">{((summary.lowTarget - summary.currentPrice) / summary.currentPrice * 100).toFixed(1)}% upside</p>
          </div>
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Building className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Analysts</span>
            </div>
            <p className="text-xl font-bold">{summary.numberOfAnalysts}</p>
            <p className="text-xs text-muted-foreground">covering the stock</p>
          </div>
        </div>

        <Tabs defaultValue="chart" className="space-y-4">
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="chart">Target Distribution</TabsTrigger>
              <TabsTrigger value="table">Analyst List</TabsTrigger>
            </TabsList>
            <Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
              <SelectTrigger className="w-32"><SelectValue placeholder="Sort by" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="date">Most Recent</SelectItem>
                <SelectItem value="target">Highest Target</SelectItem>
                <SelectItem value="upside">Highest Upside</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <TabsContent value="chart" className="space-y-4">
            <div className="h-64 flex items-end gap-1 px-4">
              {sortedTargets.slice(0, 20).map((target, i) => {
                const barHeight = ((target.targetPrice - summary.lowTarget) / (summary.highTarget - summary.lowTarget)) * 100
                const upside = (target.targetPrice - target.currentPrice) / target.currentPrice * 100
                return (
                  <TooltipProvider key={target.id}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div
                          className={cn(
                            'flex-1 rounded-t cursor-pointer transition-all hover:opacity-80',
                            upside >= 0 ? 'bg-green-500' : 'bg-red-500'
                          )}
                          style={{ height: `${Math.max(barHeight, 5)}%` }}
                        />
                      </TooltipTrigger>
                      <TooltipContent>
                        <div className="text-xs space-y-1">
                          <p className="font-semibold">{target.firmName}</p>
                          <p>Target: {formatCurrency(target.targetPrice)}</p>
                          <p>Upside: {upside >= 0 ? '+' : ''}{upside.toFixed(1)}%</p>
                          <p>Date: {target.date}</p>
                        </div>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                )
              })}
            </div>
            <div className="flex items-center justify-between px-4 text-xs text-muted-foreground">
              <span>{formatCurrency(summary.lowTarget)}</span>
              <span>Price Targets ({sortedTargets.length})</span>
              <span>{formatCurrency(summary.highTarget)}</span>
            </div>
            <div className="flex items-center gap-4 px-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded" />
                <span>Upside targets</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded" />
                <span>Downside targets</span>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="table">
            <div className="border rounded-lg">
              <div className="grid grid-cols-6 gap-4 p-3 border-b bg-muted/50 text-xs font-medium text-muted-foreground">
                <div>Analyst / Firm</div>
                <div className="text-center">Rating</div>
                <div className="text-right">Current</div>
                <div className="text-right">Target</div>
                <div className="text-right">Upside</div>
                <div className="text-center">Date</div>
              </div>
              <div className="divide-y">
                {sortedTargets.map((target) => {
                  const upside = (target.targetPrice - target.currentPrice) / target.currentPrice * 100
                  return (
                    <div key={target.id} className="grid grid-cols-6 gap-4 p-3 text-sm items-center hover:bg-muted/30">
                      <div>
                        <p className="font-medium">{target.analystName}</p>
                        <p className="text-xs text-muted-foreground">{target.firmName}</p>
                      </div>
                      <div className="flex justify-center">
                        <RatingBadge rating={target.rating} />
                      </div>
                      <div className="text-right">{formatCurrency(target.currentPrice)}</div>
                      <div className="text-right font-semibold">{formatCurrency(target.targetPrice)}</div>
                      <div className={cn('text-right font-medium', upside >= 0 ? 'text-green-600' : 'text-red-600')}>
                        {upside >= 0 ? '+' : ''}{upside.toFixed(1)}%
                      </div>
                      <div className="text-center text-muted-foreground text-xs">{target.date}</div>
                    </div>
                  )
                })}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default PriceTargetChart
