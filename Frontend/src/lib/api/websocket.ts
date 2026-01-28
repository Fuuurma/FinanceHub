/**
 * WebSocket Client
 * Manages WebSocket connections with auto-reconnection and event emission
 */

import type {
  WebSocketMessage,
  SubscriptionRequest,
  WebSocketConfig,
} from '@lib/types/realtime'
import type { ConnectionState } from '@lib/constants/realtime'
import { WS_CONFIG, CONNECTION_STATES } from '@lib/constants/realtime'

type EventHandler = (data: any) => void

class WebSocketClient {
  private ws: WebSocket | null = null
  private config: WebSocketConfig
  private connectionState: ConnectionState = CONNECTION_STATES.DISCONNECTED
  private reconnectAttempts = 0
  private reconnectTimeout: NodeJS.Timeout | null = null
  private heartbeatInterval: NodeJS.Timeout | null = null
  private connectTimeout: NodeJS.Timeout | null = null
  private eventHandlers: Map<string, Set<EventHandler>> = new Map()
  private subscriptions: Set<string> = new Set()
  private lastPongTime: number = Date.now()

  constructor(config: WebSocketConfig) {
    this.config = config
  }

  connect(token?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.connectionState === CONNECTION_STATES.CONNECTED) {
        resolve()
        return
      }

      if (this.connectionState === CONNECTION_STATES.CONNECTING) {
        reject(new Error('Already connecting'))
        return
      }

      this.setConnectionState(CONNECTION_STATES.CONNECTING)
      this.clearTimeouts()

      let wsUrl = this.config.url
      if (token) {
        const separator = wsUrl.includes('?') ? '&' : '?'
        wsUrl = `${wsUrl}${separator}token=${token}`
      }

      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        this.clearTimeouts()
        this.reconnectAttempts = 0
        this.setConnectionState(CONNECTION_STATES.CONNECTED)
        this.startHeartbeat()
        
        this.emit('connection', { state: CONNECTION_STATES.CONNECTED })
        resolve()
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onclose = (event) => {
        this.handleClose(event)
      }

      this.ws.onerror = (error) => {
        this.setConnectionState(CONNECTION_STATES.ERROR)
        this.emit('connection', { state: CONNECTION_STATES.ERROR, error })
        reject(new Error('WebSocket connection failed'))
      }

      this.connectTimeout = setTimeout(() => {
        if (this.connectionState === CONNECTION_STATES.CONNECTING) {
          this.ws?.close()
          reject(new Error('Connection timeout'))
        }
      }, this.config.connectTimeout)
    })
  }

  disconnect(): void {
    this.clearTimeouts()
    this.subscriptions.clear()
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting')
      this.ws = null
    }
    
    this.setConnectionState(CONNECTION_STATES.DISCONNECTED)
    this.emit('connection', { state: CONNECTION_STATES.DISCONNECTED })
  }

  subscribe(request: SubscriptionRequest): void {
    if (this.connectionState !== CONNECTION_STATES.CONNECTED) {
      console.warn('Cannot subscribe: not connected')
      return
    }

    request.symbols.forEach((symbol) => {
      request.dataTypes.forEach((dataType) => {
        const subscriptionKey = `${symbol}:${dataType}`
        this.subscriptions.add(subscriptionKey)
        
        const message: WebSocketMessage = {
          type: 'subscribe',
          symbol,
          dataType: dataType as any,
          timestamp: new Date().toISOString(),
        }
        
        this.sendMessage(message)
      })
    })
  }

  unsubscribe(symbol: string, dataTypes: string[] = []): void {
    if (this.connectionState !== CONNECTION_STATES.CONNECTED) {
      return
    }

    if (dataTypes.length === 0) {
      Array.from(this.subscriptions).forEach((sub) => {
        if (sub.startsWith(`${symbol}:`)) {
          this.subscriptions.delete(sub)
        }
      })
    } else {
      dataTypes.forEach((dataType) => {
        const subscriptionKey = `${symbol}:${dataType}`
        this.subscriptions.delete(subscriptionKey)
        
        const message: WebSocketMessage = {
          type: 'unsubscribe',
          symbol,
          dataType: dataType as any,
          timestamp: new Date().toISOString(),
        }
        
        this.sendMessage(message)
      })
    }
  }

  unsubscribeAll(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return
    }

    const symbols: string[] = []
    Array.from(this.subscriptions).forEach((s) => {
      const symbol = s.split(':')[0]
      symbols.push(symbol)
    })
    const uniqueSymbols = [...new Set(symbols)]

    uniqueSymbols.forEach((symbol) => {
      this.unsubscribe(symbol)
    })
    
    this.subscriptions.clear()
  }

  on(event: string, handler: EventHandler): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set())
    }
    this.eventHandlers.get(event)!.add(handler)
  }

  off(event: string, handler: EventHandler): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.delete(handler)
      if (handlers.size === 0) {
        this.eventHandlers.delete(event)
      }
    }
  }

  getConnectionState(): ConnectionState {
    return this.connectionState
  }

  getPingMs(): number {
    return Date.now() - this.lastPongTime
  }

  private sendMessage(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'data_update':
      case 'initial_data':
        this.emit('data', message)
        break
      
      case 'subscription_ack':
        this.emit('subscription', message)
        break
      
      case 'unsubscribe_ack':
        this.emit('unsubscription', message)
        break
      
      case 'pong':
        this.lastPongTime = Date.now()
        break
      
      case 'error':
        console.error('WebSocket error:', message.error)
        this.emit('error', message)
        break
    }
  }

  private handleClose(event: CloseEvent): void {
    this.clearTimeouts()
    this.setConnectionState(CONNECTION_STATES.DISCONNECTED)

    if (this.reconnectAttempts < this.config.maxReconnectAttempts) {
      this.scheduleReconnect()
    } else {
      this.emit('connection', {
        state: CONNECTION_STATES.ERROR,
        error: 'Max reconnect attempts reached',
      })
    }
  }

  private scheduleReconnect(): void {
    const delay = this.config.reconnectDelays[
      Math.min(this.reconnectAttempts, this.config.reconnectDelays.length - 1)
    ]

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++
      this.setConnectionState(CONNECTION_STATES.CONNECTING)
      this.emit('connection', { state: CONNECTION_STATES.CONNECTING })
      this.connect()
    }, delay)
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.sendMessage({
          type: 'ping',
          timestamp: new Date().toISOString(),
        })
      }
    }, this.config.heartbeatInterval)
  }

  private clearTimeouts(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    
    if (this.connectTimeout) {
      clearTimeout(this.connectTimeout)
      this.connectTimeout = null
    }
    
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  private setConnectionState(state: ConnectionState): void {
    this.connectionState = state
  }

  private emit(event: string, data: any): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in ${event} handler:`, error)
        }
      })
    }
  }
}

let wsClientInstance: WebSocketClient | null = null

export function getWebSocketClient(): WebSocketClient {
  if (!wsClientInstance) {
    const config: WebSocketConfig = {
      url: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/realtime/',
      reconnectDelays: WS_CONFIG.RECONNECT_DELAYS,
      maxReconnectAttempts: WS_CONFIG.MAX_RECONNECT_ATTEMPTS,
      heartbeatInterval: WS_CONFIG.HEARTBEAT_INTERVAL,
      connectTimeout: WS_CONFIG.CONNECT_TIMEOUT,
    }
    
    wsClientInstance = new WebSocketClient(config)
  }
  
  return wsClientInstance
}

export function resetWebSocketClient(): void {
  if (wsClientInstance) {
    wsClientInstance.disconnect()
    wsClientInstance = null
  }
}
