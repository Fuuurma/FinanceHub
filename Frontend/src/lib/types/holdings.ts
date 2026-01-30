export type AssetClass = 'stocks' | 'crypto' | 'bonds' | 'etf' | 'options' | 'cash' | 'commodities' | 'real_estate' | 'other'

export type TransactionType = 'buy' | 'sell' | 'dividend' | 'transfer' | 'split' | 'fee' | 'deposit' | 'withdrawal'

export type AttributionPeriod = '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | 'all'

export interface Holding {
  id: string
  portfolio_id: string
  symbol: string
  name: string
  asset_class: AssetClass
  quantity: number
  average_cost: number
  current_price: number
  current_value: number
  unrealized_pnl: number
  unrealized_pnl_percent: number
  day_change: number
  day_change_percent: number
  weight: number
  sector?: string
  exchange?: string
  currency: string
  created_at: string
  updated_at: string
}

export interface Transaction {
  id: string
  portfolio_id: string
  holding_id?: string
  symbol: string
  type: TransactionType
  quantity: number
  price: number
  total: number
  fees: number
  currency: string
  date: string
  notes?: string
  created_at: string
}

export interface HoldingsPortfolioSummary {
  id: string
  name: string
  total_value: number
  total_cost: number
  total_pnl: number
  total_pnl_percent: number
  day_change: number
  day_change_percent: number
  holdings_count: number
  asset_allocation: AssetAllocationItem[]
  currency: string
  is_default: boolean
  is_public: boolean
  created_at: string
  updated_at: string
}

export interface AssetAllocationItem {
  asset_class: AssetClass
  value: number
  percentage: number
  holdings_count: number
}

export interface PnLHistoryPoint {
  date: string
  value: number
  pnl: number
  pnl_percent: number
}

export interface HoldingsFilter {
  asset_class?: AssetClass | AssetClass[]
  symbol?: string
  search?: string
  min_value?: number
  max_value?: number
  sort_by?: keyof Holding
  sort_order?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export interface TransactionFilter {
  type?: TransactionType | TransactionType[]
  symbol?: string
  start_date?: string
  end_date?: string
  min_amount?: number
  max_amount?: number
  sort_by?: keyof Transaction
  sort_order?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export interface CreateHoldingInput {
  symbol: string
  name: string
  asset_class: AssetClass
  quantity: number
  average_cost: number
  currency?: string
  sector?: string
  exchange?: string
}

export interface UpdateHoldingInput {
  quantity?: number
  average_cost?: number
  current_price?: number
  sector?: string
  exchange?: string
}

export interface CreateTransactionInput {
  holding_id?: string
  symbol: string
  type: TransactionType
  quantity: number
  price: number
  fees?: number
  currency?: string
  date?: string
  notes?: string
}

export const ASSET_CLASS_LABELS: Record<AssetClass, string> = {
  stocks: 'Stocks',
  crypto: 'Cryptocurrency',
  bonds: 'Bonds',
  etf: 'ETFs',
  options: 'Options',
  cash: 'Cash',
  commodities: 'Commodities',
  real_estate: 'Real Estate',
  other: 'Other',
}

export const ASSET_CLASS_COLORS: Record<AssetClass, string> = {
  stocks: '#3B82F6',
  crypto: '#F59E0B',
  bonds: '#10B981',
  etf: '#8B5CF6',
  options: '#EC4899',
  cash: '#6B7280',
  commodities: '#F97316',
  real_estate: '#14B8A6',
  other: '#9CA3AF',
}

export const TRANSACTION_TYPE_LABELS: Record<TransactionType, string> = {
  buy: 'Buy',
  sell: 'Sell',
  dividend: 'Dividend',
  transfer: 'Transfer',
  split: 'Split',
  fee: 'Fee',
  deposit: 'Deposit',
  withdrawal: 'Withdrawal',
}

export const TRANSACTION_TYPE_COLORS: Record<TransactionType, string> = {
  buy: 'text-green-600 bg-green-100',
  sell: 'text-red-600 bg-red-100',
  dividend: 'text-blue-600 bg-blue-100',
  transfer: 'text-gray-600 bg-gray-100',
  split: 'text-purple-600 bg-purple-100',
  fee: 'text-orange-600 bg-orange-100',
  deposit: 'text-emerald-600 bg-emerald-100',
  withdrawal: 'text-rose-600 bg-rose-100',
}
