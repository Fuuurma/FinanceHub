'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { PageHeader } from '@/components/ui/page-header'
import { StatsGrid } from '@/components/ui/stats-grid'
import { PageTabs, TabContent } from '@/components/ui/page-tabs'
import { ConnectionStatus } from '@/components/realtime/ConnectionStatus'
import { LivePriceTicker } from '@/components/realtime/LivePriceTicker'
import { PageErrorBoundary } from '@/components/ui/PageErrorBoundary'
import {
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  BarChart3,
  PieChart,
  Target,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface MarketIndex {
  symbol: string
  name: string
  value: number
  change: number
  changePercent: number
}

interface SectorPerformance {
  name: string
  change: number
  topStock: string
  topStockChange: number
}

const MOCK_INDICES: MarketIndex[] = [
  { symbol: 'SPX', name: 'S&P 500', value: 5021.84, change: 35.26, changePercent: 0.71 },
  { symbol: 'NDX', name: 'NASDAQ 100', value: 15990.66, change: 156.42, changePercent: 0.99 },
  { symbol: 'DJI', name: 'Dow Jones', value: 38996.39, change: 125.69, changePercent: 0.32 },
  { symbol: 'RUT', name: 'Russell 2000', value: 2042.35, change: -8.92, changePercent: -0.43 },
  { symbol: 'VIX', name: 'VIX', value: 13.84, change: -0.45, changePercent: -3.15 },
]

const MOCK_SECTORS: SectorPerformance[] = [
  { name: 'Technology', change: 1.24, topStock: 'NVDA', topStockChange: 4.52 },
  { name: 'Healthcare', change: 0.87, topStock: 'LLY', topStockChange: 2.31 },
  { name: 'Financial', change: 0.65, topStock: 'JPM', topStockChange: 1.85 },
  { name: 'Energy', change: -0.92, topStock: 'XOM', topStockChange: -1.23 },
  { name: 'Consumer Disc.', change: 0.45, topStock: 'TSLA', topStockChange: -1.45 },
  { name: 'Utilities', change: 0.23, topStock: 'NEE', topStockChange: 0.89 },
]

const MOCK_TOP_MOVERS = {
  gainers: [
    { symbol: 'NVDA', name: 'NVIDIA Corp.', change: 4.52, price: 495.22 },
    { symbol: 'AMD', name: 'AMD Inc.', change: 3.87, price: 178.45 },
    { symbol: 'META', name: 'Meta Platforms', change: 3.21, price: 485.09 },
    { symbol: 'CRM', name: 'Salesforce Inc.', change: 2.95, price: 275.32 },
    { symbol: 'NOW', name: 'ServiceNow', change: 2.68, price: 752.18 },
  ],
  losers: [
    { symbol: 'BA', name: 'Boeing Co.', change: -2.34, price: 178.56 },
    { symbol: 'DIS', name: 'Walt Disney', change: -2.12, price: 112.45 },
    { symbol: 'INTC', name: 'Intel Corp.', change: -1.98, price: 42.87 },
    { symbol: 'COIN', name: 'Coinbase', change: -1.76, price: 189.23 },
    { symbol: 'PARA', name: 'Paramount', change: -1.54, price: 12.34 },
  ],
}

function MarketDashboardPageContent() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [indices, setIndices] = useState<MarketIndex[]>([])
  const [sectors, setSectors] = useState<SectorPerformance[]>([])
  const [topMovers, setTopMovers] = useState<typeof MOCK_TOP_MOVERS>(MOCK_TOP_MOVERS)

  useEffect(() => {
    fetchMarketData()
  }, [])

  const fetchMarketData = async () => {
    setLoading(true)
    setError('')
    try {
      await new Promise(resolve => setTimeout(resolve, 800))
      setIndices(MOCK_INDICES)
      setSectors(MOCK_SECTORS)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch market data')
    } finally {
      setLoading(false)
    }
  }

  const stats = [
    { title: 'S&P 500', value: 5021.84, change: 0.71, changeLabel: 'today' },
    { title: 'NASDAQ 100', value: 15990.66, change: 0.99, changeLabel: 'today' },
    { title: 'VIX', value: 13.84, change: -3.15, changeLabel: 'volatility' },
    { title: 'Trading Vol', value: '4.2B', change: -5.2, changeLabel: 'vs avg' },
  ]

  const formatNumber = (num: number): string => {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }

  const formatChange = (change: number): string => {
    const prefix = change >= 0 ? '+' : ''
    return `${prefix}${change.toFixed(2)}%`
  }

  const tabs = [
    { value: 'overview', label: 'Overview', icon: BarChart3 },
    { value: 'indices', label: 'Indices', icon: Target },
    { value: 'sectors', label: 'Sectors', icon: PieChart },
    { value: 'movers', label: 'Top Movers', icon: Zap },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Market Dashboard"
        description="Real-time market data, indices, and analytics"
        loading={loading}
        onRefresh={fetchMarketData}
        actions={<ConnectionStatus />}
      />

      <LivePriceTicker />

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

      <PageTabs tabs={tabs} defaultValue="overview" tabsClassName="grid w-full grid-cols-4">
        <TabContent value="overview" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {indices.slice(0, 4).map((index) => (
              <Card key={index.symbol} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {index.name}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatNumber(index.value)}</div>
                  <div className={cn(
                    'flex items-center gap-1 mt-1',
                    index.change >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    {index.change >= 0 ? (
                      <TrendingUp className="h-4 w-4" />
                    ) : (
                      <TrendingDown className="h-4 w-4" />
                    )}
                    <span className="font-medium">{formatChange(index.changePercent)}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Top Gainers</CardTitle>
                <CardDescription>Best performing stocks today</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {topMovers.gainers.slice(0, 5).map((stock) => (
                    <div key={stock.symbol} className="flex items-center justify-between">
                      <div>
                        <div className="font-semibold">{stock.symbol}</div>
                        <div className="text-sm text-muted-foreground">{stock.name}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">${formatNumber(stock.price)}</div>
                        <div className="text-sm text-green-600">+{stock.change.toFixed(2)}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Losers</CardTitle>
                <CardDescription>Worst performing stocks today</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {topMovers.losers.slice(0, 5).map((stock) => (
                    <div key={stock.symbol} className="flex items-center justify-between">
                      <div>
                        <div className="font-semibold">{stock.symbol}</div>
                        <div className="text-sm text-muted-foreground">{stock.name}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">${formatNumber(stock.price)}</div>
                        <div className="text-sm text-red-600">{stock.change.toFixed(2)}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabContent>

        <TabContent value="indices" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Major Indices</CardTitle>
              <CardDescription>Real-time performance of major market indices</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {indices.map((index) => (
                  <div
                    key={index.symbol}
                    className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold">{index.symbol}</span>
                        <Badge variant="outline">{index.name}</Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold">{formatNumber(index.value)}</div>
                      <div className={cn(
                        'flex items-center justify-end gap-1',
                        index.change >= 0 ? 'text-green-600' : 'text-red-600'
                      )}>
                        {index.change >= 0 ? (
                          <ArrowUpRight className="h-4 w-4" />
                        ) : (
                          <ArrowDownRight className="h-4 w-4" />
                        )}
                        <span>{formatChange(index.changePercent)}</span>
                        <span className="text-muted-foreground">
                          ({index.change >= 0 ? '+' : ''}{index.change.toFixed(2)})
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
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
              <div className="space-y-4">
                {sectors.map((sector) => (
                  <div
                    key={sector.name}
                    className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors"
                  >
                    <div>
                      <div className="font-semibold">{sector.name}</div>
                      <div className="text-sm text-muted-foreground">
                        Top: {sector.topStock} ({sector.topStockChange >= 0 ? '+' : ''}{sector.topStockChange.toFixed(2)}%)
                      </div>
                    </div>
                    <div className={cn(
                      'px-3 py-1 rounded-full font-semibold',
                      sector.change >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    )}>
                      {sector.change >= 0 ? '+' : ''}{sector.change.toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabContent>

        <TabContent value="movers" className="space-y-6">
          <Tabs defaultValue="gainers">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="gainers">Top Gainers</TabsTrigger>
              <TabsTrigger value="losers">Top Losers</TabsTrigger>
            </TabsList>
            <TabsContent value="gainers" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    {topMovers.gainers.map((stock, idx) => (
                      <div key={stock.symbol} className="flex items-center gap-4">
                        <span className="text-muted-foreground w-6">{idx + 1}</span>
                        <div className="flex-1">
                          <div className="font-semibold">{stock.symbol}</div>
                          <div className="text-sm text-muted-foreground">{stock.name}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">${formatNumber(stock.price)}</div>
                          <div className="text-green-600 font-medium">+{stock.change.toFixed(2)}%</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="losers" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    {topMovers.losers.map((stock, idx) => (
                      <div key={stock.symbol} className="flex items-center gap-4">
                        <span className="text-muted-foreground w-6">{idx + 1}</span>
                        <div className="flex-1">
                          <div className="font-semibold">{stock.symbol}</div>
                          <div className="text-sm text-muted-foreground">{stock.name}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">${formatNumber(stock.price)}</div>
                          <div className="text-red-600 font-medium">{stock.change.toFixed(2)}%</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </TabContent>
      </PageTabs>
    </div>
  )
}

export default function MarketDashboardPage() {
  return (
    <PageErrorBoundary
      onError={(error, errorInfo) => {
        console.error('Market Dashboard page error:', error, errorInfo)
      }}
    >
      <MarketDashboardPageContent />
    </PageErrorBoundary>
  )
}
