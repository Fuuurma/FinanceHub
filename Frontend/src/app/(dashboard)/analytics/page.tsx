'use client'

import { useEffect, useState, useCallback } from 'react'
import { portfolioAnalyticsApi } from '@/lib/api/portfolio-analytics'
import type { AnalyticsPeriod, BenchmarkType } from '@/lib/types/portfolio-analytics'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { RefreshCw, Download, Calendar, FileJson, FileSpreadsheet } from 'lucide-react'
import { ChartCard } from '@/components/analytics/ChartCard'
import { AllocationPieChart } from '@/components/analytics/AllocationPieChart'
import { PerformanceChart } from '@/components/analytics/PerformanceChart'
import BenchmarkComparisonChart from '@/components/analytics/BenchmarkComparisonChart'
import PerformanceAttributionChart from '@/components/analytics/PerformanceAttributionChart'
import RiskMetricsHistoryChart from '@/components/analytics/RiskMetricsHistoryChart'
import RollingReturnsChart from '@/components/analytics/RollingReturnsChart'
import SectorBreakdownChart from '@/components/analytics/SectorBreakdownChart'
import { ReturnCard, ValueCard, RiskCard, DrawdownCard, CAGRCard } from '@/components/analytics/KPICards'
import { PortfolioSelector } from '@/components/analytics/PortfolioSelector'
import { PortfolioComparison } from '@/components/analytics/PortfolioComparison'
import { PerformanceBreakdown } from '@/components/analytics/PerformanceBreakdown'
import { AttributionDashboard } from '@/components/attribution/AttributionDashboard'
import { useAnalyticsStore } from '@/stores/analyticsStore'
import { portfoliosApi } from '@/lib/api/portfolio'
import type { Portfolio } from '@/lib/types/portfolio'
import { exportAnalytics } from '@/lib/utils/analytics-export'
import { cn } from '@/lib/utils'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

type TabValue = 'overview' | 'performance' | 'risk' | 'attribution' | 'comparison'

const PERIODS: { value: AnalyticsPeriod; label: string }[] = [
  { value: '1d', label: '1D' },
  { value: '7d', label: '7D' },
  { value: '30d', label: '30D' },
  { value: '90d', label: '90D' },
  { value: '180d', label: '6M' },
  { value: '1y', label: '1Y' },
  { value: '3y', label: '3Y' },
  { value: '5y', label: '5Y' },
  { value: 'all', label: 'All' },
]

const BENCHMARKS: { value: BenchmarkType; label: string }[] = [
  { value: 'sp500', label: 'S&P 500' },
  { value: 'nasdaq', label: 'NASDAQ' },
  { value: 'dow', label: 'Dow Jones' },
]

