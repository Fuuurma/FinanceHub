import { useEffect, useRef, useCallback } from 'react'

export function useInterval(
  callback: () => void,
  delay: number | null,
  immediate: boolean = false
) {
  const savedCallback = useRef<() => void>(() => {})

  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  useEffect(() => {
    if (delay === null) {
      return
    }

    if (immediate) {
      savedCallback.current?.()
    }

    const tick = () => {
      savedCallback.current?.()
    }

    const id = setInterval(tick, delay)

    return () => clearInterval(id)
  }, [delay, immediate])
}

export function useTimeout(
  callback: () => void,
  delay: number | null
) {
  const savedCallback = useRef<() => void>(() => {})

  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  useEffect(() => {
    if (delay === null) {
      return
    }

    const id = setTimeout(() => {
      savedCallback.current?.()
    }, delay)

    return () => clearTimeout(id)
  }, [delay])
}

export function useThrottle<T extends (...args: unknown[]) => unknown>(
  callback: T,
  delay: number = 500
): T {
  const lastRun = useRef<Date>(new Date())
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  return useCallback(
    (...args: Parameters<T>) => {
      const now = new Date()
      const timeElapsed = now.getTime() - lastRun.current.getTime()

      if (timeElapsed >= delay) {
        lastRun.current = now
        callback(...args)
      } else {
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current)
        }

        timeoutRef.current = setTimeout(() => {
          lastRun.current = new Date()
          callback(...args)
        }, delay - timeElapsed)
      }
    },
    [callback, delay]
  ) as T
}
