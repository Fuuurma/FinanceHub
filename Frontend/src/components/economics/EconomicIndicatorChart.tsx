'use client'

import { useState, useMemo, useCallback, useEffect, useRef } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { TrendingUp, TrendingDown, Calendar, Activity, RefreshCw, Download, Filter } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

export type IndicatorCategory = 'gdp' | 'employment' | 'inflation' | 'interest' | 'consumer' | 'manufacturing'

export interface EconomicIndicator {
  id: string
  name: string
  category: IndicatorCategory
  value: number
  previousValue: number
  unit: string
  frequency: string
  lastUpdated: string
  nextRelease: string
  change: number
  changePercent: number
  historical: Array<{ date: string; value: number }>
}

export interface EconomicIndicatorSummary {
  totalIndicators: number
  positiveSignals: number
  negativeSignals: number
  neutralSignals: number
}

export interface EconomicIndicatorChartProps {
  indicators?: EconomicIndicator[]
  summary?: EconomicIndicatorSummary
  loading?: boolean
  className?: string
}

const CATEGORY_LABELS: Record<IndicatorCategory, string> = {
  gdp: 'GDP & Growth',
  employment: 'Employment',
  inflation: 'Inflation',
  interest: 'Interest Rates',
  consumer: 'Consumer Spending',
  manufacturing: 'Manufacturing',
}

const CATEGORY_COLORS: Record<IndicatorCategory, string> = {
  gdp: 'text-blue-600 bg-blue-100',
  employment: 'text-green-600 bg-green-100',
  inflation: 'text-red-600 bg-red-100',
  interest: 'text-purple-600 bg-purple-100',
  consumer: 'text-orange-600 bg-orange-100',
  manufacturing: 'text-cyan-600 bg-cyan-100',
}

function generateMockIndicators(): EconomicIndicator[] {
  const indicators: Array<{ name: string; category: IndicatorCategory; unit: string; frequency: string }> = [
    { name: 'GDP Growth Rate', category: 'gdp', unit: '%', frequency: 'Quarterly' },
    { name: 'Unemployment Rate', category: 'employment', unit: '%', frequency: 'Monthly' },
    { name: 'CPI Inflation', category: 'inflation', unit: '%', frequency: 'Monthly' },
    { name: 'Federal Funds Rate', category: 'interest', unit: '%', frequency: 'Daily' },
    { name: 'Consumer Spending', category: 'consumer', unit: 'B USD', frequency: 'Monthly' },
    { name: 'Manufacturing PMI', category: 'manufacturing', unit: 'Index', frequency: 'Monthly' },
    { name: 'Non-Farm Payrolls', category: 'employment', unit: 'K', frequency: 'Monthly' },
    { name: 'Core PCE Price Index', category: 'inflation', unit: '%', frequency: 'Monthly' },
  ]

  return indicators.map((ind, i) => {
    const baseValue = ind.name === 'Unemployment Rate' ? 3.8 : ind.name === 'Federal Funds Rate' ? 5.25 : ind.name === 'Manufacturing PMI' ? 49 : Math.random() * 10 + 100
    const value = baseValue + (Math.random() - 0.5) * 2
    const previousValue = baseValue + (Math.random() - 0.5) * 2
    const historical = Array.from({ length: 24 }, (_, j) => ({
      date: new Date(Date.now() - (24 - j) * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0].slice(0, 7),
      value: baseValue + (Math.random() - 0.5) * 4,
    }))

    return {
      id: `indicator-${i}`,
      name: ind.name,
      category: ind.category,
      value,
      previousValue,
      unit: ind.unit,
      frequency: ind.frequency,
      lastUpdated: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      nextRelease: new Date(Date.now() + Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      change: value - previousValue,
      changePercent: ((value - previousValue) / previousValue) * 100,
      historical,
    }
  })
}

function generateMockSummary(indicators: EconomicIndicator[]): EconomicIndicatorSummary {
  return {
    totalIndicators: indicators.length,
    positiveSignals: indicators.filter(i => i.change > 0).length,
    negativeSignals: indicators.filter(i => i.change < 0).length,
    neutralSignals: indicators.filter(i => i.change === 0).length,
  }
}

function EconomicIndicatorChartSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-32" />
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-16 w-full" />)}
        </div>
        <Skeleton className="h-64 w-full" />
      </CardContent>
    </Card>
  )
}

