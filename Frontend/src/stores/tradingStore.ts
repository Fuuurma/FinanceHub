import { create } from 'zustand'
import type { AccountSummary, Order, Position } from '@/lib/types/trading'

interface TradingState {
  orders: Order[]
  positions: Position[]
  accountSummary: AccountSummary | null
  loading: {
    orders: boolean
    positions: boolean
    account: boolean
  }
  error: string | null

  fetchOrders: () => Promise<void>
  createOrder: (data: any) => Promise<void>
  updateOrder: (orderId: string, data: any) => Promise<void>
  cancelOrder: (orderId: string) => Promise<void>
  fetchPositions: () => Promise<void>
  closePosition: (positionId: string) => Promise<void>
  fetchAccountSummary: () => Promise<void>
  clearError: () => void
}

export const useTradingStore = create<TradingState>((set, get) => ({
  orders: [],
  positions: [],
  accountSummary: null,
  loading: {
    orders: false,
    positions: false,
    account: false,
  },
  error: null,

  fetchOrders: async () => {
    const state = get()
    set({ loading: { ...state.loading, orders: true }, error: null })
    try {
      const { tradingApi } = await import('@/lib/api/trading')
      const orders = await tradingApi.orders.list({ limit: 100 })
      set({ orders, loading: { ...state.loading, orders: false } })
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch orders', loading: { ...state.loading, orders: false } })
    }
  },

  createOrder: async (data) => {
    const state = get()
    set({ loading: { ...state.loading, orders: true }, error: null })
    try {
      const { tradingApi } = await import('@/lib/api/trading')
      const order = await tradingApi.orders.create(data)
      set({ orders: [order, ...state.orders], loading: { ...state.loading, orders: false } })
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to create order', loading: { ...state.loading, orders: false } })
      throw err
    }
  },

  updateOrder: async (orderId, data) => {
    const state = get()
    set({ loading: { ...state.loading, orders: true }, error: null })
    try {
      const { tradingApi } = await import('@/lib/api/trading')
      const updatedOrder = await tradingApi.orders.update(orderId, data)
      set({
        orders: state.orders.map((o) => (o.id === orderId ? updatedOrder : o)),
        loading: { ...state.loading, orders: false },
      })
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to update order', loading: { ...state.loading, orders: false } })
      throw err
    }
  },

  cancelOrder: async (orderId) => {
    const state = get()
    set({ loading: { ...state.loading, orders: true }, error: null })
    try {
      const { tradingApi } = await import('@/lib/api/trading')
      await tradingApi.orders.cancel(orderId)
      set({
        orders: state.orders.map((o) =>
          o.id === orderId ? { ...o, status: 'cancelled' } : o
        ),
        loading: { ...state.loading, orders: false },
      })
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to cancel order', loading: { ...state.loading, orders: false } })
      throw err
    }
  },

  fetchPositions: async () => {
    const state = get()
    set({ loading: { ...state.loading, positions: true }, error: null })
    try {
      const { tradingApi } = await import('@/lib/api/trading')
      const positions = await tradingApi.positions.list({ limit: 100 })
      set({ positions, loading: { ...state.loading, positions: false } })
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch positions', loading: { ...state.loading, positions: false } })
    }
  },

  closePosition: async (positionId) => {
    const state = get()
    set({ loading: { ...state.loading, positions: true }, error: null })
    try {
      const { tradingApi } = await import('@/lib/api/trading')
      await tradingApi.positions.close(positionId)
      await get().fetchPositions()
      set({ loading: { ...state.loading, positions: false } })
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to close position', loading: { ...state.loading, positions: false } })
      throw err
    }
  },

  fetchAccountSummary: async () => {
    const state = get()
    set({ loading: { ...state.loading, account: true }, error: null })
    try {
      const { tradingApi } = await import('@/lib/api/trading')
      const summary = await tradingApi.account.getSummary()
      set({ accountSummary: summary, loading: { ...state.loading, account: false } })
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to fetch account summary', loading: { ...state.loading, account: false } })
    }
  },

  clearError: () => set({ error: null }),
}))
