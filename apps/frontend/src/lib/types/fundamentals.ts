/**
 * Fundamentals Types
 * Defines all fundamental data types for equities, crypto, commodities, and bonds
 */

export interface EquityValuation {
  symbol: string
  report_date: string
  period_type: 'quarterly' | 'annual' | 'ttm' | 'mrq'
  fiscal_year: number
  fiscal_period: number | null
  market_cap: number | null
  enterprise_value: number | null
  pe_ratio: number | null
  pe_forward: number | null
  pb_ratio: number | null
  ps_ratio: number | null
  ev_ebitda: number | null
  ev_sales: number | null
  peg_ratio: number | null
  dividend_yield: number | null
  payout_ratio: number | null
  beta: number | null
  price_to_fcf: number | null
  book_value_per_share: number | null
  earnings_per_share: number | null
  revenue_growth_yoy: number | null
  earnings_growth_yoy: number | null
  gross_margin: number | null
  operating_margin: number | null
  net_margin: number | null
  roe: number | null
  roa: number | null
  debt_to_equity: number | null
  current_ratio: number | null
}

export interface EquityOwnership {
  symbol: string
  report_date: string
  shares_outstanding: number | null
  shares_float: number | null
  shares_owned_by_insiders: number | null
  shares_owned_by_institutions: number | null
  insider_ownership_pct: number | null
  institutional_ownership_pct: number | null
  short_interest: number | null
  short_interest_pct: number | null
  days_to_cover: number | null
  avg_daily_volume_30d: number | null
}

export interface EarningsReport {
  symbol: string
  report_date: string
  period_type: 'quarterly' | 'annual' | 'ttm' | 'mrq'
  fiscal_year: number
  fiscal_period: number | null
  eps_actual: number | null
  eps_estimate: number | null
  eps_surprise_pct: number | null
  revenue_actual: number | null
  revenue_estimate: number | null
  revenue_surprise_pct: number | null
  net_income: number | null
  gross_profit: number | null
  operating_income: number | null
  ebitda: number | null
  next_earnings_date: string | null
}

export interface IncomeStatement {
  symbol: string
  report_date: string
  period_type: 'quarterly' | 'annual' | 'ttm' | 'mrq'
  fiscal_year: number
  fiscal_period: number | null
  total_revenue: number | null
  gross_profit: number | null
  operating_income: number | null
  net_income: number | null
  ebitda: number | null
  basic_eps: number | null
  diluted_eps: number | null
}

export interface BalanceSheet {
  symbol: string
  report_date: string
  period_type: 'quarterly' | 'annual' | 'ttm' | 'mrq'
  fiscal_year: number
  fiscal_period: number | null
  cash_and_equivalents: number | null
  total_current_assets: number | null
  total_assets: number | null
  total_current_liabilities: number | null
  total_liabilities: number | null
  total_stockholders_equity: number | null
}

export interface CashFlowStatement {
  symbol: string
  report_date: string
  period_type: 'quarterly' | 'annual' | 'ttm' | 'mrq'
  fiscal_year: number
  fiscal_period: number | null
  operating_cash_flow: number | null
  capital_expenditures: number | null
  investing_cash_flow: number | null
  financing_cash_flow: number | null
  free_cash_flow: number | null
}

export interface CryptoProtocolMetrics {
  protocol: string
  report_date: string
  tvl: number | null
  tvl_change_24h: number | null
  tvl_change_7d: number | null
  staking_yield: number | null
  number_of_stakers: number | null
  total_staked: number | null
  staking_ratio: number | null
}

export interface StakingData {
  protocol: string
  report_date: string
  total_staked: number | null
  stakers_count: number | null
  avg_staking_duration: number | null
  staking_yield_30d: number | null
  staking_yield_annual: number | null
}

export interface CryptoSupplyMetrics {
  symbol: string
  report_date: string
  circulating_supply: number | null
  total_supply: number | null
  max_supply: number | null
  inflation_rate: number | null
  burned_supply: number | null
}

export interface CommodityMetrics {
  symbol: string
  report_date: string
  spot_price: number | null
  price_change_24h: number | null
  price_change_30d: number | null
  inventory_level: number | null
  production_volume: number | null
  demand_index: number | null
}

export interface BondMetrics {
  symbol: string
  report_date: string
  yield_rate: number | null
  price: number | null
  coupon_rate: number | null
  maturity_date: string | null
  credit_rating: string | null
  duration: number | null
}

export interface YieldCurvePoint {
  maturity: string
  rate: number
  date: string
}

export interface StockScreenerFilter {
  pe_ratio_min?: number
  pe_ratio_max?: number
  market_cap_min?: number
  market_cap_max?: number
  dividend_yield_min?: number
  sector?: string
  exchange?: string
  [key: string]: string | number | undefined
}

export interface FundamentalScreenerResult {
  symbol: string
  name: string
  sector: string
  market_cap: number
  pe_ratio: number | null
  dividend_yield: number | null
  price: number
  change_percent: number
}

export type PeriodType = 'quarterly' | 'annual' | 'ttm' | 'mrq'

export interface CacheStats {
  fundamentals_keys: Record<string, string>
  cache_ttl_recommendations: Record<string, string>
  fetched_at: string
}
