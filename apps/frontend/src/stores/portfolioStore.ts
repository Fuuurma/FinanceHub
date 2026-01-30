'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { portfoliosApi } from '@/lib/api/portfolio'
import type {
  Portfolio,
  PortfolioHolding,
  PortfolioTransaction,
  PortfolioHistory,
  PortfolioMetrics,
  TransactionsFilter,
} from '@/lib/types'

export type Period = '1m' | '3m' | '6m' | '1y' | 'all'

interface PortfolioState {
  // State
  portfolios: Portfolio[]
  selectedPortfolioId: string | null
  holdings: PortfolioHolding[]
  transactions: PortfolioTransaction[]
  history: PortfolioHistory[]
  metrics: PortfolioMetrics | null
  loading: boolean
  error: string | null
  lastFetched: string | null

  // Actions
  fetchPortfolios: () => Promise<void>
  selectPortfolio: (id: string | null) => Promise<void>
  fetchHoldings: () => Promise<void>
  fetchTransactions: (filter?: TransactionsFilter) => Promise<void>
  fetchHistory: (period?: Period) => Promise<void>
  fetchMetrics: (period?: Period) => Promise<void>
  createPortfolio: (data: { name: string; description?: string }) => Promise<Portfolio>
  updatePortfolio: (id: string, data: Partial<Portfolio>) => Promise<void>
  deletePortfolio: (id: string) => Promise<void>
  clearError: () => void
}

export const usePortfolioStore = create<PortfolioState>()(
  persist(
    (set, get) => ({
      portfolios: [],
      selectedPortfolioId: null,
      holdings: [],
      transactions: [],
      history: [],
      metrics: null,
      loading: false,
      error: null,
      lastFetched: null,

      fetchPortfolios: async () => {
        set({ loading: true, error: null })
        try {
          const response = await portfoliosApi.getPortfolios()
          set({ portfolios: response.portfolios, loading: false })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch portfolios',
            loading: false,
          })
        }
      },

      selectPortfolio: async (id: string | null) => {
        set({ selectedPortfolioId: id })
        if (id) {
          await get().fetchHoldings()
          await get().fetchHistory()
          await get().fetchMetrics()
        } else {
          set({ holdings: [], history: [], metrics: null })
        }
      },

      fetchHoldings: async () => {
        const { selectedPortfolioId } = get()
        if (!selectedPortfolioId) return

        set({ loading: true, error: null })
        try {
          const holdings = await portfoliosApi.getHoldings(selectedPortfolioId)
          set({ holdings, loading: false })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch holdings',
            loading: false,
          })
        }
      },

      fetchTransactions: async (filter?: TransactionsFilter) => {
        const { selectedPortfolioId } = get()
        if (!selectedPortfolioId) return

        set({ loading: true, error: null })
        try {
          const response = await portfoliosApi.getTransactions(selectedPortfolioId, filter)
          set({ transactions: response.transactions, loading: false })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch transactions',
            loading: false,
          })
        }
      },

      fetchHistory: async (period?: Period) => {
        const { selectedPortfolioId } = get()
        if (!selectedPortfolioId) return

        set({ loading: true, error: null })
        try {
          const history = await portfoliosApi.getHistory(selectedPortfolioId, period)
          set({ history, loading: false, lastFetched: new Date().toISOString() })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch history',
            loading: false,
          })
        }
      },

      fetchMetrics: async (period?: Period) => {
        const { selectedPortfolioId } = get()
        if (!selectedPortfolioId) return

        set({ loading: true, error: null })
        try {
          const metrics = await portfoliosApi.getMetrics(selectedPortfolioId, period)
          set({ metrics, loading: false })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch metrics',
            loading: false,
          })
        }
      },

      createPortfolio: async (data) => {
        set({ loading: true, error: null })
        try {
          const portfolio = await portfoliosApi.createPortfolio(data)
          set((state) => ({
            portfolios: [...state.portfolios, portfolio],
            loading: false,
          }))
          return portfolio
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create portfolio',
            loading: false,
          })
          throw error
        }
      },

      updatePortfolio: async (id, data) => {
        set({ loading: true, error: null })
        try {
          const updated = await portfoliosApi.updatePortfolio(id, data)
          set((state) => ({
            portfolios: state.portfolios.map((p) => (p.id === id ? updated : p)),
            loading: false,
          }))
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update portfolio',
            loading: false,
          })
        }
      },

      deletePortfolio: async (id) => {
        set({ loading: true, error: null })
        try {
          await portfoliosApi.deletePortfolio(id)
          set((state) => ({
            portfolios: state.portfolios.filter((p) => p.id !== id),
            selectedPortfolioId: state.selectedPortfolioId === id ? null : state.selectedPortfolioId,
            holdings: state.selectedPortfolioId === id ? [] : state.holdings,
            loading: false,
          }))
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to delete portfolio',
            loading: false,
          })
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'portfolio-storage',
      partialize: (state) => ({ selectedPortfolioId: state.selectedPortfolioId }),
    }
  )
)
