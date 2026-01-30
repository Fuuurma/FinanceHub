/**
 * Markets API
 * All market-related API calls
 */

import { apiClient } from './client'
import type {
  MarketOverview,
  MarketMover,
  SectorPerformance,
  MarketIndex,
  MoverType,
  RealTimePriceUpdate,
  BatchPriceUpdateRequest,
  BatchPriceUpdatesResponse,
  RecentTradesRequest,
  RecentTradesResponse,
  OrderBookResponse,
  WebSocketConnectionInfo,
} from '@/lib/types'

const MARKETS_API = '/markets'

export const marketsApi = {
  getOverview(): Promise<MarketOverview> {
    return apiClient.get(`${MARKETS_API}/overview`)
  },

  getMovers(type: MoverType = 'gainers', limit: number = 10): Promise<MarketMover[]> {
    return apiClient.get(`${MARKETS_API}/movers`, {
      params: { type, limit },
    })
  },

  getSectors(): Promise<SectorPerformance[]> {
    return apiClient.get(`${MARKETS_API}/sectors`)
  },

  getIndices(): Promise<MarketIndex[]> {
    return apiClient.get(`${MARKETS_API}/indices`)
  },

  getTrending(assetType?: string, limit: number = 10): Promise<MarketMover[]> {
    const params: Record<string, string | number> = { limit }
    if (assetType) params.asset_type = assetType
    return apiClient.get(`${MARKETS_API}/trending`, { params })
  },

  // ================= REAL-TIME DATA ENDPOINTS (I5) =================

  getRealTimePrice(symbol: string, source: string = 'market'): Promise<RealTimePriceUpdate> {
    return apiClient.get(`${MARKETS_API}/price/${symbol}`, {
      params: { source },
    })
  },

  getBatchPrices(request: BatchPriceUpdateRequest): Promise<BatchPriceUpdatesResponse> {
    return apiClient.post(`${MARKETS_API}/prices/batch`, request)
  },

  getRecentTrades(request: RecentTradesRequest): Promise<RecentTradesResponse> {
    const params: Record<string, string | number> = { limit: request.limit || 20 }
    if (request.include_makers !== undefined) params.include_makers = Number(request.include_makers)
    return apiClient.get(`${MARKETS_API}/trades/${request.symbol}`, { params })
  },

  getOrderBook(symbol: string, depth: number = 10): Promise<OrderBookResponse> {
    return apiClient.get(`${MARKETS_API}/orderbook/${symbol}`, {
      params: { depth },
    })
  },

  getWebSocketConnectionInfo(userId?: string): Promise<WebSocketConnectionInfo> {
    const params = userId ? { user_id: userId } : undefined
    return apiClient.get(`${MARKETS_API}/connection-info`, params ? { params } : undefined)
  },
}
