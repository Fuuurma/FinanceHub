/**
 * Portfolios API
 * All portfolio-related API calls for portfolio management
 */

import { apiClient } from './client'
import type {
  Portfolio,
  PortfolioHolding,
  PortfolioTransaction,
  PortfolioHistory,
  PortfolioMetrics,
  PortfolioCreateInput,
  PortfolioUpdateInput,
  HoldingsSummary,
  TransactionsFilter,
  TransactionsResponse,
  PortfoliosListResponse,
} from '../types'

export const portfoliosApi = {
  /**
   * Get all user portfolios (alias for list)
   */
  getPortfolios: () =>
    apiClient.get<PortfoliosListResponse>('/portfolios/'),

  /**
   * Get all user portfolios
   */
  list: () =>
    apiClient.get<PortfoliosListResponse>('/portfolios/'),

  /**
   * Get single portfolio by ID
   */
  getPortfolio: (portfolioId: string) =>
    apiClient.get<Portfolio>(`/portfolios/${portfolioId}/`),

  /**
   * Create new portfolio
   */
  createPortfolio: (data: PortfolioCreateInput) =>
    apiClient.post<Portfolio>('/portfolios/', data),

  /**
   * Update portfolio
   */
  updatePortfolio: (portfolioId: string, data: PortfolioUpdateInput) =>
    apiClient.put<Portfolio>(`/portfolios/${portfolioId}/`, data),

  /**
   * Delete portfolio
   */
  deletePortfolio: (portfolioId: string) =>
    apiClient.delete(`/portfolios/${portfolioId}/`),

  /**
   * Get portfolio holdings
   */
  getHoldings: (portfolioId: string) =>
    apiClient.get<PortfolioHolding[]>(`/portfolios/${portfolioId}/holdings/`),

  /**
   * Get holdings summary
   */
  getHoldingsSummary: (portfolioId: string) =>
    apiClient.get<HoldingsSummary>(`/portfolios/${portfolioId}/holdings-summary/`),

  /**
   * Get portfolio transactions
   */
  getTransactions: (portfolioId: string, filter?: TransactionsFilter) => {
    const params: Record<string, string | number> = {}
    if (filter) {
      if (filter.type) params.type = filter.type
      if (filter.symbol) params.symbol = filter.symbol
      if (filter.asset_type) params.asset_type = filter.asset_type
      if (filter.start_date) params.start_date = filter.start_date
      if (filter.end_date) params.end_date = filter.end_date
    }
    return apiClient.get<TransactionsResponse>(`/portfolios/${portfolioId}/transactions/`, {
      params,
    })
  },

  /**
   * Get portfolio history (value over time)
   */
  getHistory: (portfolioId: string, period: '1m' | '3m' | '6m' | '1y' | 'all' = '1m') =>
    apiClient.get<PortfolioHistory[]>(`/portfolios/${portfolioId}/history/`, {
      params: { period },
    }),

  /**
   * Get portfolio performance metrics
   */
  getMetrics: (portfolioId: string, period: '1m' | '3m' | '6m' | '1y' | 'all' = '1m') =>
    apiClient.get<PortfolioMetrics>(`/portfolios/${portfolioId}/metrics/`, {
      params: { period },
    }),

  /**
   * Add holding to portfolio
   */
  addHolding: (
    portfolioId: string,
    data: { symbol: string; quantity: number; price: number; asset_type?: string }
  ) =>
    apiClient.post<PortfolioHolding>(`/portfolios/${portfolioId}/holdings/`, data),

  /**
   * Update holding
   */
  updateHolding: (
    portfolioId: string,
    holdingId: string,
    data: { quantity?: number; average_cost?: number }
  ) =>
    apiClient.put<PortfolioHolding>(`/portfolios/${portfolioId}/holdings/${holdingId}/`, data),

  /**
   * Remove holding from portfolio
   */
  removeHolding: (portfolioId: string, holdingId: string) =>
    apiClient.delete(`/portfolios/${portfolioId}/holdings/${holdingId}/`),

  /**
   * Add transaction to portfolio
   */
  addTransaction: (
    portfolioId: string,
    data: Omit<PortfolioTransaction, 'id' | 'portfolio_id' | 'created_at'>
  ) =>
    apiClient.post<PortfolioTransaction>(`/portfolios/${portfolioId}/transactions/`, data),
}
