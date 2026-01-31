/**
 * Screener Presets Store
 * Zustand store for managing user's screener presets
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { screenerApi } from '@/lib/api/screener'
import type { UserScreenerPreset, ScreenerRequest } from '@/lib/types/screener'

interface ScreenerPresetsState {
  presets: UserScreenerPreset[]
  loading: boolean
  error: string | null

  // Actions
  fetchPresets: () => Promise<void>
  savePreset: (name: string, filters: Partial<ScreenerRequest>) => Promise<UserScreenerPreset>
  updatePreset: (id: string, data: { name?: string; filters?: Partial<ScreenerRequest> }) => Promise<UserScreenerPreset>
  deletePreset: (id: string) => Promise<void>
  clearError: () => void
}

export const useScreenerPresets = create<ScreenerPresetsState>()(
  persist(
    (set, get) => ({
      presets: [],
      loading: false,
      error: null,

      fetchPresets: async () => {
        set({ loading: true, error: null })
        try {
          const presets = await screenerApi.getUserPresets()
          set({ presets, loading: false })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch presets',
            loading: false,
          })
        }
      },

      savePreset: async (name: string, filters: Partial<ScreenerRequest>) => {
        set({ loading: true, error: null })
        try {
          const preset = await screenerApi.savePreset(name, filters)
          set((state) => ({
            presets: [preset, ...state.presets],
            loading: false,
          }))
          return preset
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to save preset'
          set({ error: message, loading: false })
          throw new Error(message)
        }
      },

      updatePreset: async (id: string, data: { name?: string; filters?: Partial<ScreenerRequest> }) => {
        set({ loading: true, error: null })
        try {
          const preset = await screenerApi.updatePreset(id, data)
          set((state) => ({
            presets: state.presets.map((p) => (p.id === id ? preset : p)),
            loading: false,
          }))
          return preset
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to update preset'
          set({ error: message, loading: false })
          throw new Error(message)
        }
      },

      deletePreset: async (id: string) => {
        set({ loading: true, error: null })
        try {
          await screenerApi.deletePreset(id)
          set((state) => ({
            presets: state.presets.filter((p) => p.id !== id),
            loading: false,
          }))
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to delete preset'
          set({ error: message, loading: false })
          throw new Error(message)
        }
      },

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'screener-presets-storage',
      partialize: (state) => ({
        presets: state.presets,
      }),
    }
  )
)