export default function AnalyticsPage() {
  const {
    selectedPortfolioId,
    selectedPeriod,
    selectedBenchmark,
    data: analytics,
    loading,
    error,
    lastUpdated,
    setSelectedPortfolio,
    setSelectedPeriod,
    setSelectedBenchmark,
    fetchAnalytics,
  } = useAnalyticsStore()

  const [activeTab, setActiveTab] = useState<TabValue>('overview')
  const [rollingPeriod, setRollingPeriod] = useState<'7d' | '30d' | '90d'>('30d')
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])

  useEffect(() => {
    fetchAnalytics()
    const fetchPortfolios = async () => {
      try {
        const data = await portfoliosApi.list()
        setPortfolios(data.portfolios)
      } catch (err) {
        console.error('Failed to fetch portfolios:', err)
      }
    }
    fetchPortfolios()
  }, [selectedPeriod, selectedBenchmark, fetchAnalytics])

  const handleExportJSON = () => {
    if (!analytics) return

    exportAnalytics(analytics, {
      format: 'json',
      period: selectedPeriod,
    })
  }

  const handleExportCSV = () => {
    if (!analytics) return

    exportAnalytics(analytics, {
      format: 'csv',
      period: selectedPeriod,
    })
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
    { date: '2024-01-01', '7d': 2.5, '30d': 8.2, '90d': 15.5 },
    { date: '2024-01-02', '7d': 2.8, '30d': 8.5, '90d': 15.8 },
    { date: '2024-01-03', '7d': 3.1, '30d': 8.8, '90d': 16.0 },
    { date: '2024-01-04', '7d': 2.9, '30d': 8.6, '90d': 15.7 },
    { date: '2024-01-05', '7d': 3.2, '30d': 9.0, '90d': 16.2 },
    { date: '2024-01-06', '7d': 3.5, '30d': 9.2, '90d': 16.5 },
    { date: '2024-01-07', '7d': 3.3, '30d': 9.1, '90d': 16.3 },
  ]

  const mockSectorData = [
    { name: 'Technology', value: 45000, percentage: 35.5, return: 12.5 },
    { name: 'Healthcare', value: 28000, percentage: 22.1, return: 8.2 },
    { name: 'Finance', value: 22000, percentage: 17.3, return: 6.5 },
    { name: 'Consumer', value: 18000, percentage: 14.2, return: 4.8 },
    { name: 'Energy', value: 12000, percentage: 10.9, return: -2.3 },
  ]

  const mockHoldingsData = [
    { symbol: 'AAPL', name: 'Apple Inc.', weight: 15.2, return: 18.5, contribution: 2.81, value: 15200, sector: 'Technology' },
    { symbol: 'MSFT', name: 'Microsoft Corp.', weight: 14.8, return: 22.3, contribution: 3.30, value: 14800, sector: 'Technology' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', weight: 12.5, return: 15.2, contribution: 1.90, value: 12500, sector: 'Technology' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', weight: 10.3, return: 28.7, contribution: 2.96, value: 10300, sector: 'Consumer' },
    { symbol: 'NVDA', name: 'NVIDIA Corp.', weight: 8.7, return: 45.2, contribution: 3.93, value: 8700, sector: 'Technology' },
    { symbol: 'JPM', name: 'JPMorgan Chase', weight: 6.5, return: 12.3, contribution: 0.80, value: 6500, sector: 'Finance' },
    { symbol: 'V', name: 'Visa Inc.', weight: 5.8, return: 8.5, contribution: 0.49, value: 5800, sector: 'Finance' },
    { symbol: 'JNJ', name: 'Johnson & Johnson', weight: 5.2, return: -2.3, contribution: -0.12, value: 5200, sector: 'Healthcare' },
    { symbol: 'WMT', name: 'Walmart Inc.', weight: 4.8, return: 15.8, contribution: 0.76, value: 4800, sector: 'Consumer' },
    { symbol: 'XOM', name: 'Exxon Mobil', weight: 4.2, return: -8.5, contribution: -0.36, value: 4200, sector: 'Energy' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Portfolio Analytics</h1>
          <p className="text-muted-foreground">Detailed portfolio performance analysis</p>
        </div>
        <div className="flex gap-2 items-center">
          <PortfolioSelector
            selectedPortfolioId={selectedPortfolioId}
            onSelectPortfolio={setSelectedPortfolio}
          />
          <Button variant="outline" onClick={fetchAnalytics} disabled={loading}>
            <RefreshCw className={cn('w-4 h-4 mr-2', loading && 'animate-spin')} />
            Refresh
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" disabled={!analytics || loading}>
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleExportJSON}>
                <FileJson className="w-4 h-4 mr-2" />
                Export as JSON
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleExportCSV}>
                <FileSpreadsheet className="w-4 h-4 mr-2" />
                Export as CSV
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap items-center">
        {PERIODS.map((p) => (
          <Button
            key={p.value}
            variant={selectedPeriod === p.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedPeriod(p.value)}
            disabled={loading}
          >
            {p.label}
          </Button>
        ))}
        <div className="w-px h-6 bg-border mx-2" />
        <select
          value={selectedBenchmark}
          onChange={(e) => setSelectedBenchmark(e.target.value as BenchmarkType)}
          className="px-3 py-1 border rounded-md text-sm"
          disabled={loading}
        >
          {BENCHMARKS.map((b) => (
            <option key={b.value} value={b.value}>{b.label}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
          <p className="font-semibold">Error</p>
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader><Skeleton className="h-6 w-32" /></CardHeader>
              <CardContent><Skeleton className="h-12" /></CardContent>
            </Card>
          ))}
        </div>
      ) : analytics ? (
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabValue)} className="space-y-6">
           <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="risk">Risk</TabsTrigger>
            <TabsTrigger value="attribution">Attribution</TabsTrigger>
            <TabsTrigger value="comparison">Comparison</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <ReturnCard value={analytics.performance?.total_return_percent || 0} />
              <ValueCard value={analytics.summary?.total_value || 0} change={analytics.summary?.total_pnl} />
              <CAGRCard cagr={analytics.performance?.cagr || 0} annualizedReturn={analytics.performance?.annualized_return || 0} />
              <DrawdownCard maxDrawdown={analytics.performance?.max_drawdown_percent || 0} maxDrawdownDate={analytics.performance?.max_drawdown_date || undefined} recoveryTime={analytics.performance?.recovery_time || undefined} />
            </div>

            <RiskCard 
              volatility={analytics.risk_metrics.volatility} 
              beta={analytics.risk_metrics.beta} 
              sharpeRatio={analytics.risk_metrics.sharpe_ratio} 
            />

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
              <ChartCard title="Rolling Returns" description="7-day, 30-day, and 90-day rolling returns">
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
            <PerformanceBreakdown holdings={mockHoldingsData} />
            <ChartCard title="Benchmark Comparison" description="Portfolio vs benchmark performance">
              <BenchmarkComparisonChart data={mockBenchmarkData} />
            </ChartCard>
          </TabsContent>

          <TabsContent value="risk" className="space-y-6">
            <RiskCard 
              volatility={analytics.risk_metrics.volatility} 
              beta={analytics.risk_metrics.beta} 
              sharpeRatio={analytics.risk_metrics.sharpe_ratio} 
            />
            <ChartCard title="Risk Metrics History" description="Volatility and Sharpe ratio over time">
              <RiskMetricsHistoryChart data={mockRiskHistoryData} />
            </ChartCard>
           </TabsContent>

           <TabsContent value="attribution" className="space-y-6">
              <AttributionDashboard
                holdings={mockHoldingsData.map(h => ({
                  id: h.symbol,
                  portfolio_id: selectedPortfolioId || '',
                  symbol: h.symbol,
                  name: h.name,
                  asset_class: 'stocks' as const,
                  quantity: 100,
                  average_cost: h.value / (1 + h.return / 100),
                  current_price: h.value / 100,
                  current_value: h.value,
                  unrealized_pnl: h.value * h.return / 100,
                  unrealized_pnl_percent: h.return,
                  day_change: 0,
                  day_change_percent: 0,
                  weight: h.weight,
                  sector: h.sector,
                  exchange: '',
                  currency: 'USD',
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                }))}
                loading={loading}
              />
            </TabsContent>

           <TabsContent value="comparison" className="space-y-6">
            <PortfolioComparison
              portfolios={portfolios.map(p => ({
                id: p.id,
                name: p.name,
                return: p.total_pnl_percent,
                volatility: 15,
                sharpeRatio: 1.2,
                maxDrawdown: 5,
              }))}
              selectedId={selectedPortfolioId || ''}
              onSelect={setSelectedPortfolio}
            />
            <ChartCard title="Sector Breakdown" description="Performance by economic sector">
              <SectorBreakdownChart data={mockSectorData} />
            </ChartCard>
          </TabsContent>
        </Tabs>
      ) : (
        <div className="text-center py-12 text-muted-foreground">
          <p>No analytics data available. Select a portfolio to view analytics.</p>
        </div>
      )}
    </div>
  )
}
