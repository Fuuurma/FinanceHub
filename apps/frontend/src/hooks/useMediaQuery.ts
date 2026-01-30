import { useState, useEffect, useCallback, useRef } from 'react'

type MediaQueryCallback = (event: MediaQueryListEvent) => void

interface UseMediaQueryOptions {
  addEventListener?: boolean
  media?: MediaQueryList
}

interface UseMediaQueryReturn {
  matches: boolean
  mediaQuery: MediaQueryList | null
  subscribe: (callback: MediaQueryCallback) => () => void
  getCurrentValue: () => boolean
}

export function useMediaQuery(
  query: string,
  options: UseMediaQueryOptions = {}
): UseMediaQueryReturn {
  const { addEventListener = true } = options

  const [matches, setMatches] = useState<boolean>(() => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia(query).matches
    }
    return false
  })

  const mediaQueryRef = useRef<MediaQueryList | null>(null)
  const listenersRef = useRef<Set<MediaQueryCallback>>(new Set())

  const getMediaQuery = useCallback((): MediaQueryList | null => {
    if (typeof window === 'undefined') {
      return null
    }

    if (options.media) {
      return options.media
    }

    if (!mediaQueryRef.current) {
      mediaQueryRef.current = window.matchMedia(query)
    }

    return mediaQueryRef.current
  }, [query, options.media])

  const handleChange = useCallback((event: MediaQueryListEvent) => {
    setMatches(event.matches)
    listenersRef.current.forEach((callback) => {
      try {
        callback(event)
      } catch {
      }
    })
  }, [])

  useEffect(() => {
    const mql = getMediaQuery()

    if (!mql) {
      return
    }

    setMatches(mql.matches)

    if (addEventListener && mql.addEventListener) {
      mql.addEventListener('change', handleChange)
    } else if (mql.addListener) {
      mql.addListener(handleChange)
    }

    return () => {
      if (mql.removeEventListener) {
        mql.removeEventListener('change', handleChange)
      } else if (mql.removeListener) {
        mql.removeListener(handleChange)
      }
      listenersRef.current.clear()
    }
  }, [query, addEventListener, getMediaQuery, handleChange])

  const subscribe = useCallback((callback: MediaQueryCallback): (() => void) => {
    listenersRef.current.add(callback)

    return () => {
      listenersRef.current.delete(callback)
    }
  }, [])

  const getCurrentValue = useCallback((): boolean => {
    const mql = getMediaQuery()
    return mql ? mql.matches : false
  }, [getMediaQuery])

  return {
    matches,
    mediaQuery: getMediaQuery(),
    subscribe,
    getCurrentValue,
  }
}

export function useBreakpoint(breakpoint: string): boolean {
  const breakpoints: Record<string, string> = {
    xs: '(max-width: 639px)',
    sm: '(min-width: 640px)',
    md: '(min-width: 768px)',
    lg: '(min-width: 1024px)',
    xl: '(min-width: 1280px)',
    '2xl': '(min-width: 1536px)',
    mobile: '(max-width: 767px)',
    tablet: '(min-width: 768px) and (max-width: 1023px)',
    desktop: '(min-width: 1024px)',
    'portrait': '(orientation: portrait)',
    'landscape': '(orientation: landscape)',
    'dark': '(prefers-color-scheme: dark)',
    'light': '(prefers-color-scheme: light)',
  }

  const query = breakpoints[breakpoint] || breakpoint

  return useMediaQuery(query).matches
}

export function useMinWidth(minWidth: number | string): boolean {
  const width = typeof minWidth === 'number' ? `${minWidth}px` : minWidth
  return useMediaQuery(`(min-width: ${width})`).matches
}

export function useMaxWidth(maxWidth: number | string): boolean {
  const width = typeof maxWidth === 'number' ? `${maxWidth}px` : maxWidth
  return useMediaQuery(`(max-width: ${width})`).matches
}

export function useWidthRange(minWidth: number | string, maxWidth: number | string): boolean {
  const min = typeof minWidth === 'number' ? `${minWidth}px` : minWidth
  const max = typeof maxWidth === 'number' ? `${maxWidth}px` : maxWidth
  return useMediaQuery(`(min-width: ${min}) and (max-width: ${max})`).matches
}

export function useOrientation(): 'portrait' | 'landscape' | 'unknown' {
  const isPortrait = useBreakpoint('portrait')
  const isLandscape = useBreakpoint('landscape')

  if (isPortrait) return 'portrait'
  if (isLandscape) return 'landscape'
  return 'unknown'
}

export function usePrefersColorScheme(): 'dark' | 'light' {
  const isDark = useBreakpoint('dark')
  return isDark ? 'dark' : 'light'
}

export function useReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  return useMediaQuery('(prefers-reduced-motion: reduce)').matches
}

export function useHover(): boolean {
  const [isHovered, setIsHovered] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const mediaQuery = window.matchMedia('(hover: hover)')
    setIsHovered(mediaQuery.matches)

    const handleChange = (event: MediaQueryListEvent) => {
      setIsHovered(event.matches)
    }

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange)
    } else {
      mediaQuery.addListener(handleChange)
    }

    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleChange)
      } else {
        mediaQuery.removeListener(handleChange)
      }
    }
  }, [])

  return isHovered
}

export function usePointer(): 'fine' | 'coarse' | 'none' {
  const [pointer, setPointer] = useState<'fine' | 'coarse' | 'none'>('fine')

  useEffect(() => {
    if (typeof window === 'undefined') return

    const mediaQuery = window.matchMedia('(pointer: fine)')
    setPointer(mediaQuery.matches ? 'fine' : 'coarse')

    const handleChange = (event: MediaQueryListEvent) => {
      setPointer(event.matches ? 'fine' : 'coarse')
    }

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange)
    } else {
      mediaQuery.addListener(handleChange)
    }

    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleChange)
      } else {
        mediaQuery.removeListener(handleChange)
      }
    }
  }, [])

  return pointer
}

export function useMediaQuerySync<T>(
  query: string,
  value: T,
  defaultValue: T
): T {
  const { matches } = useMediaQuery(query)
  return matches ? value : defaultValue
}

export default useMediaQuery
