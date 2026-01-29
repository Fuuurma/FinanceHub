/**
 * Portfolio Hooks
 * Provides portfolio operations
 */
import { useState, useCallback } from 'react'
import { apiClient } from '@/lib/api/client'

export interface Portfolio {
  id: string
  name: string
  description?: string
  holdings_count: number
  total_value: number
  total_cost: number
  created_at: string
  updated_at: string
}

export interface Holding {
  id: string
  portfolio_id: string
  symbol: string
  name: string
  quantity: number
  avg_cost: number
  current_price: number
  value: number
  gain_loss: number
  gain_loss_percent: number
}

export function usePortfolios() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchPortfolios = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<Portfolio[]>('/api/portfolios')
      setPortfolios(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch portfolios')
    } finally {
      setLoading(false)
    }
  }, [])

  const createPortfolio = useCallback(async (name: string, description?: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.post<Portfolio>('/api/portfolios', { name, description })
      setPortfolios(prev => [...prev, result])
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create portfolio')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const deletePortfolio = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      await apiClient.delete(`/api/portfolios/${id}`)
      setPortfolios(prev => prev.filter(p => p.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete portfolio')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { portfolios, loading, error, fetchPortfolios, createPortfolio, deletePortfolio }
}

export function usePortfolioHoldings(portfolioId: string) {
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchHoldings = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.get<Holding[]>(`/api/portfolios/${portfolioId}/holdings`)
      setHoldings(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch holdings')
    } finally {
      setLoading(false)
    }
  }, [portfolioId])

  const addHolding = useCallback(async (symbol: string, quantity: number, price: number) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.post<Holding>(`/api/portfolios/${portfolioId}/holdings`, {
        symbol,
        quantity,
        price
      })
      setHoldings(prev => [...prev, result])
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add holding')
      throw err
    } finally {
      setLoading(false)
    }
  }, [portfolioId])

  const deleteHolding = useCallback(async (holdingId: string) => {
    setLoading(true)
    setError(null)
    try {
      await apiClient.delete(`/api/portfolios/${portfolioId}/holdings/${holdingId}`)
      setHoldings(prev => prev.filter(h => h.id !== holdingId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete holding')
      throw err
    } finally {
      setLoading(false)
    }
  }, [portfolioId])

  return { holdings, loading, error, fetchHoldings, addHolding, deleteHolding }
}
