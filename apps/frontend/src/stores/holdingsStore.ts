import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { holdingsApi, type HoldingsListResponse, type TransactionsListResponse } from '@/lib/api/holdings'
import type {
  Holding,
  Transaction,
  HoldingsFilter,
  TransactionFilter,
  PnLHistoryPoint,
  AssetAllocationItem,
  HoldingsPortfolioSummary,
} from '@/lib/types/holdings'

interface HoldingsState {
  // Data
  holdings: Holding[]
  transactions: Transaction[]
  selectedPortfolioId: string | null
  portfolioSummary: HoldingsPortfolioSummary | null
  pnlHistory: PnLHistoryPoint[]
  allocation: AssetAllocationItem[]

  // Loading states
  holdingsLoading: boolean
  transactionsLoading: boolean
  summaryLoading: boolean
  pnlLoading: boolean

  // Error states
  holdingsError: string | null
  transactionsError: string | null
  summaryError: string | null
  pnlError: string | null

  // Pagination
  holdingsPage: number
  holdingsTotal: number
  transactionsPage: number
  transactionsTotal: number

  // Filters
  holdingsFilters: HoldingsFilter
  transactionsFilters: TransactionFilter

  // Actions
  setSelectedPortfolio: (id: string | null) => void

  fetchHoldings: (portfolioId: string, filters?: HoldingsFilter) => Promise<void>
  fetchTransactions: (portfolioId: string, filters?: TransactionFilter) => Promise<void>
  fetchSummary: (portfolioId: string) => Promise<void>
  fetchPnL: (portfolioId: string, period?: string) => Promise<void>
  fetchAllocation: (portfolioId: string) => Promise<void>

  addHolding: (portfolioId: string, data: Parameters<typeof holdingsApi.create>[1]) => Promise<Holding>
  updateHolding: (portfolioId: string, holdingId: string, data: Parameters<typeof holdingsApi.update>[2]) => Promise<Holding>
  removeHolding: (portfolioId: string, holdingId: string) => Promise<void>

  addTransaction: (portfolioId: string, data: Parameters<typeof holdingsApi.createTransaction>[1]) => Promise<Transaction>
  removeTransaction: (portfolioId: string, transactionId: string) => Promise<void>

  setHoldingsFilters: (filters: Partial<HoldingsFilter>) => void
  setTransactionsFilters: (filters: Partial<TransactionFilter>) => void

  clearHoldings: () => void
  clearTransactions: () => void
  clearAll: () => void

  // Computed values
  getTotalValue: () => number
  getTotalPnL: () => number
  getTotalPnLPercent: () => number
  getDayChange: () => number
}

