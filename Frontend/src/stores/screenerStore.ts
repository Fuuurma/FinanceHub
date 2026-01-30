import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { ScreenerFilter, ScreenerResult, ScreenerPreset } from '@/lib/types/screener'
import { screenerApi } from '@/lib/api/screener'

interface CustomPreset {
  id: string
  name: string
  filters: ScreenerFilter[]
  createdAt: string
}

interface ScreenerState {
  results: ScreenerResult[]
  selectedFilters: ScreenerFilter[]
  presets: ScreenerPreset[]
  customPresets: CustomPreset[]
  selectedPreset: string | null
  loading: boolean
  error: string | null
  searchTerm: string
  sortBy: string
  sortOrder: 'asc' | 'desc'
  limit: number
  currentPage: number
  autoRefresh: boolean
  lastUpdated: string | null

  runScreener: () => Promise<void>
  loadPresets: () => Promise<void>
  applyPreset: (presetKey: string) => Promise<void>
  clearFilters: () => Promise<void>
  addFilter: (filter: ScreenerFilter) => void
  removeFilter: (index: number) => void
  updateFilter: (index: number, updates: Partial<ScreenerFilter>) => void
  setSearchTerm: (term: string) => void
  setSort: (sortBy: string, sortOrder: 'asc' | 'desc') => void
  setLimit: (limit: number) => void
  setCurrentPage: (page: number) => void
  setAutoRefresh: (enabled: boolean) => void
  saveCustomPreset: (name: string, filters: ScreenerFilter[]) => void
  deleteCustomPreset: (presetId: string) => void
}

export const useScreenerStore = create<ScreenerState>()(
  persist(
    (set, get) => ({
      results: [],
      selectedFilters: [],
      presets: [],
      customPresets: [],
      selectedPreset: null,
      loading: false,
      error: null,
      searchTerm: '',
      sortBy: 'market_cap',
      sortOrder: 'desc',
      limit: 20,
      currentPage: 1,
      autoRefresh: false,
      lastUpdated: null,

      runScreener: async () => {
        set({ loading: true, error: null, currentPage: 1 })
        try {
          const { selectedFilters, selectedPreset, limit, sortBy, sortOrder } = get()
          const response = await screenerApi.screenAssets(
            selectedFilters.length > 0 ? selectedFilters : undefined,
            selectedPreset,
            limit,
            sortBy,
            sortOrder
          )
          set({ results: response.results, lastUpdated: new Date().toISOString() })
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to run screener' })
        } finally {
          set({ loading: false })
        }
      },

      loadPresets: async () => {
        try {
          const presets = await screenerApi.getPresets()
          set({ presets })
        } catch (error) {
          console.error('Failed to load presets:', error)
        }
      },

      applyPreset: async (presetKey: string) => {
        set({ loading: true, error: null })
        try {
          await screenerApi.applyPreset(presetKey)
          set({ selectedPreset: presetKey })
          await get().runScreener()
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to apply preset' })
        } finally {
          set({ loading: false })
        }
      },

      clearFilters: async () => {
        set({ loading: true, error: null })
        try {
          await screenerApi.clearFilters()
          set({ selectedFilters: [], selectedPreset: null, results: [] })
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to clear filters' })
        } finally {
          set({ loading: false })
        }
      },

      addFilter: (filter: ScreenerFilter) => {
        set((state) => ({
          selectedFilters: [...state.selectedFilters, filter],
          selectedPreset: null
        }))
      },

      removeFilter: (index: number) => {
        set((state) => ({
          selectedFilters: state.selectedFilters.filter((_, i) => i !== index)
        }))
      },

      updateFilter: (index: number, updates: Partial<ScreenerFilter>) => {
        set((state) => ({
          selectedFilters: state.selectedFilters.map((f, i) =>
            i === index ? { ...f, ...updates } : f
          ),
          selectedPreset: null
        }))
      },

      setSearchTerm: (term: string) => {
        set({ searchTerm: term, currentPage: 1 })
      },

      setSort: (sortBy: string, sortOrder: 'asc' | 'desc') => {
        set({ sortBy, sortOrder })
        if (get().autoRefresh) {
          get().runScreener()
        }
      },

      setLimit: (limit: number) => {
        set({ limit, currentPage: 1 })
      },

      setCurrentPage: (page: number) => {
        set({ currentPage: page })
      },

      setAutoRefresh: (enabled: boolean) => {
        set({ autoRefresh: enabled })
        if (enabled) {
          const { runScreener } = get()
          runScreener()
        }
      },

      saveCustomPreset: (name: string, filters: ScreenerFilter[]) => {
        const newPreset: CustomPreset = {
          id: `custom-${Date.now()}`,
          name,
          filters,
          createdAt: new Date().toISOString()
        }
        set((state) => ({
          customPresets: [...state.customPresets, newPreset]
        }))
      },

      deleteCustomPreset: (presetId: string) => {
        set((state) => ({
          customPresets: state.customPresets.filter(p => p.id !== presetId)
        }))
      }
    }),
    {
      name: 'screener-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        sortBy: state.sortBy,
        sortOrder: state.sortOrder,
        limit: state.limit,
        autoRefresh: state.autoRefresh,
        customPresets: state.customPresets
      })
    }
  )
)
