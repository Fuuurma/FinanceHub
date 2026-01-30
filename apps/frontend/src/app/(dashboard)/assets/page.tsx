'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { StatsGrid } from '@/components/ui/stats-grid'
import { PageTabs, TabContent } from '@/components/ui/page-tabs'
import {
  TrendingUp,
  TrendingDown,
  Search,
  RefreshCw,
  Building2,
  Coins,
  Currency,
  Package,
  FileText,
  BarChart3,
  PieChart,
  ArrowRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface AssetCategory {
  type: string
  name: string
  description: string
  count: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  borderColor: string
  bgColor: string
}

const ASSET_CATEGORIES: AssetCategory[] = [
  {
    type: 'stocks',
    name: 'Stocks',
    description: 'Publicly traded company shares',
    count: '8,234',
    icon: Building2,
    color: 'text-blue-600',
    borderColor: 'border-blue-500/50',
    bgColor: 'bg-blue-500/10',
  },
  {
    type: 'crypto',
    name: 'Cryptocurrencies',
    description: 'Digital currencies and tokens',
    count: '2,847',
    icon: Coins,
    color: 'text-orange-600',
    borderColor: 'border-orange-500/50',
    bgColor: 'bg-orange-500/10',
  },
  {
    type: 'forex',
    name: 'Forex',
    description: 'Foreign exchange currency pairs',
    count: '175',
    icon: Currency,
    color: 'text-green-600',
    borderColor: 'border-green-500/50',
    bgColor: 'bg-green-500/10',
  },
  {
    type: 'commodity',
    name: 'Commodities',
    description: 'Physical goods and resources',
    count: '52',
    icon: Package,
    color: 'text-yellow-600',
    borderColor: 'border-yellow-500/50',
    bgColor: 'bg-yellow-500/10',
  },
  {
    type: 'bonds',
    name: 'Bonds',
    description: 'Fixed income securities',
    count: '1,234',
    icon: FileText,
    color: 'text-purple-600',
    borderColor: 'border-purple-500/50',
    bgColor: 'bg-purple-500/10',
  },
  {
    type: 'etf',
    name: 'ETFs',
    description: 'Exchange traded funds',
    count: '2,891',
    icon: BarChart3,
    color: 'text-pink-600',
    borderColor: 'border-pink-500/50',
    bgColor: 'bg-pink-500/10',
  },
  {
    type: 'index',
    name: 'Indices',
    description: 'Market index tracking funds',
    count: '156',
    icon: PieChart,
    color: 'text-cyan-600',
    borderColor: 'border-cyan-500/50',
    bgColor: 'bg-cyan-500/10',
  },
]

interface Asset {
  symbol: string
  name: string
  type: string
  price: number
  change: number
  volume: string
}

const MOCK_TRENDING_ASSETS: Asset[] = [
  { symbol: 'AAPL', name: 'Apple Inc.', type: 'stocks', price: 178.50, change: 2.3, volume: '52.3M' },
  { symbol: 'BTC', name: 'Bitcoin', type: 'crypto', price: 43250.00, change: 5.7, volume: '28.4B' },
  { symbol: 'TSLA', name: 'Tesla Inc.', type: 'stocks', price: 248.75, change: -1.2, volume: '112.5M' },
  { symbol: 'ETH', name: 'Ethereum', type: 'crypto', price: 2280.50, change: 3.8, volume: '14.2B' },
  { symbol: 'NVDA', name: 'NVIDIA Corp.', type: 'stocks', price: 495.22, change: 4.5, volume: '38.1M' },
]

export default function AssetsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [stats, setStats] = useState<{ title: string; value: string | number; change?: number; changeLabel?: string }[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [trendingAssets, setTrendingAssets] = useState<Asset[]>([])

  useEffect(() => {
    fetchAssetData()
  }, [])

  const fetchAssetData = async () => {
    setLoading(true)
    setError('')
    try {
      await new Promise(resolve => setTimeout(resolve, 800))

      setStats([
        { title: 'Total Assets', value: '15,589', change: 2.3, changeLabel: 'vs last month' },
        { title: 'Total Market Cap', value: 98400000000000, change: 1.8, changeLabel: 'global' },
        { title: '24h Volume', value: 892000000000, change: -5.2, changeLabel: 'all markets' },
        { title: 'Active Markets', value: '12,847', change: 0.5, changeLabel: 'exchanges' },
      ])

      setTrendingAssets(MOCK_TRENDING_ASSETS)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch asset data')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`)
    }
  }

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: price < 1 ? 4 : 2,
      maximumFractionDigits: price < 1 ? 6 : 2,
    }).format(price)
  }

  const tabs = [
    { value: 'categories', label: 'Categories', icon: PieChart },
    { value: 'trending', label: 'Trending', icon: TrendingUp, badge: trendingAssets.length },
    { value: 'watchlist', label: 'Watchlist', icon: BarChart3 },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Assets"
        description="Browse and search all available asset types"
        loading={loading}
        onRefresh={fetchAssetData}
        actions={
          <div className="relative w-full sm:w-64">
            <form onSubmit={handleSearch}>
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search assets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </form>
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
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : (
        <StatsGrid stats={stats} />
      )}

      <PageTabs tabs={tabs} defaultValue="categories" tabsClassName="grid w-full grid-cols-3">
        <TabContent value="categories" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {ASSET_CATEGORIES.map((category) => (
              <Card
                key={category.type}
                className={cn(
                  'cursor-pointer transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5',
                  category.borderColor,
                  'hover:bg-muted/50'
                )}
                onClick={() => router.push(`/assets/${category.type}`)}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className={cn('p-2 rounded-lg', category.bgColor)}>
                      <category.icon className={cn('h-5 w-5', category.color)} />
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <CardTitle className="text-lg mt-3">{category.name}</CardTitle>
                  <CardDescription>{category.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant="secondary" className="w-full justify-center">
                    {category.count} assets
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabContent>

        <TabContent value="trending" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Trending Assets</CardTitle>
              <CardDescription>Top assets by volume and price change</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {loading ? (
                  <div className="space-y-4">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <Skeleton key={i} className="h-16" />
                    ))}
                  </div>
                ) : (
                  trendingAssets.map((asset) => (
                    <div
                      key={asset.symbol}
                      className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer"
                      onClick={() => router.push(`/assets/${asset.type}/${asset.symbol}`)}
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center font-bold">
                          {asset.symbol[0]}
                        </div>
                        <div>
                          <div className="font-semibold">{asset.symbol}</div>
                          <div className="text-sm text-muted-foreground">{asset.name}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{formatPrice(asset.price)}</div>
                        <div className={cn(
                          'text-sm flex items-center justify-end gap-1',
                          asset.change >= 0 ? 'text-green-600' : 'text-red-600'
                        )}>
                          {asset.change >= 0 ? (
                            <TrendingUp className="h-3 w-3" />
                          ) : (
                            <TrendingDown className="h-3 w-3" />
                          )}
                          {asset.change >= 0 ? '+' : ''}{asset.change}%
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabContent>

        <TabContent value="watchlist" className="space-y-6">
          <Card>
            <CardHeader className="text-center py-12">
              <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <CardTitle>No Watchlist Yet</CardTitle>
              <CardDescription>
                Add assets to your watchlist to track them here
              </CardDescription>
              <Button className="mt-4" onClick={() => router.push('/watchlist')}>
                Go to Watchlist
              </Button>
            </CardHeader>
          </Card>
        </TabContent>
      </PageTabs>
    </div>
  )
}
