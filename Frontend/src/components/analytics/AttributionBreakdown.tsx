'use client'

import { useState, useMemo } from 'react'
import { TrendingUp, TrendingDown, PieChart, BarChart3, Activity, Percent, DollarSign, Filter } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

export type AttributionFactor = 'market' | 'size' | 'value' | 'momentum' | 'quality' | 'volatility' | 'carry' | 'selection' | 'interaction'

export interface AttributionData {
  factor: AttributionFactor
  label: string
  contribution: number
  contributionPercent: number
  allocationEffect: number
  selectionEffect: number
  interactionEffect: number
  totalEffect: number
  benchmarkWeight: number
  portfolioWeight: number
  activeWeight: number
}

export interface AttributionSummary {
  totalReturn: number
  benchmarkReturn: number
  excessReturn: number
  totalAttribution: number
  unexplained: number
}

export interface AttributionBreakdownProps {
  symbol?: string
  data?: AttributionData[]
  summary?: AttributionSummary
  loading?: boolean
  className?: string
}

const FACTOR_LABELS: Record<AttributionFactor, string> = {
  market: 'Market Beta',
  size: 'Size',
  value: 'Value',
  momentum: 'Momentum',
  quality: 'Quality',
  volatility: 'Volatility',
  carry: 'Carry',
  selection: 'Security Selection',
  interaction: 'Interaction',
}

const FACTOR_COLORS: Record<AttributionFactor, string> = {
  market: 'bg-blue-500',
  size: 'bg-indigo-500',
  value: 'bg-green-500',
  momentum: 'bg-purple-500',
  quality: 'bg-cyan-500',
  volatility: 'bg-orange-500',
  carry: 'bg-pink-500',
  selection: 'bg-teal-500',
  interaction: 'bg-gray-500',
}

function generateMockAttribution(): AttributionData[] {
  const factors: AttributionFactor[] = ['market', 'size', 'value', 'momentum', 'quality', 'selection']
  return factors.map((factor, i) => ({
    factor,
    label: FACTOR_LABELS[factor],
    contribution: (Math.random() - 0.3) * 5,
    contributionPercent: Math.random() * 100,
    allocationEffect: (Math.random() - 0.3) * 2,
    selectionEffect: (Math.random() - 0.3) * 3,
    interactionEffect: (Math.random() - 0.5) * 0.5,
    totalEffect: (Math.random() - 0.3) * 5,
    benchmarkWeight: 10 + Math.random() * 30,
    portfolioWeight: 10 + Math.random() * 30,
    activeWeight: (Math.random() - 0.5) * 10,
  }))
}

function generateMockSummary(): AttributionSummary {
  return {
    totalReturn: Math.random() * 20 - 5,
    benchmarkReturn: Math.random() * 15 - 5,
    excessReturn: Math.random() * 10 - 2,
    totalAttribution: Math.random() * 8 - 1,
    unexplained: (Math.random() - 0.5) * 2,
  }
}