function IndicatorCard({ indicator, onClick, isSelected }: { indicator: EconomicIndicator; onClick: () => void; isSelected: boolean }) {
  const isPositive = indicator.change > 0
  const colorClass = CATEGORY_COLORS[indicator.category]

  return (
    <div
      onClick={onClick}
      className={cn(
        'p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md',
        isSelected ? 'border-primary ring-1 ring-primary' : 'hover:border-primary/50'
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <Badge className={cn('text-xs', colorClass)}>{CATEGORY_LABELS[indicator.category]}</Badge>
        {isPositive ? (
          <TrendingUp className="h-4 w-4 text-green-600" />
        ) : (
          <TrendingDown className="h-4 w-4 text-red-600" />
        )}
      </div>
      <p className="font-semibold text-sm">{indicator.name}</p>
      <div className="flex items-end justify-between mt-2">
        <div>
          <p className="text-xl font-bold">
            {indicator.unit === '%' ? formatPercent(indicator.value / 100) : indicator.unit === 'B USD' ? `$${indicator.value.toFixed(1)}B` : indicator.value.toFixed(2)}
          </p>
          <p className={cn('text-xs', isPositive ? 'text-green-600' : 'text-red-600')}>
            {isPositive ? '+' : ''}{indicator.change.toFixed(2)} ({indicator.changePercent >= 0 ? '+' : ''}{indicator.changePercent.toFixed(1)}%)
          </p>
        </div>
        <span className="text-xs text-muted-foreground">{indicator.frequency}</span>
      </div>
    </div>
  )
}

function HistoricalChart({ indicator }: { indicator: EconomicIndicator }) {
  const data = indicator.historical.map(h => ({
    date: h.date,
    value: h.value,
    avg: indicator.historical.reduce((sum, x) => sum + x.value, 0) / indicator.historical.length,
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis dataKey="date" className="text-xs" tick={{ fontSize: 12 }} />
        <YAxis className="text-xs" tick={{ fontSize: 12 }} domain={['auto', 'auto']} />
        <RechartsTooltip
          content={({ active, payload }: any) => {
            if (active && payload && payload.length) {
              return (
                <div className="bg-background border rounded-lg p-3 shadow-lg">
                  <p className="text-sm font-medium">{payload[0].payload.date}</p>
                  <p className="text-lg font-bold">{payload[0].payload.value?.toFixed(2)}</p>
                </div>
              )
            }
            return null
          }}
        />
        <Area type="monotone" dataKey="value" stroke="hsl(var(--primary))" fillOpacity={1} fill="url(#colorValue)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  )
}

export function EconomicIndicatorChart({ indicators: propIndicators, summary: propSummary, loading = false, className }: EconomicIndicatorChartProps) {
  const [selectedIndicator, setSelectedIndicator] = useState<EconomicIndicator | null>(null)
  const [categoryFilter, setCategoryFilter] = useState<IndicatorCategory | 'all'>('all')

  const indicators = useMemo(() => propIndicators || generateMockIndicators(), [propIndicators])
  const summary = useMemo(() => propSummary || generateMockSummary(indicators), [propSummary, indicators])

  const filteredIndicators = useMemo(() => {
    if (categoryFilter === 'all') return indicators
    return indicators.filter(i => i.category === categoryFilter)
  }, [indicators, categoryFilter])

  useEffect(() => {
    if (filteredIndicators.length > 0 && !selectedIndicator) {
      setSelectedIndicator(filteredIndicators[0])
    }
  }, [filteredIndicators, selectedIndicator])

  const handleExport = useCallback(() => {
    const csvData = filteredIndicators.map(i => ({
      Name: i.name,
      Category: CATEGORY_LABELS[i.category],
      Value: i.value,
      Unit: i.unit,
      Change: i.change,
      'Change %': i.changePercent.toFixed(2),
      Frequency: i.frequency,
      'Last Updated': i.lastUpdated,
    }))
    const csv = ['Name,Category,Value,Unit,Change,Change %,Frequency,Last Updated', ...csvData.map(row => Object.values(row).join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `economic_indicators_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  }, [filteredIndicators])

  if (loading) return <EconomicIndicatorChartSkeleton />

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Economic Indicators
            </CardTitle>
            <CardDescription>Key U.S. economic indicators and trends</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={categoryFilter} onValueChange={(v: IndicatorCategory | 'all') => setCategoryFilter(v)}>
              <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
                  <SelectItem key={key} value={key}>{label}</SelectItem>
                ))}
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
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Total</span>
            </div>
            <p className="text-2xl font-bold">{summary.totalIndicators}</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="text-xs text-green-700">Positive</span>
            </div>
            <p className="text-2xl font-bold text-green-700">{summary.positiveSignals}</p>
          </div>
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <span className="text-xs text-red-700">Negative</span>
            </div>
            <p className="text-2xl font-bold text-red-700">{summary.negativeSignals}</p>
          </div>
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Neutral</span>
            </div>
            <p className="text-2xl font-bold">{summary.neutralSignals}</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          {filteredIndicators.map((indicator) => (
            <IndicatorCard
              key={indicator.id}
              indicator={indicator}
              isSelected={selectedIndicator?.id === indicator.id}
              onClick={() => setSelectedIndicator(indicator)}
            />
          ))}
        </div>

        {selectedIndicator && (
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h4 className="font-semibold">{selectedIndicator.name}</h4>
                <p className="text-sm text-muted-foreground">24-month historical trend</p>
              </div>
              <Badge className={CATEGORY_COLORS[selectedIndicator.category]}>{CATEGORY_LABELS[selectedIndicator.category]}</Badge>
            </div>
            <HistoricalChart indicator={selectedIndicator} />
            <div className="flex items-center justify-between mt-4 text-sm text-muted-foreground">
              <span>Last updated: {selectedIndicator.lastUpdated}</span>
              <span>Next release: {selectedIndicator.nextRelease}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default EconomicIndicatorChart
