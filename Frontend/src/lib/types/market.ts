/**
 * Market Types
 * Defines all market-related types and interfaces
 */

export interface MarketOverview {
  total_assets: number
  active_stocks: number
  active_cryptos: number
  market_cap_total: number
  volume_24h: number
  last_updated: Date
}

export interface MarketMover {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
}

export interface SectorPerformance {
  name: string
  change_percent: number
  asset_count: number
}

export interface MarketIndex {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
}

export interface MarketData {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume?: number
  market_cap?: number
  asset_type?: string
}

export type MarketIndices = MarketIndex[]
export type MarketMovers = MarketMover[]
export type SectorPerformances = SectorPerformance[]

export interface AssetDistribution {
  category: string
  value: number
  percentage: number
}

export type MoverType = 'gainers' | 'losers'
export type TimeInterval = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M'
