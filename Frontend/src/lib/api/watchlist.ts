import { apiClient } from './client'
import type { Watchlist, WatchlistInput } from '@/lib/types'

interface DeleteResponse {
  message: string
}

export const watchlistApi = {
  list(): Promise<Watchlist[]> {
    return apiClient.get<Watchlist[]>('/watchlist')
  },

  get(id: string): Promise<Watchlist> {
    return apiClient.get<Watchlist>(`/watchlist/${id}`)
  },

  create(data: WatchlistInput): Promise<Watchlist> {
    return apiClient.post<Watchlist>('/watchlist', data)
  },

  update(id: string, data: WatchlistInput): Promise<Watchlist> {
    return apiClient.put<Watchlist>(`/watchlist/${id}`, data)
  },

  delete(id: string): Promise<DeleteResponse> {
    return apiClient.delete(`/watchlist/${id}`)
  },

  addAsset(watchlistId: string, symbol: string): Promise<Watchlist> {
    return apiClient.post<Watchlist>(`/watchlist/${watchlistId}/assets`, { symbol })
  },

  removeAsset(watchlistId: string, symbol: string): Promise<Watchlist> {
    return apiClient.delete<Watchlist>(`/watchlist/${watchlistId}/assets/${symbol}`)
  },
}
