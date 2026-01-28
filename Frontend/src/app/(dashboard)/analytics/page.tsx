'use client'

import { useEffect, useState } from 'react'
import { portfolioAnalyticsApi } from '@/lib/api/portfolio-analytics'
import type { PortfolioAnalytics as PortfolioAnalyticsType, AnalyticsPeriod } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { TrendingUp, TrendingDown, PieChart, BarChart3, RefreshCw, Download, Calendar } from 'lucide-react'

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<AnalyticsPeriod>('7d')
  const [analytics, setAnalytics] = useState<PortfolioAnalyticsType | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const periods: { value: AnalyticsPeriod, label: string }[] = [
    { value: '1d', label: '1 Day' },
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' },
  ]

  useEffect(() => {
    fetchAnalytics()
  }, [period])

  const fetchAnalytics = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await portfolioAnalyticsApi.getAnalytics(period)
      if (response) {
        setAnalytics(response)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = () => {
    if (!analytics) return
    
    const data = JSON.stringify(analytics, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `portfolio-analytics-${period}-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Portfolio Analytics</h1>
          <p className="text-muted-foreground">Detailed portfolio performance analysis</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchAnalytics} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" onClick={handleExport} disabled={!analytics || loading}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        {periods.map((p) => (
          <Button
            key={p.value}
            variant={period === p.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => setPeriod(p.value)}
            disabled={loading}
          >
            {p.label}
          </Button>
        ))}
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
          <p className="font-semibold">Error</p>
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="grid gap-6 md:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-32" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : analytics ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-green-500" />
                Total Return
              </CardTitle>
              <CardDescription>Portfolio performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-3xl font-bold">
                  {analytics.total_return >= 0 ? '+' : ''}{analytics.total_return.toFixed(2)}%
                </div>
                <p className={`text-sm ${analytics.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {analytics.total_return >= 0 ? 'Profit' : 'Loss'}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <DollarSign className="w-5 h-5 mr-2 text-blue-500" />
                Total Value
              </CardTitle>
              <CardDescription>Current portfolio value</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-3xl font-bold">
                  ${analytics.total_value.toLocaleString()}
                </div>
                <p className="text-sm text-muted-foreground">
                  {analytics.total_value_change >= 0 ? '+' : ''}${Math.abs(analytics.total_value_change).toLocaleString()} ({analytics.total_value_change_percent.toFixed(2)}%)
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="md:col-span-2 lg:col-span-3">
            <CardHeader>
              <CardTitle>Performance by Asset</CardTitle>
              <CardDescription>Return breakdown by asset type</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.performance_by_asset.map((asset) => (
                  <div key={asset.asset_type} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <PieChart className="w-4 h-4 mr-2" />
                      <span className="font-semibold">{asset.asset_type}</span>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${asset.return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {asset.return >= 0 ? '+' : ''}{asset.return.toFixed(2)}%
                      </div>
                      <p className="text-sm text-muted-foreground">
                        ${asset.value.toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="w-5 h-5 mr-2 text-purple-500" />
                Risk Metrics
              </CardTitle>
              <CardDescription>Portfolio risk analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground">Volatility</p>
                  <p className="text-xl font-bold">{analytics.risk_metrics.volatility.toFixed(2)}%</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Beta</p>
                  <p className="text-xl font-bold">{analytics.risk_metrics.beta.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
                  <p className="text-xl font-bold">{analytics.risk_metrics.sharpe_ratio.toFixed(2)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="w-5 h-5 mr-2 text-orange-500" />
                Period Summary
              </CardTitle>
              <CardDescription>Selected period overview</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground">Start Date</p>
                  <p className="text-lg font-semibold">{new Date(analytics.period_start).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">End Date</p>
                  <p className="text-lg font-semibold">{new Date(analytics.period_end).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Transactions</p>
                  <p className="text-lg font-semibold">{analytics.total_transactions}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  )
}
