'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import type { Portfolio, PortfolioHolding, PortfolioHistory, PortfolioMetrics } from '@/lib/types'
import type { AssetAllocationItem } from '@/lib/types/holdings'
import { HoldingsAllocationChart } from '@/components/charts/HoldingsAllocationChart'
import { TopHoldingsChart } from '@/components/charts/TopHoldingsChart'
import { TrendingUp, TrendingDown, PieChart, BarChart3, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { useMemo } from 'react'

interface PortfolioOverviewProps {
  portfolio: Portfolio
  holdings: PortfolioHolding[]
  history: PortfolioHistory[]
  metrics: PortfolioMetrics | null
}

export default function PortfolioOverview({ portfolio, holdings, history, metrics }: PortfolioOverviewProps) {
  const topGainers = holdings.filter((h) => h.unrealized_pnl_percent > 0).slice(0, 5)
  const topLosers = holdings.filter((h) => h.unrealized_pnl_percent < 0).slice(0, 5)

  const assetAllocation: AssetAllocationItem[] = useMemo(() => {
    const allocationMap = holdings.reduce(
      (acc, h) => {
        const type = h.asset_type || 'other'
        if (!acc[type]) {
          acc[type] = { asset_class: type as any, value: 0, percentage: 0, holdings_count: 0 }
        }
        acc[type].value += h.current_value
        acc[type].holdings_count += 1
        return acc
      },
      {} as Record<string, AssetAllocationItem>
    )

    const totalValue = Object.values(allocationMap).reduce((sum, v) => sum + v.value, 0)

    return Object.values(allocationMap).map((item) => ({
      ...item,
      percentage: totalValue > 0 ? (item.value / totalValue) * 100 : 0,
    }))
  }, [holdings])

  const totalValue = assetAllocation.reduce((sum, item) => sum + item.value, 0)

  return (
    <div className="space-y-6">
      {/* Asset Allocation and Top Holdings */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="w-5 h-5" />
              Asset Allocation
            </CardTitle>
            <CardDescription>Distribution by asset type</CardDescription>
          </CardHeader>
          <CardContent>
            <HoldingsAllocationChart data={assetAllocation} type="donut" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Top Holdings
            </CardTitle>
            <CardDescription>Top 10 holdings by value</CardDescription>
          </CardHeader>
          <CardContent>
            <TopHoldingsChart holdings={holdings} topN={10} />
          </CardContent>
        </Card>
      </div>

      {/* Top Performers */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-600">
              <TrendingUp className="w-5 h-5" />
              Top Gainers
            </CardTitle>
          </CardHeader>
          <CardContent>
            {topGainers.length === 0 ? (
              <p className="text-muted-foreground text-sm">No gains yet</p>
            ) : (
              <div className="space-y-3">
                {topGainers.map((holding) => (
                  <div key={holding.id} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{holding.symbol}</p>
                      <p className="text-sm text-muted-foreground">{holding.name}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-green-600">
                        +{formatPercent(holding.unrealized_pnl_percent)}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {formatCurrency(holding.unrealized_pnl)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <TrendingDown className="w-5 h-5" />
              Top Losers
            </CardTitle>
          </CardHeader>
          <CardContent>
            {topLosers.length === 0 ? (
              <p className="text-muted-foreground text-sm">No losses yet</p>
            ) : (
              <div className="space-y-3">
                {topLosers.map((holding) => (
                  <div key={holding.id} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{holding.symbol}</p>
                      <p className="text-sm text-muted-foreground">{holding.name}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-red-600">
                        {formatPercent(holding.unrealized_pnl_percent)}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {formatCurrency(holding.unrealized_pnl)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      {metrics && (
        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
            <CardDescription>Key performance indicators for the selected period</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Total Return</p>
                <p className={cn('text-2xl font-bold', metrics.total_return >= 0 ? 'text-green-600' : 'text-red-600')}>
                  {formatPercent(metrics.total_return_percent)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Annualized Return</p>
                <p className="text-2xl font-bold">{formatPercent(metrics.annualized_return)}</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Volatility</p>
                <p className="text-2xl font-bold">{formatPercent(metrics.volatility)}</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
                <p className="text-2xl font-bold">{metrics.sharpe_ratio.toFixed(2)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
