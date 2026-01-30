/**
 * Advanced Analytics Types
 * Types for portfolio optimization, risk management, quantitative models, and backtesting
 */

// Portfolio Optimization
export interface OptimizationRequest {
  returns: number[][]
  risk_free_rate?: number
  method: 'max_sharpe' | 'min_variance' | 'risk_parity' | 'equal_weight'
}

export interface OptimizationResult {
  weights: { [symbol: string]: number }
  expected_return: number
  expected_volatility: number
  sharpe_ratio: number
  success: boolean
  message: string
  computed_in_ms?: number
}

export interface MeanVarianceRequest extends OptimizationRequest {
  target_return?: number
}

export interface BlackLittermanRequest {
  returns: number[][]
  risk_free_rate?: number
  market_caps: number[]
  tau?: number
  view_matrix?: number[][]
  view_picking?: number[][]
}

export interface RiskParityRequest {
  returns: number[][]
  risk_free_rate?: number
  max_iterations?: number
  tolerance?: number
}

export interface CVaROptimizationRequest {
  returns: number[][]
  risk_free_rate?: number
  confidence_level?: number
  n_simulations?: number
  target_return?: number
}

export interface EfficientFrontierRequest {
  returns: number[][]
  risk_free_rate?: number
  n_portfolios?: number
  method?: 'max_sharpe' | 'min_variance'
}

// Risk Management
export interface VaRRequest {
  returns: number[][]
  weights: number[]
  risk_free_rate?: number
  confidence_level?: number
  n_simulations?: number
}

export interface VaRResult {
  var_95: number
  var_99: number
  expected_shortfall_95: number
  expected_shortfall_99: number
  method?: string
  confidence_level: number
  n_scenarios?: number
}

export interface StressTestRequest {
  returns: number[][]
  weights: number[]
  risk_free_rate?: number
  scenarios: Array<{ [asset: string]: number }>
}

export interface StressTestResult {
  stress_scenarios: {
    [scenario_name: string]: {
      portfolio_return: number
      portfolio_value: number
      loss: number
    }
  }
  worst_case_scenario: string
  worst_case_loss: number
  computed_in_ms: number
}

export interface ComprehensiveRiskRequest {
  returns: number[][]
  weights: number[]
  risk_free_rate?: number
  confidence_level?: number
  n_simulations?: number
  stress_scenarios?: Array<{ [asset: string]: number }>
}

export interface ComprehensiveRiskResult {
  parametric_var: VaRResult
  historical_var: VaRResult
  monte_carlo_var: VaRResult
  expected_shortfall: VaRResult
  stress_test: StressTestResult
  risk_summary: {
    overall_risk_score: number
    recommendations: string[]
  }
}

// Quantitative Models
export interface ARIMARequest {
  data: number[]
  order_p?: number
  order_d?: number
  order_q?: number
  steps?: number
  confidence_level?: number
}

export interface ARIMAResult {
  forecast: number[]
  confidence_interval_lower: number[]
  confidence_interval_upper: number[]
  order: [number, number, number]
  aic: number
  bic: number
  compute_time_ms: number
}

export interface GARCHRequest {
  returns: number[]
  omega?: number
  alpha?: number
  beta?: number
  steps?: number
}

export interface GARCHResult {
  conditional_volatility: number[]
  forecast_volatility: number
  omega: number
  alpha: number
  beta: number
  total_volatility: number
  compute_time_ms: number
}

export interface KalmanFilterRequest {
  observations: number[]
  state_dim?: number
  process_noise?: number
  observation_noise?: number
}

export interface KalmanFilterResult {
  filtered_state: number[]
  filtered_covariance_diag: number[]
  predicted_state: number[]
  likelihood: number
  compute_time_ms: number
}

export interface HalfLifeRequest {
  prices: number[]
  lookback?: number
}

export interface HalfLifeResult {
  half_life: number
  hurst_exponent: number
  mean_reversion_strength: 'Strong' | 'Moderate' | 'Weak' | 'None'
  compute_time_ms: number
}

export interface HurstExponentRequest {
  data: number[]
  max_scale?: number
}

export interface HurstExponentResult {
  hurst_exponent: number
  trend_type: 'Mean-Reverting' | 'Random Walk' | 'Trending'
  interpretation: string
  compute_time_ms: number
}

// Backtesting
export interface BacktestRequest {
  prices: { [symbol: string]: number[] }
  weights: { [symbol: string]: number }
  initial_capital?: number
  strategy_name?: string
}

export interface BacktestResult {
  success: boolean
  data: {
    strategy_name: string
    total_return: number
    annualized_return: number
    sharpe_ratio: number
    max_drawdown: number
    win_rate: number
    equity_curve: number[]
    interpretation: string
  }
  fetched_at: string
}

export interface StrategyComparisonRequest {
  prices: { [symbol: string]: number[] }
  strategies: Array<{
    name: string
    weights: { [symbol: string]: number }
  }>
  initial_capital?: number
}

export interface StrategyComparisonResult {
  success: boolean
  data: {
    results: {
      [strategy_name: string]: {
        total_return: number
        sharpe_ratio: number
        max_drawdown: number
        win_rate: number
      }
    }
    best_by_sharpe: string
    best_by_return: string
    best_by_drawdown: string
  }
  fetched_at: string
}

export interface BacktestTrade {
  id: string
  symbol: string
  entry_date: string
  exit_date: string
  entry_price: number
  exit_price: number
  quantity: number
  pnl: number
  pnl_percent: number
  side: 'long' | 'short'
  status: 'closed' | 'open'
}

export interface MonthlyReturn {
  month: string
  year: number
  return: number
  benchmark_return?: number
}

export interface RiskMetricsDetail {
  volatility: number
  beta: number
  alpha: number
  sortino_ratio: number
  calmar_ratio: number
  var_95: number
  cvar_95: number
  recovery_time: number | null
}

export interface BacktestResultEnhanced extends BacktestResult {
  data: BacktestResult['data'] & {
    trades?: BacktestTrade[]
    monthly_returns?: MonthlyReturn[]
    risk_metrics?: RiskMetricsDetail
    benchmark_comparison?: {
      benchmark_return: number
      alpha: number
      beta: number
      tracking_error: number
    }
    total_trades: number
    profitable_trades: number
    losing_trades: number
    avg_win: number
    avg_loss: number
    profit_factor: number
    consecutive_wins: number
    consecutive_losses: number
  }
}

// Volatility Regimes
export interface VolatilityRegimePoint {
  index: number
  return: number
  volatility: number
  regime: 'low' | 'normal' | 'high'
}

export interface VolatilityRegimesResponse {
  regimes: VolatilityRegimePoint[]
  summary: {
    low: number
    normal: number
    high: number
  }
  current_regime: 'low' | 'normal' | 'high'
  thresholds: {
    low: number
    high: number
  }
  overall_volatility: number
}
