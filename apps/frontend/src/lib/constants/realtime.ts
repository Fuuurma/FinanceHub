/**
 * Real-Time Data Constants
 * WebSocket, chart, and order book configuration
 */

export const WS_CONFIG = {
  RECONNECT_DELAYS: [1000, 2000, 4000, 8000, 16000, 30000] as number[],
  MAX_RECONNECT_ATTEMPTS: 10,
  HEARTBEAT_INTERVAL: 30000,
  CONNECT_TIMEOUT: 10000,
  MESSAGE_BUFFER_SIZE: 50,
  TRADE_FEED_LIMIT: 20,
} as const

export const CHART_CONFIG = {
  BUFFER_SIZES: {
    '1m': 500,
    '5m': 300,
    '15m': 200,
    '30m': 200,
    '1h': 200,
    '4h': 100,
    '1d': 100,
    '1w': 50,
    '3m': 100,
    '6m': 50,
    '1M': 30,
    '1y': 20,
  } as const,
  DEFAULT_TIMEFRAME: '1h' as const,
  UPDATE_INTERVAL: 2000,
} as const

export const ORDERBOOK_CONFIG = {
  DEFAULT_DEPTH: 10,
  MAX_DEPTH: 100,
  DEPTH_OPTIONS: [10, 20, 50, 100] as const,
  UPDATE_DEBOUNCE_MS: 100,
} as const

export const TICKER_CONFIG = {
  SCROLL_SPEED: 30,
  PAUSE_ON_HOVER: true,
  FLASH_DURATION: 500,
  MAX_SYMBOLS: 50,
} as const

export const CONNECTION_STATES = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  ERROR: 'error',
} as const

export const CONNECTION_MESSAGES = {
  [CONNECTION_STATES.DISCONNECTED]: 'Disconnected from real-time data',
  [CONNECTION_STATES.CONNECTING]: 'Connecting to real-time data...',
  [CONNECTION_STATES.CONNECTED]: 'Connected to real-time data',
  [CONNECTION_STATES.ERROR]: 'Connection failed',
} as const

export type ConnectionState = typeof CONNECTION_STATES[keyof typeof CONNECTION_STATES]
export type ChartTimeframe = keyof typeof CHART_CONFIG.BUFFER_SIZES
export type OrderBookDepth = typeof ORDERBOOK_CONFIG.DEPTH_OPTIONS[number]
export type TradeFilter = 'all' | 'buys' | 'sells'

export interface ChartDataPoint {
  time: number | string
  price: number
  volume: number
  timestamp?: number | string
  open?: number
  high?: number
  low?: number
  close?: number
}
