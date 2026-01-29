/**
 * Market Overview API
 * All market overview and trends API calls
 */

import { apiClient } from './client'
import type { MarketOverview, MarketIndices, MarketMovers, MarketTrends, AssetDistribution } from '@/lib/types'

interface SentimentData {
  sentiment: {
    strength: number
    trending_sectors: Array<{ sector: string; avg_change_24h: number }>
  }
}

interface TreasuryYield {
  maturity: string
  rate: number
  date: string
}

export const marketOverviewApi = {
  getMarketOverview(): Promise<MarketOverview> {
    return apiClient.get<MarketOverview>('/market/overview')
  },

  getMarketIndices(): Promise<MarketIndices> {
    return apiClient.get<MarketIndices>('/market/indices')
  },

  getMarketMovers(assetType: 'equities' | 'crypto' | 'all' = 'all', limit: number = 20): Promise<MarketMovers> {
    return apiClient.get<MarketMovers>('/market/movers', {
      params: { asset_type: assetType, limit },
    })
  },

  getTrendingAssets(
    assetType: 'equities' | 'crypto' | 'commodities' | 'all' = 'all',
    limit: number = 10,
    timePeriod: '1h' | '24h' | '7d' | '30d' = '24h'
  ): Promise<MarketTrends> {
    return apiClient.get<MarketTrends>('/market/trending', {
      params: { asset_type: assetType, limit, time_period: timePeriod },
    })
  },

  getAssetDistribution(): Promise<AssetDistribution> {
    return apiClient.get<AssetDistribution>('/market/distribution')
  },

  getMarketSentiment(): Promise<SentimentData> {
    return apiClient.get<SentimentData>('/market/sentiment')
  },

  getTreasuryYields(years: number = 5): Promise<TreasuryYield[]> {
    return apiClient.get<TreasuryYield[]>('/market/treasury-yields', {
      params: { years },
    })
  },
}
