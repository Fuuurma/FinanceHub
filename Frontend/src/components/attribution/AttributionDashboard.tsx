'use client'

import { useMemo, useState, useCallback, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  TrendingUp, TrendingDown, PieChart, BarChart3, Layers, ArrowUpRight, ArrowDownRight,
  Settings2, Target, Activity, Zap
} from 'lucide-react'
import type { Holding, AttributionPeriod } from '@/lib/types/holdings'
import type { BenchmarkType } from '@/lib/types/attribution'
import {
  calculateAttributionSummary,
  calculateHoldingAttribution,
  calculateSectorAttribution,
  calculateAssetClassAttribution,
  calculateBenchmarkComparison,
  DEFAULT_ATTRIBUTION_PERIODS,
  BENCHMARK_CONFIGS,
  BENCHMARK_CATEGORIES,
  type BenchmarkConfig,
} from '@/lib/utils/attribution-calculations'
import { SECTOR_COLORS } from '@/lib/types/attribution'
import { cn } from '@/lib/utils'
import { SectorAttributionChart } from './SectorAttributionChart'
import { HoldingAttributionTable } from './HoldingAttributionTable'
import { AttributionSummary } from './AttributionSummary'
import { useMemo as useReactMemo } from 'react'

interface AttributionDashboardProps {
  holdings: Holding[]
  loading?: boolean
  onPeriodChange?: (period: AttributionPeriod) => void
  benchmark?: BenchmarkType
}

