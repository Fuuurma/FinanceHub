/**
 * Economic Data Store
 * Manages economic indicators state
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { MacroDashboardData, DashboardConfig, DEFAULT_DASHBOARD_CONFIG } from '@/lib/types'

interface EconomicStore {
  macroData: MacroDashboardData | null
  loading: boolean
  error: string | null
  lastFetched: string | null
  config: DashboardConfig

  // Actions
  setMacroData: (data: MacroDashboardData) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setLastFetched: (date: string) => void

  // Config actions
  updateConfig: (config: Partial<DashboardConfig>) => void
  resetConfig: () => void

  // Visibility actions
  toggleCategory: (category: string) => void
  setCategoryVisible: (category: string, visible: boolean) => void

  // Data fetching
  fetchMacroData: () => Promise<void>
  refreshData: () => Promise<void>
}

export const useEconomicStore = create<EconomicStore>()(
  devtools(
    persist(
      (set, get) => ({
        macroData: null,
        loading: false,
        error: null,
        lastFetched: null,
        config: DEFAULT_DASHBOARD_CONFIG,

        setMacroData: (data) => set({ macroData: data, error: null }),

        setLoading: (loading) => set({ loading }),

        setError: (error) => set({ error }),

        setLastFetched: (date) => set({ lastFetched: date }),

        updateConfig: (newConfig) =>
          set((state) => ({
            config: { ...state.config, ...newConfig },
          })),

        resetConfig: () => set({ config: DEFAULT_DASHBOARD_CONFIG }),

        toggleCategory: (category) =>
          set((state) => ({
            config: {
              ...state.config,
              visibleCategories: state.config.visibleCategories.includes(category)
                ? state.config.visibleCategories.filter((c) => c !== category)
                : [...state.config.visibleCategories, category],
            },
          })),

        setCategoryVisible: (category, visible) =>
          set((state) => ({
            config: {
              ...state.config,
              visibleCategories: visible
                ? [...new Set([...state.config.visibleCategories, category])]
                : state.config.visibleCategories.filter((c) => c !== category),
            },
          })),

        fetchMacroData: async () => {
          const { economicApi } = await import('@/lib/api/economic')
          set({ loading: true, error: null })

          try {
            const data = await economicApi.getMacroDashboard()
            if (data) {
              set({
                macroData: data,
                loading: false,
                lastFetched: new Date().toISOString(),
              })
            } else {
              set({ loading: false, error: 'Failed to fetch economic data' })
            }
          } catch (error) {
            set({
              loading: false,
              error: error instanceof Error ? error.message : 'Unknown error',
            })
          }
        },

        refreshData: async () => {
          const { economicApi } = await import('@/lib/api/economic')
          set({ loading: true, error: null })

          try {
            const result = await economicApi.refreshDashboard()
            if (result.success) {
              await get().fetchMacroData()
            } else {
              set({ loading: false, error: result.message || 'Failed to refresh' })
            }
          } catch (error) {
            set({
              loading: false,
              error: error instanceof Error ? error.message : 'Unknown error',
            })
          }
        },
      }),
      {
        name: 'economic-store',
        partialize: (state) => ({
          config: state.config,
        }),
      }
    ),
    { name: 'EconomicStore' }
  )
)
