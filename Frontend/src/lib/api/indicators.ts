/**
 * Technical Indicators API Client
 * Client for technical indicators endpoints - SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic, etc.
 */

import { apiClient } from './client'
import type {
  MovingAverageData,
  BollingerBandsData,
  MACDData,
  StochasticData,
  RSIData,
} from '@/lib/types/indicators'

export const indicatorsApi = {
  // Calculate multiple indicators at once
  calculate: (symbol: string, indicators: string[], days = 90) =>
    apiClient.post<any>('/api/v1/indicators/calculate', {
      symbol,
      indicators,
      days
    }),

  // SMA
  getSMA: (symbol: string, period = 20, days = 90) =>
    apiClient.get<MovingAverageData[]>(`/api/v1/indicators/${symbol}/sma`, {
      params: { period, days }
    }),

  // EMA
  getEMA: (symbol: string, period = 20, days = 90) =>
    apiClient.get<MovingAverageData[]>(`/api/v1/indicators/${symbol}/ema`, {
      params: { period, days }
    }),

  // RSI
  getRSI: (symbol: string, period = 14, days = 90) =>
    apiClient.get<RSIData[]>(`/api/v1/indicators/${symbol}/rsi`, {
      params: { period, days }
    }),

  // MACD
  getMACD: (
    symbol: string,
    fast_period = 12,
    slow_period = 26,
    signal_period = 9,
    days = 90
  ) =>
    apiClient.get<MACDData[]>(`/api/v1/indicators/${symbol}/macd`, {
      params: { fast_period, slow_period, signal_period, days }
    }),

  // Bollinger Bands
  getBollinger: (symbol: string, period = 20, std_dev = 2.0, days = 90) =>
    apiClient.get<BollingerBandsData[]>(`/api/v1/indicators/${symbol}/bollinger`, {
      params: { period, std_dev, days }
    }),

  // Stochastic
  getStochastic: (
    symbol: string,
    k_period = 14,
    d_period = 3,
    smooth_k = 3,
    days = 90
  ) =>
    apiClient.get<StochasticData[]>(`/api/v1/indicators/${symbol}/stochastic`, {
      params: { k_period, d_period, smooth_k, days }
    }),

  // CCI
  getCCI: (symbol: string, period = 20, days = 90) =>
    apiClient.get<any[]>(`/api/v1/indicators/${symbol}/cci`, {
      params: { period, days }
    }),

  // Williams %R
  getWilliamsR: (symbol: string, period = 14, days = 90) =>
    apiClient.get<any[]>(`/api/v1/indicators/${symbol}/williams_r`, {
      params: { period, days }
    }),

  // ATR
  getATR: (symbol: string, period = 14, days = 90) =>
    apiClient.get<any[]>(`/api/v1/indicators/${symbol}/atr`, {
      params: { period, days }
    }),

  // OBV
  getOBV: (symbol: string, days = 90) =>
    apiClient.get<any[]>(`/api/v1/indicators/${symbol}/obv`, {
      params: { days }
    }),

  // WMA
  getWMA: (symbol: string, period = 20, days = 90) =>
    apiClient.get<any[]>(`/api/v1/indicators/${symbol}/wma`, {
      params: { period, days }
    }),

  // MFI
  getMFI: (symbol: string, period = 14, days = 90) =>
    apiClient.get<any[]>(`/api/v1/indicators/${symbol}/mfi`, {
      params: { period, days }
    }),

  // VWAP
  getVWAP: (symbol: string, days = 90) =>
    apiClient.get<any[]>(`/api/v1/indicators/${symbol}/vwap`, {
      params: { days }
    }),

  // Ichimoku
  getIchimoku: (
    symbol: string,
    tenkan_period = 9,
    kijun_period = 26,
    senkou_span_b_period = 52,
    days = 180
  ) =>
    apiClient.get<any>(`/api/v1/indicators/${symbol}/ichimoku`, {
      params: { tenkan_period, kijun_period, senkou_span_b_period, days }
    }),

  // Parabolic SAR
  getParabolicSAR: (symbol: string, acceleration = 0.02, maximum = 0.2, days = 90) =>
    apiClient.get<any[]>(`/api/v1/indicators/${symbol}/parabolic-sar`, {
      params: { acceleration, maximum, days }
    }),

  // Chart data
  getChart: (symbol: string, range = '1y') =>
    apiClient.get<any[]>(`/api/v1/iex/chart/${symbol}`, {
      params: { period: range }
    }),
}
