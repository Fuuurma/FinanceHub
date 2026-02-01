'use client'

import * as React from 'react'
import { getWebSocketClient } from '@/lib/api/websocket'
import { apiClient } from '@/lib/api/client'
import type { WebSocketMessage } from '@/lib/types/realtime'

interface Position {
  id: string
  symbol: string
  name: string
  quantity: number
  avg_price: number
  current_price: number
  market_value: number
  cost_basis: number
  profit_loss: number
  profit_loss_pct: number
}

interface Portfolio {
  cash_balance: number
  portfolio_value: number
  total_value: number
  total_return: number
  day_change: number
  day_change_pct: number
  positions: Position[]
}

interface PaperTradingState {
  portfolio: Portfolio | null
  positions: Position[]
  orders: Order[]
  isConnected: boolean
  isLoading: boolean
  error: string | null
}

interface Order {
  id: string
  symbol: string
  side: 'BUY' | 'SELL'
  type: 'MARKET' | 'LIMIT' | 'STOP'
  quantity: number
  price: number | null
  status: 'PENDING' | 'FILLED' | 'CANCELLED' | 'REJECTED'
  filled_price: number | null
  filled_at: string | null
  created_at: string
}

interface UsePaperTradingReturn extends PaperTradingState {
  refreshPortfolio: () => Promise<void>
  refreshPositions: () => Promise<void>
  executeOrder: (order: {
    symbol: string
    side: 'BUY' | 'SELL'
    type: 'MARKET' | 'LIMIT' | 'STOP'
    quantity: number
    price?: number
  }) => Promise<{ success: boolean; error?: string }>
  closePosition: (positionId: string) => Promise<{ success: boolean; error?: string }>
  connect: () => Promise<void>
  disconnect: () => void
}

export function usePaperTrading(): UsePaperTradingReturn {
  const [state, setState] = React.useState<PaperTradingState>({
    portfolio: null,
    positions: [],
    orders: [],
    isConnected: false,
    isLoading: true,
    error: null,
  })

  const wsClientRef = React.useRef<ReturnType<typeof getWebSocketClient> | null>(null)

  const fetchPortfolio = React.useCallback(async () => {
    try {
      const data = await apiClient.get<{ summary: Portfolio }>(
        '/paper-trading/account'
      )
      setState((prev) => ({
        ...prev,
        portfolio: data.summary,
        positions: data.summary.positions,
      }))
    } catch (error) {
      console.error('Failed to fetch portfolio:', error)
    }
  }, [])

  const fetchPositions = React.useCallback(async () => {
    try {
      const data = await apiClient.get<{ positions: Position[] }>(
        '/paper-trading/positions'
      )
      setState((prev) => ({
        ...prev,
        positions: data.positions,
      }))
    } catch (error) {
      console.error('Failed to fetch positions:', error)
    }
  }, [])

  const executeOrder = React.useCallback(
    async (order: {
      symbol: string
      side: 'BUY' | 'SELL'
      type: 'MARKET' | 'LIMIT' | 'STOP'
      quantity: number
      price?: number
    }) => {
      try {
        const endpoint =
          order.side === 'BUY' ? '/paper-trading/buy' : '/paper-trading/sell'
        const response = await apiClient.post(endpoint, {
          asset: order.symbol,
          quantity: order.quantity,
          ...(order.type !== 'MARKET' && { price: order.price }),
        })

        await fetchPortfolio()
        await fetchPositions()

        return { success: true }
      } catch (error: any) {
        return {
          success: false,
          error: error.message || 'Order execution failed',
        }
      }
    },
    [fetchPortfolio, fetchPositions]
  )

  const closePosition = React.useCallback(
    async (positionId: string) => {
      try {
        await apiClient.post(`/paper-trading/positions/${positionId}/close`)
        await fetchPortfolio()
        await fetchPositions()
        return { success: true }
      } catch (error: any) {
        return {
          success: false,
          error: error.message || 'Failed to close position',
        }
      }
    },
    [fetchPortfolio, fetchPositions]
  )

  const connect = React.useCallback(async () => {
    if (typeof window === 'undefined') return

    const wsClient = getWebSocketClient()
    wsClientRef.current = wsClient

    wsClient.on('connection', (data: any) => {
      setState((prev) => ({
        ...prev,
        isConnected: data.state === 2,
      }))
    })

    wsClient.on('data', (message: WebSocketMessage) => {
      const messageType = message.type as string
      if (messageType === 'paper_portfolio_update') {
        setState((prev) => ({
          ...prev,
          portfolio: message.data as Portfolio,
          positions: (message.data as Portfolio).positions,
        }))
      } else if (messageType === 'paper_position_update') {
        setState((prev) => ({
          ...prev,
          positions: message.data as Position[],
        }))
      }
    })

    try {
      await wsClient.connect()
      wsClient.subscribe({
        symbols: ['PAPER_PORTFOLIO'],
        dataTypes: ['portfolio' as any, 'positions' as any],
      })
    } catch (error) {
      console.error('WebSocket connection failed:', error)
    }
  }, [])

  const disconnect = React.useCallback(() => {
    if (wsClientRef.current) {
      wsClientRef.current.disconnect()
      wsClientRef.current = null
      setState((prev) => ({
        ...prev,
        isConnected: false,
      }))
    }
  }, [])

  React.useEffect(() => {
    setState((prev) => ({ ...prev, isLoading: true }))
    fetchPortfolio()
    fetchPositions()
    setTimeout(() => {
      setState((prev) => ({ ...prev, isLoading: false }))
    }, 500)
    connect()

    return () => {
      disconnect()
    }
  }, [fetchPortfolio, fetchPositions, connect, disconnect])

  return {
    ...state,
    refreshPortfolio: fetchPortfolio,
    refreshPositions: fetchPositions,
    executeOrder,
    closePosition,
    connect,
    disconnect,
  }
}
