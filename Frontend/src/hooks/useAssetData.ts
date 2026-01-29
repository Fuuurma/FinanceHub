/**
 * Data Fetching Hooks
 * Provides convenient hooks for fetching data from the API
 */
import { useState, useCallback, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'
import type { Asset, AssetDetail, PriceHistory } from '@/lib/types/market'

const STALE_TIME = 5 * 60 * 1000

export function useAssetData(symbol: string, interval: string = '1d') {
  const [data, setData] = useState<PriceHistory | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!symbol) return

    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const result = await apiClient.get<PriceHistory>(`/api/assets/${symbol}/history?interval=${interval}`)
        setData(result)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch asset data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [symbol, interval])

  return { data, loading, error }
}

export function useAssetDetail(symbol: string) {
  const [data, setData] = useState<AssetDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!symbol) return

    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const result = await apiClient.get<AssetDetail>(`/api/assets/${symbol}`)
        setData(result)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch asset detail')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [symbol])

  return { data, loading, error }
}

export function useAssetPrice(symbol: string) {
  const [data, setData] = useState<{ price: number; change: number; changePercent: number } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchPrice = useCallback(async () => {
    if (!symbol) return

    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<{ price: number; change: number; changePercent: number }>(`/api/assets/${symbol}/price`)
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch price')
    } finally {
      setLoading(false)
    }
  }, [symbol])

  useEffect(() => {
    fetchPrice()
    const interval = setInterval(fetchPrice, 30000)
    return () => clearInterval(interval)
  }, [fetchPrice])

  return { data, loading, error, refetch: fetchPrice }
}

export function useAssets(type?: string, limit: number = 20, page: number = 1) {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAssets = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<Asset[]>(`/api/assets?type=${type || ''}&limit=${limit}&page=${page}`)
      setAssets(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch assets')
    } finally {
      setLoading(false)
    }
  }, [type, limit, page])

  useEffect(() => {
    fetchAssets()
  }, [fetchAssets])

  return { assets, loading, error, refetch: fetchAssets }
}
