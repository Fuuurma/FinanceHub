/**
 * Currency API
 * Currency conversion, exchange rates, and crypto rates
 */

import { apiClient } from './client'

const CURRENCY_API = '/currency'

export interface ExchangeRateResponse {
  base: string
  quote: string
  rate?: number
  timestamp: string
}

export interface ConvertRequest {
  amount: number
  from_currency: string
  to_currency: string
  date?: string
}

export interface ConvertResponse {
  original_amount: number
  original_currency: string
  converted_amount?: number
  converted_currency: string
  exchange_rate?: number
  formatted_original: string
  formatted_converted?: string
}

export interface AllRatesResponse {
  base: string
  rates: Record<string, number>
  timestamp: string
}

export interface CurrencyInfo {
  code: string
  name: string
  symbol: string
  symbol_native: string
  decimal_digits: number
  type: string
  countries: string[]
}

export interface CurrencyListResponse {
  currencies: CurrencyInfo[]
  total_count: number
}

export interface ConvertMultipleRequest {
  amount: number
  from_currency: string
  to_currencies: string[]
}

export interface ConvertMultipleResponse {
  original_amount: number
  original_currency: string
  conversions: Record<string, number>
}

export interface CrossRateRequest {
  from_currency: string
  to_currency: string
}

export interface CrossRateResponse {
  from_currency: string
  to_currency: string
  rate?: number
  inverse_rate?: number
}

export interface TrendPoint {
  date: string
  rate?: number
}

export interface TrendResponse {
  base: string
  quote: string
  days: number
  data: TrendPoint[]
}

export interface PopularRatesResponse {
  base: string
  rates: Record<string, number>
  timestamp: string
}

export interface RateAvailabilityResponse {
  from_currency: string
  to_currency: string
  available: boolean
}

export const currencyApi = {
  // ================= EXCHANGE RATES =================

  getExchangeRate(base: string, quote: string): Promise<ExchangeRateResponse> {
    return apiClient.get<ExchangeRateResponse>(`${CURRENCY_API}/rates/${base}/${quote}`)
  },

  getAllRates(base: string): Promise<AllRatesResponse> {
    return apiClient.get<AllRatesResponse>(`${CURRENCY_API}/rates/${base}`)
  },

  getPopularRates(base: string = 'USD'): Promise<PopularRatesResponse> {
    return apiClient.get<PopularRatesResponse>(`${CURRENCY_API}/popular`, {
      params: { base },
    })
  },

  checkRateAvailability(fromCurrency: string, toCurrency: string): Promise<RateAvailabilityResponse> {
    return apiClient.get<RateAvailabilityResponse>(`${CURRENCY_API}/check/${fromCurrency}/${toCurrency}`)
  },

  // ================= CURRENCY CONVERSION =================

  convertCurrency(request: ConvertRequest): Promise<ConvertResponse> {
    return apiClient.post<ConvertResponse>(`${CURRENCY_API}/convert`, request)
  },

  convertMultiple(request: ConvertMultipleRequest): Promise<ConvertMultipleResponse> {
    return apiClient.post<ConvertMultipleResponse>(`${CURRENCY_API}/convert-multiple`, request)
  },

  getCrossRate(request: CrossRateRequest): Promise<CrossRateResponse> {
    return apiClient.post<CrossRateResponse>(`${CURRENCY_API}/cross-rate`, request)
  },

  // ================= CURRENCY INFO =================

  getCurrencies(type?: 'fiat' | 'crypto'): Promise<CurrencyListResponse> {
    const params = type ? { type } : undefined
    return apiClient.get<CurrencyListResponse>(`${CURRENCY_API}/currencies`, params ? { params } : undefined)
  },

  getCurrencyInfo(code: string): Promise<CurrencyInfo> {
    return apiClient.get<CurrencyInfo>(`${CURRENCY_API}/currencies/${code}`)
  },

  // ================= TRENDS =================

  getRateTrend(base: string = 'USD', quote: string = 'USD', days: number = 30): Promise<TrendResponse> {
    return apiClient.get<TrendResponse>(`${CURRENCY_API}/trend`, {
      params: { base, quote, days },
    })
  },

  // ================= RATE MANAGEMENT =================

  refreshRates(base: string = 'USD'): Promise<{ success: boolean; base: string; timestamp: string }> {
    return apiClient.post(`${CURRENCY_API}/refresh`, null, {
      params: { base },
    })
  },
}

export default currencyApi
