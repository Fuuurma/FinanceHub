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
  UserScreenerPreset,
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

  /**
   * Get user's saved screener presets
   */
  getUserPresets: async (): Promise<UserScreenerPreset[]> => {
    return await apiClient.get<UserScreenerPreset[]>('/screener/presets')
  },

  /**
   * Save a new screener preset
   */
  savePreset: async (name: string, filters: Partial<ScreenerRequest>): Promise<UserScreenerPreset> => {
    return await apiClient.post<UserScreenerPreset>('/screener/presets', { name, filters })
  },

  /**
   * Update a screener preset
   */
  updatePreset: async (id: string, data: { name?: string; filters?: Partial<ScreenerRequest> }): Promise<UserScreenerPreset> => {
    return await apiClient.put<UserScreenerPreset>(`/screener/presets/${id}`, data)
  },

  /**
   * Delete a screener preset
   */
  deletePreset: async (id: string): Promise<{ success: boolean }> => {
    return await apiClient.delete<{ success: boolean }>(`/screener/presets/${id}`)
  },
}
