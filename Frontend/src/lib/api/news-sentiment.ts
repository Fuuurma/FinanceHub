/**
 * News Sentiment API
 * All news sentiment-related API calls
 */

import { apiClient } from './client'
import type { SentimentAnalysis, MarketTrends } from '../types'

export const newsSentimentApi = {
  /**
   * Get sentiment analysis for a specific symbol
   */
  getSentiment: (
    symbol: string,
    params?: {
      days?: number
      min_relevance?: number
    }
  ) => Promise<SentimentAnalysis> =>
    apiClient.get(`/news/sentiment/${symbol}`, {
      params: { days: 7, min_relevance: 0.5, ...params },
    }),

  /**
   * Get market-wide sentiment trends
   */
  getMarketTrends: (params?: {
    days?: number
    min_mentions?: number
  }) => Promise<MarketTrends> =>
    apiClient.get('/news/trends', {
      params: { days: 7, min_mentions: 5, ...params },
    }),

  /**
   * Get sentiment for multiple symbols
   */
  getBatchSentiment: (
    symbols: string[],
    params?: {
      days?: number
      min_relevance?: number
    }
  ) => Promise<Record<string, SentimentAnalysis>> =>
    apiClient.post('/news/sentiment/batch', { symbols, params }),

  /**
   * Get trending topics in the news
   */
  getTrendingTopics: (limit: number = 10) => Promise<
    Array<{
      topic: string
      sentiment_score: number
      article_count: number
      related_symbols: string[]
    }>
  > =>
    apiClient.get('/news/topics/trending', { params: { limit } }),

  /**
   * Get news for a symbol with sentiment
   */
  getNewsWithSentiment: (
    symbol: string,
    params?: {
      days?: number
      limit?: number
      min_relevance?: number
      sentiment_filter?: 'positive' | 'negative' | 'neutral'
    }
  ) => Promise<{
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
  }> =>
    apiClient.get(`/news/symbol/${symbol}`, {
      params: { days: 7, limit: 20, ...params },
    }),

  /**
   * Get sentiment history for a symbol
   */
  getSentimentHistory: (
    symbol: string,
    params?: {
      days?: number
      interval?: 'hourly' | 'daily'
    }
  ) => Promise<{
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
  }> =>
    apiClient.get(`/news/sentiment/${symbol}/history`, {
      params: { days: 30, interval: 'daily', ...params },
    }),
}
