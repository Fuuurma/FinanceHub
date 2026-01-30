/**
 * Options Pricing API Client
 * Black-Scholes model and options analytics integration
 */

import { apiClient } from './client'
import type {
  OptionPriceRequest,
  OptionPriceResponse,
  BatchPriceRequest,
  BatchPriceResponse,
  ImpliedVolatilityRequest,
  ImpliedVolatilityResponse,
  GreeksRequest,
  GreeksResponse,
  VolatilitySurfaceRequest,
  VolatilitySurfaceResponse,
  OptionsChainRequest,
  OptionsChainResponse,
} from '@/lib/types/options-pricing'

export const optionsPricingApi = {
  /**
   * Price a single option using Black-Scholes model
   * Returns option price and all Greeks (Delta, Gamma, Vega, Theta, Rho)
   */
  priceOption: (data: OptionPriceRequest) =>
    apiClient.post<OptionPriceResponse>('/options-pricing/price', {
      underlying_price: data.underlying_price,
      strike_price: data.strike_price,
      time_to_expiration: data.time_to_expiration,
      risk_free_rate: data.risk_free_rate || 0.03,
      volatility: data.volatility,
      option_type: data.option_type || 'call',
    }),

  /**
   * Price multiple options in batch for performance
   * Efficiently prices all combinations of underlying prices, strikes, expirations, and volatilities
   */
  priceBatch: (data: BatchPriceRequest) =>
    apiClient.post<BatchPriceResponse>('/options-pricing/batch-price', {
      underlying_prices: data.underlying_prices,
      strikes: data.strikes,
      expirations: data.expirations,
      volatilities: data.volatilities,
      risk_free_rate: data.risk_free_rate || 0.03,
      option_type: data.option_type || 'call',
    }),

  /**
   * Calculate implied volatility from market price using Newton-Raphson
   * Iteratively solves for volatility that yields the observed market price
   */
  calculateImpliedVolatility: (data: ImpliedVolatilityRequest) =>
    apiClient.post<ImpliedVolatilityResponse>('/options-pricing/implied-volatility', {
      market_price: data.market_price,
      underlying_price: data.underlying_price,
      strike_price: data.strike_price,
      time_to_expiration: data.time_to_expiration,
      risk_free_rate: data.risk_free_rate || 0.03,
      option_type: data.option_type || 'call',
      max_iterations: data.max_iterations || 100,
      tolerance: data.tolerance || 1e-6,
    }),

  /**
   * Calculate Greeks for an option without full pricing
   * More efficient when you only need the sensitivities
   */
  getGreeks: (params: GreeksRequest) =>
    apiClient.get<GreeksResponse>('/options-pricing/greeks', {
      params: {
        underlying_price: params.underlying_price,
        strike_price: params.strike_price,
        time_to_expiration: params.time_to_expiration,
        risk_free_rate: params.risk_free_rate || 0.03,
        volatility: params.volatility,
        option_type: params.option_type || 'call',
      },
    }),

  /**
   * Calculate volatility surface from market prices
   */
  calculateVolatilitySurface: (data: VolatilitySurfaceRequest) =>
    apiClient.post<VolatilitySurfaceResponse>('/options-pricing/volatility-surface', {
      underlying_price: data.underlying_price,
      strikes: data.strikes,
      expirations: data.expirations,
      market_prices: data.market_prices,
      risk_free_rate: data.risk_free_rate || 0.03,
      option_types: data.option_types || ['call', 'put'],
    }),

  /**
   * Get options chain for a symbol
   */
  getOptionsChain: (params: OptionsChainRequest) => {
    const queryParams: Record<string, string | number> = {
      symbol: params.symbol,
      underlying_price: params.underlying_price,
      risk_free_rate: params.risk_free_rate || 0.03,
    }
    if (params.expiration_date) {
      queryParams.expiration_date = params.expiration_date
    }
    return apiClient.get<OptionsChainResponse>('/options-pricing/chain', {
      params: queryParams,
    })
  },
}
