/**
 * Currency Types
 * TypeScript interfaces for currency exchange API
 */

export interface ExchangeRateResponse {
  base: string
  quote: string
  rate: number | null
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
  converted_amount: number | null
  converted_currency: string
  exchange_rate: number | null
  formatted_original: string
  formatted_converted: string | null
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
  rate: number | null
  inverse_rate: number | null
}

export interface TrendPoint {
  date: string
  rate: number | null
}

export interface TrendRequest {
  base_currency?: string
  quote_currency?: string
  days?: number
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

export interface RefreshRatesResponse {
  success: boolean
  base: string
  timestamp: string
}

export interface CheckAvailabilityResponse {
  from_currency: string
  to_currency: string
  available: boolean
}

export type CurrencyType = 'fiat' | 'crypto' | 'all'
