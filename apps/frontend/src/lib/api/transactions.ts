import { apiClient } from './client'

export interface Transaction {
  id: string
  transaction_type: string
  asset: {
    id: string
    ticker: string
    name: string
    asset_class: string
    asset_type: string
    currency: string
  }
  quantity: string | null
  price_per_share: string
  total_amount: string
  fees: string
  date: string
  notes: string | null
}

export interface TransactionCreate {
  transaction_type: 'buy' | 'sell' | 'dividend'
  asset_id: string
  quantity?: string
  price_per_share: string
  fees?: string
  date?: string
  notes?: string
}

export const transactionsApi = {
  list: (portfolioId: string, params?: { 
    transaction_type?: string
    start_date?: string
    end_date?: string
    limit?: number
    offset?: number
  }) =>
    apiClient.get<Transaction[]>(`/portfolios/${portfolioId}/transactions`, { params }),

  get: (portfolioId: string, transactionId: string) =>
    apiClient.get<Transaction>(`/portfolios/${portfolioId}/transactions/${transactionId}`),

  create: (portfolioId: string, data: TransactionCreate) =>
    apiClient.post<Transaction>(`/portfolios/${portfolioId}/transactions`, data),

  delete: (portfolioId: string, transactionId: string) =>
    apiClient.delete(`/portfolios/${portfolioId}/transactions/${transactionId}`),
}
