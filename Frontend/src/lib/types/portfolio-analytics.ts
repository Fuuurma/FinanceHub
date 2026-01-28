export interface PortfolioSummary {
  portfolio_id: string
  name: string
  total_value: number
  total_invested: number
  total_pnl: number
  total_pnl_percent: number
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
