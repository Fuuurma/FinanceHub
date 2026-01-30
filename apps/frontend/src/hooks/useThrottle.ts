import { useEffect, useRef, useCallback, useState } from 'react'

export function useThrottle<T extends (...args: unknown[]) => unknown>(
  callback: T,
  delay: number = 200
): T {
  const lastRan = useRef<number>(Date.now())

  return useCallback(
    (...args: Parameters<T>) => {
      if (Date.now() - lastRan.current >= delay) {
        callback(...args)
        lastRan.current = Date.now()
      }
    },
    [callback, delay]
  ) as T
}

export function useThrottledValue<T>(value: T, delay: number = 200): T {
  const [throttledValue, setThrottledValue] = useState<T>(value)
  const previousTime = useRef<number>(Date.now())

  useEffect(() => {
    const now = Date.now()
    const remaining = delay - (now - previousTime.current)

    if (remaining <= 0 || now - previousTime.current >= delay) {
      setThrottledValue(value)
      previousTime.current = now
    } else {
      const timeoutId = setTimeout(() => {
        setThrottledValue(value)
        previousTime.current = Date.now()
      }, remaining)

      return () => clearTimeout(timeoutId)
    }
  }, [value, delay])

  return throttledValue
}

export function useThrottledCallback<T extends (...args: unknown[]) => unknown>(
  callback: T,
  delay: number = 200
): T {
  const timeoutId = useRef<ReturnType<typeof setTimeout> | null>(null)
  const lastArgs = useRef<Parameters<T> | null>(null)
  const leading = useRef<boolean>(true)

  const clearThrottle = useCallback(() => {
    if (timeoutId.current) {
      clearTimeout(timeoutId.current)
      timeoutId.current = null
    }
    lastArgs.current = null
  }, [])

  useEffect(() => {
    return () => clearThrottle()
  }, [clearThrottle])

  return useCallback(
    (...args: Parameters<T>) => {
      lastArgs.current = args

      if (!timeoutId.current) {
        callback(...args)
        leading.current = false

        timeoutId.current = setTimeout(() => {
          timeoutId.current = null
          if (lastArgs.current !== null) {
            callback(...lastArgs.current)
          }
        }, delay)
      }
    },
    [callback, delay]
  ) as T
}

export default useThrottle
