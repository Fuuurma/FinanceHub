/**
 * Market Hooks
 * Provides market data operations
 */
import { useState, useCallback } from 'react'
import { apiClient } from '@/lib/api/client'
import type { MarketOverview, MarketMover } from '@/lib/types/market'

export function useMarketOverview() {
  const [data, setData] = useState<MarketOverview | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchOverview = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<MarketOverview>('/api/market/overview')
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch market overview')
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, fetchOverview }
}

export function useMarketMovers(type: 'gainers' | 'losers') {
  const [movers, setMovers] = useState<MarketMover[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchMovers = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<MarketMover[]>(`/api/market/movers/${type}`)
      setMovers(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch movers')
    } finally {
      setLoading(false)
    }
  }, [type])

  return { movers, loading, error, fetchMovers }
}

export function useSectors() {
  const [sectors, setSectors] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchSectors = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<any[]>('/api/market/sectors')
      setSectors(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sectors')
    } finally {
      setLoading(false)
    }
  }, [])

  return { sectors, loading, error, fetchSectors }
}

export function useIndices() {
  const [indices, setIndices] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchIndices = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<any[]>('/api/market/indices')
      setIndices(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch indices')
    } finally {
      setLoading(false)
    }
  }, [])

  return { indices, loading, error, fetchIndices }
}

export function useTrending() {
  const [trending, setTrending] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTrending = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<any[]>('/api/market/trending')
      setTrending(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch trending')
    } finally {
      setLoading(false)
    }
  }, [])

  return { trending, loading, error, fetchTrending }
}
