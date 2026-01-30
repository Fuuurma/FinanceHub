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
import { TradingViewChart, ChartControls } from '@/components/charts'
import { OrderBook } from '@/components/realtime/OrderBook'
import { TradeFeed } from '@/components/realtime/TradeFeed'
import { useRealtimeStore } from '@/stores/realtimeStore'
import type { ChartType, Timeframe } from '@/components/charts'

type TimeFrame = '1D' | '1W' | '1M' | '3M' | '1Y' | 'ALL'
type IndicatorType = 'SMA' | 'EMA' | 'RSI' | 'MACD' | 'BB'

const TIMEFRAME_MAP: Record<string, string> = {
  '1D': '1d',
  '1W': '1w',
  '1M': '1m',
  '3M': '3m',
  '1Y': '1y',
  'ALL': '1y',
}

function getChartTimeframe(tf: TimeFrame): '1d' | '1w' | '1m' | '1h' | '5m' | '15m' | '4h' | undefined {
  return TIMEFRAME_MAP[tf] as '1d' | '1w' | '1m' | '1h' | '5m' | '15m' | '4h' | undefined
}

interface AssetData {
  symbol: string
  name: string
  type: 'stock' | 'crypto' | 'etf' | 'index'
  price: number
  change: number
  changePercent: number
  marketCap: number
  volume: number
  dayHigh: number
  dayLow: number
  week52High: number
  week52Low: number
  avgVolume: number
  peRatio?: number
  pbRatio?: number
  eps?: number
  dividend?: {
    yield: number
    frequency: string
    lastExDate: string
    amount: number
  }
  fundamentals?: {
    sector: string
    industry: string
    description: string
    employees: number
    founded: string
    website: string
    marketCap?: number
    revenue?: number
    profitMargin?: number
    roe?: number
    debtToEquity?: number
  }
  technicals?: {
    rsi?: number
    macd?: number
    sma20?: number
    sma50?: number
    sma200?: number
    support?: number
    resistance?: number
  }
  financials?: {
    revenue?: number
    netIncome?: number
    totalAssets?: number
    totalDebt?: number
    operatingCashFlow?: number
    freeCashFlow?: number
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
        dayHigh: 180.15,
        dayLow: 176.40,
        week52High: 199.62,
        week52Low: 124.17,
        avgVolume: 58200000,
        peRatio: 28.5,
        pbRatio: 45.2,
        eps: 6.27,
        dividend: {
          yield: 0.52,
          frequency: 'Quarterly',
          lastExDate: '2024-02-09',
          amount: 0.24
        },
        fundamentals: {
          sector: 'Technology',
          industry: 'Consumer Electronics',
          description: 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.',
          employees: 164000,
          founded: '1976',
          website: 'https://www.apple.com',
          revenue: 383285000000,
          profitMargin: 25.3,
          roe: 147.9,
          debtToEquity: 1.87
        },
        technicals: {
          rsi: 58.4,
          macd: 1.2,
          sma20: 176.8,
          sma50: 179.2,
          sma200: 175.4,
          support: 175.0,
          resistance: 182.5
        },
        financials: {
          revenue: 383285000000,
          netIncome: 96995000000,
          totalAssets: 352583000000,
          totalDebt: 115964000000,
          operatingCashFlow: 110543000000,
          freeCashFlow: 99584000000
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
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || undefined : undefined
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
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <ChartControls
            symbol={assetId.toUpperCase()}
            currentTimeframe={getChartTimeframe(selectedTimeFrame) || '1d'}
            currentType="candlestick"
            onSymbolChange={() => {}}
            onTimeframeChange={(tf) => {
              const tfMap: Record<string, TimeFrame> = {
                '1m': '1M', '5m': '1M', '15m': '1M',
                '1h': '1D', '4h': '1D',
                '1d': '1D', '1w': '1W', '1M': '1M'
              }
              setSelectedTimeFrame(tfMap[tf] || '1D')
            }}
          />
          <TradingViewChart
            symbol={assetId.toUpperCase()}
            chartType="candlestick"
            timeframe={getChartTimeframe(selectedTimeFrame) || '1d'}
            height={500}
            showVolume={true}
          />
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="fundamentals">Fundamentals</TabsTrigger>
          <TabsTrigger value="technicals">Technicals</TabsTrigger>
          <TabsTrigger value="financials">Financials</TabsTrigger>
          <TabsTrigger value="news">News</TabsTrigger>
          <TabsTrigger value="dividends">Dividends</TabsTrigger>
          <TabsTrigger value="analysts">Analysts</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Compact Stats Grid - 1/4 size */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Key Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 md:grid-cols-8 lg:grid-cols-12 gap-3">
                {/* Price Data */}
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">Market Cap</p>
                  <p className="text-sm font-bold">${(assetData.marketCap / 1000000000000).toFixed(2)}T</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">Day High</p>
                  <p className="text-sm font-semibold text-green-600">${assetData.dayHigh?.toFixed(2)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">Day Low</p>
                  <p className="text-sm font-semibold text-red-600">${assetData.dayLow?.toFixed(2)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">52W High</p>
                  <p className="text-sm font-semibold">${assetData.week52High?.toFixed(2)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">52W Low</p>
                  <p className="text-sm font-semibold">${assetData.week52Low?.toFixed(2)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">Volume</p>
                  <p className="text-sm font-bold">{(assetData.volume / 1000000).toFixed(1)}M</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">Avg Vol</p>
                  <p className="text-sm font-semibold">{(assetData.avgVolume / 1000000).toFixed(1)}M</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">P/E Ratio</p>
                  <p className="text-sm font-bold">{assetData.peRatio?.toFixed(2)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">P/B Ratio</p>
                  <p className="text-sm font-semibold">{assetData.pbRatio?.toFixed(2)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">EPS</p>
                  <p className="text-sm font-bold">${assetData.eps?.toFixed(2)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">Div Yield</p>
                  <p className="text-sm font-semibold">{assetData.dividend?.yield.toFixed(2)}%</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-muted-foreground uppercase font-medium">Div Amount</p>
                  <p className="text-sm font-bold">${assetData.dividend?.amount.toFixed(2)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid md:grid-cols-2 gap-6">
            <OrderBook symbol={assetId} />
            <TradeFeed symbol={assetId} />
          </div>
        </TabsContent>

        {/* Technicals Tab */}
        <TabsContent value="technicals" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Technical Indicators</CardTitle>
              <CardDescription>Key technical metrics and levels</CardDescription>
            </CardHeader>
            <CardContent>
              {assetData.technicals ? (
                <div className="grid grid-cols-4 md:grid-cols-8 lg:grid-cols-12 gap-3">
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">RSI (14)</p>
                    <p className={`text-sm font-bold ${
                      (assetData.technicals.rsi || 0) >= 70 ? 'text-red-600' :
                      (assetData.technicals.rsi || 0) <= 30 ? 'text-green-600' :
                      ''
                    }`}>
                      {assetData.technicals.rsi?.toFixed(2)}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">MACD</p>
                    <p className={`text-sm font-bold ${(assetData.technicals.macd || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {assetData.technicals.macd?.toFixed(2)}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">SMA 20</p>
                    <p className="text-sm font-semibold">${assetData.technicals.sma20?.toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">SMA 50</p>
                    <p className="text-sm font-semibold">${assetData.technicals.sma50?.toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">SMA 200</p>
                    <p className="text-sm font-semibold">${assetData.technicals.sma200?.toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Support</p>
                    <p className="text-sm font-bold text-green-600">${assetData.technicals.support?.toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Resistance</p>
                    <p className="text-sm font-bold text-red-600">${assetData.technicals.resistance?.toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">vs SMA20</p>
                    <p className={`text-sm font-semibold ${(assetData.price || 0) > (assetData.technicals.sma20 || 0) ? 'text-green-600' : 'text-red-600'}`}>
                      {(assetData.price || 0) > (assetData.technicals.sma20 || 0) ? 'Above' : 'Below'}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-center text-muted-foreground">Technical data not available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Financials Tab */}
        <TabsContent value="financials" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Financial Metrics</CardTitle>
              <CardDescription>Key financial data (in millions)</CardDescription>
            </CardHeader>
            <CardContent>
              {assetData.financials ? (
                <div className="grid grid-cols-4 md:grid-cols-8 lg:grid-cols-12 gap-3">
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Revenue</p>
                    <p className="text-sm font-bold">${(assetData.financials.revenue! / 1000000).toFixed(0)}M</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Net Income</p>
                    <p className="text-sm font-semibold">${(assetData.financials.netIncome! / 1000000).toFixed(0)}M</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Total Assets</p>
                    <p className="text-sm font-bold">${(assetData.financials.totalAssets! / 1000000000).toFixed(1)}B</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Total Debt</p>
                    <p className="text-sm font-semibold">${(assetData.financials.totalDebt! / 1000000000).toFixed(1)}B</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Op Cash Flow</p>
                    <p className="text-sm font-bold text-green-600">${(assetData.financials.operatingCashFlow! / 1000000000).toFixed(1)}B</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Free Cash Flow</p>
                    <p className="text-sm font-semibold text-green-600">${(assetData.financials.freeCashFlow! / 1000000000).toFixed(1)}B</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Profit Margin</p>
                    <p className="text-sm font-bold">{assetData.fundamentals?.profitMargin?.toFixed(1)}%</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">ROE</p>
                    <p className="text-sm font-semibold">{assetData.fundamentals?.roe?.toFixed(1)}%</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Debt/Equity</p>
                    <p className="text-sm font-bold">{assetData.fundamentals?.debtToEquity?.toFixed(2)}</p>
                  </div>
                </div>
              ) : (
                <p className="text-center text-muted-foreground">Financial data not available</p>
              )}
            </CardContent>
          </Card>
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
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Latest News</CardTitle>
                  <CardDescription>Recent news and sentiment analysis</CardDescription>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <a href="/sentiment">View All News →</a>
                </Button>
              </div>
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
