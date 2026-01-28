import { apiClient } from './client'
import type { Watchlist, WatchlistInput } from '../types'

export const watchlistApi = {
  list: () => Promise<Watchlist[]> =>
    apiClient.get<Watchlist[]>('/watchlist'),

  get: (id: string) => Promise<Watchlist> =>
    apiClient.get<Watchlist>(`/watchlist/${id}`),

  create: (data: WatchlistInput) => Promise<Watchlist> =>
    apiClient.post<Watchlist>('/watchlist', data),

  update: (id: string, data: WatchlistInput) => Promise<Watchlist> =>
    apiClient.put<Watchlist>(`/watchlist/${id}`, data),

  delete: (id: string) => Promise<{ message: string }> =>
    apiClient.delete(`/watchlist/${id}`),

  addAsset: (watchlistId: string, symbol: string) => Promise<Watchlist> =>
    apiClient.post<Watchlist>(`/watchlist/${watchlistId}/assets`, { symbol }),

  removeAsset: (watchlistId: string, symbol: string) => Promise<Watchlist> =>
    apiClient.delete<Watchlist>(`/watchlist/${watchlistId}/assets/${symbol}`),
}
