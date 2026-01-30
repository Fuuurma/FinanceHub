/**
 * Advanced Analytics API Client
 * Client for advanced analytics endpoints - portfolio optimization, risk management, quantitative models, backtesting
 */

import { apiClient } from './client'
import type {
  OptimizationRequest,
  OptimizationResult,
  MeanVarianceRequest,
  BlackLittermanRequest,
  RiskParityRequest,
  CVaROptimizationRequest,
  EfficientFrontierRequest,
  VaRRequest,
  VaRResult,
  StressTestRequest,
  StressTestResult,
  ComprehensiveRiskRequest,
  ComprehensiveRiskResult,
  ARIMARequest,
  ARIMAResult,
  GARCHRequest,
  GARCHResult,
  KalmanFilterRequest,
  KalmanFilterResult,
  HalfLifeRequest,
  HalfLifeResult,
  HurstExponentRequest,
  HurstExponentResult,
  BacktestRequest,
  BacktestResult,
  StrategyComparisonRequest,
  StrategyComparisonResult,
} from '@/lib/types/analytics'

export const analyticsApi = {
  // Portfolio Optimization
  optimizePortfolio: (data: OptimizationRequest) =>
    apiClient.post<OptimizationResult>('/optimization/optimize', data),

  getMeanVariance: (data: MeanVarianceRequest) =>
    apiClient.post<OptimizationResult>('/advanced-portfolio/mean-variance', data),

  getBlackLitterman: (data: BlackLittermanRequest) =>
    apiClient.post<OptimizationResult>('/advanced-portfolio/black-litterman', data),

  getRiskParity: (data: RiskParityRequest) =>
    apiClient.post<OptimizationResult>('/advanced-portfolio/risk-parity', data),

  getCVaROptimization: (data: CVaROptimizationRequest) =>
    apiClient.post<OptimizationResult>('/advanced-portfolio/cvar-optimization', data),

  getEfficientFrontier: (data: EfficientFrontierRequest) =>
    apiClient.post<any>('/advanced-portfolio/efficient-frontier', data),

  // Risk Management
  calculateVaR: (data: VaRRequest) =>
    apiClient.post<VaRResult>('/advanced-risk/var', data),

  getHistoricalVaR: (returns: number[][], weights: number[], confidence_level = 0.95) =>
    apiClient.post<VaRResult>('/advanced-risk/var-historical', {
      returns,
      weights,
      confidence_level
    }),

  runStressTest: (data: StressTestRequest) =>
    apiClient.post<StressTestResult>('/advanced-risk/stress-test', data),

  getFactorStressTest: (returns: number[][], weights: number[]) =>
    apiClient.post<any>('/advanced-risk/factor-stress-test', {
      returns, weights
    }),

  getComprehensiveRisk: (data: ComprehensiveRiskRequest) =>
    apiClient.post<ComprehensiveRiskResult>('/advanced-risk/comprehensive-risk-analysis', data),

  // Quantitative Models
  forecastARIMA: (data: ARIMARequest) =>
    apiClient.post<ARIMAResult>('/quantitative/arima-forecast', data),

  forecastGARCH: (data: GARCHRequest) =>
    apiClient.post<GARCHResult>('/quantitative/garch-volatility', data),

  getKalmanFilter: (data: KalmanFilterRequest) =>
    apiClient.post<KalmanFilterResult>('/quantitative/kalman-filter', data),

  getHalfLife: (prices: number[], lookback?: number) =>
    apiClient.post<HalfLifeResult>('/quantitative/half-life', {
      prices,
      lookback
    }),

  getHurstExponent: (data: number[], max_scale = 10) =>
    apiClient.post<HurstExponentResult>('/quantitative/hurst-exponent', {
      data,
      max_scale
    }),

  // Backtesting
  backtestStrategy: (data: BacktestRequest) =>
    apiClient.post<BacktestResult>('/optimization/backtest', data),

  compareStrategies: (data: StrategyComparisonRequest) =>
    apiClient.post<StrategyComparisonResult>('/optimization/compare', data),
}
