'use client'

import { useState, useMemo } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Star,
  StarHalf,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  PieChart,
  Activity,
  ExternalLink,
  RefreshCw,
  Download,
  Filter,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import type {
  AnalystRating,
  RatingConsensus,
  RatingTrend,
  RatingDetails,
  CryptoRating,
  EtfRating,
  BondRating,
  AssetType,
  RatingSummary,
} from '@/lib/types/ratings'
import { cn } from '@/lib/utils'

const ASSET_TYPE_LABELS: Record<AssetType, string> = {
  stock: 'Stocks',
  crypto: 'Cryptocurrency',
  etf: 'ETFs',
  index: 'Indices',
  bond: 'Bonds',
  commodity: 'Commodities',
  forex: 'Forex',
  mutual_fund: 'Mutual Funds',
}

const RATING_SOURCES = [
  { id: 'all', name: 'All Sources' },
  { id: 'bloomberg', name: 'Bloomberg' },
  { id: 'reuters', name: 'Reuters' },
  { id: 'morningstar', name: 'Morningstar' },
  { id: 'zacks', name: 'Zacks' },
  { id: 'tipRanks', name: 'TipRanks' },
  { id: 'coinmarketcap', name: 'CoinMarketCap' },
  { id: 'coingecko', name: 'CoinGecko' },
  { id: 'etfdb', name: 'ETF Database' },
]

const PERIOD_OPTIONS = [
  { value: '1w', label: '1 Week' },
  { value: '1m', label: '1 Month' },
  { value: '3m', label: '3 Months' },
  { value: '6m', label: '6 Months' },
  { value: '1y', label: '1 Year' },
]

interface AnalystRatingsProps {
  symbol?: string
  assetType?: AssetType
  className?: string
}

const getRecommendationColor = (rec: string) => {
  const colors: Record<string, string> = {
    strong_buy: 'bg-green-600 text-white',
    buy: 'bg-green-500 text-white',
    hold: 'bg-yellow-500 text-white',
    sell: 'bg-red-500 text-white',
    strong_sell: 'bg-red-600 text-white',
    neutral: 'bg-gray-500 text-white',
  }
  return colors[rec] || 'bg-gray-500 text-white'
}

const getRecommendationLabel = (rec: string) => {
  const labels: Record<string, string> = {
    strong_buy: 'Strong Buy',
    buy: 'Buy',
    hold: 'Hold',
    sell: 'Sell',
    strong_sell: 'Strong Sell',
    neutral: 'Neutral',
  }
  return labels[rec] || rec
}

const formatRatingValue = (value: number | string, scale: string) => {
  if (typeof value === 'string') return value
  if (scale === '1-5') return value.toFixed(1)
  if (scale === '1-10') return value.toFixed(1)
  if (scale === 'percent') return `${value.toFixed(0)}%`
  return value.toFixed(2)
}

const RatingCardSkeleton = () => (
  <Card>
    <CardHeader className="pb-2">
      <Skeleton className="h-6 w-32" />
    </CardHeader>
    <CardContent>
      <div className="space-y-4">
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    </CardContent>
  </Card>
)

