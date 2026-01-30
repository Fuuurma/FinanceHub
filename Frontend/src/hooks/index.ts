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
export { useAuthError } from './useAuth'
export { useUpdateProfile } from './useAuth'
export { useRefreshToken } from './useAuth'

export { useAssetData, useAssetDetail, useAssetPrice, useAssets } from './useAssetData'

export { useMarketOverview, useMarketMovers, useSectors, useIndices, useTrending } from './useMarkets'

export { useWatchlists, useWatchlist } from './useWatchlists'

export { usePortfolios, usePortfolioHoldings } from './usePortfolios'

export { useDownload, useDownloadFile } from './useDownload'

export { useLocalStorage, useLocalStorageJSON, useLocalStorageNumber, useLocalStorageBoolean, useLocalStorageString } from './useLocalStorage'

export { useMediaQuery, useBreakpoint, useMinWidth, useMaxWidth, useWidthRange, useOrientation, usePrefersColorScheme, useReducedMotion, useHover, usePointer, useMediaQuerySync } from './useMediaQuery'

export { useDebounce, useDebouncedCallback, useDebouncedValue } from './useDebounce'

export { useInterval } from './useInterval'

export { useThrottle, useThrottledValue, useThrottledCallback } from './useThrottle'

export { useClipboard } from './useClipboard'

export { useClickOutside } from './useClickOutside'

export { usePrevious } from './usePrevious'

export { useKeyPress, useKeysPressed } from './useKeyPress'
