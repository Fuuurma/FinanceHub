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

// ================= REFERENCE DATA TYPES (I7) =================

export interface Sector {
  id: string
  code: string
  name: string
  description?: string
  gics_code?: number
  industry_count: number
}

export interface SectorDetail extends Sector {
  industries: Industry[]
}

export interface Industry {
  id: string
  code: string
  name: string
  sector_id: string
  sector_name: string
  sector_code: string
  gics_code?: number
  asset_count?: number
}

export interface Timezone {
  id: string
  name: string
  utc_offset: number
  utc_offset_str: string
  abbreviation: string
  is_dst_observed: boolean
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

  // ================= REFERENCE DATA ENDPOINTS (I7) =================

  getSectors(activeOnly: boolean = true): Promise<Sector[]> {
    return apiClient.get<Sector[]>('/reference/sectors', {
      params: { active_only: Number(activeOnly) },
    })
  },

  getSector(sectorId: string): Promise<SectorDetail> {
    return apiClient.get<SectorDetail>(`/reference/sectors/${sectorId}`)
  },

  getIndustries(sectorCode?: string, activeOnly: boolean = true): Promise<Industry[]> {
    const params: Record<string, string | number> = { active_only: Number(activeOnly) }
    if (sectorCode) params.sector_code = sectorCode
    return apiClient.get<Industry[]>('/reference/industries', { params })
  },

  getIndustry(industryId: string): Promise<Industry> {
    return apiClient.get<Industry>(`/reference/industries/${industryId}`)
  },

  getTimezones(activeOnly: boolean = true): Promise<Timezone[]> {
    return apiClient.get<Timezone[]>('/reference/timezones', {
      params: { active_only: Number(activeOnly) },
    })
  },

  getTimezone(timezoneId: string): Promise<Timezone> {
    return apiClient.get<Timezone>(`/reference/timezones/${timezoneId}`)
  },

  searchSectors(query: string): Promise<Array<{ id: string; code: string; name: string }>> {
    return apiClient.get<Array<{ id: string; code: string; name: string }>>('/reference/sectors/search', {
      params: { q: query },
    })
  },

  searchIndustries(query: string, sectorCode?: string): Promise<Array<{
    id: string
    code: string
    name: string
    sector_code: string
    sector_name: string
  }>> {
    const params: Record<string, string> = { q: query }
    if (sectorCode) params.sector_code = sectorCode
    return apiClient.get('/reference/industries/search', { params })
  },
}
