import { useState, useEffect, useCallback } from 'react'

type KeyFilter = string | string[] | ((event: KeyboardEvent) => boolean)

interface UseKeyPressOptions {
  target?: Window | HTMLElement
  event?: 'keydown' | 'keyup' | 'keypress'
  preventDefault?: boolean
}

export function useKeyPress(
  keyFilter: KeyFilter,
  callback: (event: KeyboardEvent) => void,
  options: UseKeyPressOptions = {}
): boolean {
  const { target = window, event = 'keydown', preventDefault = false } = options
  const [pressed, setPressed] = useState(false)

  const matchesKey = useCallback((event: KeyboardEvent): boolean => {
    if (typeof keyFilter === 'function') {
      return keyFilter(event)
    }

    const keys = Array.isArray(keyFilter) ? keyFilter : [keyFilter]
    return keys.some(key => {
      if (key.length === 1) {
        return event.key.toLowerCase() === key.toLowerCase()
      }
      return event.key === key
    })
  }, [keyFilter])

  useEffect(() => {
    const handler = (event: Event) => {
      const keyboardEvent = event as KeyboardEvent
      const isMatch = matchesKey(keyboardEvent)

      if (isMatch) {
        if (preventDefault) {
          keyboardEvent.preventDefault()
        }
        setPressed(true)
        callback(keyboardEvent)
      }
    }

    const handleUp = () => setPressed(false)

    const element = target instanceof Window ? document : target
    element.addEventListener(event, handler)
    element.addEventListener('keyup', handleUp)

    return () => {
      element.removeEventListener(event, handler)
      element.removeEventListener('keyup', handleUp)
    }
  }, [target, event, keyFilter, callback, matchesKey, preventDefault])

  return pressed
}

export function useKeysPressed(): Record<string, boolean> {
  const [pressedKeys, setPressedKeys] = useState<Record<string, boolean>>({})

  useEffect(() => {
    const handleKeyDown = (event: Event) => {
      const keyboardEvent = event as KeyboardEvent
      setPressedKeys(prev => ({ ...prev, [keyboardEvent.key.toLowerCase()]: true }))
    }

    const handleKeyUp = (event: Event) => {
      const keyboardEvent = event as KeyboardEvent
      setPressedKeys(prev => {
        const next = { ...prev }
        delete next[keyboardEvent.key.toLowerCase()]
        return next
      })
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [])

  return pressedKeys
}
