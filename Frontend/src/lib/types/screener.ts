export interface ScreenerFilter {
  key: string
  value: any
  operator?: string
}

export interface ScreenerFilterOut {
  key: string
  label: string
  value: any
  operator: string
  active: boolean
}

export interface ScreenerPreset {
  key: string
  name: string
  description: string
}

export interface ScreenerFiltersOut {
  categories: Record<string, Record<string, string[]>>
  presets: ScreenerPreset[]
  active_filters: ScreenerFilterOut[]
  available_asset_types: AssetTypeInfo[]
  available_exchanges: ExchangeInfo[]
  available_sectors: SectorInfo[]
}

export interface AssetTypeInfo {
  key: string
  label: string
  count: number
}

export interface ExchangeInfo {
  key: string
  label: string
  count: number
}

export interface SectorInfo {
  key: string
  label: string
  count: number
}

export interface ScreenerResult {
  id: string
  symbol: string
  name: string
  asset_type: string
  price: number | null
  change: number | null
  change_percent: number | null
  volume: number | null
  market_cap: number | null
  pe_ratio: number | null
  dividend_yield: number | null
}

export interface ScreenerResponse {
  results: ScreenerResult[]
  count: number
  total_screened: number
  filters_applied: number
  filters: ScreenerFilterOut[]
  elapsed_seconds: number
  limit: number
  timestamp: string
}
