'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { portfoliosApi } from '@/lib/api/portfolio'
import type { Portfolio, PortfolioHolding, PortfolioHistory, PortfolioMetrics } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowUpRight, ArrowDownRight, Wallet, TrendingUp, TrendingDown, PieChart, BarChart3, ExternalLink } from 'lucide-react'
import { cn, formatCurrency, formatPercent, formatDate } from '@/lib/utils'
import Link from 'next/link'

export default function SharedPortfolioPage() {
  const params = useParams()
  const portfolioId = params.portfolioId as string

  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [holdings, setHoldings] = useState<PortfolioHolding[]>([])
  const [history, setHistory] = useState<PortfolioHistory[]>([])
  const [metrics, setMetrics] = useState<PortfolioMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      if (!portfolioId) return

      setLoading(true)
      setError(null)

      try {
        const [portfolioData, holdingsData, historyData, metricsData] = await Promise.all([
          portfoliosApi.getPortfolio(portfolioId),
          portfoliosApi.getHoldings(portfolioId).catch(() => [] as PortfolioHolding[]),
          portfoliosApi.getHistory(portfolioId, '1m').catch(() => [] as PortfolioHistory[]),
          portfoliosApi.getMetrics(portfolioId, '1m').catch(() => null),
        ])

        setPortfolio(portfolioData)
        setHoldings(holdingsData)
        setHistory(historyData)
        setMetrics(metricsData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load portfolio')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [portfolioId])

  if (loading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (error || !portfolio) {
    return (
      <div className="space-y-6 p-6">
        <Card className="border-destructive">
          <CardContent className="pt-6 text-center">
            <Wallet className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Portfolio Not Found</h3>
            <p className="text-muted-foreground mb-4">
              {error || 'This portfolio may be private or no longer exists.'}
            </p>
            <Link href="/portfolios">
              <Button>Go to My Portfolios</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const totalValue = portfolio.total_value
  const dayPnl = portfolio.day_pnl
  const totalPnl = portfolio.total_pnl

  // Calculate allocation
  const assetAllocation = holdings.reduce((acc: Record<string, number>, h: PortfolioHolding) => {
    const type = h.asset_type || 'other'
    acc[type] = (acc[type] || 0) + h.current_value
    return acc
  }, {})

  const totalAllocValue = Object.values(assetAllocation).reduce((sum, v) => sum + v, 0)

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">{portfolio.name}</h1>
            <Badge variant="outline" className="text-xs">
              Shared Portfolio
            </Badge>
          </div>
          {portfolio.description && (
            <p className="text-muted-foreground mt-1">{portfolio.description}</p>
          )}
          <p className="text-sm text-muted-foreground mt-1">
            Last updated: {formatDate(portfolio.updated_at)}
          </p>
        </div>
        <Link href="/portfolios">
          <Button variant="outline" size="sm">
            <ExternalLink className="w-4 h-4 mr-2" />
            View My Portfolios
          </Button>
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(totalValue)}</div>
            <div className="flex items-center text-sm">
              {dayPnl >= 0 ? (
                <ArrowUpRight className="w-4 h-4 text-green-500 mr-1" />
              ) : (
                <ArrowDownRight className="w-4 h-4 text-red-500 mr-1" />
              )}
              <span className={cn(dayPnl >= 0 ? 'text-green-500' : 'text-red-500')}>
                {formatCurrency(Math.abs(dayPnl))} ({formatPercent(portfolio.day_pnl_percent)})
              </span>
              <span className="text-muted-foreground ml-1">today</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Gain/Loss</CardTitle>
            {totalPnl >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(totalPnl)}</div>
            <div className="flex items-center text-sm">
              <span className={cn(totalPnl >= 0 ? 'text-green-500' : 'text-red-500')}>
                {formatPercent(portfolio.total_pnl_percent)}
              </span>
              <span className="text-muted-foreground ml-1">all time</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Holdings</CardTitle>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{holdings.length}</div>
            <p className="text-sm text-muted-foreground">assets in portfolio</p>
          </CardContent>
        </Card>
      </div>

      {/* Asset Allocation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="w-5 h-5" />
            Asset Allocation
          </CardTitle>
          <CardDescription>Distribution by asset type</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
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
                      style={{ width: `${(value / totalAllocValue) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="flex items-center justify-center">
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Total Value</p>
                <p className="text-3xl font-bold">{formatCurrency(totalAllocValue)}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Holdings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Top Holdings
          </CardTitle>
          <CardDescription>By current value</CardDescription>
        </CardHeader>
        <CardContent>
          {holdings.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No holdings in this portfolio</p>
          ) : (
            <div className="space-y-3">
              {holdings
                .sort((a, b) => b.current_value - a.current_value)
                .slice(0, 10)
                .map((holding) => (
                  <div
                    key={holding.id}
                    className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50"
                  >
                    <div>
                      <p className="font-medium">{holding.symbol}</p>
                      <p className="text-sm text-muted-foreground">{holding.name}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{formatCurrency(holding.current_value)}</p>
                      <p className="text-sm text-muted-foreground">
                        {holding.quantity.toLocaleString()} @ {formatCurrency(holding.current_price)}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      {metrics && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Performance Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground">Total Return</p>
                <p className={cn('text-2xl font-bold', metrics.total_return >= 0 ? 'text-green-600' : 'text-red-600')}>
                  {formatPercent(metrics.total_return_percent)}
                </p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground">Annualized</p>
                <p className="text-2xl font-bold">{formatPercent(metrics.annualized_return)}</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground">Volatility</p>
                <p className="text2xl font-bold">{formatPercent(metrics.volatility)}</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
                <p className="text2xl font-bold">{metrics.sharpe_ratio.toFixed(2)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Footer */}
      <div className="text-center text-sm text-muted-foreground">
        <p>Shared via FinanceHub</p>
      </div>
    </div>
  )
}
