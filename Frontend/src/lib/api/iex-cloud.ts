/**
 * IEX Cloud API Client
 * Client for IEX Cloud API endpoints - comprehensive stock fundamentals, earnings, ownership data
 */

import { apiClient } from './client'
import type {
  CompanyInfo,
  KeyStats,
  AdvancedStats,
  EarningsReport,
  AnalystEstimates,
  InstitutionalHolder,
  InsiderTransaction,
  PeerCompany,
  MarketMover,
  SectorPerformance,
  ChartDataPoint,
  Quote,
  Dividend,
  StockSplit,
} from '@/lib/types/iex-cloud'

export const iexCloudApi = {
  // Company & Profile
  getCompanyInfo: (symbol: string) =>
    apiClient.get<CompanyInfo>(`/api/v1/iex/company/${symbol}`),

  // Pricing
  getQuote: (symbol: string) =>
    apiClient.get<Quote>(`/api/v1/iex/quote/${symbol}`),

  getQuotes: (symbols: string[]) =>
    apiClient.post<Quote[]>(`/api/v1/iex/quotes`, { symbols }),

  getChart: (symbol: string, period: string = '1y') =>
    apiClient.get<ChartDataPoint[]>(`/api/v1/iex/chart/${symbol}`, {
      params: { period }
    }),

  // Statistics
  getKeyStats: (symbol: string) =>
    apiClient.get<KeyStats>(`/api/v1/iex/keystats/${symbol}`),

  getAdvancedStats: (symbol: string) =>
    apiClient.get<AdvancedStats>(`/api/v1/iex/advancedstats/${symbol}`),

  // Earnings
  getEarnings: (symbol: string, period: 'quarterly' | 'annual' = 'annual', last: number = 4) =>
    apiClient.get<EarningsReport[]>(`/api/v1/iex/earnings/${symbol}`, {
      params: { period, last }
    }),

  getEstimates: (symbol: string, period: 'annual' | 'quarterly' = 'annual', last: number = 4) =>
    apiClient.get<AnalystEstimate[]>(`/api/v1/iex/estimates/${symbol}`, {
      params: { period, last }
    }),

  // Ownership
  getInsiderTransactions: (symbol: string) =>
    apiClient.get<InsiderTransaction[]>(`/api/v1/iex/insiders/${symbol}`),

  getInstitutionalOwnership: (symbol: string) =>
    apiClient.get<InstitutionalHolder[]>(`/api/v1/iex/institutions/${symbol}`),

  // Peers
  getPeers: (symbol: string) =>
    apiClient.get<PeerCompany[]>(`/api/v1/iex/peers/${symbol}`),

  // Market Data
  getMarketList: (listType: 'mostactive' | 'gainers' | 'losers' = 'mostactive') =>
    apiClient.get<MarketMover[]>(`/api/v1/iex/marketlist`, {
      params: { list_type: listType }
    }),

  getSectorPerformance: () =>
    apiClient.get<SectorPerformance[]>(`/api/v1/iex/sectorperformance`),

  // Dividends
  getDividends: (symbol: string, range: string = '1y') =>
    apiClient.get<Dividend[]>(`/api/v1/iex/dividends/${symbol}`, {
      params: { range }
    }),

  // Splits
  getSplits: (symbol: string, range: string = '5y') =>
    apiClient.get<StockSplit[]>(`/api/v1/iex/splits/${symbol}`, {
      params: { range }
    }),
}
