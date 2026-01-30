export type Operator = 'eq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'not'

export interface ScreenerFilter {
  key: string
  label: string
  value: any
  operator: Operator
  active: boolean
}

export interface ScreenerResult {
  id: string
  symbol: string
  name: string
  asset_type: string
  exchange: string
  sector?: string
  industry?: string
  country?: string
  current_price: number
  change_percent: number
  volume: number
  avg_volume: number
  market_cap: number
  pe_ratio?: number
  pb_ratio?: number
  dividend_yield?: number
  eps?: number
  beta?: number
  rsi?: number
  price_above_ma_20?: boolean
  price_above_ma_50?: boolean
  price_above_ma_200?: boolean
  fifty_two_week_high?: number
  fifty_two_week_low?: number
}

export interface ScreenerResponse {
  results: ScreenerResult[]
  count: number
  total_screened: number
  filters_applied: number
  filters: ScreenerFilter[]
  elapsed_seconds: number
  limit: number
  timestamp: string
}

export interface ScreenerRequest {
  market_cap_min?: number
  market_cap_max?: number
  pe_min?: number
  pe_max?: number
  pb_min?: number
  pb_max?: number
  dividend_yield_min?: number
  price_min?: number
  price_max?: number
  volume_min?: number
  volume_avg_min?: number
  change_percent_min?: number
  change_percent_max?: number
  rsi_min?: number
  rsi_max?: number
  above_ma_20?: boolean
  above_ma_50?: boolean
  above_ma_200?: boolean
  sector?: string
  industry?: string
  asset_type?: string
  exchange?: string
  country?: string
  limit?: number
}

export interface ScreenerPreset {
  key: string
  name: string
  description: string
  filters: Partial<ScreenerRequest>
}

export interface FilterCategory {
  label: string
  filters: string[]
}

export interface ScreenerFiltersResponse {
  categories: Record<string, FilterCategory>
  presets: Record<string, { name: string; description: string }>
  active_filters: ScreenerFilter[]
  available_asset_types: Array<{ key: string; label: string; count: number }>
  available_exchanges: Array<{ key: string; label: string; count: number }>
  available_sectors: Array<{ key: string; label: string; count: number }>
}

export type SortField = 'symbol' | 'name' | 'current_price' | 'change_percent' | 'volume' | 'market_cap' | 'pe_ratio' | 'dividend_yield'
export type SortDirection = 'asc' | 'desc'

export interface ScreenerState {
  filters: Partial<ScreenerRequest>
  results: ScreenerResult[]
  loading: boolean
  error: string | null
  total_count: number
  total_screened: number
  elapsed_seconds: number
  last_updated: string | null

  // Sorting
  sort_field: SortField
  sort_direction: SortDirection

  // UI State
  selected_presets: string[]
  limit: number

  // Actions
  setFilter: (key: keyof ScreenerRequest, value: any) => void
  removeFilter: (key: keyof ScreenerRequest) => void
  clearFilters: () => void
  applyPreset: (preset: ScreenerPreset) => void
  setSorting: (field: SortField, direction: SortDirection) => void
  setLimit: (limit: number) => void
  runScreener: () => Promise<void>
  exportResults: (format: 'csv' | 'json') => void
}
