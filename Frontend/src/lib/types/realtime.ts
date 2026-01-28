/**
 * Real-Time Data Types
 * WebSocket message types and data structures
 */

import type { ConnectionState, ChartTimeframe, OrderBookDepth, TradeFilter } from '@/lib/constants/realtime'

export interface RealTimePrice {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: number
  timestamp: string
  source: string
  high52w?: number
  low52w?: number
  open?: number
  close?: number
}

export interface Trade {
  tradeId: string
  symbol: string
  price: number
  quantity: number
  tradeType: string
  timestamp: string
  exchange: string
  isBuy: boolean
  maker: boolean
}

export interface OrderBookLevel {
  price: number
  volume: number
  totalSize: number
  isSpread: boolean
  spread?: number
  timestamp: string
}

export interface OrderBook {
  symbol: string
  levels: OrderBookLevel[]
  midPrice?: number
  spread: number
  depth: number
  timestamp: string
  source: string
}

export interface SubscriptionRequest {
  symbols: string[]
  dataTypes: DataType[]
}

export type DataType = 'price' | 'trades' | 'orderbook'

export interface WebSocketMessage {
  type: MessageType
  symbol?: string
  dataType?: DataType
  data?: any
  error?: string
  timestamp: string
}

export type MessageType =
  | 'subscribe'
  | 'unsubscribe'
  | 'data_update'
  | 'initial_data'
  | 'subscription_ack'
  | 'unsubscribe_ack'
  | 'ping'
  | 'pong'
  | 'error'

export interface ChartDataPoint {
  time: string
  price: number
  volume?: number
}

export interface ConnectionStatus {
  connected: boolean
  lastHeartbeat: string
  subscriptions: string[]
  connectionTime: string
  pingMs: number
}

export interface WebSocketConfig {
  url: string
  reconnectDelays: number[]
  maxReconnectAttempts: number
  heartbeatInterval: number
  connectTimeout: number
}

export interface SubscriptionResponse {
  type: 'subscription_ack' | 'unsubscribe_ack' | 'error'
  subscriptions: string[]
  timestamp: string
  error?: string
}
