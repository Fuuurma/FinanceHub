/**
 * User Data API
 * All user data-related API calls (watchlists, portfolios, alerts)
 */

import { apiClient } from './client'
import type { Watchlist, WatchlistInput, Alert, AlertCreateInput, AlertUpdateInput } from '@/lib/types'
import type { Portfolio, PortfolioCreateInput, PortfolioUpdateInput } from '@/lib/types/portfolio'
import type { Holding, CreateHoldingInput, UpdateHoldingInput } from '@/lib/types/holdings'
import type { WatchlistAsset } from '@/lib/types/watchlist'

interface AddToWatchlistInput {
  symbols: string[]
}

interface AddAssetsResponse {
  message: string
  watchlist_id: string
  assets_added: string[]
}

interface DeleteResponse {
  message: string
}

export const userDataApi = {
  getWatchlists(): Promise<Watchlist[]> {
    return apiClient.get('/data/watchlists')
  },

  createWatchlist(data: WatchlistInput): Promise<Watchlist> {
    return apiClient.post('/data/watchlists', data)
  },

  getWatchlist(id: string): Promise<Watchlist> {
    return apiClient.get(`/data/watchlists/${id}`)
  },

  addAssetsToWatchlist(id: string, data: AddToWatchlistInput): Promise<AddAssetsResponse> {
    return apiClient.post(`/data/watchlists/${id}/assets`, data)
  },

  deleteWatchlist(id: string): Promise<DeleteResponse> {
    return apiClient.delete(`/data/watchlists/${id}`)
  },

  getAlerts(activeOnly: boolean = false): Promise<Alert[]> {
    return apiClient.get('/data/alerts', {
      params: { active_only: activeOnly ? 1 : 0 },
    })
  },

  createAlert(data: AlertCreateInput): Promise<Alert> {
    return apiClient.post('/data/alerts', data)
  },

  deleteAlert(id: string): Promise<DeleteResponse> {
    return apiClient.delete(`/data/alerts/${id}`)
  },

  getPortfolios(): Promise<Portfolio[]> {
    return apiClient.get('/data/portfolios')
  },

  createPortfolio(data: PortfolioCreateInput): Promise<Portfolio> {
    return apiClient.post('/data/portfolios', data)
  },

  getPortfolioHoldings(id: string): Promise<Holding[]> {
    return apiClient.get(`/data/portfolios/${id}/holdings`)
  },

  addHolding(id: string, data: CreateHoldingInput): Promise<Holding> {
    return apiClient.post(`/data/portfolios/${id}/holdings`, data)
  },

  deletePortfolio(id: string): Promise<DeleteResponse> {
    return apiClient.delete(`/data/portfolios/${id}`)
  },
}
