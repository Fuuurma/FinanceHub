/**
 * Portfolio & Watchlist Types
 * Defines all portfolio and watchlist related types
 */

export interface Watchlist {
  id: string
  name: string
  assets: string[]
  is_public: boolean
  created_at: string
}

export interface WatchlistInput {
  name: string
  symbols?: string[]
  is_public?: boolean
}

export interface AddToWatchlistInput {
  asset_symbols: string[]
}

export interface Alert {
  id: string
  asset_symbol: string
  condition: string
  threshold: number
  is_active: boolean
  triggered_at?: Date
  created_at: Date
}

export interface AlertInput {
  asset_symbol: string
  condition: string
  threshold: number
}

export type AlertCondition = 'price_above' | 'price_below' | 'percent_change_up' | 'percent_change_down' | 'volume_above'

export interface Portfolio {
  id: string
  name: string
  created_at: Date
}

export interface PortfolioInput {
  name: string
}

export interface Holding {
  id: string
  asset_symbol: string
  quantity: number
  avg_cost: number
  current_value: number
}

export interface HoldingInput {
  asset_symbol: string
  quantity: number
  avg_cost: number
}