function ConsensusGauge({ consensus }: { consensus: RatingConsensus }) {
  const total = consensus.rating_count
  if (total === 0) return null

  const buyPercent = ((consensus.rating_distribution.strong_buy + consensus.rating_distribution.buy) / total * 100).toFixed(0)
  const holdPercent = (consensus.rating_distribution.hold / total * 100).toFixed(0)
  const sellPercent = ((consensus.rating_distribution.sell + consensus.rating_distribution.strong_sell) / total * 100).toFixed(0)

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Consensus Rating</CardTitle>
        <CardDescription>Based on {total} analyst ratings</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-center">
            <div className={cn(
              'text-4xl font-bold px-6 py-3 rounded-lg',
              getRecommendationColor(consensus.consensus_recommendation)
            )}>
              {getRecommendationLabel(consensus.consensus_recommendation)}
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex h-4 rounded-full overflow-hidden">
              <div
                className="bg-green-500 transition-all"
                style={{ width: `${buyPercent}%` }}
              />
              <div
                className="bg-yellow-500 transition-all"
                style={{ width: `${holdPercent}%` }}
              />
              <div
                className="bg-red-500 transition-all"
                style={{ width: `${sellPercent}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Buy: {buyPercent}%</span>
              <span>Hold: {holdPercent}%</span>
              <span>Sell: {sellPercent}%</span>
            </div>
          </div>

          {consensus.average_target_price && (
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="p-2 bg-muted/50 rounded">
                <div className="text-xs text-muted-foreground">Avg Target</div>
                <div className="font-semibold">${consensus.average_target_price.toFixed(2)}</div>
              </div>
              <div className="p-2 bg-muted/50 rounded">
                <div className="text-xs text-muted-foreground">High</div>
                <div className="font-semibold text-green-600">${consensus.target_price_high?.toFixed(2) || '-'}</div>
              </div>
              <div className="p-2 bg-muted/50 rounded">
                <div className="text-xs text-muted-foreground">Low</div>
                <div className="font-semibold text-red-600">${consensus.target_price_low?.toFixed(2) || '-'}</div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function RatingDistributionChart({ distribution }: { distribution: RatingConsensus['rating_distribution'] }) {
  const total = distribution.strong_buy + distribution.buy + distribution.hold + distribution.sell + distribution.strong_sell
  if (total === 0) return null

  const maxCount = Math.max(...Object.values(distribution))
  const barHeight = (count: number) => Math.max(8, (count / maxCount) * 100)

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Rating Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-end justify-center gap-1 h-32">
          <TooltipProvider>
            <div className="flex flex-col items-center">
              <Tooltip>
                <TooltipTrigger asChild>
                  <div
                    className="w-8 bg-red-600 rounded-t transition-all cursor-pointer hover:opacity-80"
                    style={{ height: `${barHeight(distribution.strong_sell)}px` }}
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Strong Sell: {distribution.strong_sell}</p>
                </TooltipContent>
              </Tooltip>
              <span className="text-xs mt-1">SS</span>
            </div>

            <div className="flex flex-col items-center">
              <Tooltip>
                <TooltipTrigger asChild>
                  <div
                    className="w-8 bg-red-400 rounded-t transition-all cursor-pointer hover:opacity-80"
                    style={{ height: `${barHeight(distribution.sell)}px` }}
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Sell: {distribution.sell}</p>
                </TooltipContent>
              </Tooltip>
              <span className="text-xs mt-1">S</span>
            </div>

            <div className="flex flex-col items-center">
              <Tooltip>
                <TooltipTrigger asChild>
                  <div
                    className="w-8 bg-yellow-500 rounded-t transition-all cursor-pointer hover:opacity-80"
                    style={{ height: `${barHeight(distribution.hold)}px` }}
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Hold: {distribution.hold}</p>
                </TooltipContent>
              </Tooltip>
              <span className="text-xs mt-1">H</span>
            </div>

            <div className="flex flex-col items-center">
              <Tooltip>
                <TooltipTrigger asChild>
                  <div
                    className="w-8 bg-green-400 rounded-t transition-all cursor-pointer hover:opacity-80"
                    style={{ height: `${barHeight(distribution.buy)}px` }}
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Buy: {distribution.buy}</p>
                </TooltipContent>
              </Tooltip>
              <span className="text-xs mt-1">B</span>
            </div>

            <div className="flex flex-col items-center">
              <Tooltip>
                <TooltipTrigger asChild>
                  <div
                    className="w-8 bg-green-600 rounded-t transition-all cursor-pointer hover:opacity-80"
                    style={{ height: `${barHeight(distribution.strong_buy)}px` }}
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Strong Buy: {distribution.strong_buy}</p>
                </TooltipContent>
              </Tooltip>
              <span className="text-xs mt-1">SB</span>
            </div>
          </TooltipProvider>
        </div>
      </CardContent>
    </Card>
  )
}

function RatingTrends({ trends }: { trends: RatingTrend[] }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Rating Trends</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {trends.map((trend) => (
            <div key={trend.period} className="flex items-center justify-between p-2 bg-muted/50 rounded">
              <div className="flex items-center gap-2">
                <Badge variant="outline">{trend.period.toUpperCase()}</Badge>
                <span className="text-sm text-muted-foreground">
                  {getRecommendationLabel(trend.previous_consensus)} →
                </span>
                <Badge className={getRecommendationColor(trend.current_consensus)}>
                  {getRecommendationLabel(trend.current_consensus)}
                </Badge>
              </div>
              <div className="flex items-center gap-1">
                {trend.trend_direction === 'up' && (
                  <ArrowUpRight className="w-4 h-4 text-green-600" />
                )}
                {trend.trend_direction === 'down' && (
                  <ArrowDownRight className="w-4 h-4 text-red-600" />
                )}
                {trend.trend_direction === 'stable' && (
                  <Minus className="w-4 h-4 text-gray-400" />
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function AnalystRatingTable({ ratings }: { ratings: AnalystRating[] }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Analyst Ratings</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-auto max-h-96">
          <table className="w-full">
            <thead className="sticky top-0 bg-background">
              <tr className="border-b">
                <th className="text-left p-2 text-sm font-medium">Source</th>
                <th className="text-left p-2 text-sm font-medium">Rating</th>
                <th className="text-right p-2 text-sm font-medium">Target</th>
                <th className="text-left p-2 text-sm font-medium">Published</th>
              </tr>
            </thead>
            <tbody>
              {ratings.map((rating) => (
                <tr key={rating.id} className="border-b hover:bg-muted/50">
                  <td className="p-2">
                    <div className="font-medium">{rating.rating_source}</div>
                    {rating.analyst_name && (
                      <div className="text-xs text-muted-foreground">{rating.analyst_name}</div>
                    )}
                  </td>
                  <td className="p-2">
                    <Badge className={getRecommendationColor(rating.recommendation)}>
                      {getRecommendationLabel(rating.recommendation)}
                    </Badge>
                    <div className="text-xs text-muted-foreground mt-1">
                      {formatRatingValue(rating.rating_value, rating.rating_scale)} / {rating.rating_scale}
                    </div>
                  </td>
                  <td className="p-2 text-right">
                    {rating.target_price && (
                      <div>${rating.target_price.toFixed(2)}</div>
                    )}
                    {rating.target_price_high && rating.target_price_low && (
                      <div className="text-xs text-muted-foreground">
                        ${rating.target_price_low.toFixed(2)} - ${rating.target_price_high.toFixed(2)}
                      </div>
                    )}
                  </td>
                  <td className="p-2 text-sm text-muted-foreground">
                    {new Date(rating.published_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}

function CryptoRatingsView({ crypto }: { crypto: CryptoRating }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">Trust Score</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-green-600">{crypto.trust_score}/10</div>
          <div className="flex items-center gap-1 mt-1">
            {crypto.trust_score_direction === 'up' && <TrendingUp className="w-4 h-4 text-green-600" />}
            {crypto.trust_score_direction === 'down' && <TrendingDown className="w-4 h-4 text-red-600" />}
            <span className="text-xs text-muted-foreground">{crypto.trust_score_direction}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">Developer</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{crypto.developer_score}/10</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">Community</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{crypto.community_score}/10</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">Liquidity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{crypto.liquidity_score}/10</div>
        </CardContent>
      </Card>
    </div>
  )
}

function EtfRatingsView({ etf }: { etf: EtfRating }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg text-white">
        <div>
          <div className="text-3xl font-bold">{etf.overall_rating}/5</div>
          <div className="text-sm opacity-90">Overall ETF Rating</div>
        </div>
        <div className="text-4xl">★</div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {[
          { label: 'Risk', value: etf.risk_rating, max: 5 },
          { label: 'Return', value: etf.return_rating, max: 5 },
          { label: 'Expense', value: etf.expense_rating, max: 5 },
          { label: 'Liquidity', value: etf.liquidity_rating, max: 5 },
          { label: 'Diversification', value: etf.diversification_rating, max: 5 },
        ].map((item) => (
          <Card key={item.label}>
            <CardContent className="pt-4">
              <div className="text-sm text-muted-foreground">{item.label}</div>
              <div className="flex items-center gap-2 mt-1">
                <div className="text-xl font-bold">{item.value}/{item.max}</div>
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500"
                    style={{ width: `${(item.value / item.max) * 100}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="flex justify-between p-2 bg-muted/50 rounded">
          <span className="text-muted-foreground">Sharpe Ratio</span>
          <span className="font-medium">{etf.sharpe_ratio.toFixed(2)}</span>
        </div>
        <div className="flex justify-between p-2 bg-muted/50 rounded">
          <span className="text-muted-foreground">Expense Ratio</span>
          <span className="font-medium">{etf.expense_ratio.toFixed(3)}%</span>
        </div>
        <div className="flex justify-between p-2 bg-muted/50 rounded">
          <span className="text-muted-foreground">AUM</span>
          <span className="font-medium">${(etf.aum / 1e9).toFixed(2)}B</span>
        </div>
      </div>
    </div>
  )
}

function BondRatingsView({ bond }: { bond: BondRating }) {
  const rating = bond.composite_rating

  const getRatingGrade = (r: string) => {
    if (r.startsWith('AAA') || r === 'Aaa') return { grade: 'A', color: 'text-green-600', bg: 'bg-green-100' }
    if (r.startsWith('AA') || r === 'Aa') return { grade: 'A', color: 'text-green-500', bg: 'bg-green-50' }
    if (r.startsWith('A')) return { grade: 'B', color: 'text-blue-600', bg: 'bg-blue-100' }
    if (r.startsWith('BBB') || r === 'Baa') return { grade: 'B', color: 'text-blue-500', bg: 'bg-blue-50' }
    if (r.startsWith('BB') || r === 'Ba') return { grade: 'C', color: 'text-yellow-600', bg: 'bg-yellow-100' }
    if (r.startsWith('B')) return { grade: 'C', color: 'text-yellow-500', bg: 'bg-yellow-50' }
    if (r.startsWith('CCC') || r === 'Caa') return { grade: 'D', color: 'text-orange-600', bg: 'bg-orange-100' }
    return { grade: 'D', color: 'text-red-600', bg: 'bg-red-100' }
  }

  const grade = getRatingGrade(rating)

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-6">
        <div className={cn('text-6xl font-bold px-4 py-2 rounded-lg', grade.color, grade.bg)}>
          {grade.grade}
        </div>
        <div>
          <div className="text-2xl font-bold">{rating}</div>
          <div className="text-muted-foreground">Composite Credit Rating</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {bond.moody_rating && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">Moody's</CardTitle>
            </CardHeader>
            <CardContent className="text-xl font-bold">{bond.moody_rating}</CardContent>
          </Card>
        )}
        {bond.sp_rating && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">S&P</CardTitle>
            </CardHeader>
            <CardContent className="text-xl font-bold">{bond.sp_rating}</CardContent>
          </Card>
        )}
        {bond.fitch_rating && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">Fitch</CardTitle>
            </CardHeader>
            <CardContent className="text-xl font-bold">{bond.fitch_rating}</CardContent>
          </Card>
        )}
      </div>

      <div className="flex items-center gap-2">
        <span className="text-muted-foreground">Outlook:</span>
        <Badge
          className={cn(
            bond.outlook === 'positive' && 'bg-green-100 text-green-700',
            bond.outlook === 'negative' && 'bg-red-100 text-red-700',
            bond.outlook === 'stable' && 'bg-gray-100 text-gray-700'
          )}
        >
          {bond.outlook}
        </Badge>
      </div>
    </div>
  )
}

