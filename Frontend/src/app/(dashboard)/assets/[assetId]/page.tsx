'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { 
  TrendingUp, TrendingDown, Activity, Globe, Info, 
  Zap, BarChart3, ShieldCheck, Calendar,
  DollarSign, PieChart, Newspaper, Star, Target,
  ArrowUpRight, ArrowDownRight, Minus
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { ConnectionStatus } from '@/components/realtime/ConnectionStatus'
import { RealTimeChart } from '@/components/realtime/RealTimeChart'
import { OrderBook } from '@/components/realtime/OrderBook'
import { TradeFeed } from '@/components/realtime/TradeFeed'
import { useRealtimeStore } from '@/stores/realtimeStore'

type TimeFrame = '1D' | '1W' | '1M' | '3M' | '1Y' | 'ALL'
type IndicatorType = 'SMA' | 'EMA' | 'RSI' | 'MACD' | 'BB'

interface AssetData {
  symbol: string
  name: string
  type: 'stock' | 'crypto' | 'etf' | 'index'
  price: number
  change: number
  changePercent: number
  marketCap: number
  volume: number
  peRatio?: number
  dividend?: {
    yield: number
    frequency: string
    lastExDate: string
  }
  fundamentals?: {
    sector: string
    industry: string
    description: string
    employees: number
    founded: string
    website: string
  }
  news?: Array<{
    id: string
    title: string
    source: string
    publishedAt: string
    sentiment: 'positive' | 'negative' | 'neutral'
    url: string
  }>
  similarAssets?: Array<{
    symbol: string
    name: string
    correlation: number
  }>
  analystRatings?: {
    rating: 'buy' | 'hold' | 'sell'
    targetPrice: number
    priceTargetUpside: number
    analysts: number
  }
}

