/**
 * CoinMarketCap Types
 * Types for CoinMarketCap API responses - crypto listings, info, global metrics
 */

// Crypto Listings
export interface CryptoListing {
  id: number
  symbol: string
  name: string
  cmc_rank: number
  price: number
  volume_24h: number
  market_cap: number
  circulating_supply: number
  total_supply?: number
  max_supply?: number
  percent_change_1h?: number
  percent_change_24h: number
  percent_change_7d: number
  last_updated: string
  quote?: {
    [currency: string]: {
      price: number
      volume_24h: number
      market_cap: number
      percent_change_1h?: number
      percent_change_24h: number
      percent_change_7d: number
      last_updated: string
    }
  }
}

// Crypto Info
export interface CryptoInfo {
  id: number
  name: string
  symbol: string
  slug: string
  logo: string
  description: string
  category: string
  tags: string[]
  urls?: {
    website?: string[]
    explorer?: string[]
    source_code?: string[]
  }
  platform?: {
    id: number
    name: string
    symbol: string
    slug: string
    token_address: string
  }
  date_added: string
  date_launched?: string
  supply: {
    circulating: number
    total: number
    max: number
    infinite?: boolean
  }
  self_reported?: boolean
  self_reported_market_cap?: number
  cmc_rank?: number
  market_pairs?: number
  circulating_supply?: number
  total_supply?: number
  max_supply?: number
}

// Crypto Info with Quote (combined for API response)
export interface CryptoInfoWithQuote extends CryptoInfo {
  quote?: {
    USD?: {
      price: number
      volume24h: number
      marketCap: number
      percentChange1h?: number
      percentChange24h?: number
      percentChange7d?: number
      lastUpdated: string
    }
  }
}

// Global Metrics
export interface GlobalMetrics {
  active_cryptocurrencies: number
  active_exchanges: number
  active_market_pairs: number
  active_market_pairs_activated: number
  active_market_pairs_as_of?: string
  bitcoin_dominance: number
  ethereum_dominance: number
  quote: {
    [currency: string]: {
      total_market_cap: number
      total_volume_24h: number
      total_volume_24h_reported: number
      altcoin_volume_24h: number
      altcoin_volume_24h_reported: number
      altcoin_market_cap: number
      defi_volume_24h?: number
      defi_volume_24h_reported?: number
      stablecoin_volume_24h?: number
      stablecoin_volume_24h_reported?: number
      defi_market_cap?: number
      stablecoin_market_cap?: number
      last_updated: string
    }
  }
  market_cap_percentage?: {
    [symbol: string]: number
  }
  volume_percentage?: {
    [symbol: string]: number
  }
  market_cap_by_category?: {
    [category: string]: {
      market_cap: number
      volume_24h: number
      dominance: number
      change_24h?: number
    }
  }
}

// Market Pairs
export interface MarketPair {
  id: number
  exchange: {
    id: number
    name: string
    slug: string
  }
  pair: string
  base_currency: {
    id: number
    symbol: string
    name: string
  }
  quote_currency: {
    id: number
    symbol: string
    name: string
  }
  market_url: string
  price: number
  volume_24h: number
  volume_percent?: number
  price_quote: {
    [currency: string]: number
  }
  updated_at: string
}

// Exchange Info
export interface CMCExchangeInfo {
  id: number
  name: string
  slug: string
  website?: string
  logo?: string
  num_market_pairs: number
  volume_24h?: number
  cmc_rank?: number
  date_launched?: string
  notice?: string
  market_pairs?: {
    id: number
    exchange_id: number
    pair: string
    base_currency_id: number
    quote_currency_id: number
  }
}

// Trending
export interface TrendingCrypto {
  id: number
  symbol: string
  name: string
  slug: string
  cmc_rank: number
  price: number
  volume_24h: number
  market_cap: number
  percent_change_1h?: number
  percent_change_24h: number
  percent_change_7d: number
  last_updated: string
}

// Historical OHLCV
export interface CryptoOHLCV {
  time_open: number
  time_close: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  market_cap?: number
  timestamp: string
}

// Fiat Map
export interface FiatCurrency {
  id: number
  name: string
  symbol: string
  code: string
}