export const useHoldingsStore = create<HoldingsState>()(
  persist(
    (set, get) => ({
      // Initial state
      holdings: [],
      transactions: [],
      selectedPortfolioId: null,
      portfolioSummary: null,
      pnlHistory: [],
      allocation: [],

      holdingsLoading: false,
      transactionsLoading: false,
      summaryLoading: false,
      pnlLoading: false,

      holdingsError: null,
      transactionsError: null,
      summaryError: null,
      pnlError: null,

      holdingsPage: 1,
      holdingsTotal: 0,
      transactionsPage: 1,
      transactionsTotal: 0,

      holdingsFilters: {},
      transactionsFilters: {},

      // Actions
      setSelectedPortfolio: (id) => {
        set({ selectedPortfolioId: id })
        if (id) {
          get().fetchHoldings(id)
          get().fetchSummary(id)
          get().fetchPnL(id)
          get().fetchAllocation(id)
        }
      },

      fetchHoldings: async (portfolioId, filters) => {
        set({ holdingsLoading: true, holdingsError: null })
        try {
          const response = await holdingsApi.list(portfolioId, filters)
          set({
            holdings: response.holdings,
            holdingsLoading: false,
            holdingsTotal: response.total,
            holdingsPage: response.page,
          })
        } catch (error) {
          set({
            holdingsError: error instanceof Error ? error.message : 'Failed to fetch holdings',
            holdingsLoading: false,
          })
        }
      },

      fetchTransactions: async (portfolioId, filters) => {
        set({ transactionsLoading: true, transactionsError: null })
        try {
          const response = await holdingsApi.listTransactions(portfolioId, filters)
          set({
            transactions: response.transactions,
            transactionsLoading: false,
            transactionsTotal: response.total,
            transactionsPage: response.page,
          })
        } catch (error) {
          set({
            transactionsError: error instanceof Error ? error.message : 'Failed to fetch transactions',
            transactionsLoading: false,
          })
        }
      },

      fetchSummary: async (portfolioId) => {
        set({ summaryLoading: true, summaryError: null })
        try {
          const summary = await holdingsApi.getSummary(portfolioId)
          set({ portfolioSummary: summary, summaryLoading: false })
        } catch (error) {
          set({
            summaryError: error instanceof Error ? error.message : 'Failed to fetch summary',
            summaryLoading: false,
          })
        }
      },

      fetchPnL: async (portfolioId, period) => {
        set({ pnlLoading: true, pnlError: null })
        try {
          const response = await holdingsApi.getPnL(portfolioId, period as any)
          set({ pnlHistory: response.history, pnlLoading: false })
        } catch (error) {
          set({
            pnlError: error instanceof Error ? error.message : 'Failed to fetch P&L',
            pnlLoading: false,
          })
        }
      },

      fetchAllocation: async (portfolioId) => {
        try {
          const response = await holdingsApi.getAllocation(portfolioId)
          set({ allocation: response.allocation })
        } catch (error) {
          console.error('Failed to fetch allocation:', error)
        }
      },

      addHolding: async (portfolioId, data) => {
        const newHolding = await holdingsApi.create(portfolioId, data)
        set((state) => ({
          holdings: [newHolding, ...state.holdings],
          holdingsTotal: state.holdingsTotal + 1,
        }))
        return newHolding
      },

      updateHolding: async (portfolioId, holdingId, data) => {
        const updatedHolding = await holdingsApi.update(portfolioId, holdingId, data)
        set((state) => ({
          holdings: state.holdings.map((h) =>
            h.id === holdingId ? updatedHolding : h
          ),
        }))
        return updatedHolding
      },

      removeHolding: async (portfolioId, holdingId) => {
        await holdingsApi.delete(portfolioId, holdingId)
        set((state) => ({
          holdings: state.holdings.filter((h) => h.id !== holdingId),
          holdingsTotal: state.holdingsTotal - 1,
        }))
      },

      addTransaction: async (portfolioId, data) => {
        const newTransaction = await holdingsApi.createTransaction(portfolioId, data)
        set((state) => ({
          transactions: [newTransaction, ...state.transactions],
          transactionsTotal: state.transactionsTotal + 1,
        }))
        return newTransaction
      },

      removeTransaction: async (portfolioId, transactionId) => {
        await holdingsApi.deleteTransaction(portfolioId, transactionId)
        set((state) => ({
          transactions: state.transactions.filter((t) => t.id !== transactionId),
          transactionsTotal: state.transactionsTotal - 1,
        }))
      },

      setHoldingsFilters: (filters) => {
        set((state) => ({
          holdingsFilters: { ...state.holdingsFilters, ...filters },
        }))
      },

      setTransactionsFilters: (filters) => {
        set((state) => ({
          transactionsFilters: { ...state.transactionsFilters, ...filters },
        }))
      },

      clearHoldings: () => {
        set({ holdings: [], holdingsTotal: 0, holdingsError: null })
      },

      clearTransactions: () => {
        set({ transactions: [], transactionsTotal: 0, transactionsError: null })
      },

      clearAll: () => {
        set({
          holdings: [],
          transactions: [],
          portfolioSummary: null,
          pnlHistory: [],
          allocation: [],
          holdingsError: null,
          transactionsError: null,
          summaryError: null,
          pnlError: null,
          holdingsTotal: 0,
          transactionsTotal: 0,
        })
      },

      // Computed values
      getTotalValue: () => {
        return get().holdings.reduce((sum, h) => sum + h.current_value, 0)
      },

      getTotalPnL: () => {
        return get().holdings.reduce((sum, h) => sum + h.unrealized_pnl, 0)
      },

      getTotalPnLPercent: () => {
        const totalValue = get().getTotalValue()
        const totalPnL = get().getTotalPnL()
        return totalValue > 0 ? (totalPnL / (totalValue - totalPnL)) * 100 : 0
      },

      getDayChange: () => {
        return get().holdings.reduce((sum, h) => sum + h.day_change, 0)
      },
    }),
    {
      name: 'holdings-storage',
      partialize: (state) => ({
        selectedPortfolioId: state.selectedPortfolioId,
        holdingsFilters: state.holdingsFilters,
        transactionsFilters: state.transactionsFilters,
      }),
    }
  )
)

export const useHoldings = () => {
  const store = useHoldingsStore()
  return {
    ...store,
    fetchHoldings: store.fetchHoldings,
    fetchTransactions: store.fetchTransactions,
    fetchSummary: store.fetchSummary,
    fetchPnL: store.fetchPnL,
    fetchAllocation: store.fetchAllocation,
    addHolding: store.addHolding,
    updateHolding: store.updateHolding,
    removeHolding: store.removeHolding,
    addTransaction: store.addTransaction,
    removeTransaction: store.removeTransaction,
    setSelectedPortfolio: store.setSelectedPortfolio,
    setHoldingsFilters: store.setHoldingsFilters,
    setTransactionsFilters: store.setTransactionsFilters,
    clearHoldings: store.clearHoldings,
    clearTransactions: store.clearTransactions,
    clearAll: store.clearAll,
  }
}
