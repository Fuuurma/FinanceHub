'use client'

import { useState, useMemo, useCallback } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, ScatterChart, Scatter, ZAxis } from 'recharts'
import { Activity, TrendingUp, TrendingDown, BarChart3, ScatterChart as ScatterChartIcon, Filter, Download } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn, formatPercent } from '@/lib/utils'

export type FactorCategory = 'style' | 'sector' | 'macro' | 'thematic'

export interface FactorData {
  name: string
  category: FactorCategory
  loading: number
  return1M: number
  return3M: number
  return6M: number
  return1Y: number
  volatility: number
  sharpe: number
  correlation: number
  historical: Array<{ date: string; value: number }>
}

export interface FactorAnalysisProps {
  factors?: FactorData[]
  loading?: boolean
  className?: string
}

const FACTOR_CATEGORY_LABELS: Record<FactorCategory, string> = {
  style: 'Style Factors',
  sector: 'Sector Factors',
  macro: 'Macro Factors',
  thematic: 'Thematic Factors',
}

const FACTOR_COLORS: Record<string, string> = {
  'Market Beta': '#3b82f6',
  'Size': '#8b5cf6',
  'Value': '#10b981',
  'Momentum': '#f59e0b',
  'Quality': '#06b6d4',
  'Low Volatility': '#ef4444',
  'Dividend Yield': '#22c55e',
  'Growth': '#6366f1',
  'Small Cap': '#ec4899',
  'Technology': '#14b8a6',
}

function generateMockFactors(): FactorData[] {
  const factors = [
    { name: 'Market Beta', category: 'style' as FactorCategory },
    { name: 'Size', category: 'style' as FactorCategory },
    { name: 'Value', category: 'style' as FactorCategory },
    { name: 'Momentum', category: 'style' as FactorCategory },
    { name: 'Quality', category: 'style' as FactorCategory },
    { name: 'Low Volatility', category: 'style' as FactorCategory },
    { name: 'Technology', category: 'sector' as FactorCategory },
    { name: 'Healthcare', category: 'sector' as FactorCategory },
    { name: 'Financials', category: 'sector' as FactorCategory },
    { name: 'Energy', category: 'sector' as FactorCategory },
  ]

  return factors.map(factor => ({
    ...factor,
    loading: Math.random() * 2 - 1,
    return1M: (Math.random() - 0.3) * 10,
    return3M: (Math.random() - 0.3) * 20,
    return6M: (Math.random() - 0.3) * 30,
    return1Y: (Math.random() - 0.3) * 50,
    volatility: Math.random() * 30 + 10,
    sharpe: Math.random() * 2 - 0.5,
    correlation: Math.random() * 0.8 + 0.1,
    historical: Array.from({ length: 24 }, (_, i) => ({
      date: new Date(Date.now() - (24 - i) * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0].slice(0, 7),
      value: Math.random() * 40 - 20,
    })),
  }))
}

function FactorAnalysisSkeleton() {
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

function FactorCard({ factor, isSelected, onClick }: { factor: FactorData; isSelected: boolean; onClick: () => void }) {
  const isPositive = factor.return1Y >= 0
  const color = FACTOR_COLORS[factor.name] || '#6b7280'

  return (
    <div
      onClick={onClick}
      className={cn(
        'p-4 border rounded-lg cursor-pointer transition-all',
        isSelected ? 'border-primary ring-1 ring-primary bg-primary/5' : 'hover:border-primary/50'
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="font-semibold text-sm">{factor.name}</span>
        <Badge variant="outline" className="text-xs">{FACTOR_CATEGORY_LABELS[factor.category]}</Badge>
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className={cn('text-xl font-bold', isPositive ? 'text-green-600' : 'text-red-600')}>
            {isPositive ? '+' : ''}{factor.return1Y.toFixed(1)}%
          </p>
          <p className="text-xs text-muted-foreground">1Y Return</p>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium">{factor.sharpe.toFixed(2)}</p>
          <p className="text-xs text-muted-foreground">Sharpe</p>
        </div>
      </div>
    </div>
  )
}

function ReturnsChart({ factors, selectedFactor }: { factors: FactorData[]; selectedFactor: FactorData | null }) {
  const data = useMemo(() => {
    if (selectedFactor) return selectedFactor.historical
    return factors[0]?.historical || []
  }, [factors, selectedFactor])

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis dataKey="date" className="text-xs" tick={{ fontSize: 12 }} />
        <YAxis className="text-xs" tick={{ fontSize: 12 }} />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const value = payload[0].value
              const formattedValue = typeof value === 'number' ? value.toFixed(2) : String(value)
              return (
                <div className="bg-background border rounded-lg p-3 shadow-lg">
                  <p className="font-medium">{payload[0].payload.date}</p>
                  <p className="text-lg font-bold">{formattedValue}%</p>
                </div>
              )
            }
            return null
          }}
        />
        <Line type="monotone" dataKey="value" stroke={selectedFactor ? FACTOR_COLORS[selectedFactor.name] : '#3b82f6'} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

function LoadingVsReturnChart({ factors }: { factors: FactorData[] }) {
  const data = useMemo(() => factors.map(f => ({
    x: f.loading,
    y: f.return1Y,
    z: f.volatility,
    name: f.name,
  })), [factors])

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis type="number" dataKey="x" name="Loading" className="text-xs" tick={{ fontSize: 12 }} />
        <YAxis type="number" dataKey="y" name="Return" className="text-xs" tick={{ fontSize: 12 }} />
        <ZAxis type="number" dataKey="z" range={[50, 400]} name="Volatility" />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const d = payload[0].payload
              return (
                <div className="bg-background border rounded-lg p-3 shadow-lg">
                  <p className="font-medium">{d.name}</p>
                  <p className="text-sm">Loading: {d.x.toFixed(2)}</p>
                  <p className="text-sm">Return: {d.y.toFixed(1)}%</p>
                  <p className="text-sm">Volatility: {d.z.toFixed(0)}%</p>
                </div>
              )
            }
            return null
          }}
        />
        <Scatter name="Factors" data={data} fill="#3b82f6" />
      </ScatterChart>
    </ResponsiveContainer>
  )
}

