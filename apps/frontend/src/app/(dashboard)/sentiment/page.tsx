'use client'

import { useEffect, useState } from 'react'
import { newsSentimentApi } from '@/lib/api/news-sentiment'
import type { SentimentAnalysis, NewsArticle } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Input } from '@/components/ui/input'
import { TrendingUp, TrendingDown, Search, RefreshCw, Filter, Newspaper, Smile, Frown, Meh } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

export default function SentimentPage() {
  const [symbol, setSymbol] = useState('')
  const [days, setDays] = useState(7)
  const [sentiment, setSentiment] = useState<SentimentAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!symbol.trim()) return
    
    setLoading(true)
    setError('')
    
    try {
      const response = await newsSentimentApi.getSentiment(symbol.toUpperCase(), { days })
      setSentiment(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sentiment')
    } finally {
      setLoading(false)
    }
  }

  const getSentimentIcon = (label: string) => {
    const lower = label.toLowerCase()
    if (lower.includes('positive')) return <Smile className="w-5 h-5 text-green-500" />
    if (lower.includes('negative')) return <Frown className="w-5 h-5 text-red-500" />
    return <Meh className="w-5 h-5 text-yellow-500" />
  }

  const getSentimentBadge = (score: number | null) => {
    if (score === null) return <Badge variant="secondary">No Data</Badge>
    if (score > 0.3) return <Badge className="bg-green-100 text-green-800 hover:bg-green-200">Positive</Badge>
    if (score < -0.3) return <Badge className="bg-red-100 text-red-800 hover:bg-red-200">Negative</Badge>
    return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-200">Neutral</Badge>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">News Sentiment</h1>
          <p className="text-muted-foreground">Market sentiment analysis from news</p>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1">
              <Input
                type="text"
                placeholder="Enter symbol (e.g., AAPL, BTC, TSLA)"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                disabled={loading}
                className="uppercase"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                disabled={loading}
                className="border rounded-md px-3 py-2 bg-background"
              >
                <option value={1}>1 Day</option>
                <option value={7}>7 Days</option>
                <option value={14}>14 Days</option>
                <option value={30}>30 Days</option>
              </select>
              <Button type="submit" disabled={loading || !symbol.trim()}>
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4 mr-2" />
                    Analyze
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {error && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
          <p className="font-semibold">Error</p>
          <p>{error}</p>
        </div>
      )}

      {sentiment && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <Newspaper className="w-5 h-5 mr-2" />
                  Sentiment Overview
                </div>
                <div className="flex items-center">
                  {getSentimentBadge(sentiment.sentiment_score)}
                </div>
              </CardTitle>
              <CardDescription>
                {sentiment.symbol} • Last {days} days
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-sm text-muted-foreground">Overall Sentiment</p>
                  <div className="flex items-center justify-center mt-2">
                    {getSentimentIcon(sentiment.overall_sentiment)}
                    <span className={`ml-2 text-lg font-semibold ${
                      sentiment.overall_sentiment === 'positive' ? 'text-green-600' :
                      sentiment.overall_sentiment === 'negative' ? 'text-red-600' :
                      'text-yellow-600'
                    }`}>
                      {sentiment.overall_sentiment}
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Sentiment Score</p>
                  <div className={`text-3xl font-bold ${
                    sentiment.sentiment_score > 0 ? 'text-green-600' :
                    sentiment.sentiment_score < 0 ? 'text-red-600' :
                    'text-yellow-600'
                  }`}>
                    {sentiment.sentiment_score.toFixed(2)}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Article Count</p>
                  <p className="text-3xl font-bold">{sentiment.article_count}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mt-6 text-center">
                <div>
                  <p className="text-sm text-green-600">Positive</p>
                  <p className="text-2xl font-bold">{sentiment.positive_count}</p>
                </div>
                <div>
                  <p className="text-sm text-red-600">Negative</p>
                  <p className="text-2xl font-bold">{sentiment.negative_count}</p>
                </div>
                <div>
                  <p className="text-sm text-yellow-600">Neutral</p>
                  <p className="text-2xl font-bold">{sentiment.neutral_count}</p>
                </div>
              </div>

              {sentiment.key_topics.length > 0 && (
                <div className="mt-6">
                  <p className="text-sm text-muted-foreground mb-2">Key Topics</p>
                  <div className="flex flex-wrap gap-2">
                    {sentiment.key_topics.map((topic) => (
                      <Badge key={topic} variant="outline">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sentiment Trend</CardTitle>
              <CardDescription>7-day sentiment movement</CardDescription>
            </CardHeader>
            <CardContent>
              {sentiment.sentiment_trend ? (
                <div className="space-y-2">
                  {Object.entries(sentiment.sentiment_trend).map(([date, score]) => (
                    <div key={date} className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">{date}</span>
                      <div className="flex items-center">
                        {score >= 0 ? (
                          <TrendingUp className="w-4 h-4 text-green-500" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-red-500" />
                        )}
                        <span className={`ml-2 font-semibold ${score >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {score.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No trend data available</p>
              )}
            </CardContent>
          </Card>

          <Card className="md:col-span-2 lg:col-span-3">
            <CardHeader>
              <CardTitle>Recent News</CardTitle>
              <CardDescription>
                Showing {sentiment.articles.length} relevant articles
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {sentiment.articles.map((article) => (
                  <div
                    key={article.id}
                    className="border rounded-lg p-4 hover:bg-accent/5 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-lg line-clamp-1">{article.title}</h3>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">{article.source}</span>
                        {article.sentiment_label && (
                          <Badge variant="outline" className="text-xs">
                            {article.sentiment_label}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                      {article.description}
                    </p>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{new Date(article.published_at).toLocaleString()}</span>
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        Read more
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
