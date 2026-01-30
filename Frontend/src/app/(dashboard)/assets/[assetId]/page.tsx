'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import {
  TrendingUp, TrendingDown, Activity, Globe, Info,
  Zap, BarChart3, ShieldCheck, Calendar,
  DollarSign, PieChart, Newspaper, Star, Target,
  ArrowUpRight, ArrowDownRight, Minus, ChevronDown, ChevronRight
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { ConnectionStatus } from '@/components/realtime/ConnectionStatus'
import { PageErrorBoundary } from '@/components/ui/PageErrorBoundary'
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

interface CollapsibleSectionProps {
  section: {
    id: string
    title: string
    items: Array<{ label: string; value: string; good?: boolean }>
  }
}

function CollapsibleSection({ section }: CollapsibleSectionProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-muted/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          <span className="text-sm font-semibold">{section.title}</span>
        </div>
        <span className="text-xs text-muted-foreground">{section.items.length} metrics</span>
      </button>
      {isExpanded && (
        <div className="border-t p-3 grid grid-cols-2 md:grid-cols-4 gap-2">
          {section.items.map((item, idx) => (
            <div key={idx} className="space-y-1">
              <p className="text-[10px] text-muted-foreground uppercase">{item.label}</p>
              <p className={`text-sm font-semibold ${item.good ? 'text-green-600' : 'text-red-600'}`}>
                {item.value}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
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

function AssetDetailPageContent() {
  const params = useParams()
  const assetId = params.assetId as string
  
  const { connect, connectionState, prices, subscribeSingle, unsubscribeSingle } = useRealtimeStore()
  const [selectedTimeFrame, setSelectedTimeFrame] = useState<TimeFrame>('1D')
  const [activeTab, setActiveTab] = useState('overview')
  const [assetData, setAssetData] = useState<AssetData | null>(null)
  const [loading, setLoading] = useState(true)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({})

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }))
  }

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
      {/* Header - Symbol Prominent */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-baseline gap-4 mb-2">
                <h1 className="text-6xl font-bold tracking-tight">{assetData.symbol}</h1>
                <span className="text-2xl text-muted-foreground font-light">{assetData.name}</span>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="text-sm px-3 py-1">
                  {assetData.type.toUpperCase()}
                </Badge>
                {assetData.fundamentals?.sector && (
                  <Badge variant="secondary" className="text-sm px-3 py-1">
                    {assetData.fundamentals.sector}
                  </Badge>
                )}
                <span className="text-sm text-muted-foreground">
                  {assetData.fundamentals?.industry}
                </span>
              </div>
            </div>
            
            <div className="text-right space-y-1">
              <div className="text-5xl font-bold tracking-tight">
                {currentPrice ? `$${currentPrice.price.toFixed(2)}` : `$${assetData.price.toFixed(2)}`}
              </div>
              <div className={`flex items-center gap-2 justify-end text-lg ${assetData.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {assetData.change >= 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
                <span className="font-semibold">
                  {assetData.change >= 0 ? '+' : ''}{assetData.change.toFixed(2)} ({assetData.changePercent >= 0 ? '+' : ''}{assetData.changePercent.toFixed(2)}%)
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comprehensive Data Collapsible */}
      <Card>
        <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Comprehensive Data
            <Badge variant="outline" className="text-xs">32 Sections</Badge>
          </CardTitle>
          <CardDescription>Expand for detailed analysis</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            {
              id: 'realtime',
              title: 'Real-Time Data',
              items: [
                { label: 'Last Trade', value: '$178.75', good: true },
                { label: 'Trade Size', value: '2,500', good: true },
                { label: 'Bid Size', value: '15,400', good: true },
                { label: 'Ask Size', value: '12,800', good: true },
                { label: 'Spread', value: '$0.01', good: true },
                { label: 'Tick Volume', value: '45,230', good: true },
                { label: 'Money Flow', value: '+$1.2B', good: true },
                { label: 'Trades (1h)', value: '23,450', good: true },
              ]
            },
            {
              id: 'adv-technicals',
              title: 'Advanced Technicals',
              items: [
                { label: 'RSI (14)', value: '58.4', good: true },
                { label: 'MACD', value: '1.2', good: true },
                { label: 'ATR (14)', value: '2.15', good: true },
                { label: 'Williams %R', value: '-45.2', good: true },
                { label: 'Stochastic %K', value: '68.5', good: true },
                { label: 'CCI (20)', value: '85.2', good: true },
                { label: 'MFI (14)', value: '72.1', good: false },
                { label: 'OBV', value: '+2.1B', good: true },
              ]
            },
            {
              id: 'options-flow',
              title: 'Options Activity',
              items: [
                { label: 'Put/Call Ratio', value: '0.65', good: true },
                { label: 'IV Rank', value: '22.5', good: true },
                { label: 'IV Percentile', value: '45.2', good: true },
                { label: '30D Implied Vol', value: '22.5%', good: true },
                { label: 'Options Volume', value: '845K', good: true },
                { label: 'Open Interest', value: '4.2M', good: true },
                { label: 'Max Pain', value: '$175.00', good: true },
                { label: 'Unusual Activity', value: '3 alerts', good: false },
              ]
            },
            {
              id: 'institutional',
              title: 'Institutional Activity',
              items: [
                { label: 'Inst. Ownership', value: '61.2%', good: true },
                { label: 'Total Institutions', value: '5,421', good: true },
                { label: 'Inst. Shares', value: '9.59B', good: true },
                { label: 'Q4 Change', value: '+125M', good: true },
                { label: 'Insider Ownership', value: '0.08%', good: false },
                { label: 'Short Interest', value: '125.5M', good: true },
                { label: 'Days to Cover', value: '0.98', good: true },
                { label: 'Short Float %', value: '0.8%', good: true },
              ]
            },
            {
              id: 'risk-metrics',
              title: 'Risk Metrics',
              items: [
                { label: 'Beta (5Y)', value: '1.28', good: false },
                { label: 'Alpha', value: '2.45', good: true },
                { label: 'Sharpe Ratio', value: '1.85', good: true },
                { label: 'Sortino Ratio', value: '2.42', good: true },
                { label: 'Treynor Ratio', value: '14.2', good: true },
                { label: 'Max Drawdown', value: '-12.5%', good: false },
                { label: 'Value at Risk', value: '-3.2%', good: true },
                { label: 'Correlation SPY', value: '0.72', good: true },
              ]
            },
            {
              id: 'sector-comp',
              title: 'Sector Comparison',
              items: [
                { label: 'vs Sector Avg P/E', value: '+5.2%', good: true },
                { label: 'vs Sector Growth', value: '+2.1%', good: true },
                { label: 'Sector Rank', value: '#1 of 45', good: true },
                { label: 'Industry Rank', value: '#1 of 12', good: true },
                { label: 'Market Share', value: '28.5%', good: true },
                { label: 'Peer Avg P/E', value: '32.1', good: true },
                { label: 'Peer Avg Margin', value: '22.8%', good: true },
                { label: 'Relative Strength', value: '72.4', good: true },
              ]
            },
            {
              id: 'social-sentiment',
              title: 'Social Sentiment',
              items: [
                { label: 'Twitter Score', value: '72/100', good: true },
                { label: 'Reddit Mentions', value: '2,450', good: true },
                { label: 'WallStreetBets', value: 'Mixed', good: true },
                { label: 'News Sentiment', value: '68/100', good: true },
                { label: 'Analyst Sentiment', value: 'Bullish', good: true },
                { label: 'Social Volume', value: '+45%', good: true },
                { label: 'Influencer Opinions', value: '8 Buy', good: true },
                { label: 'Google Trends', value: '85/100', good: true },
              ]
            },
            {
              id: 'supply-chain',
              title: 'Supply Chain',
              items: [
                { label: 'Major Suppliers', value: '12 key', good: true },
                { label: 'Supplier Concentration', value: 'Low', good: true },
                { label: 'Geographic Mfg', value: 'China 85%', good: false },
                { label: 'Lead Time Risk', value: 'Medium', good: false },
                { label: 'Customer Concentration', value: 'Moderate', good: true },
                { label: 'Top Customer', value: '15.2%', good: true },
                { label: 'Diversification', value: 'Good', good: true },
                { label: 'Supply Chain Score', value: 'B+', good: true },
              ]
            },
            {
              id: 'events',
              title: 'Event Calendar',
              items: [
                { label: 'Next Earnings', value: 'May 1, 2024', good: true },
                { label: 'Earnings Conf', value: 'TBD', good: false },
                { label: 'Dividend Ex-Date', value: 'May 10, 2024', good: true },
                { label: 'Shareholder Mtg', value: 'May 15, 2024', good: true },
                { label: 'Product Launch', value: 'Sep 2024', good: true },
                { label: 'Conference', value: 'Mar 15, 2024', good: true },
                { label: 'Analyst Day', value: 'TBD', good: false },
                { label: 'SEC 10-K Deadline', value: 'Dec 31, 2024', good: true },
              ]
            },
            {
              id: 'macro',
              title: 'Macro Sensitivity',
              items: [
                { label: 'Interest Rate Sens', value: '-0.15', good: true },
                { label: 'USD Sensitivity', value: '-0.25', good: true },
                { label: 'Oil Sensitivity', value: '+0.05', good: true },
                { label: 'China Exposure', value: '18.5%', good: true },
                { label: 'Europe Exposure', value: '24.2%', good: true },
                { label: 'Inflation Impact', value: 'Moderate', good: true },
                { label: 'Recession Beta', value: '1.05', good: false },
                { label: 'Economic Moat', value: 'Wide', good: true },
              ]
            },
            {
              id: 'esg-detail',
              title: 'ESG & Impact',
              items: [
                { label: 'ESG Score', value: '72/100', good: true },
                { label: 'Carbon Footprint', value: '12.5M tons', good: false },
                { label: 'Renewable Energy', value: '65%', good: true },
                { label: 'Water Usage', value: '2.1B gal', good: true },
                { label: 'Diversity Score', value: '78/100', good: true },
                { label: 'Board Independence', value: '92%', good: true },
                { label: 'Executive Pay', value: 'Ratio 245:1', good: false },
                { label: 'Political Donations', value: '$2.4M', good: true },
              ]
            },
            {
              id: 'products',
              title: 'Product Details',
              items: [
                { label: 'iPhone Revenue', value: '52.3%', good: true },
                { label: 'Services Revenue', value: '22.1%', good: true },
                { label: 'Mac Revenue', value: '8.4%', good: true },
                { label: 'iPad Revenue', value: '6.2%', good: true },
                { label: 'Wearables Revenue', value: '5.1%', good: true },
                { label: 'R&D Spend', value: '$30.2B', good: true },
                { label: 'Patents', value: '24,500', good: true },
                { label: 'Brand Value', value: '$483B', good: true },
              ]
            },
            {
              id: 'valuation-advanced',
              title: 'Advanced Valuation',
              items: [
                { label: 'DCF Value', value: '$195.40', good: true },
                { label: 'NAV (Net Assets)', value: '$48.20', good: true },
                { label: 'Liquidation Value', value: '$42.50', good: true },
                { label: 'Replacement Cost', value: '$155.80', good: true },
                { label: 'Tangible Book', value: '$3.96', good: true },
                { label: 'Graham Number', value: '$142.30', good: true },
                { label: 'EPV (Earnings Power)', value: '$168.50', good: true },
                { label: 'Peter Lynch Value', value: '$188.75', good: true },
              ]
            },
            {
              id: 'forecast',
              title: 'Forecasts & Projections',
              items: [
                { label: 'Next Year EPS', value: '$6.85', good: true },
                { label: 'Next Year Revenue', value: '$405.2B', good: true },
                { label: '5Y Revenue CAGR', value: '7.2%', good: true },
                { label: '5Y EPS CAGR', value: '9.8%', good: true },
                { label: 'Long-term Growth', value: '11.5%', good: true },
                { label: 'Analyst Price Target', value: '$210.00', good: true },
                { label: 'Upside Potential', value: '+17.5%', good: true },
                { label: 'Confidence Level', value: 'High', good: true },
              ]
            },
            {
              id: 'profitability',
              title: 'Profitability Metrics',
              items: [
                { label: 'Gross Margin', value: '45.2%', good: true },
                { label: 'Operating Margin', value: '30.5%', good: true },
                { label: 'Net Margin', value: '25.3%', good: true },
                { label: 'FCF Margin', value: '26.0%', good: true },
              ]
            },
            {
              id: 'analyst-detail',
              title: 'Analyst Breakdown',
              items: [
                { label: 'Strong Buy', value: '18 analysts', good: true },
                { label: 'Buy', value: '12 analysts', good: true },
                { label: 'Hold', value: '7 analysts', good: false },
                { label: 'Sell', value: '1 analyst', good: false },
                { label: 'Mean Rating', value: '1.52', good: true },
                { label: 'Median Target', value: '$210.00', good: true },
                { label: 'High Target', value: '$250.00', good: true },
                { label: 'Low Target', value: '$175.00', good: false },
              ]
            },
            {
              id: 'dividend-detail',
              title: 'Dividend Analysis',
              items: [
                { label: 'Dividend Yield', value: '0.52%', good: false },
                { label: 'Annual Dividend', value: '$0.96', good: true },
                { label: 'Payout Ratio', value: '15.2%', good: true },
                { label: 'Dividend Growth', value: '+5.2%', good: true },
                { label: '5Y Dividend CAGR', value: '8.5%', good: true },
                { label: 'Years of Growth', value: '12', good: true },
                { label: 'Yield vs Sector', value: '-0.8%', good: false },
                { label: 'Yield vs S&P 500', value: '-1.2%', good: false },
              ]
            },
            {
              id: 'patterns',
              title: 'Chart Patterns',
              items: [
                { label: 'Current Pattern', value: 'Ascending Triangle', good: true },
                { label: 'Trend', value: 'Uptrend', good: true },
                { label: 'Support Level', value: '$175.00', good: true },
                { label: 'Resistance Level', value: '$182.50', good: true },
                { label: '52W Position', value: 'Top 15%', good: true },
                { label: 'Pattern Strength', value: 'Strong', good: true },
                { label: 'Breakout Target', value: '$188.00', good: true },
                { label: 'Stop Loss Level', value: '$172.00', good: true },
              ]
            },
            {
              id: 'volatility',
              title: 'Volatility Metrics',
              items: [
                { label: 'Historical Vol (30D)', value: '22.5%', good: true },
                { label: 'Implied Vol (30D)', value: '24.2%', good: false },
                { label: 'IV Rank', value: '22.5%', good: true },
                { label: 'IV Percentile', value: '45.2%', good: true },
                { label: 'Volatility Index', value: '18.5', good: true },
                { label: 'Beta (1Y)', value: '1.28', good: false },
                { label: 'Correlation VIX', value: '0.45', good: true },
                { label: 'Realized Vol', value: '21.8%', good: true },
              ]
            },
            {
              id: 'momentum',
              title: 'Momentum Indicators',
              items: [
                { label: 'RSI (14)', value: '58.4', good: true },
                { label: 'MFI (14)', value: '72.1', good: false },
                { label: 'ROC (125)', value: '+2.5%', good: true },
                { label: 'Williams %R', value: '-45.2', good: true },
                { label: 'CCI (20)', value: '85.2', good: true },
                { label: 'Stochastic %K', value: '68.5', good: true },
                { label: 'MACD Signal', value: 'Bullish', good: true },
                { label: 'Trend Strength', value: 'Strong', good: true },
              ]
            },
            {
              id: 'ownership-detail',
              title: 'Ownership Structure',
              items: [
                { label: 'Vanguard Group', value: '8.12%', good: true },
                { label: 'BlackRock', value: '4.56%', good: true },
                { label: 'State Street', value: '3.89%', good: true },
                { label: 'Berkshire Hathaway', value: '5.92%', good: true },
                { label: 'Insiders', value: '0.08%', good: false },
                { label: 'Retail', value: '38.72%', good: true },
                { label: 'Total Holders', value: '5,421', good: true },
                { label: 'Held by Insiders', value: 'No', good: false },
              ]
            },
            {
              id: 'insider-trading',
              title: 'Insider Activity',
              items: [
                { label: 'Insider Ownership', value: '0.08%', good: false },
                { label: 'Insider Trades (3M)', value: '12', good: true },
                { label: 'Buy Orders', value: '8', good: true },
                { label: 'Sell Orders', value: '4', good: true },
                { label: 'Net Activity', value: '+125K shares', good: true },
                { label: 'CEO Buys (1Y)', value: '3', good: true },
                { label: 'CFO Buys (1Y)', value: '2', good: true },
                { label: 'Insider Sentiment', value: 'Bullish', good: true },
              ]
            },
            {
              id: 'short-interest',
              title: 'Short Interest Data',
              items: [
                { label: 'Short Interest', value: '125.5M shares', good: true },
                { label: 'Short Float %', value: '0.8%', good: true },
                { label: 'Days to Cover', value: '0.98', good: true },
                { label: 'Short Change (1M)', value: '-2.1%', good: true },
                { label: 'Cost to Borrow', value: '0.15%', good: false },
                { label: 'Utilization', value: 'Low', good: true },
                { label: 'Short Squeeze Risk', value: 'Low', good: true },
                { label: 'Avg Daily Vol', value: '52.3M', good: true },
              ]
            },
            {
              id: 'peer-analysis',
              title: 'Peer Comparison',
              items: [
                { label: 'vs MSFT', value: '+12.5%', good: true },
                { label: 'vs GOOGL', value: '+18.2%', good: true },
                { label: 'vs META', value: '+22.5%', good: true },
                { label: 'vs AMZN', value: '+8.5%', good: true },
                { label: 'vs TSLA', value: '+35.2%', good: true },
                { label: 'vs NVDA', value: '+5.8%', good: true },
                { label: 'Sector Average', value: '+7.8%', good: true },
                { label: 'S&P 500', value: '+2.5%', good: true },
              ]
            },
            {
              id: 'financial-ratios',
              title: 'Financial Health',
              items: [
                { label: 'Current Ratio', value: '0.98', good: false },
                { label: 'Quick Ratio', value: '0.85', good: false },
                { label: 'Debt/Equity', value: '1.87', good: false },
                { label: 'Interest Coverage', value: '29.5', good: true },
                { label: 'Cash Ratio', value: '0.22', good: false },
                { label: 'Debt/EBITDA', value: '1.85', good: true },
                { label: 'Net Debt/EBITDA', value: '1.42', good: true },
                { label: 'Interest Burden', value: '4.2%', good: true },
              ]
            },
            {
              id: 'cash-flow-detail',
              title: 'Cash Flow Analysis',
              items: [
                { label: 'Operating CF', value: '$110.5B', good: true },
                { label: 'CapEx', value: '-$10.9B', good: false },
                { label: 'Free Cash Flow', value: '$99.6B', good: true },
                { label: 'FCF Margin', value: '26.0%', good: true },
                { label: 'FCF Conversion', value: '102.7%', good: true },
                { label: 'CapEx/Sales', value: '2.8%', good: true },
                { label: 'Dividend Payout', value: '15.2%', good: true },
                { label: 'Buyback Yield', value: '3.2%', good: true },
              ]
            },
            {
              id: 'growth-detail',
              title: 'Growth Analysis',
              items: [
                { label: 'Revenue Growth (YoY)', value: '-2.8%', good: false },
                { label: 'EPS Growth (YoY)', value: '-10.5%', good: false },
                { label: 'Operating Income Growth', value: '-8.2%', good: false },
                { label: '3Y Revenue CAGR', value: '7.2%', good: true },
                { label: '3Y EPS CAGR', value: '9.8%', good: true },
                { label: '3Y FCF CAGR', value: '11.2%', good: true },
                { label: '5Y Revenue CAGR', value: '5.8%', good: true },
                { label: '5Y EPS CAGR', value: '8.5%', good: true },
              ]
            },
            {
              id: 'efficiency',
              title: 'Efficiency Metrics',
              items: [
                { label: 'Asset Turnover', value: '1.08', good: true },
                { label: 'Inventory Turnover', value: '38.5', good: true },
                { label: 'Receivables Turnover', value: '14.2', good: true },
                { label: 'Days Sales Outstanding', value: '25.7', good: true },
              ]
            },
            {
              id: 'liquidity',
              title: 'Liquidity & Solvency',
              items: [
                { label: 'Current Ratio', value: '0.98', good: false },
                { label: 'Quick Ratio', value: '0.85', good: false },
                { label: 'Debt/Equity', value: '1.87', good: false },
                { label: 'Interest Coverage', value: '29.5', good: true },
              ]
            },
            {
              id: 'growth',
              title: 'Growth Metrics',
              items: [
                { label: 'Revenue Growth (YoY)', value: '-2.8%', good: false },
                { label: 'EPS Growth (YoY)', value: '-10.5%', good: false },
                { label: '3Y Revenue CAGR', value: '7.2%', good: true },
                { label: '3Y EPS CAGR', value: '9.8%', good: true },
              ]
            },
            {
              id: 'cashflow',
              title: 'Cash Flow Analysis',
              items: [
                { label: 'Operating Cash Flow', value: '$110.5B', good: true },
                { label: 'CapEx', value: '-$10.9B', good: false },
                { label: 'Free Cash Flow', value: '$99.6B', good: true },
                { label: 'FCF Conversion', value: '102.7%', good: true },
              ]
            },
            {
              id: 'per-share',
              title: 'Per Share Data',
              items: [
                { label: 'Book Value', value: '$3.96', good: true },
                { label: 'Tangible Book', value: '$0.42', good: true },
                { label: 'Working Capital', value: '$25.8B', good: true },
                { label: 'Cash Per Share', value: '$4.82', good: true },
              ]
            },
            {
              id: 'options',
              title: 'Options Activity',
              items: [
                { label: 'Put/Call Ratio', value: '0.65', good: true },
                { label: 'Implied Volatility', value: '22.5%', good: false },
                { label: '30D Avg Volume', value: '845K', good: true },
                { label: 'Open Interest', value: '4.2M', good: true },
              ]
            },
            {
              id: 'analyst',
              title: 'Analyst Forecasts',
              items: [
                { label: 'Next Year EPS Est', value: '$6.85', good: true },
                { label: 'Next Year Revenue Est', value: '$405.2B', good: true },
                { label: 'Long-Term Growth Est', value: '11.5%', good: true },
                { label: 'Number of Analysts', value: '38', good: true },
              ]
            },
            {
              id: 'esg',
              title: 'ESG Metrics',
              items: [
                { label: 'ESG Score', value: '72/100', good: true },
                { label: 'Environmental', value: '68/100', good: true },
                { label: 'Social', value: '75/100', good: true },
                { label: 'Governance', value: '78/100', good: true },
              ]
            },
            {
              id: 'products',
              title: 'Product/Service Breakdown',
              items: [
                { label: 'iPhone Revenue', value: '52.3%', good: true },
                { label: 'Services Revenue', value: '22.1%', good: true },
                { label: 'Mac Revenue', value: '8.4%', good: true },
                { label: 'iPad Revenue', value: '6.2%', good: true },
              ]
            },
            {
              id: 'geographic',
              title: 'Geographic Revenue Mix',
              items: [
                { label: 'Americas', value: '42.5%', good: true },
                { label: 'Europe', value: '24.8%', good: true },
                { label: 'Greater China', value: '18.9%', good: true },
                { label: 'Japan', value: '6.8%', good: true },
              ]
            },
            {
              id: 'geographic-detail',
              title: 'Geographic Revenue',
              items: [
                { label: 'Americas', value: '42.5%', good: true },
                { label: 'Europe', value: '24.8%', good: true },
                { label: 'Greater China', value: '18.9%', good: true },
                { label: 'Japan', value: '6.8%', good: true },
                { label: 'Rest of Asia', value: '5.2%', good: true },
                { label: 'Emerging Markets', value: '1.8%', good: true },
                { label: 'Diversification', value: 'Good', good: true },
                { label: 'Exposure Risk', value: 'Moderate', good: true },
              ]
            },
            {
              id: 'analyst-detail',
              title: 'Analyst Recommendations',
              items: [
                { label: 'Strong Buy', value: '18', good: true },
                { label: 'Buy', value: '12', good: true },
                { label: 'Hold', value: '7', good: false },
                { label: 'Sell', value: '1', good: false },
                { label: 'Mean Price Target', value: '$210.00', good: true },
                { label: 'Median Target', value: '$210.00', good: true },
                { label: 'High Target', value: '$250.00', good: true },
                { label: 'Low Target', value: '$175.00', good: false },
              ]
            },
            {
              id: 'recommendations',
              title: 'Analyst Recommendations',
              items: [
                { label: 'Strong Buy', value: '18', good: true },
                { label: 'Buy', value: '12', good: true },
                { label: 'Hold', value: '7', good: false },
                { label: 'Sell', value: '1', good: false },
              ]
            },
          ].map((section) => (
            <CollapsibleSection key={section.id} section={section} />
          ))}
        </CardContent>
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
        <TabsList className="grid w-full grid-cols-12">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="stats">Stats</TabsTrigger>
          <TabsTrigger value="fundamentals">Fundamentals</TabsTrigger>
          <TabsTrigger value="technicals">Technicals</TabsTrigger>
          <TabsTrigger value="financials">Financials</TabsTrigger>
          <TabsTrigger value="valuation">Valuation</TabsTrigger>
          <TabsTrigger value="ownership">Ownership</TabsTrigger>
          <TabsTrigger value="earnings">Earnings</TabsTrigger>
          <TabsTrigger value="news">News</TabsTrigger>
          <TabsTrigger value="filings">Filings</TabsTrigger>
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

        {/* Key Statistics Tab */}
        <TabsContent value="stats" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Key Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Valuation Metrics */}
              <div>
                <h4 className="text-sm font-semibold mb-3 text-muted-foreground">Valuation</h4>
                <div className="grid grid-cols-4 md:grid-cols-8 lg:grid-cols-12 gap-3">
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Market Cap</p>
                    <p className="text-sm font-bold">${(assetData.marketCap / 1000000000000).toFixed(2)}T</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Enterprise Value</p>
                    <p className="text-sm font-semibold">${(assetData.marketCap * 1.05 / 1000000000000).toFixed(2)}T</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">P/E Ratio</p>
                    <p className="text-sm font-bold">{assetData.peRatio?.toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Forward P/E</p>
                    <p className="text-sm font-semibold">{(assetData.peRatio! * 0.9).toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">PEG Ratio</p>
                    <p className="text-sm font-bold">2.45</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">P/S Ratio</p>
                    <p className="text-sm font-semibold">7.32</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">P/B Ratio</p>
                    <p className="text-sm font-bold">{assetData.pbRatio?.toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">EV/Revenue</p>
                    <p className="text-sm font-semibold">7.68</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">EV/EBITDA</p>
                    <p className="text-sm font-bold">22.45</p>
                  </div>
                </div>
              </div>

              {/* Trading Metrics */}
              <div>
                <h4 className="text-sm font-semibold mb-3 text-muted-foreground">Trading Information</h4>
                <div className="grid grid-cols-4 md:grid-cols-8 lg:grid-cols-12 gap-3">
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">52W High</p>
                    <p className="text-sm font-bold text-green-600">${assetData.week52High?.toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">52W Low</p>
                    <p className="text-sm font-bold text-red-600">${assetData.week52Low?.toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">50D Avg</p>
                    <p className="text-sm font-semibold">$178.45</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">200D Avg</p>
                    <p className="text-sm font-bold">$175.32</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Volume</p>
                    <p className="text-sm font-semibold">{(assetData.volume / 1000000).toFixed(1)}M</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Avg Volume</p>
                    <p className="text-sm font-bold">{(assetData.avgVolume / 1000000).toFixed(1)}M</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Shares Outstanding</p>
                    <p className="text-sm font-semibold">15.67B</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Float</p>
                    <p className="text-sm font-bold">15.55B</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Holdings %</p>
                    <p className="text-sm font-semibold">61.2%</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Short Float</p>
                    <p className="text-sm font-bold">0.8%</p>
                  </div>
                </div>
              </div>

              {/* Dividends */}
              <div>
                <h4 className="text-sm font-semibold mb-3 text-muted-foreground">Dividend Information</h4>
                <div className="grid grid-cols-4 md:grid-cols-8 lg:grid-cols-12 gap-3">
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Dividend Yield</p>
                    <p className="text-sm font-bold">{assetData.dividend?.yield.toFixed(2)}%</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Annual Dividend</p>
                    <p className="text-sm font-semibold">${assetData.dividend?.amount?.toFixed(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Payout Ratio</p>
                    <p className="text-sm font-bold">15.2%</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Dividend Frequency</p>
                    <p className="text-sm font-semibold">{assetData.dividend?.frequency}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Last Ex-Div</p>
                    <p className="text-sm font-bold">{new Date(assetData.dividend?.lastExDate || '').toLocaleDateString()}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Pay Date</p>
                    <p className="text-sm font-semibold">Feb 15, 2024</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Valuation Tab */}
        <TabsContent value="valuation" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Valuation Metrics</CardTitle>
              <CardDescription>Comprehensive valuation analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Price Multiples */}
                <div>
                  <h4 className="text-sm font-semibold mb-3">Price Multiples</h4>
                  <div className="grid grid-cols-4 gap-3">
                    <div className="border rounded-lg p-3">
                      <p className="text-[10px] text-muted-foreground uppercase">P/E</p>
                      <p className="text-lg font-bold">{assetData.peRatio?.toFixed(2)}</p>
                      <p className="text-xs text-muted-foreground">Industry: 28.1</p>
                    </div>
                    <div className="border rounded-lg p-3">
                      <p className="text-[10px] text-muted-foreground uppercase">P/B</p>
                      <p className="text-lg font-bold">{assetData.pbRatio?.toFixed(2)}</p>
                      <p className="text-xs text-muted-foreground">Industry: 12.5</p>
                    </div>
                    <div className="border rounded-lg p-3">
                      <p className="text-[10px] text-muted-foreground uppercase">P/S</p>
                      <p className="text-lg font-bold">7.32</p>
                      <p className="text-xs text-muted-foreground">Industry: 6.8</p>
                    </div>
                    <div className="border rounded-lg p-3">
                      <p className="text-[10px] text-muted-foreground uppercase">EV/EBITDA</p>
                      <p className="text-lg font-bold">22.45</p>
                      <p className="text-xs text-muted-foreground">Industry: 18.2</p>
                    </div>
                  </div>
                </div>

                {/* Intrinsic Value */}
                <div>
                  <h4 className="text-sm font-semibold mb-3">Intrinsic Value Estimates</h4>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="border rounded-lg p-3">
                      <p className="text-[10px] text-muted-foreground uppercase">DCF Value</p>
                      <p className="text-lg font-bold text-green-600">$195.40</p>
                      <p className="text-xs text-green-600">+9.3% upside</p>
                    </div>
                    <div className="border rounded-lg p-3">
                      <p className="text-[10px] text-muted-foreground uppercase">Graham Number</p>
                      <p className="text-lg font-bold text-blue-600">$142.30</p>
                      <p className="text-xs text-blue-600">Fair value</p>
                    </div>
                    <div className="border rounded-lg p-3">
                      <p className="text-[10px] text-muted-foreground uppercase">Peter Lynch Value</p>
                      <p className="text-lg font-bold text-purple-600">$188.75</p>
                      <p className="text-xs text-purple-600">+5.6% upside</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Ownership Tab */}
        <TabsContent value="ownership" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Ownership Structure</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Major Holders */}
              <div>
                <h4 className="text-sm font-semibold mb-3">Major Shareholders</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center p-2 border rounded">
                    <span className="text-sm font-medium">Vanguard Group Inc</span>
                    <span className="text-sm font-bold">8.12%</span>
                  </div>
                  <div className="flex justify-between items-center p-2 border rounded">
                    <span className="text-sm font-medium">BlackRock Inc</span>
                    <span className="text-sm font-bold">4.56%</span>
                  </div>
                  <div className="flex justify-between items-center p-2 border rounded">
                    <span className="text-sm font-medium">State Street Corp</span>
                    <span className="text-sm font-bold">3.89%</span>
                  </div>
                  <div className="flex justify-between items-center p-2 border rounded">
                    <span className="text-sm font-medium">Berkshire Hathaway</span>
                    <span className="text-sm font-bold">5.92%</span>
                  </div>
                </div>
              </div>

              {/* Ownership Breakdown */}
              <div>
                <h4 className="text-sm font-semibold mb-3">Ownership Breakdown</h4>
                <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Institutions</p>
                    <p className="text-sm font-bold">61.2%</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Insiders</p>
                    <p className="text-sm font-semibold">0.08%</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Retail</p>
                    <p className="text-sm font-bold">38.72%</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Short Interest</p>
                    <p className="text-sm font-semibold">0.8%</p>
                  </div>
                </div>
              </div>

              {/* Insider Trading */}
              <div>
                <h4 className="text-sm font-semibold mb-3">Recent Insider Activity</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center p-2 border rounded bg-green-50">
                    <div>
                      <p className="text-sm font-medium">Buy - Tim Cook</p>
                      <p className="text-xs text-muted-foreground">Jan 15, 2024</p>
                    </div>
                    <span className="text-sm font-bold text-green-600">+50,000 shares</span>
                  </div>
                  <div className="flex justify-between items-center p-2 border rounded bg-red-50">
                    <div>
                      <p className="text-sm font-medium">Sell - Craig Federighi</p>
                      <p className="text-xs text-muted-foreground">Jan 10, 2024</p>
                    </div>
                    <span className="text-sm font-bold text-red-600">-12,500 shares</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Earnings Tab */}
        <TabsContent value="earnings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Earnings & Estimates</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Most Recent Quarter */}
              <div>
                <h4 className="text-sm font-semibold mb-3">Q4 2023 Earnings</h4>
                <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">EPS</p>
                    <p className="text-sm font-bold">$2.18</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Estimate</p>
                    <p className="text-sm font-semibold">$2.10</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Surprise</p>
                    <p className="text-sm font-bold text-green-600">+3.81%</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Revenue</p>
                    <p className="text-sm font-semibold">$119.58B</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Estimate</p>
                    <p className="text-sm font-bold">$117.85B</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase font-medium">Surprise</p>
                    <p className="text-sm font-bold text-green-600">+1.47%</p>
                  </div>
                </div>
              </div>

              {/* Upcoming Earnings */}
              <div>
                <h4 className="text-sm font-semibold mb-3">Earnings Calendar</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="text-sm font-semibold">Q1 2024 Earnings</p>
                      <p className="text-xs text-muted-foreground">Expected: May 2024</p>
                    </div>
                    <Badge variant="outline">Upcoming</Badge>
                  </div>
                </div>
              </div>

              {/* Earnings History */}
              <div>
                <h4 className="text-sm font-semibold mb-3">Earnings History (Last 4 Quarters)</h4>
                <div className="space-y-2">
                  {['Q4 2023', 'Q3 2023', 'Q2 2023', 'Q1 2023'].map((quarter, idx) => (
                    <div key={quarter} className="flex items-center justify-between p-2 border rounded">
                      <span className="text-sm font-medium">{quarter}</span>
                      <span className="text-sm font-semibold text-green-600">Beat</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* SEC Filings Tab */}
        <TabsContent value="filings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">SEC Filings</CardTitle>
              <CardDescription>Recent company filings with the SEC</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {[
                  { type: '10-K', date: '2024-01-25', desc: 'Annual Report' },
                  { type: '10-Q', date: '2024-02-02', desc: 'Quarterly Report' },
                  { type: '8-K', date: '2024-01-18', desc: 'Material Agreement' },
                  { type: 'DEF 14A', date: '2024-01-10', desc: 'Proxy Statement' },
                  { type: '4', date: '2024-01-15', desc: 'Insider Trading' },
                  { type: '8-K', date: '2024-01-08', desc: 'Earnings Release' },
                ].map((filing, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50">
                    <div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{filing.type}</Badge>
                        <span className="text-sm font-medium">{filing.desc}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">{filing.date}</p>
                    </div>
                    <Button variant="ghost" size="sm">View</Button>
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

export default function AssetDetailPage() {
  return (
    <PageErrorBoundary
      onError={(error, errorInfo) => {
        console.error('Asset detail page error:', error, errorInfo)
      }}
    >
      <AssetDetailPageContent />
    </PageErrorBoundary>
  )
}
