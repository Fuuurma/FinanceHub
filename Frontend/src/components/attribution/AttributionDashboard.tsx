'use client'

import { useMemo, useState } from 'react'
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
import { TrendingUp, TrendingDown, PieChart, BarChart3, Layers, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import type { Holding, AttributionPeriod } from '@/lib/types/holdings'
import {
  calculateAttributionSummary,
  calculateHoldingAttribution,
  calculateSectorAttribution,
  calculateAssetClassAttribution,
  DEFAULT_ATTRIBUTION_PERIODS,
} from '@/lib/utils/attribution-calculations'
import { SECTOR_COLORS } from '@/lib/types/attribution'
import { cn } from '@/lib/utils'
import { SectorAttributionChart } from './SectorAttributionChart'
import { HoldingAttributionTable } from './HoldingAttributionTable'
import { AttributionSummary } from './AttributionSummary'

interface AttributionDashboardProps {
  holdings: Holding[]
  loading?: boolean
  onPeriodChange?: (period: AttributionPeriod) => void
}

export function AttributionDashboard({
  holdings,
  loading = false,
  onPeriodChange,
}: AttributionDashboardProps) {
  const [period, setPeriod] = useState<AttributionPeriod>('1m')
  const [activeTab, setActiveTab] = useState('summary')

  const summary = useMemo(() => calculateAttributionSummary(holdings), [holdings])
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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-10 w-32" />
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
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Performance Attribution</h2>
          <p className="text-muted-foreground">
            Analyze how each holding, sector, and asset class contributed to your returns
          </p>
        </div>
        <Select
          value={period}
          onValueChange={(value) => {
            setPeriod(value as AttributionPeriod)
            onPeriodChange?.(value as AttributionPeriod)
          }}
        >
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Select period" />
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
