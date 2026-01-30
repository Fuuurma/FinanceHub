/**
 * Currency Exchange API Client
 * Currency conversion, exchange rates, and currency info
 */

import { apiClient } from './client'
import type {
  ExchangeRateResponse,
  ConvertRequest,
  ConvertResponse,
  AllRatesResponse,
  CurrencyInfo,
  CurrencyListResponse,
  ConvertMultipleRequest,
  ConvertMultipleResponse,
  CrossRateRequest,
  CrossRateResponse,
  TrendRequest,
  TrendResponse,
  PopularRatesResponse,
  RefreshRatesResponse,
  CheckAvailabilityResponse,
  CurrencyType,
} from '@/lib/types/currency'

export const currencyApi = {
  /**
   * Get exchange rate between two currencies
   */
  getExchangeRate: (base: string, quote: string) =>
    apiClient.get<ExchangeRateResponse>(`/currency/rates/${base}/${quote}`),

  /**
   * Convert an amount from one currency to another
   */
  convert: (data: ConvertRequest) =>
    apiClient.post<ConvertResponse>('/currency/convert', data),

  /**
   * Get all exchange rates for a base currency
   */
  getAllRates: (base: string = 'USD') =>
    apiClient.get<AllRatesResponse>(`/currency/rates/${base}`),

  /**
   * List all available currencies
   */
  listCurrencies: (type?: CurrencyType) => {
    const params = type && type !== 'all' ? { type } : undefined
    return apiClient.get<CurrencyListResponse>('/currency/currencies', params ? { params } : undefined)
  },

  /**
   * Get information about a specific currency
   */
  getCurrencyInfo: (code: string) =>
    apiClient.get<CurrencyInfo>(`/currency/currencies/${code}`),

  /**
   * Convert an amount to multiple currencies at once
   */
  convertMultiple: (data: ConvertMultipleRequest) =>
    apiClient.post<ConvertMultipleResponse>('/currency/convert-multiple', data),

  /**
   * Get cross rate between two currencies
   */
  getCrossRate: (fromCurrency: string, toCurrency: string) =>
    apiClient.post<CrossRateResponse>('/currency/cross-rate', {
      from_currency: fromCurrency,
      to_currency: toCurrency,
    }),

  /**
   * Get exchange rate trend over time
   */
  getTrend: (params?: TrendRequest) => {
    const queryParams: Record<string, string | number> = {}
    if (params?.base_currency) queryParams.base = params.base_currency
    if (params?.quote_currency) queryParams.quote = params.quote_currency
    if (params?.days) queryParams.days = params.days

    return apiClient.get<TrendResponse>('/currency/trend', { params: queryParams })
  },

  /**
   * Get popular exchange rates
   */
  getPopularRates: (base: string = 'USD') =>
    apiClient.get<PopularRatesResponse>(`/currency/popular`, {
      params: { base },
    }),

  /**
   * Refresh exchange rates from external source
   */
  refreshRates: (base: string = 'USD') =>
    apiClient.post<RefreshRatesResponse>('/currency/refresh', null, {
      params: { base },
    }),

  /**
   * Check if a currency pair is available
   */
  checkAvailability: (fromCurrency: string, toCurrency: string) =>
    apiClient.get<CheckAvailabilityResponse>(`/currency/check/${fromCurrency}/${toCurrency}`),
}
