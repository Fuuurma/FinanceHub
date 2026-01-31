/**
 * Settings Store
 * Zustand store for user settings with localStorage persistence
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { useTheme } from 'next-themes'
import type {
  UserSettings,
  SettingsUpdate,
  DisplaySettings,
  NotificationSettings,
  ProfileSettings,
  InvestmentProfile,
  ThemeMode,
  PreferredAssetClass,
} from '@/lib/types/settings'
import {
  defaultSettings,
  defaultDisplaySettings,
  defaultNotificationSettings,
  defaultProfileSettings,
  defaultInvestmentProfile,
} from '@/lib/types/settings'

interface SettingsState extends UserSettings {
  isLoading: boolean
  error: string | null
  lastSaved: string | null

  setDisplaySettings: (settings: Partial<DisplaySettings>) => void
  setNotificationSettings: (settings: Partial<NotificationSettings>) => void
  setProfileSettings: (settings: Partial<ProfileSettings>) => void
  setInvestmentProfile: (settings: Partial<InvestmentProfile>) => void
  setTheme: (theme: ThemeMode) => void
  
  resetSettings: () => void
  resetDisplaySettings: () => void
  resetNotificationSettings: () => void
  
  saveSettings: () => Promise<void>
  loadSettings: () => Promise<void>
  exportSettings: () => string
  importSettings: (json: string) => void
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      display: defaultDisplaySettings,
      notifications: defaultNotificationSettings,
      profile: defaultProfileSettings,
      investment: defaultInvestmentProfile,
      isLoading: false,
      error: null,
      lastSaved: null,

      setDisplaySettings: (settings) => {
        set((state) => ({
          display: { ...state.display, ...settings },
        }))
      },

      setNotificationSettings: (settings) => {
        set((state) => ({
          notifications: { ...state.notifications, ...settings },
        }))
      },

      setProfileSettings: (settings) => {
        set((state) => ({
          profile: { ...state.profile, ...settings },
        }))
      },

      setInvestmentProfile: (settings) => {
        set((state) => ({
          investment: { ...state.investment, ...settings },
        }))
      },

      setTheme: (theme) => {
        set((state) => ({
          display: { ...state.display, theme },
        }))
      },

      resetSettings: () => {
        set({
          display: defaultDisplaySettings,
          notifications: defaultNotificationSettings,
          profile: defaultProfileSettings,
          investment: defaultInvestmentProfile,
          error: null,
        })
      },

      resetDisplaySettings: () => {
        set({ display: defaultDisplaySettings })
      },

      resetNotificationSettings: () => {
        set({ notifications: defaultNotificationSettings })
      },

      saveSettings: async () => {
        set({ isLoading: true, error: null })
        
        try {
          const state = get()
          
          // TODO: Integrate with backend API when available
          // For now, settings are automatically persisted via zustand persist middleware
          
          set({
            isLoading: false,
            lastSaved: new Date().toISOString(),
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to save settings',
            isLoading: false,
          })
        }
      },

      loadSettings: async () => {
        set({ isLoading: true, error: null })
        
        try {
          // TODO: Load from backend API when available
          // For now, settings are automatically loaded from localStorage via zustand persist
          
          set({
            isLoading: false,
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to load settings',
            isLoading: false,
          })
        }
      },

      exportSettings: () => {
        const state = get()
        const exportable = {
          display: state.display,
          notifications: state.notifications,
          profile: {
            ...state.profile,
            // Don't export sensitive data
            email: undefined,
            phone: undefined,
          },
          investment: state.investment,
          exportedAt: new Date().toISOString(),
          version: '1.0',
        }
        return JSON.stringify(exportable, null, 2)
      },

      importSettings: (json) => {
        try {
          const imported = JSON.parse(json)
          
          if (imported.version !== '1.0') {
            throw new Error('Invalid settings version')
          }
          
          set({
            display: { ...defaultDisplaySettings, ...imported.display },
            notifications: { ...defaultNotificationSettings, ...imported.notifications },
            profile: { ...defaultProfileSettings, ...imported.profile },
            investment: { ...defaultInvestmentProfile, ...imported.investment },
            lastSaved: new Date().toISOString(),
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to import settings',
          })
        }
      },
    }),
    {
      name: 'financehub-settings',
      partialize: (state) => ({
        display: state.display,
        notifications: state.notifications,
        profile: state.profile,
        investment: state.investment,
        lastSaved: state.lastSaved,
      }),
    }
  )
)