function AttributionBreakdownSkeleton() {
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

function FactorRow({ data, isExpanded, onClick }: { data: AttributionData; isExpanded: boolean; onClick: () => void }) {
  const isPositive = data.totalEffect >= 0

  return (
    <div className="space-y-2">
      <div
        onClick={onClick}
        className="flex items-center justify-between p-4 border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className={cn('w-3 h-3 rounded-full', FACTOR_COLORS[data.factor])} />
          <div>
            <p className="font-semibold">{data.label}</p>
            <p className="text-sm text-muted-foreground">
              Portfolio: {data.portfolioWeight.toFixed(1)}% | Benchmark: {data.benchmarkWeight.toFixed(1)}%
            </p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-right">
            <p className={cn('font-bold', isPositive ? 'text-green-600' : 'text-red-600')}>
              {isPositive ? '+' : ''}{data.totalEffect.toFixed(2)}%
            </p>
            <p className="text-xs text-muted-foreground">Total Effect</p>
          </div>
          <Progress value={50 + data.totalEffect * 10} className="w-24 h-2" />
        </div>
      </div>
      {isExpanded && (
        <div className="p-4 bg-muted/50 rounded-lg border ml-4 space-y-3">
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-xs text-muted-foreground mb-1">Allocation Effect</p>
              <p className={cn('font-bold', data.allocationEffect >= 0 ? 'text-green-600' : 'text-red-600')}>
                {data.allocationEffect >= 0 ? '+' : ''}{data.allocationEffect.toFixed(3)}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-muted-foreground mb-1">Selection Effect</p>
              <p className={cn('font-bold', data.selectionEffect >= 0 ? 'text-green-600' : 'text-red-600')}>
                {data.selectionEffect >= 0 ? '+' : ''}{data.selectionEffect.toFixed(3)}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-muted-foreground mb-1">Interaction Effect</p>
              <p className={cn('font-bold', data.interactionEffect >= 0 ? 'text-green-600' : 'text-red-600')}>
                {data.interactionEffect >= 0 ? '+' : ''}{data.interactionEffect.toFixed(3)}%
              </p>
            </div>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Active Weight</span>
            <Badge variant={data.activeWeight > 0 ? 'default' : 'secondary'}>
              {data.activeWeight >= 0 ? '+' : ''}{data.activeWeight.toFixed(2)}%
            </Badge>
          </div>
        </div>
      )}
    </div>
  )
}

export function AttributionBreakdown({ data: propData, summary: propSummary, loading = false, className }: AttributionBreakdownProps) {
  const [period, setPeriod] = useState<'mtd' | 'qtd' | 'ytd' | '1y' | '3y' | '5y'>('ytd')
  const [expandedFactor, setExpandedFactor] = useState<AttributionFactor | null>(null)

  const data = useMemo(() => propData || generateMockAttribution(), [propData])
  const summary = useMemo(() => propSummary || generateMockSummary(), [propSummary])

  const sortedData = useMemo(() => {
    return [...data].sort((a, b) => Math.abs(b.totalEffect) - Math.abs(a.totalEffect))
  }, [data])

  const positiveContributors = useMemo(() => data.filter(d => d.totalEffect > 0), [data])
  const negativeContributors = useMemo(() => data.filter(d => d.totalEffect < 0), [data])

  if (loading) return <AttributionBreakdownSkeleton />

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <PieChart className="h-5 w-5" />
              Performance Attribution
            </CardTitle>
            <CardDescription>Factor contribution to portfolio returns</CardDescription>
          </div>
          <Select value={period} onValueChange={(v: any) => setPeriod(v)}>
            <SelectTrigger className="w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="mtd">MTD</SelectItem>
              <SelectItem value="qtd">QTD</SelectItem>
              <SelectItem value="ytd">YTD</SelectItem>
              <SelectItem value="1y">1 Year</SelectItem>
              <SelectItem value="3y">3 Year</SelectItem>
              <SelectItem value="5y">5 Year</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Portfolio Return</span>
            </div>
            <p className={cn('text-2xl font-bold', summary.totalReturn >= 0 ? 'text-green-600' : 'text-red-600')}>
              {summary.totalReturn >= 0 ? '+' : ''}{summary.totalReturn.toFixed(2)}%
            </p>
          </div>
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Benchmark Return</span>
            </div>
            <p className="text-2xl font-bold">{summary.benchmarkReturn >= 0 ? '+' : ''}{summary.benchmarkReturn.toFixed(2)}%</p>
          </div>
          <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-primary" />
              <span className="text-xs text-primary font-medium">Excess Return</span>
            </div>
            <p className={cn('text-2xl font-bold', summary.excessReturn >= 0 ? 'text-green-600' : 'text-red-600')}>
              {summary.excessReturn >= 0 ? '+' : ''}{summary.excessReturn.toFixed(2)}%
            </p>
          </div>
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Percent className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Unexplained</span>
            </div>
            <p className="text-2xl font-bold">{summary.unexplained >= 0 ? '+' : ''}{summary.unexplained.toFixed(2)}%</p>
          </div>
        </div>

        <Tabs defaultValue="breakdown" className="space-y-4">
          <TabsList>
            <TabsTrigger value="breakdown">Factor Breakdown</TabsTrigger>
            <TabsTrigger value="allocation">Allocation</TabsTrigger>
            <TabsTrigger value="selection">Selection</TabsTrigger>
          </TabsList>

          <TabsContent value="breakdown" className="space-y-3">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-xs">Positive ({positiveContributors.length})</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-xs">Negative ({negativeContributors.length})</span>
              </div>
            </div>
            {sortedData.map((item) => (
              <FactorRow
                key={item.factor}
                data={item}
                isExpanded={expandedFactor === item.factor}
                onClick={() => setExpandedFactor(expandedFactor === item.factor ? null : item.factor)}
              />
            ))}
          </TabsContent>

          <TabsContent value="allocation" className="space-y-3">
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold mb-4">Allocation Effects by Factor</h4>
              <div className="space-y-3">
                {data.map((item) => (
                  <div key={item.factor} className="flex items-center gap-4">
                    <div className="w-32 truncate">{item.label}</div>
                    <Progress value={50 + item.allocationEffect * 20} className="flex-1 h-2" />
                    <div className="w-16 text-right">
                      <span className={cn('text-sm font-medium', item.allocationEffect >= 0 ? 'text-green-600' : 'text-red-600')}>
                        {item.allocationEffect >= 0 ? '+' : ''}{item.allocationEffect.toFixed(3)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="selection" className="space-y-3">
            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold mb-4">Selection Effects by Factor</h4>
              <div className="space-y-3">
                {data.map((item) => (
                  <div key={item.factor} className="flex items-center gap-4">
                    <div className="w-32 truncate">{item.label}</div>
                    <Progress value={50 + item.selectionEffect * 20} className="flex-1 h-2" />
                    <div className="w-16 text-right">
                      <span className={cn('text-sm font-medium', item.selectionEffect >= 0 ? 'text-green-600' : 'text-red-600')}>
                        {item.selectionEffect >= 0 ? '+' : ''}{item.selectionEffect.toFixed(3)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default AttributionBreakdown
