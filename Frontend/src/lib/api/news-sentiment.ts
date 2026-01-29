/**
 * News Sentiment API
 * All news sentiment-related API calls
 */

import { apiClient } from './client'
import type { SentimentAnalysis, MarketTrends } from '@/lib/types'

interface TrendingTopic {
  topic: string
  sentiment_score: number
  article_count: number
  related_symbols: string[]
}

interface NewsWithSentiment {
  symbol: string
  articles: Array<{
    id: string
    title: string
    description: string
    source: string
    author: string | null
    published_at: string
    url: string
    image_url: string | null
    sentiment_score: number | null
    sentiment_label: string | null
    relevance_score: number | null
  }>
  message: string
}

interface SentimentHistory {
  symbol: string
  history: Array<{
    timestamp: string
    sentiment_score: number
    article_count: number
    positive_count: number
    negative_count: number
    neutral_count: number
  }>
  analyzed_at: string
}

interface GetSentimentParams {
  days?: number
  min_relevance?: number
}

interface GetMarketTrendsParams {
  days?: number
  min_mentions?: number
}

interface GetBatchSentimentParams {
  days?: number
  min_relevance?: number
}

interface GetNewsParams {
  days?: number
  limit?: number
  min_relevance?: number
  sentiment_filter?: 'positive' | 'negative' | 'neutral'
}

interface GetHistoryParams {
  days?: number
  interval?: 'hourly' | 'daily'
}

export const newsSentimentApi = {
  getSentiment(symbol: string, params?: GetSentimentParams): Promise<SentimentAnalysis> {
    return apiClient.get(`/news/sentiment/${symbol}`, {
      params: { days: 7, min_relevance: 0.5, ...params },
    })
  },

  getMarketTrends(params?: GetMarketTrendsParams): Promise<MarketTrends> {
    return apiClient.get('/news/trends', {
      params: { days: 7, min_mentions: 5, ...params },
    })
  },

  getBatchSentiment(symbols: string[], params?: GetBatchSentimentParams): Promise<Record<string, SentimentAnalysis>> {
    return apiClient.post('/news/sentiment/batch', { symbols, params })
  },

  getTrendingTopics(limit: number = 10): Promise<TrendingTopic[]> {
    return apiClient.get('/news/topics/trending', { params: { limit } })
  },

  getNewsWithSentiment(symbol: string, params?: GetNewsParams): Promise<NewsWithSentiment> {
    return apiClient.get(`/news/symbol/${symbol}`, {
      params: { days: 7, limit: 20, ...params },
    })
  },

  getSentimentHistory(symbol: string, params?: GetHistoryParams): Promise<SentimentHistory> {
    return apiClient.get(`/news/sentiment/${symbol}/history`, {
      params: { days: 30, interval: 'daily', ...params },
    })
  },
}
