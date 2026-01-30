// Technical Indicator Types
export type IndicatorType =
  | 'sma'     // Simple Moving Average
  | 'ema'     // Exponential Moving Average
  | 'wma'     // Weighted Moving Average
  | 'bollinger' // Bollinger Bands
  | 'rsi'     // Relative Strength Index
  | 'macd'    // Moving Average Convergence Divergence
  | 'stochastic' // Stochastic Oscillator
  | 'cci'     // Commodity Channel Index
  | 'williams_r' // Williams %R
  | 'atr'     // Average True Range
  | 'obv'     // On-Balance Volume
  | 'mfi'     // Money Flow Index
  | 'ad'      // Accumulation/Distribution Line
  | 'ichimoku' // Ichimoku Cloud
  | 'parabolic_sar' // Parabolic SAR

export type DrawingType =
  | 'horizontal_line'
  | 'vertical_line'
  | 'trend_line'
  | 'fibonacci'
  | 'rectangle'
  | 'text'

export type TimeFrame = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M' | '3m' | '6m' | '1y'
export type TimeInterval = TimeFrame

export interface IndicatorConfig {
  type: IndicatorType
  params: Record<string, number>
  visible: boolean
  color: string
  secondary_yaxis?: boolean
}

export interface IndicatorData {
  indicator: IndicatorType
  symbol: string
  timeframe: TimeFrame
  values: Array<{
    timestamp: string
    value: number
    signal?: 'buy' | 'sell' | 'neutral'
  }>
  params: Record<string, number>
  calculated_at: string
}

export interface ChartDataPoint {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface TechnicalAnalysis {
  symbol: string
  timeframe: TimeFrame
  trend: 'bullish' | 'bearish' | 'neutral'
  strength: number // 0-100
  support_levels: number[]
  resistance_levels: number[]
  indicators: {
    [key: string]: IndicatorData
  }
  signals: TradingSignal[]
  analyzed_at: string
}

export interface TradingSignal {
  type: 'buy' | 'sell' | 'hold'
  indicator: string
  strength: 'weak' | 'moderate' | 'strong'
  price: number
  timestamp: string
  description: string
}

// Indicator-specific data types
export interface MovingAverageData {
  symbol: string
  timeframe: TimeFrame
  ma_type: 'sma' | 'ema' | 'wma'
  period: number
  values: Array<{
    timestamp: string
    ma: number
    price: number
  }>
}

export interface BollingerBandsData {
  symbol: string
  timeframe: TimeFrame
  period: number
  standard_deviation: number
  values: Array<{
    timestamp: string
    upper: number
    middle: number
    lower: number
    price: number
    bandwidth: number
    percent_b: number
  }>
}

export interface MACDData {
  symbol: string
  timeframe: TimeFrame
  fast_period: number
  slow_period: number
  signal_period: number
  values: Array<{
    timestamp: string
    macd: number
    signal: number
    histogram: number
  }>
}

export interface StochasticData {
  symbol: string
  timeframe: TimeFrame
  k_period: number
  d_period: number
  values: Array<{
    timestamp: string
    k: number
    d: number
    signal: string
  }>
}

export interface RSIData {
  symbol: string
  timeframe: TimeFrame
  period: number
  values: Array<{
    timestamp: string
    rsi: number
    signal: string
  }>
}

// Default indicator configurations
export const DEFAULT_INDICATORS: Record<IndicatorType, IndicatorConfig> = {
  sma: {
    type: 'sma',
    params: { period: 20 },
    visible: true,
    color: '#3b82f6',
  },
  ema: {
    type: 'ema',
    params: { period: 12 },
    visible: true,
    color: '#8b5cf6',
  },
  wma: {
    type: 'wma',
    params: { period: 10 },
    visible: false,
    color: '#06b6d4',
  },
  bollinger: {
    type: 'bollinger',
    params: { period: 20, stdDev: 2 },
    visible: false,
    color: '#f59e0b',
  },
  rsi: {
    type: 'rsi',
    params: { period: 14 },
    visible: false,
    color: '#ef4444',
    secondary_yaxis: true,
  },
  macd: {
    type: 'macd',
    params: { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 },
    visible: false,
    color: '#10b981',
    secondary_yaxis: true,
  },
  stochastic: {
    type: 'stochastic',
    params: { kPeriod: 14, dPeriod: 3 },
    visible: false,
    color: '#f97316',
    secondary_yaxis: true,
  },
  cci: {
    type: 'cci',
    params: { period: 20 },
    visible: false,
    color: '#06b6d4',
    secondary_yaxis: true,
  },
  williams_r: {
    type: 'williams_r',
    params: { period: 14 },
    visible: false,
    color: '#eab308',
    secondary_yaxis: true,
  },
  atr: {
    type: 'atr',
    params: { period: 14 },
    visible: false,
    color: '#a855f7',
    secondary_yaxis: true,
  },
  obv: {
    type: 'obv',
    params: {},
    visible: false,
    color: '#22c55e',
    secondary_yaxis: true,
  },
  mfi: {
    type: 'mfi',
    params: { period: 14 },
    visible: false,
    color: '#ec4899',
    secondary_yaxis: true,
  },
  ad: {
    type: 'ad',
    params: {},
    visible: false,
    color: '#14b8a6',
    secondary_yaxis: true,
  },
  ichimoku: {
    type: 'ichimoku',
    params: {
      tenkanPeriod: 9,
      kijunPeriod: 26,
      senkouSpanBPeriod: 52,
    },
    visible: false,
    color: '#6366f1',
  },
  parabolic_sar: {
    type: 'parabolic_sar',
    params: { step: 0.02, max: 0.2 },
    visible: false,
    color: '#f43f5e',
  },
}
