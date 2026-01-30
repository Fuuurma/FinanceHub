import { useState, useCallback } from 'react'
import { useScreenerStore } from '@/stores/screenerStore'
import { screenerApi } from '@/lib/api/screener'
import type { ScreenerFilter } from '@/lib/types/screener'

interface UseScreenerReturn {
  runScreener: () => Promise<void>
  applyPreset: (presetKey: string) => Promise<void>
  clearFilters: () => Promise<void>
  addFilter: (filter: ScreenerFilter) => void
  removeFilter: (index: number) => void
  updateFilter: (index: number, updates: Partial<ScreenerFilter>) => void
  loading: boolean
  error: string | null
  retryCount: number
  retryScreener: () => Promise<void>
}

export function useScreener(): UseScreenerReturn {
  const {
    results,
    selectedFilters,
    selectedPreset,
    loading: storeLoading,
    error: storeError,
    limit,
    sortBy,
    sortOrder,
    runScreener: runFromStore,
    applyPreset: applyFromStore,
    clearFilters: clearFromStore,
    addFilter,
    removeFilter,
    updateFilter,
  } = useScreenerStore()

  const [retryCount, setRetryCount] = useState(0)

  const runScreener = useCallback(async () => {
    try {
      const response = await screenerApi.screenAssets(
        selectedFilters.length > 0 ? selectedFilters : undefined,
        selectedPreset,
        limit,
        sortBy,
        sortOrder
      )
      useScreenerStore.setState({ results: response.results, loading: false, error: null })
    } catch (error) {
      useScreenerStore.setState({
        error: error instanceof Error ? error.message : 'Failed to run screener',
        loading: false
      })
    }
  }, [selectedFilters, selectedPreset, limit, sortBy, sortOrder])

  const applyPreset = useCallback(async (presetKey: string) => {
    try {
      useScreenerStore.setState({ loading: true, error: null })
      await screenerApi.applyPreset(presetKey)
      useScreenerStore.setState({ selectedPreset: presetKey })
      await runScreener()
    } catch (error) {
      useScreenerStore.setState({
        error: error instanceof Error ? error.message : 'Failed to apply preset',
        loading: false
      })
    }
  }, [runScreener])

  const clearFilters = useCallback(async () => {
    try {
      useScreenerStore.setState({ loading: true, error: null })
      await screenerApi.clearFilters()
      useScreenerStore.setState({ selectedFilters: [], selectedPreset: null, results: [] })
    } catch (error) {
      useScreenerStore.setState({
        error: error instanceof Error ? error.message : 'Failed to clear filters',
        loading: false
      })
    }
  }, [])

  const retryScreener = useCallback(async () => {
    setRetryCount(prev => prev + 1)
    await runScreener()
  }, [runScreener])

  return {
    runScreener,
    applyPreset,
    clearFilters,
    addFilter,
    removeFilter,
    updateFilter,
    loading: storeLoading,
    error: storeError,
    retryCount,
    retryScreener
  }
}