export function AnalystRatings({ symbol, assetType = 'stock', className }: AnalystRatingsProps) {
  const params = useParams()
  const currentSymbol = symbol || (params.symbol as string) || 'AAPL'

  const [loading, setLoading] = useState(false)
  const [selectedSource, setSelectedSource] = useState('all')
  const [selectedPeriod, setSelectedPeriod] = useState('3m')

  const [summary, setSummary] = useState<RatingSummary | null>(null)

  useState(() => {
    const fetchRatings = async () => {
      setLoading(true)
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        const mockSummary: RatingSummary = {
          symbol: currentSymbol,
          asset_type: assetType,
          consensus: {
            symbol: currentSymbol,
            asset_type: assetType,
            rating_count: 24,
            average_rating: 4.2,
            min_rating: 2.1,
            max_rating: 5.0,
            median_rating: 4.3,
            rating_distribution: {
              strong_buy: 8,
              buy: 10,
              hold: 4,
              sell: 1,
              strong_sell: 1,
            },
            average_target_price: 185.50,
            target_price_high: 220.00,
            target_price_low: 150.00,
            upside_potential: 15.2,
            consensus_recommendation: 'buy',
            last_updated: new Date().toISOString(),
          },
          ratings: [
            {
              id: '1',
              symbol: currentSymbol,
              asset_type: assetType,
              rating_source: 'Goldman Sachs',
              rating_value: 4.8,
              rating_scale: '1-5',
              target_price: 195.00,
              recommendation: 'strong_buy',
              confidence_score: 92,
              analyst_name: 'John Smith',
              published_at: '2026-01-25',
              last_updated: new Date().toISOString(),
            },
            {
              id: '2',
              symbol: currentSymbol,
              asset_type: assetType,
              rating_source: 'Morgan Stanley',
              rating_value: 4.5,
              rating_scale: '1-5',
              target_price: 190.00,
              recommendation: 'buy',
              confidence_score: 88,
              analyst_name: 'Jane Doe',
              published_at: '2026-01-22',
              last_updated: new Date().toISOString(),
            },
            {
              id: '3',
              symbol: currentSymbol,
              asset_type: assetType,
              rating_source: 'JP Morgan',
              rating_value: 4.2,
              rating_scale: '1-5',
              target_price: 180.00,
              recommendation: 'buy',
              confidence_score: 85,
              published_at: '2026-01-20',
              last_updated: new Date().toISOString(),
            },
          ],
          trends: [
            { symbol: currentSymbol, period: '1m', previous_consensus: 'hold', current_consensus: 'buy', trend_direction: 'up', rating_change_count: 5, average_rating_change: 0.3 },
            { symbol: currentSymbol, period: '3m', previous_consensus: 'hold', current_consensus: 'buy', trend_direction: 'up', rating_change_count: 12, average_rating_change: 0.5 },
            { symbol: currentSymbol, period: '6m', previous_consensus: 'buy', current_consensus: 'buy', trend_direction: 'stable', rating_change_count: 18, average_rating_change: 0.1 },
          ],
          last_updated: new Date().toISOString(),
        }
        setSummary(mockSummary)
      } catch (error) {
        console.error('Failed to fetch ratings:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchRatings()
  }, [currentSymbol, assetType])

  const filteredRatings = useMemo(() => {
    if (!summary) return []
    if (selectedSource === 'all') return summary.ratings
    return summary.ratings.filter(r => r.rating_source.toLowerCase() === selectedSource.toLowerCase())
  }, [summary, selectedSource])

  if (loading) {
    return (
      <div className={cn('grid gap-4', className)}>
        <RatingCardSkeleton />
        <RatingCardSkeleton />
      </div>
    )
  }

  if (!summary) {
    return (
      <Card className={className}>
        <CardContent className="py-8 text-center text-muted-foreground">
          No rating data available for {currentSymbol}
        </CardContent>
      </Card>
    )
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          <h2 className="text-xl font-semibold">Analyst Ratings</h2>
          <Badge variant="outline">{ASSET_TYPE_LABELS[assetType]}</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Select value={selectedSource} onValueChange={setSelectedSource}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {RATING_SOURCES.map(source => (
                <SelectItem key={source.id} value={source.id}>{source.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <ConsensusGauge consensus={summary.consensus} />
        <RatingDistributionChart distribution={summary.consensus.rating_distribution} />
        <RatingTrends trends={summary.trends} />
      </div>

      <AnalystRatingTable ratings={filteredRatings} />
    </div>
  )
}

export default AnalystRatings
