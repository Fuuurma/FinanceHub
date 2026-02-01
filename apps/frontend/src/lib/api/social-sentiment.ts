/**
 * Social Sentiment API
 * Social media sentiment from Twitter and Reddit
 */

import { apiClient } from './client'

export interface SocialSentimentData {
  symbol: string
  sentiment_score: number
  sentiment_label: 'bullish' | 'bearish' | 'neutral'
  mention_count: number
  volume_change: number | null
  sources: {
    twitter: {
      score: number
      label: string
      count: number
    }
    reddit: {
      score: number
      label: string
      count: number
    }
  }
  trend: 'improving' | 'worsening' | 'stable'
}

export interface SentimentHistoryPoint {
  timestamp: string
  sentiment_score: number
  mention_count: number
}

export interface SocialFeedItem {
  id: string
  source: 'twitter' | 'reddit'
  author: string
  content: string
  timestamp: string
  sentiment_score: number
  sentiment_label: 'bullish' | 'bearish' | 'neutral'
  url: string
  engagement?: {
    likes?: number
    retweets?: number
    upvotes?: number
    comments?: number
  }
}

export interface TrendingAsset {
  symbol: string
  sentiment_score: number
  sentiment_label: 'bullish' | 'bearish' | 'neutral'
  mention_count: number
  volume_change: number | null
}

export const socialSentimentApi = {
  getSentiment(symbol: string, hours: number = 24): Promise<SocialSentimentData> {
    return apiClient.get(`/sentiment/${symbol}`, {
      params: { hours },
    })
  },

  getSentimentHistory(
    symbol: string,
    period: '24h' | '7d' | '30d' = '7d'
  ): Promise<{ symbol: string; history: SentimentHistoryPoint[] }> {
    return apiClient.get(`/sentiment/${symbol}/history`, {
      params: { period },
    })
  },

  getSocialFeed(
    symbol: string,
    options?: {
      source?: 'all' | 'twitter' | 'reddit'
      limit?: number
    }
  ): Promise<{ symbol: string; feed: SocialFeedItem[] }> {
    return apiClient.get(`/sentiment/${symbol}/feed`, {
      params: { source: 'all', limit: 50, ...options },
    })
  },

  getTrendingAssets(limit: number = 20): Promise<{ trending: TrendingAsset[] }> {
    return apiClient.get('/sentiment/trending', {
      params: { limit },
    })
  },
}
