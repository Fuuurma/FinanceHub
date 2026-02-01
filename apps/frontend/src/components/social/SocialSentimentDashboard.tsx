'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { SentimentGauge, SentimentGaugeSkeleton } from './SentimentGauge'
import { SocialFeed } from './SocialFeed'
import { TrendingAssets } from './TrendingAssets'
import { SentimentHistoryChart } from './SentimentHistoryChart'
import { socialSentimentApi, type SocialSentimentData, type TrendingAsset, type SocialFeedItem, type SentimentHistoryPoint } from '@/lib/api/social-sentiment'
import {
  Search, TrendingUp, RefreshCw, Zap, Twitter, MessageCircle,
  ArrowUpRight, ArrowDownRight
} from 'lucide-react'

interface SocialSentimentDashboardProps {
  className?: string
}

export function SocialSentimentDashboard({ className }: SocialSentimentDashboardProps) {
  const [symbol, setSymbol] = React.useState('')
  const [searchSymbol, setSearchSymbol] = React.useState('')
  const [sentiment, setSentiment] = React.useState<SocialSentimentData | null>(null)
  const [history, setHistory] = React.useState<SentimentHistoryPoint[]>([])
  const [feed, setFeed] = React.useState<SocialFeedItem[]>([])
  const [trending, setTrending] = React.useState<TrendingAsset[]>([])
  const [isLoading, setIsLoading] = React.useState(false)
  const [historyPeriod, setHistoryPeriod] = React.useState('7d')
  const [error, setError] = React.useState<string | null>(null)

  const fetchSentiment = React.useCallback(async (sym: string) => {
    if (!sym.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const [sentimentData, historyData, feedData, trendingData] = await Promise.all([
        socialSentimentApi.getSentiment(sym),
        socialSentimentApi.getSentimentHistory(sym, historyPeriod as any),
        socialSentimentApi.getSocialFeed(sym),
        socialSentimentApi.getTrendingAssets(10),
      ])

      setSentiment(sentimentData)
      setHistory(historyData.history)
      setFeed(feedData.feed)
      setTrending(trendingData.trending)
      setSearchSymbol(sym)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sentiment data')
    } finally {
      setIsLoading(false)
    }
  }, [historyPeriod])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    fetchSentiment(symbol.toUpperCase())
  }

  const handleSelectTrending = (sym: string) => {
    setSymbol(sym)
    fetchSentiment(sym)
  }

  const refreshData = () => {
    if (searchSymbol) {
      fetchSentiment(searchSymbol)
    }
  }

  React.useEffect(() => {
    if (searchSymbol) {
      fetchSentiment(searchSymbol)
    }
  }, [historyPeriod, fetchSentiment])

  return (
    <div className={cn('space-y-6', className)}>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black uppercase tracking-tight flex items-center gap-2">
            <Zap className="h-6 w-6" />
            Social Sentiment
          </h1>
          <p className="text-muted-foreground font-mono text-sm mt-1">
            Real-time social media sentiment from Twitter & Reddit
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="border-2 font-mono text-sm">
            <Twitter className="h-3 w-3 mr-1" />
            Twitter
          </Badge>
          <Badge variant="outline" className="border-2 font-mono text-sm">
            <MessageCircle className="h-3 w-3 mr-1" />
            Reddit
          </Badge>
        </div>
      </div>

      <Card className="rounded-none border-2 border-foreground">
        <CardContent className="p-4">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1">
              <Input
                type="text"
                placeholder="Enter symbol (e.g., AAPL, TSLA, BTC)"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                disabled={isLoading}
                className="uppercase font-mono rounded-none border-2"
              />
            </div>
            <Button
              type="submit"
              disabled={isLoading || !symbol.trim()}
              className="rounded-none border-2 font-black uppercase bg-foreground text-background hover:bg-foreground/90"
            >
              <Search className="h-4 w-4 mr-2" />
              Analyze
            </Button>
          </form>
        </CardContent>
      </Card>

      {error && (
        <div className="border-2 border-red-500 bg-red-50 p-4">
          <p className="font-bold text-red-700 uppercase text-sm">{error}</p>
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-6">
            <SentimentGaugeSkeleton />
            <SentimentGaugeSkeleton />
          </div>
          <div>
            <Skeleton className="h-96 w-full rounded-none border-2 border-foreground" />
          </div>
        </div>
      ) : sentiment ? (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <SentimentGauge
                score={sentiment.sentiment_score}
                label={sentiment.sentiment_label}
                mentionCount={sentiment.mention_count}
                source="aggregated"
              />

              <div className="grid grid-cols-2 gap-4">
                <SentimentGauge
                  score={sentiment.sources.twitter.score}
                  label={sentiment.sources.twitter.label as any}
                  mentionCount={sentiment.sources.twitter.count}
                  source="twitter"
                />
                <SentimentGauge
                  score={sentiment.sources.reddit.score}
                  label={sentiment.sources.reddit.label as any}
                  mentionCount={sentiment.sources.reddit.count}
                  source="reddit"
                />
              </div>

              <Card className="rounded-none border-2 border-foreground">
                <CardHeader className="border-b-2 border-foreground">
                  <CardTitle className="font-black uppercase text-sm flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Trend Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {sentiment.trend === 'improving' && (
                        <ArrowUpRight className="h-5 w-5 text-green-600" />
                      )}
                      {sentiment.trend === 'worsening' && (
                        <ArrowDownRight className="h-5 w-5 text-red-600" />
                      )}
                      {sentiment.trend === 'stable' && (
                        <TrendingUp className="h-5 w-5 text-yellow-600" />
                      )}
                      <span className="font-bold uppercase">
                        {sentiment.trend}
                      </span>
                    </div>
                    <Badge
                      className={cn(
                        'font-mono text-sm',
                        sentiment.volume_change !== null && sentiment.volume_change >= 0
                          ? 'bg-green-100 text-green-800'
                          : sentiment.volume_change !== null
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      )}
                    >
                      {sentiment.volume_change !== null
                        ? `${sentiment.volume_change >= 0 ? '+' : ''}${sentiment.volume_change.toFixed(1)}%`
                        : 'No data'}
                      {' '}vs yesterday
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>

            <SentimentHistoryChart
              symbol={sentiment.symbol}
              data={history}
              isLoading={isLoading}
              period={historyPeriod}
              onPeriodChange={setHistoryPeriod}
              onRefresh={refreshData}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <SocialFeed
                symbol={sentiment.symbol}
                items={feed}
                isLoading={isLoading}
                onRefresh={refreshData}
              />
            </div>
            <div>
              <TrendingAssets
                assets={trending}
                isLoading={isLoading}
                onRefresh={refreshData}
                onSelectAsset={handleSelectTrending}
              />
            </div>
          </div>
        </>
      ) : (
        <Card className="rounded-none border-2 border-foreground">
          <CardContent className="p-12 text-center">
            <Zap className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-black uppercase text-xl mb-2">Ready to Analyze</h3>
            <p className="text-muted-foreground font-mono text-sm max-w-md mx-auto">
              Enter a stock symbol above to see real-time social media sentiment from Twitter and Reddit.
              Track trending assets and see what the community is talking about.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
