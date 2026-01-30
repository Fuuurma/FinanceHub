// Technical Indicator Constants
export const INDICATOR_CATEGORIES = {
  trend: {
    label: 'Trend Indicators',
    indicators: ['sma', 'ema', 'wma', 'ichimoku', 'parabolic_sar'],
  },
  momentum: {
    label: 'Momentum Indicators',
    indicators: ['rsi', 'stochastic', 'cci', 'williams_r', 'mfi'],
  },
  volatility: {
    label: 'Volatility Indicators',
    indicators: ['bollinger', 'atr'],
  },
  volume: {
    label: 'Volume Indicators',
    indicators: ['obv', 'ad', 'mfi'],
  },
} as const

export const INDICATOR_LABELS: Record<string, string> = {
  sma: 'Simple Moving Average',
  ema: 'Exponential Moving Average',
  wma: 'Weighted Moving Average',
  bollinger: 'Bollinger Bands',
  rsi: 'Relative Strength Index',
  macd: 'Moving Average Convergence Divergence',
  stochastic: 'Stochastic Oscillator',
  cci: 'Commodity Channel Index',
  williams_r: 'Williams %R',
  atr: 'Average True Range',
  obv: 'On-Balance Volume',
  mfi: 'Money Flow Index',
  ad: 'Accumulation/Distribution Line',
  ichimoku: 'Ichimoku Cloud',
  parabolic_sar: 'Parabolic SAR',
} as const

export const INDICATOR_COLORS = {
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  tertiary: '#06b6d4',
  quaternary: '#10b981',
  bullish: '#22c55e',
  bearish: '#ef4444',
  neutral: '#f59e0b',
} as const

export const RSI_LEVELS = {
  overbought: 70,
  oversold: 30,
} as const

export const MACD_SIGNALS = {
  bullish: 'crossover',
  bearish: 'crossunder',
} as const

export const BOLLINGER_BANDS_DEFAULTS = {
  period: 20,
  stdDev: 2,
  upperMultiplier: 2,
  lowerMultiplier: 2,
} as const

export const TIMEFRAMES = [
  { value: '1m', label: '1 Minute', seconds: 60 },
  { value: '5m', label: '5 Minutes', seconds: 300 },
  { value: '15m', label: '15 Minutes', seconds: 900 },
  { value: '1h', label: '1 Hour', seconds: 3600 },
  { value: '4h', label: '4 Hours', seconds: 14400 },
  { value: '1d', label: '1 Day', seconds: 86400 },
  { value: '1w', label: '1 Week', seconds: 604800 },
] as const

export const CHART_UPDATE_INTERVAL = 2000 // ms
export const INDICATOR_BUFFER_SIZE = 200 // data points

// Drawing tool types
export const DRAWING_TOOLS = [
  { type: 'horizontal_line', label: 'Horizontal Line', icon: 'minus' },
  { type: 'vertical_line', label: 'Vertical Line', icon: 'minus' },
  { type: 'trend_line', label: 'Trend Line', icon: 'trending-up' },
  { type: 'support_resistance', label: 'Support/Resistance', icon: 'minus' },
  { type: 'fibonacci', label: 'Fibonacci Retracement', icon: 'activity' },
  { type: 'rectangle', label: 'Rectangle', icon: 'square' },
  { type: 'text', label: 'Text Annotation', icon: 'type' },
] as const

export const FIBONACCI_LEVELS = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1] as const

export const DEFAULT_INDICATORS: string[] = ['sma', 'rsi', 'macd']
