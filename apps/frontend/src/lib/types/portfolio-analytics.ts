export interface PortfolioSummary {
  portfolio_id: string
  name: string
  total_value: number
  total_invested: number
  total_pnl: number
  total_pnl_percent: number
  day_change: number
  day_change_percent: number
  total_fees_paid: number
  asset_count: number
  top_performers: Array<{
    symbol: string
    pnl: number
    pnl_percent: number
    current_value: number
  }>
  worst_performers: Array<{
    symbol: string
    pnl: number
    pnl_percent: number
    current_value: number
  }>
  allocation: Record<string, { value: number; percentage: number }>
  last_updated: string
}

export interface PerformanceMetrics {
  portfolio_id: string
  time_period: string
  total_return: number
  total_return_percent: number
  annualized_return: number
  volatility: number | null
  sharpe_ratio: number | null
  max_drawdown: number | null
  max_drawdown_percent: number | null
  best_day: { date: string; value: number } | null
  worst_day: { date: string; value: number } | null
  win_rate: number | null
  alpha_vs_sp500: number | null
  beta_vs_sp500: number | null
}

export interface RiskAnalysis {
  portfolio_id: string
  overall_risk_score: number
  risk_level: 'Low' | 'Medium' | 'High'
  concentration_risk: number
  diversification_score: number
  sector_exposure: Record<string, { value: number; percentage: number }>
  largest_holding_percent: number
  volatility_exposure: number | null
  liquidity_score: number | null
  recommendations: string[]
  analyzed_at: string
}

export interface HoldingsAnalysis {
  portfolio_id: string
  holdings: Array<{
    asset_id: string
    symbol: string
    name: string
    quantity: number
    average_cost: number
    current_price: number
    current_value: number
    unrealized_pnl: number
    unrealized_pnl_percent: number
    weight: number
  }>
  sector_breakdown: Record<string, { value: number; percentage: number }>
  asset_class_breakdown: Record<string, { value: number; percentage: number }>
  geographic_breakdown: Record<string, { value: number; percentage: number }> | null
  unrealized_gains: number
  unrealized_losses: number
  total_dividends: number
  analyzed_at: string
}

export interface RebalancingSuggestions {
  portfolio_id: string
  current_allocation: Record<string, { value: number; percentage: number }>
  suggested_allocation: Record<string, { value: number; percentage: number }>
  suggested_trades: Array<{
    action: 'buy' | 'sell'
    asset_class: string
    current_percentage: number
    target_percentage: number
    priority: 'high' | 'medium' | 'low'
  }>
  rebalancing_reason: string
  estimated_savings: number | null
  priority_trades: Array<{
    action: 'buy' | 'sell'
    asset_class: string
    current_percentage: number
    target_percentage: number
    priority: 'high' | 'medium' | 'low'
  }>
  analyzed_at: string
}

export interface ComparisonResponse {
  portfolio_id: string
  benchmark_type: 'sp500' | 'custom' | 'peer_average'
  portfolio_return: number
  benchmark_return: number
  excess_return: number
  percentile: number | null
  relative_performance: 'outperforming' | 'underperforming' | 'in line'
  comparison_period: string
  analyzed_at: string
}

export type AnalyticsPeriod = '1d' | '7d' | '30d' | '90d' | '180d' | '1y' | '3y' | '5y' | 'ytd' | 'all'

export interface AssetPerformance {
  asset_type: string
  return: number
  value: number
}

export interface RiskMetrics {
  volatility: number
  beta: number
  sharpe_ratio: number
}

