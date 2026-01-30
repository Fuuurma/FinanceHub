export interface Portfolio {
  id: string
  user_id: string
  name: string
  description?: string
  is_public: boolean
  is_default?: boolean
  total_value: number
  total_cost: number
  total_pnl: number
  total_pnl_percent: number
  day_pnl: number
  day_pnl_percent: number
  holdings_count: number
  created_at: string
  updated_at: string
}

export interface PortfolioHolding {
  id: string
  portfolio_id: string
  symbol: string
  name: string
  asset_type: 'stock' | 'crypto' | 'bond' | 'etf' | 'mutual_fund' | 'option' | 'cash'
  quantity: number
  average_cost: number
  current_price: number
  current_value: number
  cost_basis: number
  unrealized_pnl: number
  unrealized_pnl_percent: number
  day_change: number
  day_change_percent: number
  weight: number
  sector?: string
  last_updated: string
}

export interface PortfolioTransaction {
  id: string
  portfolio_id: string
  type: 'buy' | 'sell' | 'dividend' | 'deposit' | 'withdrawal' | 'transfer_in' | 'transfer_out'
  symbol?: string
  asset_type?: 'stock' | 'crypto' | 'bond' | 'etf' | 'mutual_fund' | 'option' | 'cash'
  quantity?: number
  price?: number
  amount: number
  fees: number
  notes?: string
  date: string
  created_at: string
}

export interface PortfolioHistory {
  date: string
  value: number
  change: number
  change_percent: number
}

export interface PortfolioMetrics {
  total_return: number
  total_return_percent: number
  annualized_return: number
  volatility: number
  sharpe_ratio: number
  max_drawdown: number
  max_drawdown_percent: number
  beta: number
  alpha: number
}

export interface PortfolioCreateInput {
  name: string
  description?: string
  is_public?: boolean
  initial_deposit?: number
}

export interface PortfolioUpdateInput {
  name?: string
  description?: string
  is_public?: boolean
}

export interface HoldingsSummary {
  total_holdings: number
  total_value: number
  top_performers: PortfolioHolding[]
  worst_performers: PortfolioHolding[]
  sector_allocation: Record<string, { value: number; percentage: number }>
  asset_allocation: Record<string, { value: number; percentage: number }>
}

export interface TransactionsFilter {
  type?: PortfolioTransaction['type']
  symbol?: string
  asset_type?: PortfolioHolding['asset_type']
  start_date?: string
  end_date?: string
}

export interface TransactionsResponse {
  transactions: PortfolioTransaction[]
  total_count: number
  page: number
  page_size: number
}

export interface PortfoliosListResponse {
  portfolios: Portfolio[]
  total_count: number
}
