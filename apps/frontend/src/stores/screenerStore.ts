/**
 * Screener Store
 * Zustand store for screener state management
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { screenerApi } from '@/lib/api/screener'
import type {
  ScreenerState,
  ScreenerRequest,
  ScreenerResult,
  SortField,
  SortDirection,
  ScreenerPreset,
} from '@/lib/types/screener'

export const useScreenerStore = create<ScreenerState>()(
  persist(
    (set, get) => ({
      // Initial state
      filters: {},
      results: [],
      loading: false,
      error: null,
      total_count: 0,
      total_screened: 0,
      elapsed_seconds: 0,
      last_updated: null,
      sort_field: 'market_cap',
      sort_direction: 'desc',
      selected_presets: [],
      limit: 100,

      // Actions
      setFilter: (key, value) => {
        set((state) => ({
          filters: {
            ...state.filters,
            [key]: value,
          },
        }))
      },

      removeFilter: (key) => {
        set((state) => {
          const newFilters = { ...state.filters }
          delete newFilters[key]
          return { filters: newFilters }
        })
      },

      clearFilters: () => {
        set({
          filters: {},
          selected_presets: [],
          results: [],
        })
      },

      applyPreset: (preset) => {
        set({
          filters: preset.filters,
          selected_presets: [preset.key],
        })
        get().runScreener()
      },

      setSorting: (field, direction) => {
        set({
          sort_field: field,
          sort_direction: direction,
        })
      },

      setLimit: (limit) => {
        set({ limit })
      },

      runScreener: async () => {
        const { filters, limit } = get()
        set({ loading: true, error: null })

        try {
          const response = await screenerApi.runScreener({
            ...filters,
            limit,
          })

          set({
            results: response.results || [],
            total_count: response.count || 0,
            total_screened: response.total_screened || 0,
            elapsed_seconds: response.elapsed_seconds || 0,
            loading: false,
            last_updated: new Date().toISOString(),
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to run screener',
            loading: false,
            results: [],
          })
        }
      },

      exportResults: (format) => {
        const { results } = get()

        if (results.length === 0) {
          return
        }

        const filename = `screener-results-${new Date().toISOString().split('T')[0]}`

        if (format === 'json') {
          const data = JSON.stringify(results, null, 2)
          const blob = new Blob([data], { type: 'application/json' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `${filename}.json`
          a.click()
          URL.revokeObjectURL(url)
        } else if (format === 'csv') {
          const headers = Object.keys(results[0])
          const csv = [
            headers.join(','),
            ...results.map((row) =>
              headers.map((header) => {
                const value = row[header as keyof ScreenerResult]
                if (value === null || value === undefined) return ''
                if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                  return `"${value.replace(/"/g, '""')}"`
                }
                return String(value)
              }).join(',')
            ),
          ].join('\n')

          const blob = new Blob([csv], { type: 'text/csv' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `${filename}.csv`
          a.click()
          URL.revokeObjectURL(url)
        }
      },
    }),
    {
      name: 'screener-storage',
      partialize: (state) => ({
        filters: state.filters,
        sort_field: state.sort_field,
        sort_direction: state.sort_direction,
        limit: state.limit,
      }),
    }
  )
)