export function AttributionDashboard({
  holdings,
  loading = false,
  onPeriodChange,
  initialBenchmark = 'sp500',
}: AttributionDashboardProps) {
  const [period, setPeriod] = useState<AttributionPeriod>('1m')
  const [activeTab, setActiveTab] = useState('summary')
  const [benchmark, setBenchmark] = useState<BenchmarkType>(initialBenchmark)
  const [showBenchmarkSettings, setShowBenchmarkSettings] = useState(false)
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['us_indices', 'etf'])

  const filteredBenchmarks = useMemo(() => {
    return BENCHMARK_CONFIGS.filter(b => selectedCategories.includes(b.category))
  }, [selectedCategories])

  const summary = useMemo(() => {
    const baseSummary = calculateAttributionSummary(holdings)
    const benchmarkConfig = BENCHMARK_CONFIGS.find(b => b.type === benchmark)
    if (benchmarkConfig) {
      return calculateBenchmarkComparison(baseSummary, holdings, benchmarkConfig, period)
    }
    return baseSummary
  }, [holdings, benchmark, period])

  const holdingAttribution = useMemo(() => calculateHoldingAttribution(holdings), [holdings])
  const sectorAttribution = useMemo(() => calculateSectorAttribution(holdings), [holdings])
  const assetClassAttribution = useMemo(() => calculateAssetClassAttribution(holdings), [holdings])

  const formatPercent = (value: number) =>
    `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)

  const benchmarkConfig = BENCHMARK_CONFIGS.find(b => b.type === benchmark)
  const excessReturn = summary.benchmark_comparison?.excess_return ?? 0

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-10 w-64" />
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-96" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Performance Attribution</h2>
          <p className="text-muted-foreground">
            Analyze how each holding, sector, and asset class contributed to your returns
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Benchmark Selector */}
          <Popover open={showBenchmarkSettings} onOpenChange={setShowBenchmarkSettings}>
            <PopoverTrigger asChild>
              <Button variant="outline" className="min-w-[180px]">
                <Target className="w-4 h-4 mr-2" />
                <span className="truncate">
                  {benchmarkConfig?.name || 'Select Benchmark'}
                </span>
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80" align="end">
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Benchmark Settings</h4>
                  <p className="text-sm text-muted-foreground">
                    Compare your portfolio performance against market indices, ETFs, or custom benchmarks.
                  </p>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs">Categories</Label>
                  <div className="flex flex-wrap gap-2">
                    {BENCHMARK_CATEGORIES.map(cat => (
                      <Badge
                        key={cat.value}
                        variant={selectedCategories.includes(cat.value) ? 'default' : 'outline'}
                        className="cursor-pointer"
                        onClick={() => {
                          if (selectedCategories.includes(cat.value)) {
                            setSelectedCategories(prev => prev.filter(c => c !== cat.value))
                          } else {
                            setSelectedCategories(prev => [...prev, cat.value])
                          }
                        }}
                      >
                        {cat.label}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  <Label className="text-xs">Select Benchmark</Label>
                  {filteredBenchmarks.map(b => (
                    <div
                      key={b.type}
                      className={cn(
                        'flex items-center gap-2 p-2 rounded cursor-pointer transition-colors',
                        benchmark === b.type ? 'bg-primary/10' : 'hover:bg-muted'
                      )}
                      onClick={() => {
                        setBenchmark(b.type)
                        setShowBenchmarkSettings(false)
                      }}
                    >
                      <div className={cn(
                        'w-3 h-3 rounded-full',
                        benchmark === b.type ? 'bg-primary' : 'border border-muted-foreground'
                      )} />
                      <div className="flex-1">
                        <div className="font-medium text-sm">{b.name}</div>
                        <div className="text-xs text-muted-foreground">{b.description}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </PopoverContent>
          </Popover>

          {/* Period Selector */}
          <Select
            value={period}
            onValueChange={(value) => {
              setPeriod(value as AttributionPeriod)
              onPeriodChange?.(value as AttributionPeriod)
            }}
          >
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Period" />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_ATTRIBUTION_PERIODS.map((p) => (
                <SelectItem key={p.value} value={p.value}>
                  {p.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Benchmark Comparison Header */}
      {summary.benchmark_comparison && (
        <Card className="bg-muted/50">
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">vs</span>
                  <span className="font-semibold">{benchmarkConfig?.name}</span>
                </div>
                <div className="h-8 w-px bg-border" />
                <div className="flex items-center gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Portfolio: </span>
                    <span className={cn(
                      'font-semibold',
                      summary.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                    )}>
                      {formatPercent(summary.total_return)}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">{benchmarkConfig?.name}: </span>
                    <span className={cn(
                      'font-semibold',
                      summary.benchmark_comparison.benchmark_return >= 0 ? 'text-green-600' : 'text-red-600'
                    )}>
                      {formatPercent(summary.benchmark_comparison.benchmark_return)}
                    </span>
                  </div>
                  <div className="h-4 w-px bg-border" />
                  <div>
                    <span className="text-muted-foreground">Excess Return: </span>
                    <span className={cn(
                      'font-semibold',
                      excessReturn >= 0 ? 'text-green-600' : 'text-red-600'
                    )}>
                      {formatPercent(excessReturn)}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                {summary.benchmark_comparison.information_ratio !== undefined && (
                  <div className="flex items-center gap-1">
                    <Activity className="w-3 h-3" />
                    <span>IR: {summary.benchmark_comparison.information_ratio.toFixed(2)}</span>
                  </div>
                )}
                {summary.benchmark_comparison.beta !== undefined && (
                  <div className="flex items-center gap-1">
                    <Zap className="w-3 h-3" />
                    <span>β: {summary.benchmark_comparison.beta.toFixed(2)}</span>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Return</CardTitle>
            {summary.total_return >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className={cn(
              'text-2xl font-bold',
              summary.total_return >= 0 ? 'text-green-600' : 'text-red-600'
            )}>
              {formatPercent(summary.total_return)}
            </div>
            <p className="text-xs text-muted-foreground">
              {formatCurrency(summary.total_contribution)} contribution
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Top Contributor</CardTitle>
            <ArrowUpRight className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.top_contributor?.symbol || '-'}</div>
            <p className="text-xs text-muted-foreground">
              {summary.top_contributor
                ? `${formatPercent(summary.top_contributor.contribution)} contribution`
                : 'No data'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Worst Performer</CardTitle>
            <ArrowDownRight className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.bottom_contributor?.symbol || '-'}</div>
            <p className="text-xs text-muted-foreground">
              {summary.bottom_contributor
                ? `${formatPercent(summary.bottom_contributor.contribution)} contribution`
                : 'No data'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Allocation vs Selection</CardTitle>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>Allocation</span>
                <span className={cn(
                  'font-medium',
                  summary.allocation_effect >= 0 ? 'text-green-600' : 'text-red-600'
                )}>
                  {formatPercent(summary.allocation_effect)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Selection</span>
                <span className={cn(
                  'font-medium',
                  summary.selection_effect >= 0 ? 'text-green-600' : 'text-red-600'
                )}>
                  {formatPercent(summary.selection_effect)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Attribution Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Attribution Breakdown</CardTitle>
          <CardDescription>
            {summary.positive_holdings} holdings positive, {summary.negative_holdings} negative
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="mb-4">
              <TabsTrigger value="summary">
                <Layers className="w-4 h-4 mr-2" />
                Summary
              </TabsTrigger>
              <TabsTrigger value="holdings">
                <BarChart3 className="w-4 h-4 mr-2" />
                By Holding
              </TabsTrigger>
              <TabsTrigger value="sectors">
                <PieChart className="w-4 h-4 mr-2" />
                By Sector
              </TabsTrigger>
              <TabsTrigger value="assets">
                <Layers className="w-4 h-4 mr-2" />
                By Asset Class
              </TabsTrigger>
            </TabsList>

            <TabsContent value="summary">
              <AttributionSummary
                summary={summary}
                sectorAttribution={sectorAttribution}
                assetClassAttribution={assetClassAttribution}
              />
            </TabsContent>

            <TabsContent value="holdings">
              <HoldingAttributionTable
                attribution={holdingAttribution}
                formatCurrency={formatCurrency}
                formatPercent={formatPercent}
              />
            </TabsContent>

            <TabsContent value="sectors">
              <SectorAttributionChart
                data={sectorAttribution}
                type="bar"
                showBenchmark={!!summary.benchmark_comparison}
                benchmarkReturn={summary.benchmark_comparison?.benchmark_return}
              />
            </TabsContent>

            <TabsContent value="assets">
              <SectorAttributionChart
                data={sectorAttribution}
                type="pie"
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
