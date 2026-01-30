'use client'

import { useState, useCallback, useEffect, useMemo } from 'react'
import { TradingViewChart, ChartControls, IndicatorConfigModal, type ChartType, type Timeframe } from '@/components/charts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { PageErrorBoundary } from '@/components/ui/PageErrorBoundary'
import {
  LineChart,
  TrendingUp,
  TrendingDown,
  Activity,
  DollarSign,
  Maximize2,
  Minimize2,
  Download,
  Share2,
  Bell,
  Clock,
  Calendar,
  Zap,
  Settings,
} from 'lucide-react'
import { assetsApi } from '@/lib/api/assets'
import { IndicatorConfig } from '@/lib/utils/technical-indicators'

function AdvancedChartsPageContent() {
  const [symbol, setSymbol] = useState('AAPL')
  const [timeframe, setTimeframe] = useState<Timeframe>('1d')
  const [chartType, setChartType] = useState<ChartType>('candlestick')
  const [showVolume, setShowVolume] = useState(true)
  const [activeIndicators, setActiveIndicators] = useState<string[]>([])
  const [indicatorConfig, setIndicatorConfig] = useState<IndicatorConfig>({})
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

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

  const [priceChangePercent, setPriceChangePercent] = useState<number | null>(null)

  const loadPriceData = useCallback(async () => {
    try {
      setIsLoading(true)
      const quote = await assetsApi.getPrice(symbol)
      if (quote) {
        const change = quote.change_percent || 0
        setPriceChangePercent(change)
        setPriceData({
          current: quote.price || null,
          change: quote.change || null,
          changePercent: change,
          high: quote.high || null,
          low: quote.low || null,
          open: quote.open || null,
          previousClose: null,
          volume: quote.volume || null,
        })
      }
    } catch (error) {
      console.error('Failed to load price data:', error)
    } finally {
      setIsLoading(false)
    }
  }, [symbol])

  useEffect(() => {
    loadPriceData()
  }, [loadPriceData])

  const handleSymbolChange = useCallback((newSymbol: string) => {
    setSymbol(newSymbol)
  }, [])

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

  const formatVolume = (value: number | null) => {
    if (value === null) return '--'
    if (value >= 1000000000) return `${(value / 1000000000).toFixed(2)}B`
    if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`
    if (value >= 1000) return `${(value / 1000).toFixed(2)}K`
    return value.toString()
  }

  const priceCards = useMemo(() => [
    {
      title: 'Current Price',
      value: formatPrice(priceData.current),
      icon: DollarSign,
      color: 'text-foreground',
    },
    {
      title: '24h Change',
      value: formatChange(priceData.changePercent),
      icon: priceData.changePercent !== null && priceData.changePercent >= 0 ? TrendingUp : TrendingDown,
      color: priceData.changePercent !== null && priceData.changePercent >= 0 ? 'text-green-500' : 'text-red-500',
      badge: priceData.changePercent !== null && priceData.changePercent >= 0 ? '+' : '',
    },
    {
      title: '24h High / Low',
      value: `${formatPrice(priceData.high)} / ${formatPrice(priceData.low)}`,
      icon: Activity,
      color: 'text-foreground',
      mono: true,
    },
    {
      title: '24h Volume',
      value: formatVolume(priceData.volume),
      icon: Clock,
      color: 'text-muted-foreground',
    },
  ], [priceData])

  const popularSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'BTC', 'ETH', 'SPY', 'QQQ']

  return (
    <div className={`container mx-auto py-6 space-y-6 ${isFullscreen ? 'fixed inset-0 z-50 bg-background p-6' : ''}`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">Advanced Charts</h1>
            <Badge variant="outline" className="text-sm">
              {symbol} / USD
            </Badge>
            {priceChangePercent !== null && (
              <Badge variant={priceChangePercent >= 0 ? 'default' : 'destructive'} className={priceChangePercent >= 0 ? 'bg-green-500' : ''}>
                {priceChangePercent >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                {priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%
              </Badge>
            )}
          </div>
          <p className="text-muted-foreground mt-1">
            Professional charting powered by TradingView Lightweight Charts with technical indicators
          </p>
        </div>
        <div className="flex items-center gap-2">
          <IndicatorConfigModal
            showIndicators={activeIndicators}
            indicatorConfig={indicatorConfig}
            onShowIndicatorsChange={setActiveIndicators}
            onIndicatorConfigChange={setIndicatorConfig}
          >
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-1" />
              Indicators
              {activeIndicators.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
                  {activeIndicators.length}
                </span>
              )}
            </Button>
          </IndicatorConfigModal>
          <Button variant="outline" size="sm" onClick={() => setIsFullscreen(!isFullscreen)}>
            {isFullscreen ? <Minimize2 className="h-4 w-4 mr-1" /> : <Maximize2 className="h-4 w-4 mr-1" />}
            {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="h-4 w-4 mr-1" />
            Share
          </Button>
          <Button variant="outline" size="sm">
            <Bell className="h-4 w-4 mr-1" />
            Alert
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {priceCards.map((card, index) => (
          <Card key={card.title} className={index === 1 && priceData.changePercent !== null && priceData.changePercent < 0 ? 'border-red-200 dark:border-red-900' : ''}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <card.icon className="h-4 w-4" />
                {card.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <div className={`text-2xl font-bold ${card.color}`}>
                  {card.badge && <span className="text-sm mr-0.5">{card.badge}</span>}
                  {card.value}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="chart" className="space-y-4">
        <TabsList>
          <TabsTrigger value="chart">
            <LineChart className="h-4 w-4 mr-2" />
            Chart
          </TabsTrigger>
          <TabsTrigger value="analysis">
            <Activity className="h-4 w-4 mr-2" />
            Technical Analysis
          </TabsTrigger>
          <TabsTrigger value="watchlist">
            <Zap className="h-4 w-4 mr-2" />
            Watchlist
          </TabsTrigger>
        </TabsList>

        <TabsContent value="chart" className="space-y-4">
          <IndicatorConfigModal
            showIndicators={activeIndicators}
            indicatorConfig={indicatorConfig}
            onShowIndicatorsChange={setActiveIndicators}
            onIndicatorConfigChange={setIndicatorConfig}
          >
            <div />
          </IndicatorConfigModal>

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
            height={isFullscreen ? window.innerHeight - 300 : 700}
            showVolume={showVolume}
            showIndicators={activeIndicators}
            indicatorConfig={indicatorConfig}
            onSymbolChange={handleSymbolChange}
          />

          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-sm bg-green-500" />
                Bullish
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-sm bg-red-500" />
                Bearish
              </span>
              <span>Keyboard shortcuts: 1-8 for timeframes, C/L/A/B for chart types</span>
            </div>
            <div className="flex items-center gap-2">
              <Separator orientation="vertical" className="h-4" />
              <span className="flex items-center gap-1">
                <Download className="h-4 w-4" />
                Data by Polygon.io
              </span>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="analysis">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Technical Analysis
              </CardTitle>
              <CardDescription>
                Select indicators to overlay on the chart. Active indicators will appear on your chart.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {activeIndicators.length > 0 && (
                <div className="mb-4 p-3 bg-primary/5 border border-primary/20 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Active Indicators</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-xs"
                      onClick={() => setActiveIndicators([])}
                    >
                      Clear all
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {activeIndicators.map((id) => {
                      const indicator = [
                        { id: 'sma20', name: 'SMA 20' },
                        { id: 'sma50', name: 'SMA 50' },
                        { id: 'sma200', name: 'SMA 200' },
                        { id: 'ema12', name: 'EMA 12' },
                        { id: 'ema26', name: 'EMA 26' },
                        { id: 'rsi', name: 'RSI 14' },
                        { id: 'macd', name: 'MACD' },
                        { id: 'bollinger', name: 'Bollinger Bands' },
                      ].find((i) => i.id === id)
                      return (
                        <Badge key={id} variant="secondary" className="flex items-center gap-1">
                          {indicator?.name || id}
                          <button
                            className="ml-1 hover:text-destructive"
                            onClick={() => handleIndicatorToggle(id, false)}
                          >
                            ×
                          </button>
                        </Badge>
                      )
                    })}
                  </div>
                </div>
              )}

              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {[
                  { id: 'sma20', name: 'SMA 20', desc: 'Simple Moving Average (20 periods)', category: 'Moving Averages', color: '#3b82f6' },
                  { id: 'sma50', name: 'SMA 50', desc: 'Simple Moving Average (50 periods)', category: 'Moving Averages', color: '#22c55e' },
                  { id: 'sma200', name: 'SMA 200', desc: 'Simple Moving Average (200 periods)', category: 'Moving Averages', color: '#f59e0b' },
                  { id: 'ema12', name: 'EMA 12', desc: 'Exponential Moving Average (12 periods)', category: 'Moving Averages', color: '#8b5cf6' },
                  { id: 'ema26', name: 'EMA 26', desc: 'Exponential Moving Average (26 periods)', category: 'Moving Averages', color: '#ec4899' },
                  { id: 'rsi', name: 'RSI 14', desc: 'Relative Strength Index (14 periods)', category: 'Oscillators', color: '#06b6d4' },
                  { id: 'macd', name: 'MACD', desc: 'Moving Average Convergence Divergence', category: 'Oscillators', color: '#f97316' },
                  { id: 'bollinger', name: 'Bollinger Bands', desc: 'Bollinger Bands (20, 2)', category: 'Volatility', color: '#84cc16' },
                ].map((indicator) => (
                  <div
                    key={indicator.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      activeIndicators.includes(indicator.id)
                        ? 'border-primary bg-primary/5 shadow-sm'
                        : 'hover:border-primary/50 hover:bg-muted/50'
                    }`}
                    onClick={() => handleIndicatorToggle(
                      indicator.id,
                      !activeIndicators.includes(indicator.id)
                    )}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium flex items-center gap-2">
                        <span
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: indicator.color }}
                        />
                        {indicator.name}
                      </span>
                      {activeIndicators.includes(indicator.id) && (
                        <Badge variant="default" className="text-xs">Active</Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{indicator.desc}</p>
                    <p className="text-xs text-muted-foreground mt-2">{indicator.category}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="watchlist">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Quick Access Watchlist
              </CardTitle>
              <CardDescription>
                Click on any symbol to load it in the chart
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 md:grid-cols-4 lg:grid-cols-6">
                {popularSymbols.map((sym) => (
                  <Button
                    key={sym}
                    variant={symbol === sym ? 'default' : 'outline'}
                    size="sm"
                    className="font-mono"
                    onClick={() => handleSymbolChange(sym)}
                  >
                    {sym}
                  </Button>
                ))}
              </div>
              <Separator className="my-4" />
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  Press number keys 1-8 to change timeframe
                </span>
                <span className="flex items-center gap-1">
                  <span className="font-mono">C</span> / <span className="font-mono">L</span> / <span className="font-mono">A</span> / <span className="font-mono">B</span> to change chart type
                </span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default function AdvancedChartsPage() {
  return (
    <PageErrorBoundary
      onError={(error, errorInfo) => {
        console.error('Advanced Charts page error:', error, errorInfo)
      }}
    >
      <AdvancedChartsPageContent />
    </PageErrorBoundary>
  )
}
