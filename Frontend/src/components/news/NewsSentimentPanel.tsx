'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { TrendingUp, TrendingDown, Minus, Zap, Globe, BarChart2 } from 'lucide-react'
import type { SentimentAnalysis, MarketTrends } from '@/lib/types/news-sentiment'
import { cn } from '@/lib/utils'

interface NewsSentimentPanelProps {
  sentiment?: SentimentAnalysis
  trends?: MarketTrends
  className?: string
}

function SentimentGauge({ label, value, status, color }: {
  label: string
  value: number
  status: string
  color: string
}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[10px] font-black uppercase">
        <span>{label}</span>
        <span className={cn(color)}>{status}</span>
      </div>
      <div className="h-4 w-full border-2 border-foreground bg-background p-[2px]">
        <div
          className={cn('h-full transition-all', color)}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  )
}

export function NewsSentimentPanel({ sentiment, trends, className }: NewsSentimentPanelProps) {
  const mockSentiment: SentimentAnalysis = {
    symbol: 'SPY',
    overall_sentiment: 'BULLISH',
    sentiment_score: 0.72,
    article_count: 156,
    positive_count: 98,
    negative_count: 32,
    neutral_count: 26,
    average_sentiment_7d: 0.65,
    articles: [],
    sentiment_trend: {
      '1d': 0.72,
      '3d': 0.68,
      '7d': 0.65,
      '14d': 0.58,
      '30d': 0.52,
    },
    key_topics: ['AI', 'Earnings', 'Fed Policy', 'Tech', 'Inflation'],
    analyzed_at: new Date().toISOString(),
  }

  const mockTrends: MarketTrends = {
    time_period: '24h',
    hot_topics: [
      { topic: 'AI ARMS RACE', sentiment_score: 0.85, article_count: 45, related_symbols: ['NVDA', 'MSFT', 'GOOGL'] },
      { topic: 'FED RATE CUTS', sentiment_score: 0.45, article_count: 38, related_symbols: ['SPY', 'QQQ'] },
      { topic: 'BITCOIN ETF', sentiment_score: 0.62, article_count: 32, related_symbols: ['BTC', 'COIN'] },
      { topic: 'EARNINGS SEASON', sentiment_score: 0.58, article_count: 28, related_symbols: ['AAPL', 'AMZN'] },
      { topic: 'GEOPOLITICAL', sentiment_score: -0.32, article_count: 22, related_symbols: ['USO', 'TLT'] },
    ],
    trending_symbols: [
      { symbol: 'NVDA', sentiment_score: 0.88, article_count: 52 },
      { symbol: 'TSLA', sentiment_score: 0.45, article_count: 41 },
      { symbol: 'AAPL', sentiment_score: 0.62, article_count: 38 },
      { symbol: 'AMD', sentiment_score: 0.75, article_count: 29 },
      { symbol: 'META', sentiment_score: 0.55, article_count: 24 },
    ],
    sentiment_distribution: {
      positive: 58,
      negative: 22,
      neutral: 20,
    },
    most_mentioned: [
      { symbol: 'NVDA', mention_count: 234 },
      { symbol: 'AAPL', mention_count: 189 },
      { symbol: 'TSLA', mention_count: 156 },
      { symbol: 'MSFT', mention_count: 142 },
      { symbol: 'GOOGL', mention_count: 128 },
    ],
    fetched_at: new Date().toISOString(),
  }

  const data = sentiment || mockSentiment
  const marketTrends = trends || mockTrends

  const getSentimentColor = (score: number) => {
    if (score >= 0.6) return 'text-green-600 bg-green-100'
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-100'
    if (score >= 0.2) return 'text-orange-600 bg-orange-100'
    return 'text-red-600 bg-red-100'
  }

  const getSentimentIcon = (score: number) => {
    if (score >= 0.4) return TrendingUp
    if (score >= 0) return Minus
    return TrendingDown
  }

  return (
    <div className={cn('space-y-4', className)}>
      <Card className="border-2 border-foreground">
        <CardHeader className="py-3 border-b-2 border-foreground bg-muted/30">
          <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Market Sentiment
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <SentimentGauge
              label="MARKET_MOOD"
              value={72}
              status="GREED"
              color="bg-green-500"
            />
            <SentimentGauge
              label="MACRO_STRESS"
              value={34}
              status="MODERATE"
              color="bg-orange-500"
            />
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div className="text-center p-2 border border-foreground/20">
              <p className="text-lg font-black text-green-600">+{marketTrends.sentiment_distribution.positive}%</p>
              <p className="text-[10px] font-bold uppercase text-muted-foreground">Positive</p>
            </div>
            <div className="text-center p-2 border border-foreground/20">
              <p className="text-lg font-black text-gray-600">{marketTrends.sentiment_distribution.neutral}%</p>
              <p className="text-[10px] font-bold uppercase text-muted-foreground">Neutral</p>
            </div>
            <div className="text-center p-2 border border-foreground/20">
              <p className="text-lg font-black text-red-600">-{marketTrends.sentiment_distribution.negative}%</p>
              <p className="text-[10px] font-bold uppercase text-muted-foreground">Negative</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-2 border-foreground">
        <CardHeader className="py-3 border-b-2 border-foreground bg-muted/30">
          <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
            <BarChart2 className="h-4 w-4" />
            Trending Symbols
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          <div className="space-y-2">
            {marketTrends.trending_symbols.map((item, idx) => {
              const Icon = getSentimentIcon(item.sentiment_score)
              return (
                <div key={item.symbol} className="flex items-center justify-between p-2 border border-foreground/10">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black w-4">{idx + 1}</span>
                    <Badge variant="outline" className="font-bold">${item.symbol}</Badge>
                    <Icon className={cn('h-4 w-4', item.sentiment_score >= 0.4 ? 'text-green-600' : 'text-red-600')} />
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold">{item.article_count} articles</span>
                    <Progress value={(item.article_count / 60) * 100} className="h-1 w-16 mt-1" />
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      <Card className="border-2 border-foreground">
        <CardHeader className="py-3 border-b-2 border-foreground bg-muted/30">
          <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
            <Globe className="h-4 w-4" />
            Hot Topics
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-2">
            {marketTrends.hot_topics.map((topic) => (
              <div
                key={topic.topic}
                className="group cursor-pointer border-2 border-foreground px-3 py-2 bg-background hover:bg-muted transition-colors"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs font-black uppercase">{topic.topic}</span>
                  <Badge
                    className={cn(
                      'text-[10px] font-bold',
                      topic.sentiment_score >= 0.4 ? 'bg-green-100 text-green-700' :
                      topic.sentiment_score >= 0 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    )}
                  >
                    {topic.sentiment_score >= 0 ? '+' : ''}{topic.sentiment_score.toFixed(2)}
                  </Badge>
                </div>
                <div className="flex gap-1 mt-1">
                  {topic.related_symbols.slice(0, 3).map((symbol) => (
                    <span key={symbol} className="text-[10px] font-mono text-muted-foreground">
                      ${symbol}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="border-2 border-foreground bg-primary/5">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 text-xs font-black uppercase mb-2">
            <Zap className="h-4 w-4 text-primary" />
            AI Summary
          </div>
          <p className="text-xs font-mono leading-relaxed opacity-80">
            Market sentiment remains bullish driven by strong AI sector momentum and positive earnings reports.
            Monitor NVDA closely for volatility around the upcoming chip announcement. Fed policy uncertainty
            remains a key driver for the near term.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default NewsSentimentPanel
