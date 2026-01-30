'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  TrendingDown,
  PieChart,
  Layers,
} from 'lucide-react'
import type {
  AttributionSummary,
  SectorAttribution,
  AssetClassAttribution,
} from '@/lib/types/attribution'
import { SECTOR_COLORS } from '@/lib/types/attribution'
import { cn } from '@/lib/utils'

interface AttributionSummaryProps {
  summary: AttributionSummary
  sectorAttribution: SectorAttribution[]
  assetClassAttribution: AssetClassAttribution[]
}

export function AttributionSummary({
  summary,
  sectorAttribution,
  assetClassAttribution,
}: AttributionSummaryProps) {
  const formatPercent = (value: number) =>
    `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)

  return (
    <div className="space-y-6">
      {/* Top/Bottom Contributors */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="border-green-200 bg-green-50/50 dark:bg-green-900/20 dark:border-green-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <ArrowUpRight className="h-4 w-4 text-green-600" />
              Top Contributors
            </CardTitle>
          </CardHeader>
          <CardContent>
            {summary.top_contributor ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-lg">{summary.top_contributor.symbol}</p>
                    <p className="text-sm text-muted-foreground">{summary.top_contributor.name}</p>
                  </div>
                  <Badge className="bg-green-100 text-green-700">
                    {formatPercent(summary.top_contributor.contribution)}
                  </Badge>
                </div>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div>
                    <p className="text-muted-foreground">Weight</p>
                    <p className="font-medium">{summary.top_contributor.weight.toFixed(1)}%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Return</p>
                    <p className="font-medium text-green-600">
                      {formatPercent(summary.top_contributor.return)}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Value</p>
                    <p className="font-medium">{formatCurrency(summary.top_contributor.value_end)}</p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">No data available</p>
            )}
          </CardContent>
        </Card>

        <Card className="border-red-200 bg-red-50/50 dark:bg-red-900/20 dark:border-red-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <ArrowDownRight className="h-4 w-4 text-red-600" />
              Bottom Contributors
            </CardTitle>
          </CardHeader>
          <CardContent>
            {summary.bottom_contributor ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-lg">{summary.bottom_contributor.symbol}</p>
                    <p className="text-sm text-muted-foreground">{summary.bottom_contributor.name}</p>
                  </div>
                  <Badge className="bg-red-100 text-red-700">
                    {formatPercent(summary.bottom_contributor.contribution)}
                  </Badge>
                </div>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div>
                    <p className="text-muted-foreground">Weight</p>
                    <p className="font-medium">{summary.bottom_contributor.weight.toFixed(1)}%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Return</p>
                    <p className="font-medium text-red-600">
                      {formatPercent(summary.bottom_contributor.return)}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Value</p>
                    <p className="font-medium">{formatCurrency(summary.bottom_contributor.value_end)}</p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">No data available</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Sector Performance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="h-5 w-5" />
            Sector Performance
          </CardTitle>
          <CardDescription>
            How each sector contributed to overall returns
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {sectorAttribution.slice(0, 6).map((sector) => (
              <div
                key={sector.sector}
                className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: SECTOR_COLORS[sector.sector] || '#6B7280' }}
                  />
                  <div>
                    <p className="font-medium">{sector.sector}</p>
                    <p className="text-xs text-muted-foreground">
                      {sector.holdings_count} holding{sector.holdings_count !== 1 ? 's' : ''}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Weight</p>
                    <p className="font-medium">{sector.weight.toFixed(1)}%</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Return</p>
                    <p className={cn(
                      'font-medium',
                      sector.return >= 0 ? 'text-green-600' : 'text-red-600'
                    )}>
                      {formatPercent(sector.return)}
                    </p>
                  </div>
                  <div className="text-right w-20">
                    <p className="text-sm text-muted-foreground">Contribution</p>
                    <p className={cn(
                      'font-semibold',
                      sector.contribution >= 0 ? 'text-green-600' : 'text-red-600'
                    )}>
                      {formatPercent(sector.contribution)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Asset Class Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Layers className="h-5 w-5" />
            Asset Class Breakdown
          </CardTitle>
          <CardDescription>
            Performance by asset class
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {assetClassAttribution.map((assetClass) => (
              <div
                key={assetClass.asset_class}
                className="p-4 rounded-lg border"
              >
                <div className="flex items-center justify-between mb-2">
                  <p className="font-medium capitalize">{assetClass.asset_class.replace('_', ' ')}</p>
                  <Badge variant="secondary">
                    {assetClass.holdings_count} holding{assetClass.holdings_count !== 1 ? 's' : ''}
                  </Badge>
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Weight</span>
                    <span className="font-medium">{assetClass.weight.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Return</span>
                    <span className={cn(
                      'font-medium',
                      assetClass.return >= 0 ? 'text-green-600' : 'text-red-600'
                    )}>
                      {formatPercent(assetClass.return)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Contribution</span>
                    <span className={cn(
                      'font-semibold',
                      assetClass.contribution >= 0 ? 'text-green-600' : 'text-red-600'
                    )}>
                      {formatPercent(assetClass.contribution)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Attribution Effect */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Attribution Effect Analysis
          </CardTitle>
          <CardDescription>
            Breakdown of allocation vs selection effects
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
              <p className="text-sm text-muted-foreground mb-1">Allocation Effect</p>
              <p className={cn(
                'text-2xl font-bold',
                summary.allocation_effect >= 0 ? 'text-blue-600' : 'text-red-600'
              )}>
                {formatPercent(summary.allocation_effect)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Impact of weight differences vs benchmark
              </p>
            </div>
            <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
              <p className="text-sm text-muted-foreground mb-1">Selection Effect</p>
              <p className={cn(
                'text-2xl font-bold',
                summary.selection_effect >= 0 ? 'text-green-600' : 'text-red-600'
              )}>
                {formatPercent(summary.selection_effect)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Impact of security selection within sectors
              </p>
            </div>
            <div className="p-4 rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
              <p className="text-sm text-muted-foreground mb-1">Total Effect</p>
              <p className={cn(
                'text-2xl font-bold',
                summary.total_effect >= 0 ? 'text-purple-600' : 'text-red-600'
              )}>
                {formatPercent(summary.total_effect)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Combined allocation + selection effects
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
