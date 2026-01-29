export interface Order {
  id: string
  user_id: string
  portfolio_id: string
  asset_id: string
  asset_symbol: string
  asset_name: string
  order_type: 'market' | 'limit' | 'stop' | 'stop_limit' | 'oco'
  side: 'buy' | 'sell'
  quantity: number
  price: number | null
  stop_price: number | null
  status: 'pending' | 'filled' | 'partially_filled' | 'cancelled' | 'rejected' | 'expired'
  filled_quantity: number
  remaining_quantity: number
  filled_price: number | null
  average_fill_price: number | null
  fees: number
  total_value: number | null
  time_in_force: 'day' | 'gtc' | 'ioc' | 'fok'
  expiry_date: string | null
  created_at: string
  updated_at: string
  notes: string | null
  is_active: boolean
  is_oco: boolean
}

export interface Position {
  id: string
  user_id: string
  portfolio_id: string
  asset_id: string
  asset_symbol: string
  asset_name: string
  side: 'long' | 'short'
  quantity: number
  avg_entry_price: number
  current_price: number | null
  market_value: number | null
  cost_basis: number
  unrealized_pnl: number
  unrealized_pnl_percent: number
  realized_pnl: number
  total_pnl: number
  total_pnl_percent: number
  total_fees: number
  is_open: boolean
  opened_at: string
  closed_at: string | null
  days_open: number
  notes: string | null
}

export interface AccountSummary {
  total_cash: number
  available_cash: number
  margin_used: number
  margin_available: number
  buying_power: number
  total_positions_value: number
  total_account_value: number
  unrealized_pnl: number
  realized_pnl_today: number
  day_trading_volume: number
  day_trades_count: number
}

export interface PositionSummary {
  total_positions: number
  open_positions: number
  long_positions: number
  short_positions: number
  total_market_value: number
  total_unrealized_pnl: number
  today_pnl: number
  largest_win: number
  largest_loss: number
  win_rate: number
}

export interface OrderCreateInput {
  portfolio_id: string
  asset_id: string
  order_type: 'market' | 'limit' | 'stop' | 'stop_limit' | 'oco'
  side: 'buy' | 'sell'
  quantity: number
  price?: number
  stop_price?: number
  time_in_force?: 'day' | 'gtc' | 'ioc' | 'fok'
  expiry_date?: string
  notes?: string
  oco_linked_order_id?: string
}

export interface PositionSize {
  max_quantity: number
  buying_power: number
  cost: number
  fees: number
  total_cost: number
}
