/**
 * Asset Types
 * Defines all asset-related types and interfaces
 */

export interface Asset {
  id: string
  symbol: string
  name: string
  asset_type: string
  exchange?: string
  currency?: string
  description?: string
  sector?: string
  industry?: string
  market_cap?: number
  country?: string
  website?: string
  is_active: boolean
}

export interface AssetDetail extends Asset {
  fundamentals?: AssetFundamentals
  metrics?: AssetMetrics
}

export interface AssetFundamentals {
  market_cap: number
  pe_ratio: number
  pb_ratio: number
  eps: number
  dividend_yield: number
  beta: number
  revenue: number
  net_income: number
  total_assets: number
  total_debt: number
}

export interface AssetMetrics {
  symbol: string
  timestamp: Date
  open: number
  high: number
  low: number
  close: number
  volume: number
  change?: number
  change_percent?: number
}

export interface PriceHistory {
  timestamp: Date
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface AssetFilter {
  search?: string
  asset_type?: string
  exchange?: string
  sector?: string
}

export type AssetType = 'stock' | 'crypto' | 'etf' | 'index' | 'bond' | 'commodity' | 'forex'
