/**
 * Fixed Income Types
 * TypeScript interfaces for fixed income analytics API
 */

export type CouponFrequency = 1 | 2 | 4
export type PriceType = 'clean' | 'dirty'

export interface BondPricingRequest {
  face_value: number
  coupon_rate: number
  yield_rate: number
  time_to_maturity: number
  frequency?: CouponFrequency
  price_type?: PriceType
}

export interface BondPricingResponse {
  price: number
  yield_to_maturity: number
  duration: number
  modified_duration: number
  convexity: number
  oas: number
  z_spread: number
  computed_in_ms: number
}

export interface ZeroCouponBondRequest {
  face_value: number
  yield_rate: number
  time_to_maturity: number
}

export interface ZeroCouponBondResponse {
  price: number
  yield_to_maturity: number
  time_to_maturity: number
  computed_in_ms: number
}

export interface YieldCurveBootstrapRequest {
  bond_prices: number[]
  maturities: number[]
  frequencies: CouponFrequency[]
}

export interface YieldCurveResponse {
  rates: Record<string, number>
  zero_rates: number[]
  computed_in_ms: number
}

export interface BondCashFlowRequest {
  face_value: number
  coupon_rate: number
  time_to_maturity: number
  frequency?: CouponFrequency
}

export interface CashFlow {
  time_years: number
  amount: number
  discount_factor: number
}

export interface BondCashFlowResponse {
  cash_flows: CashFlow[]
  total_coupons: number
  principal_repayment: number
  pv_coupons: number
  pv_principal: number
}

export interface DurationConvexityRequest {
  price: number
  yield_rate: number
  time_to_maturity: number
  frequency?: CouponFrequency
}

export interface DurationConvexityResponse {
  macaulay_duration: number
  modified_duration: number
  convexity: number
  price_change_1bp_up: number
  price_change_1bp_down: number
}

export interface OASRequest {
  price: number
  yield_rate: number
  time_to_maturity: number
  frequency?: CouponFrequency
}

export interface OASResponse {
  oas: number
  computed_in_ms: number
}

export interface ZSpreadRequest {
  price: number
  yield_rate: number
  time_to_maturity: number
  treasury_yields: number[]
  frequency?: CouponFrequency
}

export interface ZSpreadResponse {
  z_spread: number
  computed_in_ms: number
}

export interface TreasuryYieldRequest {
  maturity: string
}

export interface TreasuryYieldResponse {
  yields: Record<string, number>
  last_updated: string
}
