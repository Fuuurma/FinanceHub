import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ScreenerFilter, ScreenerResult, ScreenerPreset } from '@/lib/types/screener'
import { screenerApi } from '@/lib/api/screener'

interface ScreenerState {
  results: ScreenerResult[]
  selectedFilters: ScreenerFilter[]
  presets: ScreenerPreset[]
  selectedPreset: string | null
  loading: boolean
  error: string | null
  searchTerm: string
  sortBy: string
  sortOrder: 'asc' | 'desc'
  limit: number
  currentPage: number

  runScreener: () => Promise<void>
  loadPresets: () => Promise<void>
  applyPreset: (presetKey: string) => Promise<void>
  clearFilters: () => Promise<void>
  addFilter: (filter: ScreenerFilter) => void
  removeFilter: (index: number) => void
  updateFilter: (index: number, updates: Partial<ScreenerFilter>) => void
  setSearchTerm: (term: string) => void
  setSortBy: (sortBy: string) => void
  setSortOrder: (sortOrder: 'asc' | 'desc') => void
  setLimit: (limit: number) => void
  setCurrentPage: (page: number) => void
}

export const useScreenerStore = create<ScreenerState>()(
  persist(
    (set, get) => ({
      results: [],
      selectedFilters: [],
      presets: [],
      selectedPreset: null,
      loading: false,
      error: null,
      searchTerm: '',
      sortBy: 'relevance',
      sortOrder: 'desc',
      limit: 20,
      currentPage: 1,

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
          set({ results: response.results })
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

      setSortBy: (sortBy: string) => {
        set({ sortBy })
      },

      setSortOrder: (sortOrder: 'asc' | 'desc') => {
        set({ sortOrder })
      },

      setLimit: (limit: number) => {
        set({ limit, currentPage: 1 })
      },

      setCurrentPage: (page: number) => {
        set({ currentPage: page })
      }
    }),
    {
      name: 'screener-storage',
      partialize: (state) => ({
        sortBy: state.sortBy,
        sortOrder: state.sortOrder,
        limit: state.limit
      })
    }
  )
)
