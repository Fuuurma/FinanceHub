/**
 * Assets API
 * All asset-related API calls
 */

import { apiClient } from './client'
import type { Asset, AssetDetail, PriceHistory, AssetFilter } from '@/lib/types'

interface AssetPrice {
  symbol: string
  price: number
  change: number
  change_percent: number
  timestamp: string
  high: number
  low: number
  open: number
  volume: number
}

interface AssetFundamentals {
  symbol: string
  name: string
  metrics: {
    market_cap: number
    pe_ratio: number
    pb_ratio: number
    eps: number
    dividend_yield: number
    beta: number
    revenue: number
    net_income: number
    total_assets: number
    total_debt: number
  }
  timestamp: string
}

interface AssetNews {
  symbol: string
  news: any[]
  message: string
}

export const assetsApi = {
  list(filter: AssetFilter, limit: number = 20, offset: number = 0): Promise<Asset[]> {
    return apiClient.get('/assets/', {
      params: { ...filter, limit, offset },
    })
  },

  get(symbol: string): Promise<AssetDetail> {
    return apiClient.get(`/assets/${symbol}`)
  },

  getPrice(symbol: string): Promise<AssetPrice> {
    return apiClient.get(`/assets/${symbol}/price`)
  },

  getHistorical(
    symbol: string,
    from_date?: string,
    to_date?: string,
    interval: string = '1d'
  ): Promise<PriceHistory[]> {
    const params: Record<string, string | number> = { interval }
    if (from_date) params.from_date = from_date
    if (to_date) params.to_date = to_date
    return apiClient.get(`/assets/${symbol}/historical`, { params })
  },

  getFundamentals(symbol: string): Promise<AssetFundamentals> {
    return apiClient.get(`/assets/${symbol}/fundamentals`)
  },

  getNews(symbol: string, limit: number = 10): Promise<AssetNews> {
    return apiClient.get(`/assets/${symbol}/news`, {
      params: { limit },
    })
  },
}
