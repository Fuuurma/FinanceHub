/**
 * CoinMarketCap API Client
 * Client for CoinMarketCap API endpoints - crypto listings, info, global metrics, market pairs
 */

import { apiClient } from './client'
import type {
  CryptoListing,
  CryptoInfo,
  GlobalMetrics,
  MarketPair,
  CMCExchangeInfo as ExchangeInfo,
  TrendingCrypto,
  CryptoOHLCV,
} from '@/lib/types/coinmarketcap'

export const coinmarketcapApi = {
  // Listings
  getListings: (start = 1, limit = 100, convert = 'USD') =>
    apiClient.get<{ data: CryptoListing[] }>(`/api/v1/cmc/listings`, {
      params: { start, limit, convert }
    }),

  // Info
  getCryptoInfo: (symbol: string) =>
    apiClient.get<{ data: { [symbol: string]: CryptoInfo } }>(`/api/v1/cmc/info/${symbol}`),

  // Quotes
  getQuotesLatest: (symbol: string, convert = 'USD') =>
    apiClient.get<{ data: { [symbol: string]: any } }>(`/api/v1/cmc/quotes/${symbol}`, {
      params: { convert }
    }),

  // Historical
  getHistoricalData: (id: string, interval = 'day', count = 100) =>
    apiClient.get<{ data: CryptoOHLCV[] }>(`/api/v1/cmc/historical/${id}`, {
      params: { interval, count }
    }),

  // Global Metrics
  getGlobalMetrics: (convert = 'USD') =>
    apiClient.get<{ data: GlobalMetrics }>(`/api/v1/cmc/global`, {
      params: { convert }
    }),

  // Trending
  getTrendingGainersLosers: (sort = 'percent_change_24h', limit = 50) =>
    apiClient.get<{ data: TrendingCrypto[] }>(`/api/v1/cmc/trending`, {
      params: { sort, limit }
    }),

  getTrendingMostVisited: (limit = 50) =>
    apiClient.get<{ data: TrendingCrypto[] }>(`/api/v1/cmc/trending/most-visited`, {
      params: { limit }
    }),

  // Market Pairs
  getMarketPairs: (id: string, limit = 100) =>
    apiClient.get<{ data: MarketPair[] }>(`/api/v1/cmc/pairs/${id}`, {
      params: { limit }
    }),

  // Exchanges
  getExchangeListings: (limit = 100) =>
    apiClient.get<{ data: ExchangeInfo[] }>(`/api/v1/cmc/exchanges`, {
      params: { limit }
    }),

  getExchangeInfo: (slug: string) =>
    apiClient.get<{ data: ExchangeInfo }>(`/api/v1/cmc/exchange/${slug}`),
}
