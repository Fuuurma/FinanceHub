'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { PageHeader } from '@/components/ui/page-header'
import { StatsGrid } from '@/components/ui/stats-grid'
import {
  Building2,
  Coins,
  Currency,
  Package,
  FileText,
  BarChart3,
  PieChart,
  TrendingUp,
  TrendingDown,
  ArrowLeft,
  ExternalLink,
  Info,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface CategoryDetail {
  type: string
  name: string
  description: string
  fullDescription: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  bgLight: string
  borderColor: string
  examples: { symbol: string; name: string }[]
  metrics: {
    label: string
    value: string
  }[]
  features: string[]
}

const CATEGORY_DETAILS: CategoryDetail[] = [
  {
    type: 'stocks',
    name: 'Stocks',
    description: 'Publicly traded company shares',
    fullDescription: 'Stocks represent ownership in companies. When you buy a stock, you become a partial owner of that company and may receive dividends and capital gains.',
    icon: Building2,
    color: 'text-blue-600',
    bgLight: 'bg-blue-50 dark:bg-blue-950',
    borderColor: 'border-blue-200 dark:border-blue-800',
    examples: [
      { symbol: 'AAPL', name: 'Apple Inc.' },
      { symbol: 'MSFT', name: 'Microsoft Corp.' },
      { symbol: 'GOOGL', name: 'Alphabet Inc.' },
      { symbol: 'AMZN', name: 'Amazon.com Inc.' },
      { symbol: 'NVDA', name: 'NVIDIA Corp.' },
    ],
    metrics: [
      { label: 'Total Listed', value: '8,234' },
      { label: 'Market Cap', value: '$47.2T' },
      { label: 'Avg. Volume', value: '4.2B/day' },
      { label: 'Dividend Yield', value: '1.8%' },
    ],
    features: [
      'Ownership in companies',
      'Voting rights (some stocks)',
      'Dividend income',
      'Capital appreciation',
      'Liquid trading',
    ],
  },
  {
    type: 'crypto',
    name: 'Cryptocurrencies',
    description: 'Digital currencies and tokens',
    fullDescription: 'Cryptocurrencies are digital or virtual currencies that use cryptography for security. They operate on decentralized networks based on blockchain technology.',
    icon: Coins,
    color: 'text-orange-600',
    bgLight: 'bg-orange-50 dark:bg-orange-950',
    borderColor: 'border-orange-200 dark:border-orange-800',
    examples: [
      { symbol: 'BTC', name: 'Bitcoin' },
      { symbol: 'ETH', name: 'Ethereum' },
      { symbol: 'SOL', name: 'Solana' },
      { symbol: 'XRP', name: 'Ripple' },
      { symbol: 'ADA', name: 'Cardano' },
    ],
    metrics: [
      { label: 'Total Coins', value: '2,847' },
      { label: 'Market Cap', value: '$1.8T' },
      { label: '24h Volume', value: '$52.4B' },
      { label: 'Top Exchange', value: 'Binance' },
    ],
    features: [
      'Decentralized finance',
      'Blockchain technology',
      '24/7 trading',
      'Smart contracts (some)',
      'DeFi integration',
    ],
  },
  {
    type: 'forex',
    name: 'Forex',
    description: 'Foreign exchange currency pairs',
    fullDescription: 'The foreign exchange market (Forex or FX) is the largest financial market in the world, with a daily trading volume exceeding $6 trillion.',
    icon: Currency,
    color: 'text-green-600',
    bgLight: 'bg-green-50 dark:bg-green-950',
    borderColor: 'border-green-200 dark:border-green-800',
    examples: [
      { symbol: 'EUR/USD', name: 'Euro/US Dollar' },
      { symbol: 'GBP/USD', name: 'British Pound/USD' },
      { symbol: 'USD/JPY', name: 'US Dollar/Japanese Yen' },
      { symbol: 'USD/CHF', name: 'US Dollar/Swiss Franc' },
      { symbol: 'AUD/USD', name: 'Australian Dollar/USD' },
    ],
    metrics: [
      { label: 'Pairs', value: '175+' },
      { label: 'Daily Volume', value: '$6.6T' },
      { label: 'Trading Hours', value: '24/5' },
      { label: 'Margin Available', value: 'Up to 1:500' },
    ],
    features: [
      'Highest liquidity',
      '24/5 trading',
      'Leverage options',
      'Low spreads (major pairs)',
      'Global market access',
    ],
  },
  {
    type: 'commodity',
    name: 'Commodities',
    description: 'Physical goods and resources',
    fullDescription: 'Commodities are raw materials or primary agricultural products that can be bought, sold, or traded. They include energy, metals, and agricultural products.',
    icon: Package,
    color: 'text-yellow-600',
    bgLight: 'bg-yellow-50 dark:bg-yellow-950',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
    examples: [
      { symbol: 'GC', name: 'Gold' },
      { symbol: 'SI', name: 'Silver' },
      { symbol: 'CL', name: 'Crude Oil' },
      { symbol: 'NG', name: 'Natural Gas' },
      { symbol: 'HG', name: 'Copper' },
    ],
    metrics: [
      { label: 'Commodities', value: '52+' },
      { label: 'Energy Market', value: '$3.1T' },
      { label: 'Metals Market', value: '$280B' },
      { label: 'Agricultural', value: '$100B' },
    ],
    features: [
      'Inflation hedge',
      'Portfolio diversification',
      'Physical delivery option',
      'Commodity ETFs',
      'Futures contracts',
    ],
  },
  {
    type: 'bonds',
    name: 'Bonds',
    description: 'Fixed income securities',
    fullDescription: 'Bonds are fixed-income instruments that represent a loan made by an investor to a borrower (typically corporate or governmental).',
    icon: FileText,
    color: 'text-purple-600',
    bgLight: 'bg-purple-50 dark:bg-purple-950',
    borderColor: 'border-purple-200 dark:border-purple-800',
    examples: [
      { symbol: 'US10Y', name: 'US 10-Year Treasury' },
      { symbol: 'US30Y', name: 'US 30-Year Treasury' },
      { symbol: 'CORP', name: 'Corporate Bonds' },
      { symbol: 'MUNI', name: 'Municipal Bonds' },
      { symbol: 'TIPS', name: 'Inflation-Protected' },
    ],
    metrics: [
      { label: 'Bond Types', value: '1,234+' },
      { label: 'Treasury Market', value: '$26T' },
      { label: 'Corporate Bonds', value: '$9T' },
      { label: 'Avg. Yield', value: '4.2%' },
    ],
    features: [
      'Fixed income stream',
      'Lower risk (gov bonds)',
      'Predictable returns',
      'Tax advantages (muni)',
      'Capital preservation',
    ],
  },
  {
    type: 'etf',
    name: 'ETFs',
    description: 'Exchange traded funds',
    fullDescription: 'ETFs are investment funds that trade on stock exchanges, much like stocks. They hold assets like stocks, commodities, or bonds.',
    icon: BarChart3,
    color: 'text-pink-600',
    bgLight: 'bg-pink-50 dark:bg-pink-950',
    borderColor: 'border-pink-200 dark:border-pink-800',
    examples: [
      { symbol: 'SPY', name: 'SPDR S&P 500 ETF' },
      { symbol: 'QQQ', name: 'Invesco QQQ' },
      { symbol: 'VTI', name: 'Vanguard Total Stock' },
      { symbol: 'IWM', name: 'iShares Russell 2000' },
      { symbol: 'VEA', name: 'Vanguard Developed Mkts' },
    ],
    metrics: [
      { label: 'Total ETFs', value: '2,891' },
      { label: 'AUM', value: '$10.1T' },
      { label: 'Avg. Expense', value: '0.18%' },
      { label: 'Trading Volume', value: '$142B/day' },
    ],
    features: [
      'Instant diversification',
      'Low expense ratios',
      'Tax efficient',
      'Flexible trading',
      'Transparent holdings',
    ],
  },
  {
    type: 'index',
    name: 'Indices',
    description: 'Market index tracking',
    fullDescription: 'Indices are statistical measures of the changes in a portfolio of stocks representing a portion of the overall market.',
    icon: PieChart,
    color: 'text-cyan-600',
    bgLight: 'bg-cyan-50 dark:bg-cyan-950',
    borderColor: 'border-cyan-200 dark:border-cyan-800',
    examples: [
      { symbol: 'SPX', name: 'S&P 500' },
      { symbol: 'NDX', name: 'NASDAQ 100' },
      { symbol: 'DJI', name: 'Dow Jones Industrial' },
      { symbol: 'RUT', name: 'Russell 2000' },
      { symbol: 'VIX', name: 'Volatility Index' },
    ],
    metrics: [
      { label: 'Major Indices', value: '156' },
      { label: 'S&P 500 Cap', value: '$45T' },
      { label: 'NASDAQ 100 Cap', value: '$21T' },
      { label: 'Tracking Funds', value: '$4.8T' },
    ],
    features: [
      'Market benchmarks',
      'Performance tracking',
      'Index funds',
      'Index futures',
      'Options available',
    ],
  },
]

export default function AssetsCategoriesPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<CategoryDetail | null>(null)

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 600)
    return () => clearTimeout(timer)
  }, [])

  const stats = [
    { title: 'Total Categories', value: '7', description: 'asset types' },
    { title: 'Total Assets', value: '15,589', change: 2.3, changeLabel: 'this month' },
    { title: 'Market Coverage', value: '99.8%', description: 'global markets' },
    { title: 'Data Providers', value: '10+', description: 'real-time feeds' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push('/assets')}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Asset Categories</h1>
          <p className="text-muted-foreground">
            Explore all available asset types and their characteristics
          </p>
        </div>
      </div>

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

      {loading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6, 7].map((i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {CATEGORY_DETAILS.map((category) => (
            <Card
              key={category.type}
              className={cn(
                'cursor-pointer transition-all duration-200 hover:shadow-lg hover:-translate-y-1',
                selectedCategory === category && 'ring-2 ring-primary',
                category.borderColor
              )}
              onClick={() => setSelectedCategory(
                selectedCategory?.type === category.type ? null : category
              )}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className={cn('p-3 rounded-xl', category.bgLight)}>
                    <category.icon className={cn('h-6 w-6', category.color)} />
                  </div>
                  <Badge variant="outline">{category.name}</Badge>
                </div>
                <CardTitle className="mt-4">{category.name}</CardTitle>
                <CardDescription>{category.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    {category.examples.slice(0, 3).map((ex) => (
                      <Badge key={ex.symbol} variant="secondary" className="text-xs">
                        {ex.symbol}
                      </Badge>
                    ))}
                    {category.examples.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{category.examples.length - 3} more
                      </Badge>
                    )}
                  </div>

                  {selectedCategory?.type === category.type && (
                    <div className="pt-4 border-t animate-in slide-in-from-top-2">
                      <p className="text-sm text-muted-foreground mb-4">
                        {category.fullDescription}
                      </p>

                      <div className="grid grid-cols-2 gap-2 mb-4">
                        {category.metrics.map((metric) => (
                          <div key={metric.label} className="bg-muted/50 p-2 rounded">
                            <div className="text-xs text-muted-foreground">{metric.label}</div>
                            <div className="font-semibold">{metric.value}</div>
                          </div>
                        ))}
                      </div>

                      <div className="space-y-2">
                        <div className="text-sm font-medium">Key Features</div>
                        <div className="flex flex-wrap gap-1">
                          {category.features.map((feature) => (
                            <Badge key={feature} variant="outline" className="text-xs">
                              {feature}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <Button
                        className="w-full mt-4"
                        onClick={(e) => {
                          e.stopPropagation()
                          router.push(`/assets/${category.type}`)
                        }}
                      >
                        Browse {category.name}
                        <ExternalLink className="ml-2 h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card className="bg-muted/50">
        <CardContent className="py-6">
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-lg bg-primary/10">
              <Info className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold">Understanding Asset Classes</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Each asset class has different risk-return characteristics. Diversifying across
                multiple asset classes can help reduce portfolio volatility. Click on any category
                above to learn more about its features, examples, and how it can fit into your
                investment strategy.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
