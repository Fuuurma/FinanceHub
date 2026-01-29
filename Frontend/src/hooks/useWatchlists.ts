/**
 * Watchlist Hooks
 * Provides watchlist operations
 */
import { useState, useCallback } from 'react'
import { apiClient } from '@/lib/api/client'

export interface Watchlist {
  id: string
  name: string
  assets: string[]
  created_at: string
  updated_at: string
}

export function useWatchlists() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchWatchlists = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<Watchlist[]>('/api/watchlists')
      setWatchlists(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch watchlists')
    } finally {
      setLoading(false)
    }
  }, [])

  const createWatchlist = useCallback(async (name: string, assets: string[] = []) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.post<Watchlist>('/api/watchlists', { name, assets })
      setWatchlists(prev => [...prev, result])
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create watchlist')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const deleteWatchlist = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      await apiClient.delete(`/api/watchlists/${id}`)
      setWatchlists(prev => prev.filter(w => w.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete watchlist')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { watchlists, loading, error, fetchWatchlists, createWatchlist, deleteWatchlist }
}

export function useWatchlist(id: string) {
  const [watchlist, setWatchlist] = useState<Watchlist | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchWatchlist = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<Watchlist>(`/api/watchlists/${id}`)
      setWatchlist(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch watchlist')
    } finally {
      setLoading(false)
    }
  }, [id])

  const addAsset = useCallback(async (symbol: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.post<Watchlist>(`/api/watchlists/${id}/assets`, { symbol })
      setWatchlist(result)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add asset')
      throw err
    } finally {
      setLoading(false)
    }
  }, [id])

  const removeAsset = useCallback(async (symbol: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.delete<Watchlist>(`/api/watchlists/${id}/assets/${symbol}`)
      setWatchlist(result)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove asset')
      throw err
    } finally {
      setLoading(false)
    }
  }, [id])

  return { watchlist, loading, error, fetchWatchlist, addAsset, removeAsset }
}