function FactorReturnsBar({ factors }: { factors: FactorData[] }) {
  const sortedFactors = useMemo(() => [...factors].sort((a, b) => b.return1Y - a.return1Y), [factors])

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={sortedFactors} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis type="number" className="text-xs" tick={{ fontSize: 12 }} />
        <YAxis type="category" dataKey="name" className="text-xs" tick={{ fontSize: 10 }} width={100} />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const value = payload[0].value
              const formattedValue = typeof value === 'number' ? value.toFixed(1) : String(value)
              return (
                <div className="bg-background border rounded-lg p-3 shadow-lg">
                  <p className="font-medium">{payload[0].payload.name}</p>
                  <p className="text-lg font-bold">{formattedValue}%</p>
                </div>
              )
            }
            return null
          }}
        />
        <Bar dataKey="return1Y" fill="#3b82f6" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function FactorAnalysis({ factors: propFactors, loading = false, className }: FactorAnalysisProps) {
  const [period, setPeriod] = useState<'1M' | '3M' | '6M' | '1Y'>('1Y')
  const [category, setCategory] = useState<FactorCategory | 'all'>('all')
  const [selectedFactor, setSelectedFactor] = useState<FactorData | null>(null)

  const factors = useMemo(() => propFactors || generateMockFactors(), [propFactors])

  const filteredFactors = useMemo(() => {
    if (category === 'all') return factors
    return factors.filter(f => f.category === category)
  }, [factors, category])

  const summary = useMemo(() => {
    const topPerformer = [...filteredFactors].sort((a, b) => b.return1Y - a.return1Y)[0]
    const worstPerformer = [...filteredFactors].sort((a, b) => a.return1Y - b.return1Y)[0]
    const avgReturn = filteredFactors.reduce((sum, f) => sum + f.return1Y, 0) / filteredFactors.length

    return { topPerformer, worstPerformer, avgReturn }
  }, [filteredFactors])

  if (loading) return <FactorAnalysisSkeleton />

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Factor Analysis
            </CardTitle>
            <CardDescription>Factor performance and risk characteristics</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={category} onValueChange={(v: FactorCategory | 'all') => setCategory(v)}>
              <SelectTrigger className="w-36">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Factors</SelectItem>
                <SelectItem value="style">Style</SelectItem>
                <SelectItem value="sector">Sector</SelectItem>
                <SelectItem value="macro">Macro</SelectItem>
                <SelectItem value="thematic">Thematic</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="text-xs text-green-700 font-medium">Top Performer</span>
            </div>
            <p className="text-lg font-bold text-green-700">{summary.topPerformer?.name}</p>
            <p className="text-sm text-green-600">+{summary.topPerformer?.return1Y.toFixed(1)}%</p>
          </div>
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <span className="text-xs text-red-700 font-medium">Worst Performer</span>
            </div>
            <p className="text-lg font-bold text-red-700">{summary.worstPerformer?.name}</p>
            <p className="text-sm text-red-600">{summary.worstPerformer?.return1Y.toFixed(1)}%</p>
          </div>
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Average Return</span>
            </div>
            <p className={cn('text-2xl font-bold', summary.avgReturn >= 0 ? 'text-green-600' : 'text-red-600')}>
              {summary.avgReturn >= 0 ? '+' : ''}{summary.avgReturn.toFixed(1)}%
            </p>
          </div>
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Factors Analyzed</span>
            </div>
            <p className="text-2xl font-bold">{filteredFactors.length}</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          {filteredFactors.slice(0, 6).map((factor) => (
            <FactorCard
              key={factor.name}
              factor={factor}
              isSelected={selectedFactor?.name === factor.name}
              onClick={() => setSelectedFactor(factor.name === selectedFactor?.name ? null : factor)}
            />
          ))}
        </div>

        <Tabs defaultValue="returns" className="space-y-4">
          <TabsList>
            <TabsTrigger value="returns">Returns Over Time</TabsTrigger>
            <TabsTrigger value="comparison">Factor Comparison</TabsTrigger>
            <TabsTrigger value="loading">Loading vs Return</TabsTrigger>
          </TabsList>

          <TabsContent value="returns" className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold">
                {selectedFactor ? selectedFactor.name : 'All Factors'} - {period} Performance
              </h4>
              {selectedFactor && (
                <Button size="sm" variant="ghost" onClick={() => setSelectedFactor(null)}>
                  Show All
                </Button>
              )}
            </div>
            <ReturnsChart factors={filteredFactors} selectedFactor={selectedFactor} />
          </TabsContent>

          <TabsContent value="comparison" className="space-y-4">
            <h4 className="font-semibold">1-Year Returns by Factor</h4>
            <FactorReturnsBar factors={filteredFactors} />
          </TabsContent>

          <TabsContent value="loading" className="space-y-4">
            <h4 className="font-semibold">Factor Loading vs Return</h4>
            <p className="text-sm text-muted-foreground">Bubble size represents volatility</p>
            <LoadingVsReturnChart factors={filteredFactors} />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default FactorAnalysis