export default function AssetDetailPage() {
  const params = useParams()
  const assetId = params.assetId as string
  
  const { connect, connectionState, prices, subscribeSingle, unsubscribeSingle } = useRealtimeStore()
  const [selectedTimeFrame, setSelectedTimeFrame] = useState<TimeFrame>('1D')
  const [selectedIndicators, setSelectedIndicators] = useState<IndicatorType[]>([])
  const [activeTab, setActiveTab] = useState('overview')
  const [assetData, setAssetData] = useState<AssetData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAssetData()
  }, [assetId])

  useEffect(() => {
    if (connectionState === 'connected' && assetId) {
      subscribeSingle(assetId, ['price', 'trades', 'orderbook'])
    }
    
    return () => {
      if (assetId) {
        unsubscribeSingle(assetId, ['price', 'trades', 'orderbook'])
      }
    };
  }, [connectionState, assetId, subscribeSingle, unsubscribeSingle])

  const fetchAssetData = async () => {
    try {
      setLoading(true)
      // Mock data - replace with API call
      setAssetData({
        symbol: assetId.toUpperCase(),
        name: 'Apple Inc.',
        type: 'stock',
        price: 178.72,
        change: 2.35,
        changePercent: 1.33,
        marketCap: 2800000000000,
        volume: 52340000,
        peRatio: 28.5,
        dividend: {
          yield: 0.52,
          frequency: 'Quarterly',
          lastExDate: '2024-02-09'
        },
        fundamentals: {
          sector: 'Technology',
          industry: 'Consumer Electronics',
          description: 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.',
          employees: 164000,
          founded: '1976',
          website: 'https://www.apple.com'
        },
        news: [
          {
            id: '1',
            title: 'Apple Reports Record Q1 Revenue',
            source: 'Bloomberg',
            publishedAt: '2024-01-25T10:00:00Z',
            sentiment: 'positive',
            url: '#'
          },
          {
            id: '2',
            title: 'Analysts Upgrade Apple Price Target',
            source: 'Reuters',
            publishedAt: '2024-01-24T14:30:00Z',
            sentiment: 'positive',
            url: '#'
          },
          {
            id: '3',
            title: 'Apple Faces Supply Chain Concerns',
            source: 'WSJ',
            publishedAt: '2024-01-23T09:15:00Z',
            sentiment: 'negative',
            url: '#'
          }
        ],
        similarAssets: [
          { symbol: 'MSFT', name: 'Microsoft Corporation', correlation: 0.75 },
          { symbol: 'GOOGL', name: 'Alphabet Inc.', correlation: 0.68 },
          { symbol: 'META', name: 'Meta Platforms Inc.', correlation: 0.62 }
        ],
        analystRatings: {
          rating: 'buy',
          targetPrice: 210,
          priceTargetUpside: 17.5,
          analysts: 38
        }
      })
    } catch (error) {
      console.error('Failed to fetch asset data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : undefined
      await connect(token)
    } catch (err) {
      console.error('Failed to connect:', err)
    }
  }

  const currentPrice = prices[assetId]

  const timeFrames: TimeFrame[] = ['1D', '1W', '1M', '3M', '1Y', 'ALL']
  
  const indicators: { value: IndicatorType, label: string }[] = [
    { value: 'SMA', label: 'SMA' },
    { value: 'EMA', label: 'EMA' },
    { value: 'RSI', label: 'RSI' },
    { value: 'MACD', label: 'MACD' },
    { value: 'BB', label: 'Bollinger Bands' }
  ]

  if (loading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-96 w-full" />
        <div className="grid md:grid-cols-3 gap-6">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
      </div>
    )
  }

  if (!assetData) {
    return (
      <div className="p-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">Asset not found</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <ConnectionStatus />
                <div>
                  <CardTitle className="text-3xl">{assetData.symbol}</CardTitle>
                  <CardDescription className="text-base">{assetData.name}</CardDescription>
                </div>
                <Badge variant="outline">{assetData.type.toUpperCase()}</Badge>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-3xl font-bold">
                {currentPrice ? `$${currentPrice.price.toFixed(2)}` : `$${assetData.price.toFixed(2)}`}
              </div>
              <div className={`flex items-center gap-1 justify-end ${assetData.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {assetData.change >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
                <span className="font-semibold">
                  {assetData.change >= 0 ? '+' : ''}{assetData.changePercent.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Chart Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Price Chart</CardTitle>
            <div className="flex gap-2">
              <div className="flex gap-1 border rounded-md p-1">
                {timeFrames.map((tf) => (
                  <button
                    key={tf}
                    onClick={() => setSelectedTimeFrame(tf)}
                    className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                      selectedTimeFrame === tf
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-muted'
                    }`}
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            {indicators.map((ind) => (
              <Button
                key={ind.value}
                variant={selectedIndicators.includes(ind.value) ? 'default' : 'outline'}
                size="sm"
                onClick={() => {
                  if (selectedIndicators.includes(ind.value)) {
                    setSelectedIndicators(selectedIndicators.filter(i => i !== ind.value))
                  } else {
                    setSelectedIndicators([...selectedIndicators, ind.value])
                  }
                }}
              >
                {ind.label}
              </Button>
            ))}
          </div>
          <RealTimeChart symbol={assetId} timeframe={selectedTimeFrame.toLowerCase()} />
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="fundamentals">Fundamentals</TabsTrigger>
          <TabsTrigger value="news">News</TabsTrigger>
          <TabsTrigger value="dividends">Dividends</TabsTrigger>
          <TabsTrigger value="similar">Similar</TabsTrigger>
          <TabsTrigger value="analysts">Analysts</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">Market Cap</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ${(assetData.marketCap / 1000000000).toFixed(2)}B
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">Volume</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(assetData.volume / 1000000).toFixed(2)}M
                </div>
              </CardContent>
            </Card>

            {assetData.peRatio && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground">P/E Ratio</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{assetData.peRatio.toFixed(2)}</div>
                </CardContent>
              </Card>
            )}

            {assetData.dividend && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Dividend Yield</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{assetData.dividend.yield.toFixed(2)}%</div>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <OrderBook symbol={assetId} />
            <TradeFeed symbol={assetId} />
          </div>
        </TabsContent>

        <TabsContent value="fundamentals">
          <Card>
            <CardHeader>
              <CardTitle>Company Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {assetData.fundamentals && (
                <>
                  <div>
                    <h4 className="font-semibold mb-2">Description</h4>
                    <p className="text-sm text-muted-foreground">{assetData.fundamentals.description}</p>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-2">Sector</h4>
                      <Badge variant="secondary">{assetData.fundamentals.sector}</Badge>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Industry</h4>
                      <Badge variant="secondary">{assetData.fundamentals.industry}</Badge>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Employees</h4>
                      <p className="text-sm">{assetData.fundamentals.employees.toLocaleString()}</p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">Founded</h4>
                      <p className="text-sm">{assetData.fundamentals.founded}</p>
                    </div>
                  </div>

                  {assetData.fundamentals.website && (
                    <div>
                      <h4 className="font-semibold mb-2">Website</h4>
                      <a href={assetData.fundamentals.website} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline">
                        {assetData.fundamentals.website}
                      </a>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="news">
          <Card>
            <CardHeader>
              <CardTitle>Latest News</CardTitle>
              <CardDescription>Recent news and sentiment analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {assetData.news?.map((article) => (
                  <div key={article.id} className="flex items-start justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                    <div className="flex-1">
                      <h4 className="font-semibold mb-1">{article.title}</h4>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span>{article.source}</span>
                        <span>•</span>
                        <span>{new Date(article.publishedAt).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <Badge
                      variant={
                        article.sentiment === 'positive' ? 'default' :
                        article.sentiment === 'negative' ? 'destructive' : 'secondary'
                      }
                    >
                      {article.sentiment}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dividends">
          {assetData.dividend ? (
            <Card>
              <CardHeader>
                <CardTitle>Dividend Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <h4 className="font-semibold mb-2">Dividend Yield</h4>
                    <p className="text-2xl font-bold">{assetData.dividend.yield.toFixed(2)}%</p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Frequency</h4>
                    <p className="text-lg">{assetData.dividend.frequency}</p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Last Ex-Dividend Date</h4>
                    <p className="text-lg">{new Date(assetData.dividend.lastExDate).toLocaleDateString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <p className="text-center text-muted-foreground">No dividend information available for this asset</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="similar">
          <Card>
            <CardHeader>
              <CardTitle>Similar Assets</CardTitle>
              <CardDescription>Assets with high correlation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {assetData.similarAssets?.map((asset) => (
                  <div key={asset.symbol} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-semibold">{asset.symbol}</p>
                      <p className="text-sm text-muted-foreground">{asset.name}</p>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline">
                        {asset.correlation >= 0.7 ? 'High' : asset.correlation >= 0.5 ? 'Moderate' : 'Low'} Correlation
                      </Badge>
                      <p className="text-sm text-muted-foreground mt-1">{(asset.correlation * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysts">
          {assetData.analystRatings ? (
            <Card>
              <CardHeader>
                <CardTitle>Analyst Ratings</CardTitle>
                <CardDescription>Consensus ratings and price targets</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-4 gap-4">
                  <div>
                    <h4 className="font-semibold mb-2">Rating</h4>
                    <Badge
                      variant={
                        assetData.analystRatings.rating === 'buy' ? 'default' :
                        assetData.analystRatings.rating === 'hold' ? 'secondary' : 'destructive'
                      }
                      className="text-base px-4 py-2"
                    >
                      {assetData.analystRatings.rating.toUpperCase()}
                    </Badge>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Price Target</h4>
                    <p className="text-2xl font-bold">${assetData.analystRatings.targetPrice}</p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Upside Potential</h4>
                    <p className={`text-2xl font-bold ${assetData.analystRatings.priceTargetUpside >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {assetData.analystRatings.priceTargetUpside >= 0 ? '+' : ''}{assetData.analystRatings.priceTargetUpside.toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Number of Analysts</h4>
                    <p className="text-2xl font-bold">{assetData.analystRatings.analysts}</p>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-4">Rating Distribution</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="w-24 text-sm">Buy</div>
                      <div className="flex-1 bg-muted rounded-full h-4 overflow-hidden">
                        <div className="bg-green-500 h-full" style={{ width: '65%' }}></div>
                      </div>
                      <div className="w-12 text-sm text-right">65%</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-24 text-sm">Hold</div>
                      <div className="flex-1 bg-muted rounded-full h-4 overflow-hidden">
                        <div className="bg-yellow-500 h-full" style={{ width: '28%' }}></div>
                      </div>
                      <div className="w-12 text-sm text-right">28%</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-24 text-sm">Sell</div>
                      <div className="flex-1 bg-muted rounded-full h-4 overflow-hidden">
                        <div className="bg-red-500 h-full" style={{ width: '7%' }}></div>
                      </div>
                      <div className="w-12 text-sm text-right">7%</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <p className="text-center text-muted-foreground">No analyst ratings available for this asset</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {connectionState === 'disconnected' || connectionState === 'error' ? (
        <Card>
          <CardContent className="pt-6">
            <Button onClick={handleConnect} className="w-full">
              Connect Real-Time Data
            </Button>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
