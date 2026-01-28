/**
 * Fundamentals API
 * All fundamentals-related API calls for equities, crypto, commodities, and bonds
 */

import { apiClient } from './client'
import type {
  EquityValuation,
  EquityOwnership,
  EarningsReport,
  IncomeStatement,
  BalanceSheet,
  CashFlowStatement,
  CryptoProtocolMetrics,
  StakingData,
  CryptoSupplyMetrics,
  CommodityMetrics,
  BondMetrics,
  YieldCurvePoint,
  ScreenerFilter,
  ScreenerResult,
  PeriodType,
  CacheStats,
} from '../types'

export const fundamentalsApi = {
  /**
   * Get equity fundamentals for a symbol
   */
  getEquityFundamentals: (symbol: string) =>
    apiClient.get<{
      valuation: EquityValuation | null
      ownership: EquityOwnership | null
      earnings: EarningsReport | null
    }>(`/fundamentals/fundamentals/${symbol}`),

  /**
   * Get equity valuation metrics
   */
  getEquityValuation: (symbol: string, periodType?: PeriodType) =>
    apiClient.get<EquityValuation>(`/fundamentals/valuation/${symbol}`, {
      params: { period_type: periodType },
    }),

  /**
   * Get equity financials (income statement, balance sheet, cash flow)
   */
  getEquityFinancials: (symbol: string, periodType?: PeriodType) =>
    apiClient.get<{
      income_statement: IncomeStatement | null
      balance_sheet: BalanceSheet | null
      cash_flow: CashFlowStatement | null
    }>(`/fundamentals/financials/${symbol}`, {
      params: { period_type: periodType },
    }),

  /**
   * Get historical fundamentals for trend analysis
   */
  getHistoricalFundamentals: (symbol: string, periodType: PeriodType = 'annual', limit: number = 5) =>
    apiClient.get<{
      symbol: string
      period_type: PeriodType
      data: Array<{
        date: string
        period: string
        pe_ratio: number | null
        eps: number | null
        revenue: number | null
      }>
    }>(`/fundamentals/historical/${symbol}`, {
      params: { period_type: periodType, limit },
    }),

  /**
   * Get crypto protocol metrics
   */
  getCryptoProtocol: (protocol: string) =>
    apiClient.get<CryptoProtocolMetrics>(`/fundamentals/crypto/protocol/${protocol}`),

  /**
   * Get all crypto protocols
   */
  getAllCryptoProtocols: () =>
    apiClient.get<CryptoProtocolMetrics[]>('/fundamentals/crypto/protocols'),

  /**
   * Get chain TVL
   */
  getChainTVL: (chain: string) =>
    apiClient.get<{ chain: string; tvl: number; change_24h: number }>(
      `/fundamentals/crypto/chain/${chain}`
    ),

  /**
   * Get bond metrics
   */
  getBondMetrics: (symbol?: string) =>
    apiClient.get<BondMetrics[]>('/fundamentals/bonds/metrics', {
      params: { symbol },
    }),

  /**
   * Get yield curve data
   */
  getYieldCurve: () =>
    apiClient.get<YieldCurvePoint[]>('/fundamentals/bonds/yield-curve'),

  /**
   * Get treasury history
   */
  getTreasuryHistory: (years: number = 5) =>
    apiClient.get<{ date: string; rate: number; maturity: string }[]>(
      '/fundamentals/bonds/treasury-history',
      { params: { years } }
    ),

  /**
   * Screen stocks based on filters
   */
  screenStocks: (filter: ScreenerFilter) =>
    apiClient.get<ScreenerResult[]>('/fundamentals/screener', {
      params: filter,
    }),

  /**
   * Batch fetch equity fundamentals for multiple symbols
   */
  batchFetchEquities: (symbols: string[]) =>
    apiClient.post<Record<string, EquityValuation | null>>(
      '/fundamentals/batch/equities',
      { symbols: symbols.join(',') }
    ),

  /**
   * Get sector performance
   */
  getSectorPerformance: () =>
    apiClient.get<{ sector: string; avg_pe: number; avg_yield: number; change: number }[]>(
      '/fundamentals/sectors'
    ),

  /**
   * Get cache statistics
   */
  getCacheStats: () =>
    apiClient.get<CacheStats>('/fundamentals/cache/stats'),

  /**
   * Invalidate cache for a symbol
   */
  invalidateCache: (symbol: string) =>
    apiClient.post<{ symbol: string; invalidated: boolean; message: string }>(
      `/fundamentals/cache/invalidate/${symbol}`
    ),
}
