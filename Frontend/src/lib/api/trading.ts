import { apiClient } from './client'
import type {
  Order,
  OrderCreateInput,
  Position,
  AccountSummary,
  PositionSummary,
  Trade,
  TradeFilters,
  TradeStats,
} from '../types/trading'

export const tradingApi = {
  orders: {
    list: async (params?: {
      status?: string
      portfolio_id?: string
      asset_id?: string
      limit?: number
      offset?: number
    }) => {
      const queryParams = new URLSearchParams()
      if (params?.status) queryParams.append('status', params.status)
      if (params?.portfolio_id) queryParams.append('portfolio_id', params.portfolio_id)
      if (params?.asset_id) queryParams.append('asset_id', params.asset_id)
      if (params?.limit) queryParams.append('limit', params.limit.toString())
      if (params?.offset) queryParams.append('offset', params.offset.toString())

      return apiClient.get<Order[]>(`/trading/orders?${queryParams.toString()}`)
    },

    get: async (orderId: string) => {
      return apiClient.get<Order>(`/trading/orders/${orderId}`)
    },

    create: async (data: OrderCreateInput) => {
      return apiClient.post<Order>('/trading/orders', data)
    },

    update: async (orderId: string, data: Partial<OrderCreateInput>) => {
      return apiClient.put<Order>(`/trading/orders/${orderId}`, data)
    },

    cancel: async (orderId: string) => {
      return apiClient.delete<{ success: boolean; message: string }>(`/trading/orders/${orderId}`)
    },
  },

  positions: {
    list: async (params?: {
      portfolio_id?: string
      is_open?: boolean
      limit?: number
      offset?: number
    }) => {
      const queryParams = new URLSearchParams()
      if (params?.portfolio_id) queryParams.append('portfolio_id', params.portfolio_id)
      if (params?.is_open !== undefined) queryParams.append('is_open', params.is_open.toString())
      if (params?.limit) queryParams.append('limit', params.limit.toString())
      if (params?.offset) queryParams.append('offset', params.offset.toString())

      return apiClient.get<Position[]>(`/trading/positions?${queryParams.toString()}`)
    },

    get: async (positionId: string) => {
      return apiClient.get<Position>(`/trading/positions/${positionId}`)
    },

    close: async (positionId: string) => {
      return apiClient.post<{ success: boolean; message: string; realized_pnl: number; closed_price: number }>(`/trading/positions/${positionId}/close`)
    },
  },

  account: {
    getSummary: async () => {
      return apiClient.get<AccountSummary>('/trading/account/summary')
    },
  },

  positionsSummary: {
    get: async (params?: { portfolio_id?: string }) => {
      const queryParams = new URLSearchParams()
      if (params?.portfolio_id) queryParams.append('portfolio_id', params.portfolio_id)

      return apiClient.get<PositionSummary>(`/trading/positions/summary?${queryParams.toString()}`)
    },
  },

  trades: {
    list: async (params?: TradeFilters & { limit?: number; offset?: number }) => {
      const queryParams = new URLSearchParams()
      if (params?.portfolio_id) queryParams.append('portfolio_id', params.portfolio_id)
      if (params?.asset_id) queryParams.append('asset_id', params.asset_id)
      if (params?.asset_symbol) queryParams.append('asset_symbol', params.asset_symbol)
      if (params?.side) queryParams.append('side', params.side)
      if (params?.start_date) queryParams.append('start_date', params.start_date)
      if (params?.end_date) queryParams.append('end_date', params.end_date)
      if (params?.min_value) queryParams.append('min_value', params.min_value.toString())
      if (params?.max_value) queryParams.append('max_value', params.max_value.toString())
      if (params?.limit) queryParams.append('limit', params.limit.toString())
      if (params?.offset) queryParams.append('offset', params.offset.toString())

      return apiClient.get<Trade[]>(`/trading/trades?${queryParams.toString()}`)
    },

    get: async (tradeId: string) => {
      return apiClient.get<Trade>(`/trading/trades/${tradeId}`)
    },

    getStats: async (params?: { portfolio_id?: string; start_date?: string; end_date?: string }) => {
      const queryParams = new URLSearchParams()
      if (params?.portfolio_id) queryParams.append('portfolio_id', params.portfolio_id)
      if (params?.start_date) queryParams.append('start_date', params.start_date)
      if (params?.end_date) queryParams.append('end_date', params.end_date)

      return apiClient.get<TradeStats>(`/trading/trades/stats?${queryParams.toString()}`)
    },
  },
}
