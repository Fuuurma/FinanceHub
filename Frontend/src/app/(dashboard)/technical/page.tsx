'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { PageHeader } from '@/components/ui/page-header'
import { PageTabs, TabContent } from '@/components/ui/page-tabs'
import { cn } from '@/lib/utils'
import {
  Search,
  TrendingUp,
  BarChart2,
  Activity,
  LineChart as LineChartIcon,
  Zap,
  Target,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Filter,
} from 'lucide-react'

const POPULAR_SYMBOLS = [
  { symbol: 'AAPL', name: 'Apple Inc.', type: 'Stock' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', type: 'Stock' },
  { symbol: 'MSFT', name: 'Microsoft Corp.', type: 'Stock' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', type: 'Stock' },
  { symbol: 'TSLA', name: 'Tesla Inc.', type: 'Stock' },
  { symbol: 'NVDA', name: 'NVIDIA Corp.', type: 'Stock' },
  { symbol: 'META', name: 'Meta Platforms', type: 'Stock' },
  { symbol: 'BTC', name: 'Bitcoin', type: 'Crypto' },
  { symbol: 'ETH', name: 'Ethereum', type: 'Crypto' },
  { symbol: 'SOL', name: 'Solana', type: 'Crypto' },
]

interface TechnicalSignal {
  symbol: string
  name: string
  type: 'Stock' | 'Crypto'
  indicator: string
  signal: 'BUY' | 'SELL' | 'NEUTRAL'
  strength: number
  price: number
  change: number
}

interface TrendingIndicator {
  name: string
  description: string
  usage: number
  category: 'trend' | 'momentum' | 'volatility' | 'volume'
}

const MOCK_SIGNALS: TechnicalSignal[] = [
  { symbol: 'NVDA', name: 'NVIDIA Corp.', type: 'Stock', indicator: 'RSI', signal: 'BUY', strength: 85, price: 495.22, change: 4.52 },
  { symbol: 'AAPL', name: 'Apple Inc.', type: 'Stock', indicator: 'MACD', signal: 'BUY', strength: 72, price: 178.50, change: 2.31 },
  { symbol: 'BTC', name: 'Bitcoin', type: 'Crypto', indicator: 'SMA', signal: 'BUY', strength: 68, price: 43250.00, change: 5.17 },
  { symbol: 'TSLA', name: 'Tesla Inc.', type: 'Stock', indicator: 'RSI', signal: 'SELL', strength: 78, price: 248.75, change: -1.23 },
  { symbol: 'AMD', name: 'AMD Inc.', type: 'Stock', indicator: 'Bollinger', signal: 'BUY', strength: 65, price: 178.45, change: 3.87 },
  { symbol: 'ETH', name: 'Ethereum', type: 'Crypto', indicator: 'MACD', signal: 'BUY', strength: 62, price: 2280.50, change: 3.84 },
  { symbol: 'META', name: 'Meta Platforms', type: 'Stock', indicator: 'Stochastic', signal: 'NEUTRAL', strength: 45, price: 485.09, change: 1.56 },
  { symbol: 'JPM', name: 'JPMorgan Chase', type: 'Stock', indicator: 'CCI', signal: 'BUY', strength: 58, price: 172.45, change: 0.89 },
]

const TRENDING_INDICATORS: TrendingIndicator[] = [
  { name: 'RSI', description: 'Relative Strength Index', usage: 15420, category: 'momentum' },
  { name: 'MACD', description: 'Moving Average Convergence Divergence', usage: 12350, category: 'trend' },
  { name: 'SMA 50/200', description: 'Golden/Death Cross', usage: 9870, category: 'trend' },
  { name: 'Bollinger Bands', description: 'Volatility Bands', usage: 8540, category: 'volatility' },
  { name: 'ATR', description: 'Average True Range', usage: 6780, category: 'volatility' },
  { name: 'Volume Profile', description: 'Volume by Price', usage: 5430, category: 'volume' },
]

export default function TechnicalPage() {
  const router = useRouter()
  const [searchInput, setSearchInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [signals, setSignals] = useState<TechnicalSignal[]>([])
  const [trending, setTrending] = useState<TrendingIndicator[]>([])

  useEffect(() => {
    fetchTechnicalData()
  }, [])

  const fetchTechnicalData = async () => {
    setLoading(true)
    setError('')
    try {
      await new Promise(resolve => setTimeout(resolve, 800))
      setSignals(MOCK_SIGNALS)
      setTrending(TRENDING_INDICATORS)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch technical data')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchInput.trim()) {
      router.push(`/technical/${searchInput.toUpperCase()}`)
    }
  }

  const handleSymbolClick = (symbol: string) => {
    router.push(`/technical/${symbol}`)
  }

  const tabs = [
    { value: 'signals', label: 'Live Signals', icon: Zap, badge: signals.length },
    { value: 'trending', label: 'Trending', icon: TrendingUp },
    { value: 'indicators', label: 'Indicators', icon: Target },
  ]

  const formatStrength = (strength: number): string => {
    if (strength >= 70) return 'Strong'
    if (strength >= 50) return 'Moderate'
    return 'Weak'
  }

  const signalColors = {
    BUY: 'bg-green-100 text-green-700 border-green-300',
    SELL: 'bg-red-100 text-red-700 border-red-300',
    NEUTRAL: 'bg-gray-100 text-gray-700 border-gray-300',
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Technical Analysis"
        description="Advanced technical indicators, signals, and chart analysis"
        loading={loading}
        onRefresh={fetchTechnicalData}
        actions={
          <div className="relative w-full sm:w-64">
            <form onSubmit={handleSearch}>
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Enter symbol..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
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

      <PageTabs tabs={tabs} defaultValue="signals" tabsClassName="grid w-full grid-cols-3">
        <TabContent value="signals" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                Today's Top Signals
              </CardTitle>
              <CardDescription>
                Assets with strong technical signals (RSI, MACD, Bollinger Bands)
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((i) => (
                    <Skeleton key={i} className="h-20" />
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {signals.map((signal) => (
                    <div
                      key={signal.symbol}
                      className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer"
                      onClick={() => handleSymbolClick(signal.symbol)}
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center font-bold">
                          {signal.symbol[0]}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold">{signal.symbol}</span>
                            <Badge variant="outline" className="text-xs">
                              {signal.type}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">{signal.name}</div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {signal.indicator} • Strength: {signal.strength}%
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">${signal.price.toLocaleString()}</div>
                        <div className={cn(
                          'flex items-center justify-end gap-1 text-sm',
                          signal.change >= 0 ? 'text-green-600' : 'text-red-600'
                        )}>
                          {signal.change >= 0 ? (
                            <ArrowUpRight className="h-4 w-4" />
                          ) : (
                            <ArrowDownRight className="h-4 w-4" />
                          )}
                          {signal.change >= 0 ? '+' : ''}{signal.change.toFixed(2)}%
                        </div>
                        <Badge className={cn('mt-2', signalColors[signal.signal])}>
                          {signal.signal} • {formatStrength(signal.strength)}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabContent>

        <TabContent value="trending" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-500" />
                Trending Indicators
              </CardTitle>
              <CardDescription>
                Most used technical indicators by FinanceHub users today
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((i) => (
                    <Skeleton key={i} className="h-16" />
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {trending.map((indicator, idx) => (
                    <div
                      key={indicator.name}
                      className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <span className="text-muted-foreground font-mono w-6">{idx + 1}</span>
                        <div>
                          <div className="font-semibold flex items-center gap-2">
                            {indicator.name}
                            <Badge variant="outline" className="text-xs">
                              {indicator.category}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">{indicator.description}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{indicator.usage.toLocaleString()}</div>
                        <div className="text-xs text-muted-foreground">uses today</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabContent>

        <TabContent value="indicators" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-500" />
                  Trend Indicators
                </CardTitle>
                <CardDescription>
                  SMA, EMA, WMA, VWAP, Ichimoku
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Identify trends and trend reversals with moving averages and cloud indicators
                </p>
                <div className="flex flex-wrap gap-2 mt-4">
                  {['SMA', 'EMA', 'WMA', 'VWAP', 'Ichimoku', 'Parabolic SAR'].map((ind) => (
                    <Badge key={ind} variant="outline">{ind}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-orange-500" />
                  Momentum Indicators
                </CardTitle>
                <CardDescription>
                  RSI, MACD, Stochastic, CCI, MFI
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Measure overbought/oversold conditions and momentum strength
                </p>
                <div className="flex flex-wrap gap-2 mt-4">
                  {['RSI', 'MACD', 'Stochastic', 'CCI', 'MFI', 'Williams %R'].map((ind) => (
                    <Badge key={ind} variant="outline">{ind}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChartIcon className="h-5 w-5 text-purple-500" />
                  Volatility Indicators
                </CardTitle>
                <CardDescription>
                  Bollinger Bands, ATR, Parabolic SAR
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Analyze price volatility and set stop-loss levels
                </p>
                <div className="flex flex-wrap gap-2 mt-4">
                  {['Bollinger Bands', 'ATR', 'Keltner Channels', 'Donchian'].map((ind) => (
                    <Badge key={ind} variant="outline">{ind}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Volume Indicators</CardTitle>
              <CardDescription>
                On-Balance Volume, Volume RSI, Accumulation/Distribution
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {['OBV', 'VWAP', 'Volume Profile', 'A/D Line', 'CMF'].map((ind) => (
                  <Badge key={ind} variant="outline">{ind}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabContent>
      </PageTabs>

      <Card>
        <CardHeader>
          <CardTitle>Quick Access</CardTitle>
          <CardDescription>
            Click a symbol to start technical analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-5">
            {POPULAR_SYMBOLS.map((item) => (
              <button
                key={item.symbol}
                onClick={() => handleSymbolClick(item.symbol)}
                className="flex flex-col items-start p-3 rounded-lg border hover:bg-accent hover:border-primary transition-colors text-left"
              >
                <div className="flex items-center justify-between w-full">
                  <span className="font-medium">{item.symbol}</span>
                  <Badge variant={item.type === 'Crypto' ? 'default' : 'secondary'} className="text-xs">
                    {item.type}
                  </Badge>
                </div>
                <span className="text-sm text-muted-foreground truncate w-full">
                  {item.name}
                </span>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
