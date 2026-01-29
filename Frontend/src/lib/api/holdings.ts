import { apiClient } from './client'
import type {
  Holding,
  Transaction,
  PortfolioSummary,
  HoldingsFilter,
  TransactionFilter,
  CreateHoldingInput,
  UpdateHoldingInput,
  CreateTransactionInput,
  PnLHistoryPoint,
  AssetAllocationItem,
} from '@/lib/types/holdings'

export type { Holding, Transaction, PortfolioSummary, HoldingsFilter, TransactionFilter, CreateHoldingInput, UpdateHoldingInput, CreateTransactionInput, PnLHistoryPoint, AssetAllocationItem }

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
  ): Promise<HoldingsListResponse> =>
    apiClient.get(`/portfolios/${portfolioId}/holdings/`, {
      params: filters,
    }),

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
  ): Promise<TransactionsListResponse> =>
    apiClient.get(`/portfolios/${portfolioId}/transactions/`, {
      params: filters,
    }),

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
      params: { period },
    }),

  getAllocation: (portfolioId: string): Promise<PortfolioAllocationResponse> =>
    apiClient.get(`/portfolios/${portfolioId}/allocation/`),

  getSummary: (portfolioId: string): Promise<PortfolioSummary> =>
    apiClient.get(`/portfolios/${portfolioId}/summary/`),

  // Bulk operations
  bulkUpdatePrices: (portfolioId: string): Promise<void> =>
    apiClient.post(`/portfolios/${portfolioId}/holdings/refresh-prices/`),

  recalculateAllocations: (portfolioId: string): Promise<void> =>
    apiClient.post(`/portfolios/${portfolioId}/recalculate-allocations/`),
}
