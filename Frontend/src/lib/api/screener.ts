import { apiClient } from './client'
import type {
  ScreenerFilter,
  ScreenerFiltersOut,
  ScreenerResponse,
  ScreenerPreset,
} from '@/lib/types/screener'

export const screenerApi = {
  getFilters: async (): Promise<ScreenerFiltersOut> => {
    return await apiClient.get<ScreenerFiltersOut>('/screener/filters')
  },

  getPresets: async (): Promise<ScreenerPreset[]> => {
    return await apiClient.get<ScreenerPreset[]>('/screener/presets')
  },

  screenAssets: async (
    filters?: ScreenerFilter[],
    preset?: string | null,
    limit: number = 20,
    sortBy: string = 'relevance',
    sortOrder: string = 'desc'
  ): Promise<ScreenerResponse> => {
    const params = new URLSearchParams()
    if (limit) params.append('limit', limit.toString())
    if (sortBy) params.append('sort_by', sortBy)
    if (sortOrder) params.append('sort_order', sortOrder)

    if (preset) {
      params.append('preset', preset)
    } else if (filters && filters.length > 0) {
      return await apiClient.post<ScreenerResponse>(`/screener/screen?${params.toString()}`, filters)
    } else {
      return await apiClient.get<ScreenerResponse>(`/screener/screen?${params.toString()}`)
    }
  },

  applyPreset: async (presetName: string): Promise<{ preset_name: string; filters_applied: number; success: boolean }> => {
    return await apiClient.post<{ preset_name: string; filters_applied: number; success: boolean }>(
      '/screener/apply-preset',
      { preset_name: presetName }
    )
  },

  clearFilters: async (): Promise<{ message: string }> => {
    return await apiClient.post<{ message: string }>('/screener/clear-filters')
  },
}
