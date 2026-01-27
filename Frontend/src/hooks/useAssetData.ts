/**
 * Data Fetching Hooks
 * Provides convenient hooks for fetching data from the API
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import type { 
  Asset, 
  AssetDetail, 
  PriceHistory, 
  AssetFilter,
  MarketOverview,
  MarketMover,
  SectorPerformance,
  MarketIndex,
  MarketType,
  TimeInterval,
  MoverType
} from '@/lib/types'

import * as assetsApi from '@/lib/api/assets'
import * as marketsApi from '@/lib/api/markets'
import * as userDataApi from '@/lib/api/userData'

const STALE_TIME = 5 * 60 * 1000 // 5 minutes
const CACHE_TIME = 10 * 60 * 1000 // 10 minutes

export function useAssetData(symbol: string, interval: TimeInterval = '1d') {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['asset', symbol, interval],
    queryFn: () => assetsApi.getHistorical(symbol, interval),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function useAssetDetail(symbol: string) {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['asset', symbol, 'detail'],
    queryFn: () => assetsApi.get(symbol),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function useAssetPrice(symbol: string) {
  const { token } =Auth()
  
  return useQuery({
    queryKey: ['asset', symbol, 'price'],
    queryFn: () => assetsApi.getPrice(symbol),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME * 3, // Price data cached longer
    refetchInterval: 30, // Refetch price every 30s
  })
}

export function useAssetFundamentals(symbol: string) {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['asset', symbol, 'fundamentals'],
    queryFn: () => assetsApi.getFundamentals(symbol),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME * 6, // Fundamentals cached longer
  })
}

export function useAssetNews(symbol: string, limit: number = 10) {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['asset', symbol, 'news', limit],
    queryFn: () => assetsApi.getNews(symbol, limit),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME * 3,
  })
}

export function useAssets(filter: AssetFilter, limit: number = 20, page: number = 1) {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['assets', 'filter', 'limit', 'page'],
    queryFn: () => assetsApi.list(filter, limit, (page - 1) * limit),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function useMarketOverview() {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['market', 'overview'],
    queryFn: () => marketsApi.getOverview(),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function useMarketMovers(type: MoverType = 'gainers', limit: number = 10) {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['market', 'movers', type, limit],
    queryFn: () => marketsApi.getMovers(type, limit),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function useSectors() {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['market', 'sectors'],
    queryFn: () => marketsApi.getSectors(),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function useIndices() {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['market', 'indices'],
    queryFn: () => marketsApi.getIndices(),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function useTrending(assetType?: string, limit: number = 20) {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['market', 'trending', assetType, limit],
    queryFn: () => marketsApi.getTrending(assetType, limit),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function useWatchlists() {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['data', 'watchlists'],
    queryFn: () => userDataApi.getWatchlists(),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function useAlerts(activeOnly: boolean = false) {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['data', 'alerts', 'activeOnly'],
    queryFn: () => userDataApi.getAlerts(activeOnly),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function usePortfolios() {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['data', 'portfolios'],
    queryFn: () => userDataApi.getPortfolios(),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function usePortfolioHoldings(portfolioId: string) {
  const { token } = useAuth()
  
  return useQuery({
    queryKey: ['data', 'portfolios', 'holdings', portfolioId],
    queryFn: () => userDataApi.getPortfolioHoldings(portfolioId),
    enabled: !!token,
    staleTime: STALE_TIME,
    cacheTime: CACHE_TIME,
  })
}

export function useCreateWatchlist() {
  const queryClient = useQueryClient()
  const { token } = useAuth()
  
  return useMutation({
    mutationFn: (data: { name: string }) => userDataApi.createWatchlist(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['data', 'watchlists'])
    },
    })
}

export function useAddToWatchlist() {
  const queryClient = useQueryClient()
  const { token } = useAuth()
  
  return useMutation({
    mutationFn: ({ watchlistId, assetSymbols }: { watchlistId: string; assetSymbols: string[] }) =>
      userDataApi.addAssetsToWatchlist(watchlistId, { assetSymbols }),
    onSuccess: () => {
      queryClient.invalidateQueries(['data', 'watchlists'])
    },
  })
}

export function useDeleteWatchlist() {
  const queryClient = useQueryClient()
  const { token } = useAuth()
  
  return useMutation({
    mutationFn: (watchlistId: string) =>
      userDataApi.deleteWatchlist(watchlistId),
    onSuccess: () => {
      queryClient.invalidateQueries(['data', 'watchlists'])
    },
  })
}

export function useCreateAlert() {
  const queryClient = useQueryClient()
  const { token } = useAuth()
  
  return useMutation({
    mutationFn: (data: { assetSymbol: string; condition: string; threshold: number }) =>
      userDataApi.createAlert(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['data', 'alerts'])
    },
  })
}

export function useDeleteAlert() {
  const queryClient = useQueryClient()
  const { token } = useAuth()
  
  return useMutation({
    mutationFn: (alertId: string) => userDataApi.deleteAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries(['data', 'alerts'])
    },
  })
}

export function useCreatePortfolio() {
  const queryClient = useQueryClient()
  const { token } = useAuth()
  
  return useMutation({
    mutationFn: (data: { name: string }) =>
      userDataApi.createPortfolio(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['data', 'portfolios'])
    },
  })
}

export function useAddHolding() {
  const queryClient = useQueryClient()
  const { token } = useAuth()
  
  return useMutation({
    mutationFn: ({ portfolioId, data }: { portfolioId: string; data: any }) =>
      userDataApi.addHolding(portfolioId, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['data', 'portfolios'])
    },
  })
}

export function useDeletePortfolio() {
  const queryClient = useQueryClient()
  const { token } = useAuth()
  
  return useMutation({
    mutationFn: (portfolioId: string) =>
      userDataApi.deletePortfolio(portfolioId),
    onSuccess: () => {
      queryClient.invalidateQueries(['data', 'portfolios'])
    },
  })
}
