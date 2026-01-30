export type AttributionPeriod = '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | 'ytd' | 'all'

export interface HoldingAttribution {
  holding_id: string
  symbol: string
  name: string
  sector: string
  asset_class: string
  weight: number
  return: number
  contribution: number
  contribution_percent: number
  value_start: number
  value_end: number
  value_change: number
  avg_weight: number
}

export interface SectorAttribution {
  sector: string
  weight: number
  return: number
  contribution: number
  contribution_percent: number
  holdings_count: number
  top_holding: string
  top_holding_return: number
  allocation_effect: number
  selection_effect: number
  total_effect: number
}

export interface AssetClassAttribution {
  asset_class: string
  weight: number
  return: number
  contribution: number
  contribution_percent: number
  holdings_count: number
  sectors_count: number
}

export interface PeriodAttribution {
  period: AttributionPeriod
  start_date: string
  end_date: string
  portfolio_return: number
  portfolio_value_start: number
  portfolio_value_end: number
  total_contribution: number
  holdings: HoldingAttribution[]
  sectors: SectorAttribution[]
  asset_classes: AssetClassAttribution[]
}

export interface AttributionSummary {
  total_return: number
  total_contribution: number
  allocation_effect: number
  selection_effect: number
  total_effect: number
  top_contributor: HoldingAttribution | null
  bottom_contributor: HoldingAttribution | null
  best_sector: SectorAttribution | null
  worst_sector: SectorAttribution | null
  positive_holdings: number
  negative_holdings: number
  neutral_holdings: number
}

export interface AttributionTrend {
  date: string
  daily_return: number
  cumulative_contribution: number
  allocation_effect: number
  selection_effect: number
}

export interface BenchmarkAttribution {
  benchmark_weight: number
  benchmark_return: number
  portfolio_weight: number
  portfolio_return: number
  weight_difference: number
  return_difference: number
  allocation_impact: number
  selection_impact: number
  total_impact: number
}

export interface AttributionFilters {
  period?: AttributionPeriod
  asset_class?: string[]
  sector?: string[]
  min_contribution?: number
  max_contribution?: number
  sort_by?: 'contribution' | 'return' | 'weight' | 'name'
  sort_order?: 'asc' | 'desc'
  limit?: number
}

export const SECTOR_COLORS: Record<string, string> = {
  'Technology': '#3B82F6',
  'Healthcare': '#10B981',
  'Financial': '#F59E0B',
  'Consumer': '#EC4899',
  'Energy': '#EF4444',
  'Industrial': '#8B5CF6',
  'Materials': '#06B6D4',
  'Real Estate': '#14B8A6',
  'Utilities': '#F97316',
  'Communication': '#6366F1',
  'Other': '#6B7280',
}

export const DEFAULT_ATTRIBUTION_PERIODS: { value: AttributionPeriod; label: string }[] = [
  { value: '1d', label: '1D' },
  { value: '1w', label: '1W' },
  { value: '1m', label: '1M' },
  { value: '3m', label: '3M' },
  { value: '6m', label: '6M' },
  { value: '1y', label: '1Y' },
  { value: 'ytd', label: 'YTD' },
  { value: 'all', label: 'All' },
]
