/**
 * Enhanced News with Sentiment Analysis Component
 * Displays news items with visual sentiment indicators and trends
 */

'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ExternalLink } from 'lucide-react'

interface NewsItem {
  id: string
  title: string
  source: string
  publishedAt: string
  sentiment: 'positive' | 'negative' | 'neutral'
  sentimentScore?: number
  url: string
}

interface NewsWithSentimentProps {
  news: NewsItem[]
  title?: string
  maxItems?: number
}

export function NewsWithSentiment({ news, title = "Latest News", maxItems = 10 }: NewsWithSentimentProps) {
  if (!news || news.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground">No news available</p>
        </CardContent>
      </Card>
    )
  }

  const displayNews = maxItems ? news.slice(0, maxItems) : news

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-500'
      case 'negative':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getSentimentBg = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-500/10 border-green-500/20'
      case 'negative':
        return 'bg-red-500/10 border-red-500/20'
      default:
        return 'bg-gray-500/10 border-gray-500/20'
    }
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return '📈'
      case 'negative':
        return '📉'
      default:
        return '📊'
    }
  }

  // Calculate overall sentiment
  const positiveCount = news.filter(n => n.sentiment === 'positive').length
  const negativeCount = news.filter(n => n.sentiment === 'negative').length
  const neutralCount = news.filter(n => n.sentiment === 'neutral').length
  const total = news.length

  const overallSentiment = positiveCount > negativeCount ? 'positive' : 
                          negativeCount > positiveCount ? 'negative' : 'neutral'
  const sentimentPercent = Math.round((Math.max(positiveCount, negativeCount) / total) * 100)

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>{title}</CardTitle>
            <CardDescription>
              Recent news and sentiment analysis • {news.length} articles
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Overall:</span>
            <Badge variant="outline" className={`${getSentimentBg(overallSentiment)}`}>
              {getSentimentIcon(overallSentiment)} {overallSentiment} ({sentimentPercent}%)
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Sentiment Summary */}
        <div className="flex gap-2 mb-4">
          <div className="flex-1 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Positive</span>
              <span className="text-lg font-bold text-green-600">{positiveCount}</span>
            </div>
            <div className="w-full bg-green-500/20 rounded-full h-1.5 mt-2">
              <div className="bg-green-500 h-full rounded-full" style={{ width: `${(positiveCount / total) * 100}%` }}></div>
            </div>
          </div>
          <div className="flex-1 p-3 bg-gray-500/10 border border-gray-500/20 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Neutral</span>
              <span className="text-lg font-bold text-gray-600">{neutralCount}</span>
            </div>
            <div className="w-full bg-gray-500/20 rounded-full h-1.5 mt-2">
              <div className="bg-gray-500 h-full rounded-full" style={{ width: `${(neutralCount / total) * 100}%` }}></div>
            </div>
          </div>
          <div className="flex-1 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Negative</span>
              <span className="text-lg font-bold text-red-600">{negativeCount}</span>
            </div>
            <div className="w-full bg-red-500/20 rounded-full h-1.5 mt-2">
              <div className="bg-red-500 h-full rounded-full" style={{ width: `${(negativeCount / total) * 100}%` }}></div>
            </div>
          </div>
        </div>

        {/* News List */}
        <div className="space-y-3">
          {displayNews.map((article, index) => (
            <a
              key={article.id}
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className={`block p-4 rounded-lg border-2 transition-all hover:shadow-md ${getSentimentBg(article.sentiment)}`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 space-y-2">
                  <div className="flex items-start gap-2">
                    <span className="text-lg">{getSentimentIcon(article.sentiment)}</span>
                    <h4 className="font-semibold leading-tight">{article.title}</h4>
                  </div>
                  
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <Badge variant="outline" className="text-xs">
                      {article.source}
                    </Badge>
                    <span>•</span>
                    <span>{new Date(article.publishedAt).toLocaleDateString()}</span>
                    <span>•</span>
                    <span>{new Date(article.publishedAt).toLocaleTimeString()}</span>
                  </div>

                  {article.sentimentScore !== undefined && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">Sentiment Score:</span>
                      <div className="flex-1 max-w-[100px] bg-muted rounded-full h-2">
                        <div
                          className={`h-full rounded-full ${getSentimentColor(article.sentiment)}`}
                          style={{ width: `${Math.abs(article.sentimentScore) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-xs font-medium">{(article.sentimentScore * 100).toFixed(0)}%</span>
                    </div>
                  )}
                </div>

                <ExternalLink className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-1" />
              </div>
            </a>
          ))}
        </div>

        {news.length > maxItems && (
          <div className="mt-4 text-center">
            <Button variant="outline" size="sm">
              View All {news.length} Articles
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
