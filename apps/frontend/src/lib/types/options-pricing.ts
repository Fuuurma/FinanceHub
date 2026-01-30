/**
 * Options Pricing Types
 * TypeScript interfaces for options pricing API
 */

export type OptionType = 'call' | 'put'

export interface OptionPriceRequest {
  underlying_price: number
  strike_price: number
  time_to_expiration: number
  risk_free_rate?: number
  volatility: number
  option_type?: OptionType
}

export interface GreeksResponse {
  price: number
  delta: number
  gamma: number
  vega: number
  theta: number
  rho: number
}

export interface OptionPriceResponse {
  underlying_price: number
  strike_price: number
  time_to_expiration: number
  option_type: string
  price: number
  greeks: GreeksResponse
  computed_in_ms: number
}

export interface BatchPriceRequest {
  underlying_prices: number[]
  strikes: number[]
  expirations: number[]
  volatilities: number[]
  risk_free_rate?: number
  option_type?: OptionType
}

export interface BatchPriceResult {
  underlying_price: number
  strike_price: number
  expiration: number
  volatility: number
  option_type: string
  price: number
  delta: number
  gamma: number
  vega: number
  theta: number
  rho: number
}

export interface BatchPriceResponse {
  results: BatchPriceResult[]
  total_calculations: number
  computed_in_ms: number
}

export interface ImpliedVolatilityRequest {
  market_price: number
  underlying_price: number
  strike_price: number
  time_to_expiration: number
  risk_free_rate?: number
  option_type?: OptionType
  max_iterations?: number
  tolerance?: number
}

export interface ImpliedVolatilityResponse {
  market_price: number
  implied_volatility: number
  iterations: number
  computed_in_ms: number
}

export interface GreeksRequest {
  underlying_price: number
  strike_price: number
  time_to_expiration: number
  risk_free_rate?: number
  volatility: number
  option_type?: OptionType
}

export interface VolatilitySurfaceRequest {
  underlying_price: number
  strikes: number[]
  expirations: number[]
  market_prices: number[][]
  risk_free_rate?: number
  option_types?: OptionType[]
}

export interface VolatilitySurfaceResponse {
  surface: Record<string, number>
  strikes: number[]
  expirations: number[]
  computed_in_ms: number
}

export interface OptionsChainRequest {
  symbol: string
  underlying_price: number
  risk_free_rate?: number
  expiration_date?: string
}

export interface OptionsChainResponse {
  symbol: string
  underlying_price: number
  expiration_date: string
  calls: OptionsChainStrike[]
  puts: OptionsChainStrike[]
  computed_in_ms: number
}

export interface OptionsChainStrike {
  strike: number
  bid: number
  ask: number
  last: number
  volume: number
  open_interest: number
  delta: number
  gamma: number
  theta: number
  vega: number
  implied_volatility: number
}
