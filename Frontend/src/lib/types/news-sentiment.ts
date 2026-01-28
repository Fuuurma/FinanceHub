/**
 * News Sentiment Types
 */

export interface NewsArticle {
  id: string
  title: string
  description: string
  source: string
  author: string | null
  published_at: string
  url: string
  image_url: string | null
  symbols: string[]
  sentiment_score: number | null
  sentiment_label: string | null
  relevance_score: number | null
}

export interface SentimentAnalysis {
  symbol: string
  overall_sentiment: string
  sentiment_score: number
  article_count: number
  positive_count: number
  negative_count: number
  neutral_count: number
  average_sentiment_7d: number | null
  articles: NewsArticle[]
  sentiment_trend: {
    [key: string]: number
  } | null
  key_topics: string[]
  analyzed_at: string
}

export interface MarketTrends {
  time_period: string
  hot_topics: Array<{
    topic: string
    sentiment_score: number
    article_count: number
    related_symbols: string[]
  }>
  trending_symbols: Array<{
    symbol: string
    sentiment_score: number
    article_count: number
  }>
  sentiment_distribution: {
    positive: number
    negative: number
    neutral: number
  }
  most_mentioned: Array<{
    symbol: string
    mention_count: number
  }>
  fetched_at: string
}

export interface SentimentHistory {
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

export interface TrendingTopic {
  topic: string
  sentiment_score: number
  article_count: number
  related_symbols: string[]
}
