import { useEffect, useRef } from 'react'
import { type CallbackRef } from './utility-types'

export function useClickOutside<T extends HTMLElement = HTMLElement>(
  callback: (event: MouseEvent | TouchEvent) => void
): CallbackRef<T> {
  const ref = useRef<T>(null)

  useEffect(() => {
    const handler = (event: MouseEvent | TouchEvent) => {
      const element = ref.current
      if (!element || element.contains(event.target as Node)) {
        return
      }
      callback(event)
    }

    document.addEventListener('mousedown', handler)
    document.addEventListener('touchstart', handler)

    return () => {
      document.removeEventListener('mousedown', handler)
      document.removeEventListener('touchstart', handler)
    }
  }, [callback])

  return ref
}
