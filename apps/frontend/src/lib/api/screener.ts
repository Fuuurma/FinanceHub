/**
 * Screener API Client
 * Stock screener endpoints
 */

import { apiClient } from './client'
import type {
  ScreenerResponse,
  ScreenerRequest,
  ScreenerFiltersResponse,
  ScreenerFilter,
} from '../types/screener'

export const screenerApi = {
  /**
   * Run stock screener with filters
   * Backend endpoint: POST /api/fundamentals/screener
   */
  runScreener: async (filters: ScreenerRequest): Promise<ScreenerResponse> => {
    return await apiClient.post<ScreenerResponse>('/fundamentals/screener', filters)
  },

  /**
   * Get available screener filters and presets
   */
  getFilters: async (): Promise<ScreenerFiltersResponse> => {
    return await apiClient.get<ScreenerFiltersResponse>('/screener/filters')
  },

  /**
   * Get available screener presets
   */
  getPresets: async (): Promise<Record<string, { name: string; description: string }>> => {
    return await apiClient.get<Record<string, { name: string; description: string }>>('/screener/presets')
  },
}
