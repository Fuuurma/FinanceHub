/**
 * All Hooks Export
 * Centralizes all custom hooks for easy importing
 */

export { useAuth } from './useAuth'
export { useLogin } from './useAuth'
export { useRegister } from './useAuth'
export { useLogout } from './useAuth'
export { useAuthCheck } from './useAuth'
export { useCurrentUser } from './useAuth'
export { useIsAuthenticated } from './useAuth'
export { useAuthLoading } from './useAuth'
export { useUpdateProfile } from './useAuth'
export { useRefreshToken } from './useAuth'
export { useClearAuthError } from './useAuth'

export { useAssetData } from './useAssetData'
export { useAssetDetail } from './useAssetData'
export { useAssetPrice } from './useAssetData'
export { useAssetFundamentals } from './useAssetData'
export { useAssetNews } from './useAssetData'
export { useAssets } from './useAssetData'

export { useMarketOverview } from './useMarkets'
export { useMarketMovers } from './useMarkets'
export { useSectors } from './useMarkets'
export { useIndices } from './useMarkets'
export { useTrending } from './useMarkets'

export { useWatchlists } from './useWatchlists'
export { useWatchlist } from './useWatchlists'
export { useCreateWatchlist } from './useWatchlists'
export { useAddToWatchlist } from './useWatchlists'
export { useDeleteWatchlist } from './useWatchlists'

export { usePortfolios } from './usePortfolios'
export { usePortfolioHoldings } from './usePortfolios'
export { useCreatePortfolio } from './usePortfolios'
export { useAddHolding } from './usePortfolios'
export { useDeletePortfolio } from './usePortfolios'
