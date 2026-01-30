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

// ================= REAL-TIME DATA TYPES (I5) =================

export interface RealTimePriceUpdate {
  symbol: string
  price: number
  change: number
  change_percent: number
  volume: number
  timestamp: string
  bid?: number
  ask?: number
  spread?: number
  high_52w?: number
  low_52w?: number
  open?: number
  close?: number
  last_update: string
  source: string
}

export interface BatchPriceUpdateRequest {
  symbols: string[]
  include_volume?: boolean
  include_spread?: boolean
  include_orderbook?: boolean
}

export interface BatchPriceUpdatesResponse {
  updates: RealTimePriceUpdate[]
  total_symbols: number
  fetched_at: string
  source: string
}

export interface RecentTrade {
  trade_id: string
  symbol: string
  price: number
  quantity: number
  trade_type: string
  timestamp: string
  exchange: string
  is_buy: boolean
  maker: boolean
}

export interface RecentTradesRequest {
  symbol: string
  limit?: number
  include_makers?: boolean
}

export interface RecentTradesResponse {
  symbol: string
  trades: RecentTrade[]
  count: number
  volume_24h?: number
  avg_trade_size?: number
  fetched_at: string
  source: string
}

export interface OrderBookLevel {
  price: number
  volume: number
  total_size: number
  is_spread: boolean
  spread?: number
  timestamp: string
}

export interface OrderBookResponse {
  symbol: string
  levels: OrderBookLevel[]
  mid_price?: number
  spread: number
  depth: number
  timestamp: string
  source: string
}

export interface WebSocketConnectionInfo {
  connected: boolean
  last_heartbeat: string
  subscriptions: string[]
  connection_time: string
  ping_ms: number
}
