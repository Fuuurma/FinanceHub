/**
 * Real-Time Data Store
 * Zustand store for WebSocket state and real-time data
 */

import { create } from 'zustand'
import type {
  RealTimePrice,
  Trade,
  OrderBook,
} from '@/lib/types/realtime'
import type { ConnectionState, ChartTimeframe, DataType } from '@/lib/constants/realtime'
import { getWebSocketClient } from '@/lib/api/websocket'
import { WS_CONFIG, CONNECTION_STATES, CHART_CONFIG } from '@/lib/constants/realtime'
import { apiClient } from '@/lib/api/client'
import type { SubscriptionRequest } from '@/lib/types/realtime'

interface RealTimeStore {
  connectionState: ConnectionState
  error: string | null
  subscribedSymbols: string[]
  prices: Record<string, RealTimePrice>
  trades: Record<string, Trade[]>
  orderBooks: Record<string, OrderBook>
  charts: Record<string, ChartTimeframe>
  
  connect: (token?: string) => Promise<void>
  disconnect: () => void
  subscribe: (symbols: string[], dataTypes: DataType[]) => void
  unsubscribe: (symbol: string, dataTypes?: DataType[]) => void
  subscribeSingle: (symbol: string, dataTypes: DataType[]) => void
  unsubscribeSingle: (symbol: string, dataTypes?: DataType[]) => void
  unsubscribeAll: () => void
  clearData: (symbol?: string) => void
  
  updatePrice: (symbol: string, price: RealTimePrice) => void
  addTrade: (symbol: string, trade: Trade) => void
  updateOrderBook: (symbol: string, orderBook: OrderBook) => void
  setChartTimeframe: (symbol: string, timeframe: ChartTimeframe) => void
  setError: (error: string | null) => void
  setConnectionState: (state: ConnectionState) => void
}

export const useRealtimeStore = create<RealTimeStore>((set, get) => ({
  connectionState: CONNECTION_STATES.DISCONNECTED,
  error: null,
  subscribedSymbols: [],
  prices: {},
  trades: {},
  orderBooks: {},
  charts: {},

  connect: async (token?: string) => {
    try {
      set({ connectionState: CONNECTION_STATES.CONNECTING, error: null })
      
      const wsClient = getWebSocketClient()
      
      wsClient.on('connection', ({ state, error }) => {
        set({ connectionState: state })
        
        if (state === CONNECTION_STATES.ERROR && error) {
          set({ error: error as string })
        }
      })
      
      wsClient.on('data', (message) => {
        if (message.data) {
          const { symbol, dataType, data } = message
          
          switch (dataType) {
            case 'price':
              if (symbol && data) {
                get().updatePrice(symbol, data)
              }
              break
            
            case 'trades':
              if (symbol && Array.isArray(data.trades)) {
                data.trades.forEach((trade: Trade) => {
                  get().addTrade(symbol, trade)
                })
              }
              break
            
            case 'orderbook':
              if (symbol && data) {
                get().updateOrderBook(symbol, data)
              }
              break
          }
        }
      })
      
      wsClient.on('error', (message) => {
        set({ error: message.error || 'WebSocket error' })
      })
      
      await wsClient.connect(token)
    } catch (error) {
      set({
        connectionState: CONNECTION_STATES.ERROR,
        error: error instanceof Error ? error.message : 'Failed to connect',
      })
    }
  },

  disconnect: () => {
    const wsClient = getWebSocketClient()
    wsClient.disconnect()
    
    set({
      connectionState: CONNECTION_STATES.DISCONNECTED,
      subscribedSymbols: [],
      error: null,
    })
  },

  subscribe: (symbols: string[], dataTypes: DataType[]) => {
    const wsClient = getWebSocketClient()
    
    if (wsClient.getConnectionState() !== CONNECTION_STATES.CONNECTED) {
      console.warn('Cannot subscribe: not connected')
      return
    }
    
    const request: SubscriptionRequest = {
      symbols,
      dataTypes,
    }
    
    wsClient.subscribe(request)
    
    set((state) => ({
      subscribedSymbols: [
        ...new Set([...state.subscribedSymbols, ...symbols]),
      ],
    }))
  },

  unsubscribe: (symbol: string, dataTypes?: DataType[]) => {
    const wsClient = getWebSocketClient()
    wsClient.unsubscribe(symbol, dataTypes || [])
    
    set((state) => ({
      subscribedSymbols: state.subscribedSymbols.filter((s) => s !== symbol),
    }))
  },

  subscribeSingle: (symbol: string, dataTypes: DataType[]) => {
    get().subscribe([symbol], dataTypes)
  },

  unsubscribeSingle: (symbol: string, dataTypes?: DataType[]) => {
    get().unsubscribe(symbol, dataTypes)
  },

  unsubscribeAll: () => {
    const wsClient = getWebSocketClient()
    wsClient.unsubscribeAll()
    
    set({ subscribedSymbols: [] })
  },

  clearData: (symbol?: string) => {
    if (symbol) {
      set((state) => {
        const newState: Partial<RealTimeStore> = {}
        
        if (state.prices[symbol]) {
          newState.prices = { ...state.prices }
          delete newState.prices[symbol]
        }
        
        if (state.trades[symbol]) {
          newState.trades = { ...state.trades }
          delete newState.trades[symbol]
        }
        
        if (state.orderBooks[symbol]) {
          newState.orderBooks = { ...state.orderBooks }
          delete newState.orderBooks[symbol]
        }
        
        if (state.charts[symbol]) {
          newState.charts = { ...state.charts }
          delete newState.charts[symbol]
        }
        
        return newState
      })
    } else {
      set({
        prices: {},
        trades: {},
        orderBooks: {},
        charts: {},
      })
    }
  },

  updatePrice: (symbol: string, price: RealTimePrice) => {
    set((state) => ({
      prices: {
        ...state.prices,
        [symbol]: price,
      },
    }))
  },

  addTrade: (symbol: string, trade: Trade) => {
    set((state) => {
      const symbolTrades = state.trades[symbol] || []
      const newTrades = [trade, ...symbolTrades].slice(0, WS_CONFIG.TRADE_FEED_LIMIT)
      
      return {
        trades: {
          ...state.trades,
          [symbol]: newTrades,
        },
      }
    })
  },

  updateOrderBook: (symbol: string, orderBook: OrderBook) => {
    set((state) => ({
      orderBooks: {
        ...state.orderBooks,
        [symbol]: orderBook,
      },
    }))
  },

  setChartTimeframe: (symbol: string, timeframe: ChartTimeframe) => {
    set((state) => ({
      charts: {
        ...state.charts,
        [symbol]: timeframe,
      },
    }))
  },

  setError: (error: string | null) => {
    set({ error })
  },

  setConnectionState: (state: ConnectionState) => {
    set({ connectionState: state })
  },
}))
