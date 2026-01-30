export interface MarketOverview {
  indices: Array<{
    symbol: string
    name: string
    price: number
    change: number
    change_percent: number
  }>
  sectors: Array<{
    sector: string
    avg_pe: number
    avg_yield: number
    change: number
  }>
  top_gainers: Array<{
    symbol: string
    name: string
    price: number
    change: number
    change_percent: number
  }>
  top_losers: Array<{
    symbol: string
    name: string
    price: number
    change: number
    change_percent: number
  }>
  crypto_gainers: Array<{
    symbol: string
    name: string
    price: number
    change: number
    change_percent: number
  }>
  crypto_losers: Array<{
    symbol: string
    name: string
    price: number
    change: number
    change_percent: number
  }>
  asset_distribution: {
    equities: { value: number; percentage: number }
    crypto: { value: number; percentage: number }
    commodities: { value: number; percentage: number }
    bonds: { value: number; percentage: number }
    cash: { value: number; percentage: number }
    total_value: number
    distribution_percent: Record<string, { value: number; percentage: number }>
  }
  market_sentiment: {
    overall: 'bullish' | 'bearish' | 'neutral'
    strength: number
    trending_sectors: Array<{ sector: string; avg_change_24h: number }>
  }
  fetched_at: string
  sources: string[]
}

export interface MarketIndices {
  indices: MarketIndex[]
  fetched_at: string
  source: string
}

export interface MarketIndex {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
  high_52w: number
  low_52w: number
}

export interface MarketMovers {
  gainers: MarketMover[]
  losers: MarketMover[]
  crypto_gainers: MarketMover[]
  crypto_losers: MarketMover[]
  fetched_at: string
}

export interface MarketMover {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
}

export interface AssetDistribution {
  equities: { value: number; percentage: number }
  crypto: { value: number; percentage: number }
  commodities: { value: number; percentage: number }
  bonds: { value: number; percentage: number }
  cash: { value: number; percentage: number }
  total_value: number
  distribution_percent: Record<string, { value: number; percentage: number }>
}

export interface MarketTrends {
  time_period: string
  hot_topics: Array<{
    topic: string
    count: number
    sample_titles: string[]
  }>
  trending_symbols: Array<{
    symbol: string
    mention_count: number
    sentiment: number
  }>
  sentiment_distribution: {
    positive: { count: number; percentage: number }
    negative: { count: number; percentage: number }
    neutral: { count: number; percentage: number }
  }
  most_mentioned: Array<{
    symbol: string
    count: number
  }>
  fetched_at: string
}