export interface PortfolioAnalytics {
  total_return: number
  total_value: number
  total_value_change: number
  total_value_change_percent: number
  performance_by_asset: AssetPerformance[]
  risk_metrics: RiskMetrics
  period_start: string
  period_end: string
  total_transactions: number
  summary?: {
    portfolio_id: string
    name: string
    total_value: number
    total_invested: number
    total_pnl: number
    total_pnl_percent: number
    total_fees_paid: number
    asset_count: number
    top_performers: Array<{ symbol: string; pnl: number; pnl_percent: number; current_value: number }>
    worst_performers: Array<{ symbol: string; pnl: number; pnl_percent: number; current_value: number }>
    allocation: Record<string, { value: number; percentage: number }>
    last_updated: string
  }
  performance?: {
    portfolio_id: string
    time_period: string
    cagr: number
    total_return: number
    total_return_percent: number
    annualized_return: number
    volatility: number | null
    sharpe_ratio: number | null
    sortino_ratio: number | null
    max_drawdown: number | null
    max_drawdown_percent: number | null
    max_drawdown_date: string | null
    recovery_time: number | null
    best_day: { date: string; value: number } | null
    worst_day: { date: string; value: number } | null
    win_rate: number | null
    alpha_vs_sp500: number | null
    beta_vs_sp500: number | null
    var_95: number | null
    var_99: number | null
    avg_win: number | null
    avg_loss: number | null
    profit_factor: number | null
  }
  risk?: {
    portfolio_id: string
    overall_risk_score: number
    risk_level: 'Low' | 'Medium' | 'High'
    concentration_risk: number
    diversification_score: number
    sector_exposure: Record<string, { value: number; percentage: number }>
    largest_holding_percent: number
    volatility_exposure: number | null
    liquidity_score: number | null
    beta: number | null
    correlation: number | null
    recommendations: string[]
    analyzed_at: string
  }
}

export interface SectorData {
  name: string
  value: number
  percentage: number
}

export interface BenchmarkData {
  date: string
  portfolio: number
  benchmark: number
}

export interface AttributionData {
  symbol: string
  contribution: number
  value: number
}

export interface RollingReturnsData {
  date: string
  '7d': number
  '30d': number
}

export interface RiskHistoryData {
  date: string
  volatility: number
  sharpeRatio: number
}

export type BenchmarkType = 'sp500' | 'nasdaq' | 'dow' | 'custom'

export interface PerformanceMetricsEnhanced {
  portfolio_id: string
  time_period: string
  cagr: number
  total_return: number
  total_return_percent: number
  annualized_return: number
  volatility: number | null
  sharpe_ratio: number | null
  sortino_ratio: number | null
  max_drawdown: number | null
  max_drawdown_percent: number | null
  max_drawdown_date: string | null
  recovery_time: number | null
  best_day: { date: string; value: number } | null
  worst_day: { date: string; value: number } | null
  win_rate: number | null
  alpha_vs_sp500: number | null
  beta_vs_sp500: number | null
  var_95: number | null
  var_99: number | null
  avg_win: number | null
  avg_loss: number | null
  profit_factor: number | null
}

export interface RiskAnalysisEnhanced {
  portfolio_id: string
  overall_risk_score: number
  risk_level: 'Low' | 'Medium' | 'High'
  concentration_risk: number
  diversification_score: number
  sector_exposure: Record<string, { value: number; percentage: number }>
  largest_holding_percent: number
  volatility_exposure: number | null
  liquidity_score: number | null
  beta: number | null
  correlation: number | null
  recommendations: string[]
  analyzed_at: string
}

export interface TimeSeriesPoint {
  date: string
  value: number
}

export interface DrawdownPoint {
  date: string
  drawdown: number
  peak_date: string
  trough_date: string
}

export interface CorrelationMatrix {
  labels: string[]
  matrix: number[][]
}

export interface KPIMetric {
  id: string
  label: string
  value: number
  unit: 'percent' | 'currency' | 'ratio' | 'number'
  change?: number
  changePercent?: number
  trend: 'up' | 'down' | 'neutral'
  description: string
  color: string
  icon: string
}

export interface AnalyticsState {
  selectedPortfolioId: string | null
  selectedPeriod: AnalyticsPeriod
  selectedBenchmark: BenchmarkType
  data: PortfolioAnalytics | null
  loading: boolean
  error: string | null
  lastUpdated: string | null

  setSelectedPortfolio: (id: string | null) => void
  setSelectedPeriod: (period: AnalyticsPeriod) => void
  setSelectedBenchmark: (benchmark: BenchmarkType) => void
  fetchAnalytics: () => Promise<void>
  clearAnalytics: () => void
}
