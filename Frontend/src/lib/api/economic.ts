/**
 * Economic Indicators API Client
 * FRED Economic Data integration
 */

import { apiClient } from './client'
import type { MacroDashboardData, EconomicIndicator, EconomicDataPoint, YieldCurveData, CreditSpreadsData, InflationData, ChartDataPoint } from '@/lib/types'

export const economicApi = {
  /**
   * Get latest macro dashboard data
   */
  async getMacroDashboard(): Promise<MacroDashboardData | null> {
    try {
      const response = await apiClient.get<MacroDashboardData>('/economic/macro-dashboard')
      return response
    } catch (error) {
      console.error('Failed to fetch macro dashboard:', error)
      return null
    }
  },

  /**
   * Get specific economic indicator by series ID
   */
  async getIndicator(seriesId: string, params?: {
    observation_start?: string
    observation_end?: string
    frequency?: string
    limit?: number
  }): Promise<EconomicIndicator | null> {
    try {
      const response = await apiClient.get<EconomicIndicator>(`/economic/indicators/${seriesId}`, params)
      return response
    } catch (error) {
      console.error(`Failed to fetch indicator ${seriesId}:`, error)
      return null
    }
  },

  /**
   * Get economic data points for a series
   */
  async getDataPoints(seriesId: string, params?: {
    start_date?: string
    end_date?: string
    limit?: number
  }): Promise<EconomicDataPoint[] | null> {
    try {
      const response = await apiClient.get<EconomicDataPoint[]>(`/economic/data/${seriesId}`, params)
      return response
    } catch (error) {
      console.error(`Failed to fetch data points for ${seriesId}:`, error)
      return null
    }
  },

  /**
   * Get yield curve data
   */
  async getYieldCurve(params?: {
    start_date?: string
    end_date?: string
  }): Promise<YieldCurveData | null> {
    try {
      const response = await apiClient.get<YieldCurveData>('/economic/yield-curve', params)
      return response
    } catch (error) {
      console.error('Failed to fetch yield curve:', error)
      return null
    }
  },

  /**
   * Get credit spreads
   */
  async getCreditSpreads(): Promise<CreditSpreadsData | null> {
    try {
      const response = await apiClient.get<CreditSpreadsData>('/economic/credit-spreads')
      return response
    } catch (error) {
      console.error('Failed to fetch credit spreads:', error)
      return null
    }
  },

  /**
   * Get inflation data
   */
  async getInflationData(): Promise<InflationData | null> {
    try {
      const response = await apiClient.get<InflationData>('/economic/inflation')
      return response
    } catch (error) {
      console.error('Failed to fetch inflation data:', error)
      return null
    }
  },

  /**
   * Get GDP data
   */
  async getGDP(params?: {
    real_gdp?: boolean
    start_date?: string
    end_date?: string
  }): Promise<ChartDataPoint[] | null> {
    try {
      const response = await apiClient.get<ChartDataPoint[]>('/economic/gdp', params)
      return response
    } catch (error) {
      console.error('Failed to fetch GDP data:', error)
      return null
    }
  },

  /**
   * Get unemployment data
   */
  async getUnemployment(params?: {
    start_date?: string
    end_date?: string
  }): Promise<ChartDataPoint[] | null> {
    try {
      const response = await apiClient.get<ChartDataPoint[]>('/economic/unemployment', params)
      return response
    } catch (error) {
      console.error('Failed to fetch unemployment data:', error)
      return null
    }
  },

  /**
   * Get interest rates data
   */
  async getInterestRates(params?: {
    maturity?: string
    start_date?: string
    end_date?: string
  }): Promise<ChartDataPoint[] | null> {
    try {
      const response = await apiClient.get<ChartDataPoint[]>('/economic/interest-rates', params)
      return response
    } catch (error) {
      console.error('Failed to fetch interest rates:', error)
      return null
    }
  },

  /**
   * Get housing data
   */
  async getHousingData(params?: {
    start_date?: string
    end_date?: string
  }): Promise<any | null> {
    try {
      const response = await apiClient.get<any>('/economic/housing', params)
      return response
    } catch (error) {
      console.error('Failed to fetch housing data:', error)
      return null
    }
  },

  /**
   * Refresh macro dashboard cache
   */
  async refreshDashboard(): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await apiClient.post<{ success: boolean; message?: string }>('/economic/refresh')
      return response
    } catch (error) {
      console.error('Failed to refresh dashboard:', error)
      return { success: false, message: 'Failed to refresh dashboard' }
    }
  },

  /**
   * Get economic indicator by category
   */
  async getCategoryIndicators(category: string): Promise<EconomicIndicator[] | null> {
    try {
      const response = await apiClient.get<EconomicIndicator[]>(`/economic/categories/${category}`)
      return response
    } catch (error) {
      console.error(`Failed to fetch category ${category}:`, error)
      return null
    }
  },

  /**
   * Search economic indicators
   */
  async searchIndicators(query: string, limit: number = 20): Promise<EconomicIndicator[] | null> {
    try {
      const response = await apiClient.get<EconomicIndicator[]>('/economic/search', {
        search: query,
        limit
      })
      return response
    } catch (error) {
      console.error(`Failed to search indicators:`, error)
      return null
    }
  },
}
