'use client'

import { useEffect, useState } from 'react'
import { portfolioAnalyticsApi } from '@/lib/api/portfolio-analytics'
import type { PortfolioAnalytics as PortfolioAnalyticsType, AnalyticsPeriod } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { TrendingUp, TrendingDown, PieChart, BarChart3, RefreshCw, Download, Calendar, DollarSign, Activity, LineChart, Target } from 'lucide-react'
import { ChartCard } from '@/components/analytics/ChartCard'
import { AllocationPieChart } from '@/components/analytics/AllocationPieChart'
import { PerformanceChart } from '@/components/analytics/PerformanceChart'
import BenchmarkComparisonChart from '@/components/analytics/BenchmarkComparisonChart'
import PerformanceAttributionChart from '@/components/analytics/PerformanceAttributionChart'
import RiskMetricsHistoryChart from '@/components/analytics/RiskMetricsHistoryChart'
import RollingReturnsChart from '@/components/analytics/RollingReturnsChart'
import SectorBreakdownChart from '@/components/analytics/SectorBreakdownChart'

type TabValue = 'overview' | 'performance' | 'risk' | 'comparison'

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<AnalyticsPeriod>('7d')
  const [activeTab, setActiveTab] = useState<TabValue>('overview')
  const [analytics, setAnalytics] = useState<PortfolioAnalyticsType | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [rollingPeriod, setRollingPeriod] = useState<'7d' | '30d'>('7d')

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

  const mockAllocationData = analytics?.performance_by_asset?.map(asset => ({
    name: asset.asset_type,
    value: asset.value,
    percentage: ((asset.value / (analytics?.total_value || 1)) * 100).toFixed(1)
  })) || []

  const mockPerformanceData = analytics?.performance_by_asset?.map(asset => ({
    symbol: asset.asset_type,
    return: asset.return,
    current_value: asset.value
  })) || []

  const mockBenchmarkData = [
    { date: '2024-01-01', portfolio: 0, benchmark: 0 },
    { date: '2024-01-02', portfolio: 1.2, benchmark: 0.8 },
    { date: '2024-01-03', portfolio: 2.5, benchmark: 1.5 },
    { date: '2024-01-04', portfolio: 1.8, benchmark: 1.2 },
    { date: '2024-01-05', portfolio: 3.2, benchmark: 2.1 },
    { date: '2024-01-06', portfolio: 4.1, benchmark: 2.8 },
    { date: '2024-01-07', portfolio: 3.8, benchmark: 2.5 },
  ]

  const mockAttributionData = [
    { symbol: 'Technology', contribution: 2.5, value: 45000 },
    { symbol: 'Healthcare', contribution: 1.2, value: 28000 },
    { symbol: 'Finance', contribution: 0.8, value: 22000 },
    { symbol: 'Consumer', contribution: 0.5, value: 18000 },
    { symbol: 'Energy', contribution: -0.3, value: 12000 },
  ]

  const mockRiskHistoryData = [
    { date: '2024-01-01', volatility: 15, sharpeRatio: 1.2 },
    { date: '2024-01-02', volatility: 16, sharpeRatio: 1.1 },
    { date: '2024-01-03', volatility: 14, sharpeRatio: 1.3 },
    { date: '2024-01-04', volatility: 15, sharpeRatio: 1.2 },
    { date: '2024-01-05', volatility: 17, sharpeRatio: 1.0 },
    { date: '2024-01-06', volatility: 16, sharpeRatio: 1.1 },
    { date: '2024-01-07', volatility: 15, sharpeRatio: 1.2 },
  ]

  const mockRollingReturnsData = [
    { date: '2024-01-01', '7d': 2.5, '30d': 8.2 },
    { date: '2024-01-02', '7d': 2.8, '30d': 8.5 },
    { date: '2024-01-03', '7d': 3.1, '30d': 8.8 },
    { date: '2024-01-04', '7d': 2.9, '30d': 8.6 },
    { date: '2024-01-05', '7d': 3.2, '30d': 9.0 },
    { date: '2024-01-06', '7d': 3.5, '30d': 9.2 },
    { date: '2024-01-07', '7d': 3.3, '30d': 9.1 },
  ]

  const mockSectorData = [
    { name: 'Technology', value: 45000, percentage: 35.5 },
    { name: 'Healthcare', value: 28000, percentage: 22.1 },
    { name: 'Finance', value: 22000, percentage: 17.3 },
    { name: 'Consumer', value: 18000, percentage: 14.2 },
    { name: 'Energy', value: 12000, percentage: 10.9 },
  ]

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
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabValue)} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="risk">Risk</TabsTrigger>
            <TabsTrigger value="comparison">Comparison</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
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

            <div className="grid gap-6 md:grid-cols-2">
              <ChartCard title="Asset Allocation" description="Portfolio distribution by asset type">
                <AllocationPieChart data={mockAllocationData} />
              </ChartCard>

              <ChartCard title="Performance by Asset" description="Return breakdown by asset">
                <PerformanceChart data={mockPerformanceData} />
              </ChartCard>
            </div>
          </TabsContent>

          <TabsContent value="performance" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              <ChartCard title="Rolling Returns" description="7-day and 30-day rolling returns">
                <RollingReturnsChart 
                  data={mockRollingReturnsData} 
                  selectedPeriod={rollingPeriod}
                  onPeriodChange={setRollingPeriod}
                />
              </ChartCard>

              <ChartCard title="Performance Attribution" description="Sector contribution to returns">
                <PerformanceAttributionChart data={mockAttributionData} />
              </ChartCard>
            </div>

            <ChartCard title="Benchmark Comparison" description="Portfolio vs S&P 500 performance">
              <BenchmarkComparisonChart data={mockBenchmarkData} />
            </ChartCard>
          </TabsContent>

          <TabsContent value="risk" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Activity className="w-5 h-5 mr-2 text-purple-500" />
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
            </div>

            <ChartCard title="Risk Metrics History" description="Volatility and Sharpe ratio over time">
              <RiskMetricsHistoryChart data={mockRiskHistoryData} />
            </ChartCard>
          </TabsContent>

          <TabsContent value="comparison" className="space-y-6">
            <ChartCard title="Sector Breakdown" description="Performance by economic sector">
              <SectorBreakdownChart data={mockSectorData} />
            </ChartCard>

            <div className="grid gap-6 md:grid-cols-2">
              <ChartCard title="Asset Type Performance" description="Returns by asset class">
                <PerformanceChart data={mockPerformanceData} />
              </ChartCard>

              <ChartCard title="Benchmark Comparison" description="Portfolio vs benchmark">
                <BenchmarkComparisonChart data={mockBenchmarkData} />
              </ChartCard>
            </div>
          </TabsContent>
        </Tabs>
      ) : null}
    </div>
  )
}
