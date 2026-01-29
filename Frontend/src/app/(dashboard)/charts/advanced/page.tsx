'use client'

import { useState, useCallback } from 'react'
import { TradingViewChart, ChartControls, type ChartType, type Timeframe } from '@/components/charts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { LineChart, TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react'
import { assetsApi } from '@/lib/api/assets'

export default function AdvancedChartsPage() {
  const [symbol, setSymbol] = useState('AAPL')
  const [timeframe, setTimeframe] = useState<Timeframe>('1d')
  const [chartType, setChartType] = useState<ChartType>('candlestick')
  const [showVolume, setShowVolume] = useState(true)
  const [activeIndicators, setActiveIndicators] = useState<string[]>([])

  const [priceData, setPriceData] = useState<{
    current: number | null
    change: number | null
    changePercent: number | null
    high: number | null
    low: number | null
    open: number | null
    previousClose: number | null
    volume: number | null
  }>({
    current: null,
    change: null,
    changePercent: null,
    high: null,
    low: null,
    open: null,
    previousClose: null,
    volume: null,
  })

  const loadPriceData = useCallback(async () => {
    try {
      const quote = await assetsApi.getPrice(symbol)
      if (quote) {
        setPriceData({
          current: quote.price || null,
          change: quote.change || null,
          changePercent: quote.change_percent || null,
          high: quote.high || null,
          low: quote.low || null,
          open: quote.open || null,
          previousClose: null,
          volume: quote.volume || null,
        })
      }
    } catch (error) {
      console.error('Failed to load price data:', error)
    }
  }, [symbol])

  const handleSymbolChange = useCallback((newSymbol: string) => {
    setSymbol(newSymbol)
    loadPriceData()
  }, [loadPriceData])

  const handleTimeframeChange = useCallback((tf: Timeframe) => {
    setTimeframe(tf)
  }, [])

  const handleTypeChange = useCallback((type: ChartType) => {
    setChartType(type)
  }, [])

  const handleVolumeToggle = useCallback((show: boolean) => {
    setShowVolume(show)
  }, [])

  const handleIndicatorToggle = useCallback((indicator: string, show: boolean) => {
    setActiveIndicators((prev) =>
      show ? [...prev, indicator] : prev.filter((i) => i !== indicator)
    )
  }, [])

  const formatPrice = (value: number | null) => {
    if (value === null) return '--'
    return `$${value.toFixed(2)}`
  }

  const formatChange = (value: number | null) => {
    if (value === null) return '--'
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(2)}%`
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Advanced Charts</h1>
          <p className="text-muted-foreground mt-1">
            Professional charting powered by TradingView Lightweight Charts
          </p>
        </div>
        <Badge variant="outline" className="text-sm">
          {symbol} / USD
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Current Price
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <span className="text-2xl font-bold">{formatPrice(priceData.current)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              24h Change
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {(priceData.changePercent ?? 0) >= 0 ? (
                <TrendingUp className="h-4 w-4 text-green-500" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-500" />
              )}
              <span className={`text-2xl font-bold ${
                (priceData.changePercent ?? 0) >= 0 ? 'text-green-500' : 'text-red-500'
              }`}>
                {formatChange(priceData.changePercent)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              24h High / Low
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium">{formatPrice(priceData.high)}</span>
              <span className="text-muted-foreground">/</span>
              <span className="font-medium">{formatPrice(priceData.low)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              24h Volume
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="text-2xl font-bold">
                {priceData.volume ? (priceData.volume / 1000000).toFixed(2) + 'M' : '--'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="chart" className="space-y-4">
        <TabsList>
          <TabsTrigger value="chart">Chart</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="watchlist">Watchlist</TabsTrigger>
        </TabsList>

        <TabsContent value="chart" className="space-y-4">
          <ChartControls
            symbol={symbol}
            currentTimeframe={timeframe}
            currentType={chartType}
            showVolume={showVolume}
            activeIndicators={activeIndicators}
            onSymbolChange={handleSymbolChange}
            onTimeframeChange={handleTimeframeChange}
            onTypeChange={handleTypeChange}
            onVolumeToggle={handleVolumeToggle}
            onIndicatorToggle={handleIndicatorToggle}
          />

          <TradingViewChart
            symbol={symbol}
            chartType={chartType}
            timeframe={timeframe}
            height={600}
            showVolume={showVolume}
            showIndicators={activeIndicators}
            onSymbolChange={handleSymbolChange}
          />

          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Chart by TradingView Lightweight Charts</span>
            <Separator orientation="vertical" className="h-4" />
            <span>Data provided by Polygon.io</span>
          </div>
        </TabsContent>

        <TabsContent value="analysis">
          <Card>
            <CardHeader>
              <CardTitle>Technical Analysis</CardTitle>
              <CardDescription>
                Select indicators to overlay on the chart
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                {[
                  { id: 'sma20', name: 'SMA 20', desc: 'Simple Moving Average (20 periods)' },
                  { id: 'sma50', name: 'SMA 50', desc: 'Simple Moving Average (50 periods)' },
                  { id: 'sma200', name: 'SMA 200', desc: 'Simple Moving Average (200 periods)' },
                  { id: 'ema12', name: 'EMA 12', desc: 'Exponential Moving Average (12 periods)' },
                  { id: 'ema26', name: 'EMA 26', desc: 'Exponential Moving Average (26 periods)' },
                  { id: 'rsi14', name: 'RSI 14', desc: 'Relative Strength Index (14 periods)' },
                  { id: 'macd', name: 'MACD', desc: 'Moving Average Convergence Divergence' },
                  { id: 'bollinger', name: 'Bollinger Bands', desc: 'Bollinger Bands (20, 2)' },
                ].map((indicator) => (
                  <div
                    key={indicator.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      activeIndicators.includes(indicator.id)
                        ? 'border-primary bg-primary/5'
                        : 'hover:border-primary/50'
                    }`}
                    onClick={() => handleIndicatorToggle(
                      indicator.id,
                      !activeIndicators.includes(indicator.id)
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{indicator.name}</span>
                      {activeIndicators.includes(indicator.id) && (
                        <Badge variant="default">Active</Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{indicator.desc}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="watchlist">
          <Card>
            <CardHeader>
              <CardTitle>Watchlist</CardTitle>
              <CardDescription>
                Quick access to your favorite symbols
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 md:grid-cols-4">
                {['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM'].map((sym) => (
                  <Button
                    key={sym}
                    variant={symbol === sym ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleSymbolChange(sym)}
                  >
                    {sym}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
