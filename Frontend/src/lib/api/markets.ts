/**
 * Markets API
 * All market-related API calls
 */

import { apiClient } from './client'
import type { MarketOverview, MarketMover, SectorPerformance, MarketIndex, MoverType } from '@/lib/types'

export const marketsApi = {
  getOverview(): Promise<MarketOverview> {
    return apiClient.get('/markets/overview')
  },

  getMovers(type: MoverType = 'gainers', limit: number = 10): Promise<MarketMover[]> {
    return apiClient.get('/markets/movers', {
      params: { type, limit },
    })
  },

  getSectors(): Promise<SectorPerformance[]> {
    return apiClient.get('/markets/sectors')
  },

  getIndices(): Promise<MarketIndex[]> {
    return apiClient.get('/markets/indices')
  },

  getTrending(assetType?: string, limit: number = 10): Promise<MarketMover[]> {
    const params: Record<string, string | number> = { limit }
    if (assetType) params.asset_type = assetType
    return apiClient.get('/markets/trending', { params })
  },
}
