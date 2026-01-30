import { apiClient } from './client'
import type {
  Holding,
  Transaction,
  HoldingsPortfolioSummary,
  HoldingsFilter,
  TransactionFilter,
  CreateHoldingInput,
  UpdateHoldingInput,
  CreateTransactionInput,
  PnLHistoryPoint,
  AssetAllocationItem,
} from '@/lib/types/holdings'

export type { Holding, Transaction, HoldingsPortfolioSummary as PortfolioSummary, HoldingsFilter, TransactionFilter, CreateHoldingInput, UpdateHoldingInput, CreateTransactionInput, PnLHistoryPoint, AssetAllocationItem }

export interface HoldingsListResponse {
  holdings: Holding[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface TransactionsListResponse {
  transactions: Transaction[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface PortfolioPnLResponse {
  portfolio_id: string
  current_value: number
  total_cost: number
  total_pnl: number
  total_pnl_percent: number
  day_change: number
  day_change_percent: number
  history: PnLHistoryPoint[]
}

export interface PortfolioAllocationResponse {
  portfolio_id: string
  allocation: AssetAllocationItem[]
  as_of: string
}

export const holdingsApi = {
  // Holdings CRUD
  list: (
    portfolioId: string,
    filters?: HoldingsFilter
  ): Promise<HoldingsListResponse> => {
    const params: Record<string, string | number> = {}
    if (filters) {
      if (filters.asset_class) {
        params.asset_class = Array.isArray(filters.asset_class) 
          ? filters.asset_class.join(',') 
          : filters.asset_class
      }
      if (filters.symbol) params.symbol = filters.symbol
      if (filters.search) params.search = filters.search
      if (filters.min_value !== undefined) params.min_value = filters.min_value
      if (filters.max_value !== undefined) params.max_value = filters.max_value
      if (filters.sort_by) params.sort_by = filters.sort_by
      if (filters.sort_order) params.sort_order = filters.sort_order
      if (filters.page !== undefined) params.page = filters.page
      if (filters.limit !== undefined) params.limit = filters.limit
    }
    return apiClient.get(`/portfolios/${portfolioId}/holdings/`, { params })
  },

  get: (portfolioId: string, holdingId: string): Promise<Holding> =>
    apiClient.get(`/portfolios/${portfolioId}/holdings/${holdingId}/`),

  create: (
    portfolioId: string,
    data: CreateHoldingInput
  ): Promise<Holding> =>
    apiClient.post(`/portfolios/${portfolioId}/holdings/`, data),

  update: (
    portfolioId: string,
    holdingId: string,
    data: UpdateHoldingInput
  ): Promise<Holding> =>
    apiClient.put(`/portfolios/${portfolioId}/holdings/${holdingId}/`, data),

  delete: (portfolioId: string, holdingId: string): Promise<void> =>
    apiClient.delete(`/portfolios/${portfolioId}/holdings/${holdingId}/`),

  // Transactions CRUD
  listTransactions: (
    portfolioId: string,
    filters?: TransactionFilter
  ): Promise<TransactionsListResponse> => {
    const params: Record<string, string | number> = {}
    if (filters) {
      if (filters.type) {
        params.type = Array.isArray(filters.type) 
          ? filters.type.join(',') 
          : filters.type
      }
      if (filters.symbol) params.symbol = filters.symbol
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date
      if (filters.min_amount !== undefined) params.min_amount = filters.min_amount
      if (filters.max_amount !== undefined) params.max_amount = filters.max_amount
      if (filters.sort_by) params.sort_by = filters.sort_by
      if (filters.sort_order) params.sort_order = filters.sort_order
      if (filters.page !== undefined) params.page = filters.page
      if (filters.limit !== undefined) params.limit = filters.limit
    }
    return apiClient.get(`/portfolios/${portfolioId}/transactions/`, { params })
  },

  getTransaction: (
    portfolioId: string,
    transactionId: string
  ): Promise<Transaction> =>
    apiClient.get(`/portfolios/${portfolioId}/transactions/${transactionId}/`),

  createTransaction: (
    portfolioId: string,
    data: CreateTransactionInput
  ): Promise<Transaction> =>
    apiClient.post(`/portfolios/${portfolioId}/transactions/`, data),

  deleteTransaction: (
    portfolioId: string,
    transactionId: string
  ): Promise<void> =>
    apiClient.delete(`/portfolios/${portfolioId}/transactions/${transactionId}/`),

  // Portfolio metrics
  getPnL: (
    portfolioId: string,
    period?: '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | 'all'
  ): Promise<PortfolioPnLResponse> =>
    apiClient.get(`/portfolios/${portfolioId}/pnl/`, {
      params: { period } as Record<string, string | number>,
    }),

  getAllocation: (portfolioId: string): Promise<PortfolioAllocationResponse> =>
    apiClient.get(`/portfolios/${portfolioId}/allocation/`),

  getSummary: (portfolioId: string): Promise<HoldingsPortfolioSummary> =>
    apiClient.get(`/portfolios/${portfolioId}/summary/`),

  // Bulk operations
  bulkUpdatePrices: (portfolioId: string): Promise<void> =>
    apiClient.post(`/portfolios/${portfolioId}/holdings/refresh-prices/`),

  recalculateAllocations: (portfolioId: string): Promise<void> =>
    apiClient.post(`/portfolios/${portfolioId}/recalculate-allocations/`),
}
