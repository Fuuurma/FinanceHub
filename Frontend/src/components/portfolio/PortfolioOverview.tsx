'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import type { Portfolio, PortfolioHolding, PortfolioHistory, PortfolioMetrics } from '@/lib/types'
import { TrendingUp, TrendingDown, PieChart, ArrowUpRight, ArrowDownRight } from 'lucide-react'

interface PortfolioOverviewProps {
  portfolio: Portfolio
  holdings: PortfolioHolding[]
  history: PortfolioHistory[]
  metrics: PortfolioMetrics | null
}

export default function PortfolioOverview({ portfolio, holdings, history, metrics }: PortfolioOverviewProps) {
  const topGainers = holdings.filter((h) => h.unrealized_pnl_percent > 0).slice(0, 5)
  const topLosers = holdings.filter((h) => h.unrealized_pnl_percent < 0).slice(0, 5)

  const assetAllocation = holdings.reduce(
    (acc, h) => {
      const type = h.asset_type || 'other'
      acc[type] = (acc[type] || 0) + h.current_value
      return acc
    },
    {} as Record<string, number>
  )

  const totalValue = Object.values(assetAllocation).reduce((sum, v) => sum + v, 0)

  const sectorAllocation = holdings.reduce(
    (acc, h) => {
      const sector = h.sector || 'Other'
      acc[sector] = (acc[sector] || 0) + h.current_value
      return acc
    },
    {} as Record<string, number>
  )

  return (
    <div className="space-y-6">
      {/* Asset Allocation */}
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
            <div className="space-y-3">
              {Object.entries(assetAllocation).map(([type, value]) => (
                <div key={type} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="capitalize">{type}</span>
                    <span className="text-muted-foreground">{formatCurrency(value)}</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${(value / totalValue) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="w-5 h-5" />
              Sector Allocation
            </CardTitle>
            <CardDescription>Distribution by sector</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(sectorAllocation)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([sector, value]) => (
                  <div key={sector} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>{sector}</span>
                      <span className="text-muted-foreground">{formatCurrency(value)}</span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-secondary rounded-full"
                        style={{ width: `${(value / totalValue) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
            </div>
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
