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
    apiClient.post<OptimizationResult>('/api/v1/optimization/optimize', data),

  getMeanVariance: (data: MeanVarianceRequest) =>
    apiClient.post<OptimizationResult>('/api/v1/advanced-portfolio-optimization/mean-variance', data),

  getBlackLitterman: (data: BlackLittermanRequest) =>
    apiClient.post<OptimizationResult>('/api/v1/advanced-portfolio-optimization/black-litterman', data),

  getRiskParity: (data: RiskParityRequest) =>
    apiClient.post<OptimizationResult>('/api/v1/advanced-portfolio-optimization/risk-parity', data),

  getCVaROptimization: (data: CVaROptimizationRequest) =>
    apiClient.post<OptimizationResult>('/api/v1/advanced-portfolio-optimization/cvar-optimization', data),

  getEfficientFrontier: (data: EfficientFrontierRequest) =>
    apiClient.post<any>('/api/v1/advanced-portfolio-optimization/efficient-frontier', data),

  // Risk Management
  calculateVaR: (data: VaRRequest) =>
    apiClient.post<VaRResult>('/api/v1/advanced-risk-management/var', data),

  getHistoricalVaR: (returns: number[][], weights: number[], confidence_level = 0.95) =>
    apiClient.post<VaRResult>('/api/v1/advanced-risk-management/var-historical', {
      returns,
      weights,
      confidence_level
    }),

  runStressTest: (data: StressTestRequest) =>
    apiClient.post<StressTestResult>('/api/v1/advanced-risk-management/stress-test', data),

  getFactorStressTest: (returns: number[][], weights: number[]) =>
    apiClient.post<any>('/api/v1/advanced-risk-management/factor-stress-test', {
      returns, weights
    }),

  getComprehensiveRisk: (data: ComprehensiveRiskRequest) =>
    apiClient.post<ComprehensiveRiskResult>('/api/v1/advanced-risk-management/comprehensive-risk-analysis', data),

  // Quantitative Models
  forecastARIMA: (data: ARIMARequest) =>
    apiClient.post<ARIMAResult>('/api/v1/quantitative/arima-forecast', data),

  forecastGARCH: (data: GARCHRequest) =>
    apiClient.post<GARCHResult>('/api/v1/quantitative/garch-volatility', data),

  getKalmanFilter: (data: KalmanFilterRequest) =>
    apiClient.post<KalmanFilterResult>('/api/v1/quantitative/kalman-filter', data),

  getHalfLife: (prices: number[], lookback?: number) =>
    apiClient.post<HalfLifeResult>('/api/v1/quantitative/half-life', {
      data: prices,
      lookback
    }),

  getHurstExponent: (data: number[], max_scale = 10) =>
    apiClient.post<HurstExponentResult>('/api/v1/quantitative/hurst-exponent', {
      data,
      max_scale
    }),

  // Backtesting
  backtestStrategy: (data: BacktestRequest) =>
    apiClient.post<BacktestResult>('/api/v1/optimization/backtest', data),

  compareStrategies: (data: StrategyComparisonRequest) =>
    apiClient.post<StrategyComparisonResult>('/api/v1/optimization/compare', data),
}
