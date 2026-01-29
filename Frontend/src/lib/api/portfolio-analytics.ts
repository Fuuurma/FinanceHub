/**
 * Portfolio Analytics API
 * All portfolio-related API calls for performance analysis and recommendations
 */

import { apiClient } from './client'
import type {
  PortfolioSummary,
  PerformanceMetrics,
  RiskAnalysis,
  HoldingsAnalysis,
  RebalancingSuggestions,
  ComparisonResponse,
  AnalyticsPeriod,
  PortfolioAnalytics,
} from '../types'

export const portfolioAnalyticsApi = {
  /**
   * Get portfolio summary
   */
  getPortfolioSummary: (portfolioId: string) =>
    apiClient.get<PortfolioSummary>(`/portfolios/${portfolioId}/summary`),

  /**
   * Get performance metrics
   */
  getPerformanceMetrics: (portfolioId: string, period: '1y' | '6m' | '3m' = '1y') =>
    apiClient.get<PerformanceMetrics>(`/portfolios/${portfolioId}/performance`, {
      params: { period },
    }),

  /**
   * Get risk analysis
   */
  getRiskAnalysis: (portfolioId: string) =>
    apiClient.get<RiskAnalysis>(`/portfolios/${portfolioId}/risk-analysis`),

  /**
   * Get holdings analysis
   */
  getHoldingsAnalysis: (portfolioId: string) =>
    apiClient.get<HoldingsAnalysis>(`/portfolios/${portfolioId}/holdings`),

  /**
   * Get rebalancing suggestions
   */
  getRebalancingSuggestions: (portfolioId: string) =>
    apiClient.get<RebalancingSuggestions>(`/portfolios/${portfolioId}/rebalance-suggestions`),

  /**
   * Get portfolio comparison
   */
  getPortfolioComparison: (
    portfolioId: string,
    benchmarkType: 'sp500' | 'custom' = 'sp500',
    period: '1y' | '6m' | '3m' = '1y'
  ) =>
    apiClient.get<ComparisonResponse>(`/portfolios/${portfolioId}/comparison`, {
      params: {
        benchmark_type: benchmarkType,
        period,
      },
    }),

  /**
   * Get analytics overview (for analytics dashboard)
   */
  getAnalytics: (period: AnalyticsPeriod = '7d') =>
    apiClient.get<PortfolioAnalytics>('/analytics', {
      params: { period },
    }),
}
