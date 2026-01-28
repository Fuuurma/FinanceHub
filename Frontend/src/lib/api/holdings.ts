import { apiClient } from './client'

export interface Holding {
  id: string
  asset: {
    id: string
    ticker: string
    name: string
    asset_class: string
    asset_type: string
    currency: string
  }
  quantity: string
  average_buy_price: string | null
  current_price: string | null
  current_value: string | null
  unrealized_pnl: string | null
}

export interface HoldingUpdate {
  quantity: string
  average_buy_price?: string
}

export const holdingsApi = {
  list: (portfolioId: string) =>
    apiClient.get<Holding[]>(`/portfolios/${portfolioId}/holdings`),

  get: (portfolioId: string, holdingId: string) =>
    apiClient.get<Holding>(`/portfolios/${portfolioId}/holdings/${holdingId}`),

  create: (portfolioId: string, data: { asset_id: string; quantity: string }) =>
    apiClient.post<Holding>(`/portfolios/${portfolioId}/holdings`, data),

  update: (portfolioId: string, holdingId: string, data: HoldingUpdate) =>
    apiClient.put<Holding>(`/portfolios/${portfolioId}/holdings/${holdingId}`, data),

  delete: (portfolioId: string, holdingId: string) =>
    apiClient.delete(`/portfolios/${portfolioId}/holdings/${holdingId}`),
}
