export type AttributionPeriod = '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | '2y' | '3y' | '5y' | 'ytd' | 'all'

export type BenchmarkType =
  | 'sp500'          // S&P 500
  | 'nasdaq100'      // NASDAQ-100
  | 'dow30'          // Dow Jones Industrial Average
  | 'russell2000'    // Russell 2000 (small cap)
  | 'vti'            // Vanguard Total Stock Market ETF
  | 'qqq'            // Invesco QQQ (tech-heavy)
  | 'spy'            // SPDR S&P 500 ETF
  | 'dia'            // SPDR Dow Jones ETF
  | 'iwm'            // iShares Russell 2000 ETF
  | 'vgt'            // Vanguard Information Technology ETF
  | 'vht'            // Vanguard Health Care ETF
  | 'vcr'            // Vanguard Consumer Discretionary ETF
  | 'vdc'            // Vanguard Consumer Staples ETF
  | 'ven'            // Vanguard Energy ETF
  | 'vfi'            // Vanguard Financials ETF
  | 'viu'            // Vanguard International (ex-US)
  | 'acwx'           // iShares MSCI All Country World ex-US
  | 'bnd'            // Vanguard Total Bond Market ETF
  | 'agg'            // iShares Core US Aggregate Bond
  | 'tlt'            // iShares 20+ Year Treasury Bond
  | 'gld'            // SPDR Gold Shares
  | 'bitcoin'        // Bitcoin
  | 'ethereum'       // Ethereum
  | 'custom'         // Custom benchmark

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
  benchmark_comparison?: BenchmarkComparison
}

export interface BenchmarkComparison {
  benchmark_type: BenchmarkType
  benchmark_return: number
  portfolio_return: number
  excess_return: number
  excess_return_percent: number
  tracking_error: number
  information_ratio: number
  beta: number
  correlation: number
  sector_outperformance: SectorAttribution[]
  sector_underperformance: SectorAttribution[]
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
  { value: '2y', label: '2Y' },
  { value: '3y', label: '3Y' },
  { value: '5y', label: '5Y' },
  { value: 'ytd', label: 'YTD' },
  { value: 'all', label: 'All' },
]

export interface BenchmarkConfig {
  type: BenchmarkType
  name: string
  description: string
  category: 'us_indices' | 'etf' | 'crypto' | 'bonds' | 'international' | 'custom'
  annualized_return?: number
  volatility?: number
}

export const BENCHMARK_CONFIGS: BenchmarkConfig[] = [
  { type: 'sp500', name: 'S&P 500', description: '500 largest US companies', category: 'us_indices' },
  { type: 'nasdaq100', name: 'NASDAQ-100', description: '100 largest non-financial stocks', category: 'us_indices' },
  { type: 'dow30', name: 'Dow Jones 30', description: '30 blue-chip companies', category: 'us_indices' },
  { type: 'russell2000', name: 'Russell 2000', description: '2000 small-cap companies', category: 'us_indices' },
  { type: 'vti', name: 'VTI', description: 'Vanguard Total Stock Market', category: 'etf' },
  { type: 'qqq', name: 'QQQ', description: 'Invesco NASDAQ 100', category: 'etf' },
  { type: 'spy', name: 'SPY', description: 'SPDR S&P 500 ETF', category: 'etf' },
  { type: 'dia', name: 'DIA', description: 'SPDR Dow Jones ETF', category: 'etf' },
  { type: 'iwm', name: 'IWM', description: 'iShares Russell 2000', category: 'etf' },
  { type: 'vgt', name: 'VGT', description: 'Vanguard Information Tech', category: 'etf' },
  { type: 'vht', name: 'VHT', description: 'Vanguard Health Care', category: 'etf' },
  { type: 'vcr', name: 'VCR', description: 'Vanguard Consumer Disc.', category: 'etf' },
  { type: 'vdc', name: 'VDC', description: 'Vanguard Consumer Staples', category: 'etf' },
  { type: 'ven', name: 'VEN', description: 'Vanguard Energy', category: 'etf' },
  { type: 'vfi', name: 'VFI', description: 'Vanguard Financials', category: 'etf' },
  { type: 'viu', name: 'VIU', description: 'Vanguard Developed ex-US', category: 'international' },
  { type: 'acwx', name: 'ACWX', description: 'iShares MSCI AC World ex-US', category: 'international' },
  { type: 'bnd', name: 'BND', description: 'Vanguard Total Bond Market', category: 'bonds' },
  { type: 'agg', name: 'AGG', description: 'iShares Core US Aggregate', category: 'bonds' },
  { type: 'tlt', name: 'TLT', description: 'iShares 20+ Year Treasury', category: 'bonds' },
  { type: 'gld', name: 'GLD', description: 'SPDR Gold Shares', category: 'custom' },
  { type: 'bitcoin', name: 'Bitcoin', description: 'BTC/USD', category: 'crypto' },
  { type: 'ethereum', name: 'Ethereum', description: 'ETH/USD', category: 'crypto' },
]

export const BENCHMARK_CATEGORIES = [
  { value: 'us_indices', label: 'US Indices' },
  { value: 'etf', label: 'ETFs' },
  { value: 'crypto', label: 'Cryptocurrency' },
  { value: 'bonds', label: 'Bonds' },
  { value: 'international', label: 'International' },
]
