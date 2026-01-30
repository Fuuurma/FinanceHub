'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { StatsGrid } from '@/components/ui/stats-grid'
import { PageTabs, TabContent } from '@/components/ui/page-tabs'
import { PageErrorBoundary } from '@/components/ui/PageErrorBoundary'
import {
  Search,
  TrendingUp,
  TrendingDown,
  Newspaper,
  Building2,
  RefreshCw,
} from 'lucide-react'

const MOCK_INDICES = [
  { name: 'S&P 500', value: 4875.43, change: 1.23 },
  { name: 'NASDAQ', value: 15234.56, change: 2.45 },
  { name: 'DOW JONES', value: 38234.12, change: 0.89 },
  { name: 'FTSE 100', value: 7567.89, change: -0.34 },
  { name: 'DAX', value: 16789.23, change: 1.56 },
  { name: 'Nikkei 225', value: 34567.89, change: 0.12 },
]

const MOCK_SECTORS = [
  { name: 'Technology', change: 2.34, volume: 'High' },
  { name: 'Healthcare', change: 1.23, volume: 'Medium' },
  { name: 'Financials', change: -0.45, volume: 'High' },
  { name: 'Energy', change: 3.45, volume: 'Low' },
  { name: 'Consumer', change: 1.56, volume: 'Medium' },
  { name: 'Industrial', change: 0.89, volume: 'High' },
]

const MOCK_NEWS = [
  { title: 'Fed signals potential rate cut in Q2', time: '2 hours ago', sentiment: 'Bullish' },
  { title: 'Tech stocks surge on AI optimism', time: '4 hours ago', sentiment: 'Bullish' },
  { title: 'Oil prices stabilize amid supply concerns', time: '6 hours ago', sentiment: 'Neutral' },
]

function MarketOverviewPageContent() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 600)
    return () => clearTimeout(timer)
  }, [])

  const stats = [
    { title: 'S&P 500', value: 4875.43, change: 1.23, changeLabel: 'today' },
    { title: 'NASDAQ', value: 15234.56, change: 2.45, changeLabel: 'today' },
    { title: 'VIX', value: 13.84, change: -3.15, changeLabel: 'volatility' },
    { title: 'Trading Vol', value: '4.2B', change: 5.2, changeLabel: 'vs avg' },
  ]

  const tabs = [
    { value: 'indices', label: 'Indices', icon: Building2 },
    { value: 'sectors', label: 'Sectors', icon: TrendingUp },
    { value: 'news', label: 'News', icon: Newspaper },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Market Overview"
        description="Comprehensive market data and analysis"
        loading={loading}
        onRefresh={() => setLoading(true)}
        actions={
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search markets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        }
      />

      {error && (
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : (
        <StatsGrid stats={stats} />
      )}

      <PageTabs tabs={tabs} defaultValue="indices" tabsClassName="grid w-full grid-cols-3">
        <TabContent value="indices" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Major Market Indices</CardTitle>
              <CardDescription>Global market index performance</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {[1, 2, 3, 4, 5, 6].map((i) => (
                    <Skeleton key={i} className="h-24" />
                  ))}
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {MOCK_INDICES.map((index) => (
                    <div key={index.name} className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                      <div className="font-semibold text-muted-foreground text-sm">{index.name}</div>
                      <div className="text-2xl font-bold mt-1">{index.value.toFixed(2)}</div>
                      <div className={`text-sm mt-1 ${index.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {index.change >= 0 ? '+' : ''}{index.change.toFixed(2)}%
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabContent>

        <TabContent value="sectors" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Sector Performance</CardTitle>
              <CardDescription>Daily performance by economic sector</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {[1, 2, 3, 4, 5, 6].map((i) => (
                    <Skeleton key={i} className="h-24" />
                  ))}
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {MOCK_SECTORS.map((sector) => (
                    <div key={sector.name} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-center">
                        <div className="font-semibold">{sector.name}</div>
                        <Badge variant="outline">{sector.volume}</Badge>
                      </div>
                      <div className={`text-xl font-bold mt-2 ${sector.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {sector.change >= 0 ? '+' : ''}{sector.change.toFixed(2)}%
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabContent>

        <TabContent value="news" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Market News</CardTitle>
              <CardDescription>Latest market news and updates</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-24" />
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {MOCK_NEWS.map((news, idx) => (
                    <div key={idx} className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
                      <div className="font-semibold">{news.title}</div>
                      <div className="flex justify-between mt-2 text-sm text-muted-foreground">
                        <span>{news.time}</span>
                        <Badge variant={news.sentiment === 'Bullish' ? 'default' : news.sentiment === 'Bearish' ? 'destructive' : 'secondary'}>
                          {news.sentiment}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabContent>
      </PageTabs>
    </div>
  )
}

export default function MarketOverviewPage() {
  return (
    <PageErrorBoundary
      onError={(error, errorInfo) => {
        console.error('Market Overview page error:', error, errorInfo)
      }}
    >
      <MarketOverviewPageContent />
    </PageErrorBoundary>
  )
}
