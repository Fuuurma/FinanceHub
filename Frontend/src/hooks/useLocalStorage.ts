import { useState, useCallback, useEffect } from 'react'

interface UseLocalStorageOptions<T> {
  defaultValue: T
  serialize?: (value: T) => string
  deserialize?: (raw: string) => T
}

interface UseLocalStorageReturn<T> {
  value: T
  rawValue: string | null
  setValue: (value: T | ((prev: T) => T)) => void
  removeValue: () => void
  error: Error | null
  isHydrated: boolean
}

export function useLocalStorage<T>(
  key: string,
  options: UseLocalStorageOptions<T>
): UseLocalStorageReturn<T>

export function useLocalStorage<T = null>(
  key: string
): UseLocalStorageReturn<T>

export function useLocalStorage<T>(
  key: string,
  options?: Partial<UseLocalStorageOptions<T>> | undefined
): UseLocalStorageReturn<T> {
  const {
    defaultValue = null as T,
    serialize = (value: T) => JSON.stringify(value),
    deserialize = (raw: string) => JSON.parse(raw),
  } = options || {}

  const [isHydrated, setIsHydrated] = useState(false)

  useEffect(() => {
    setIsHydrated(true)
  }, [])

  const [value, setValue] = useState<T>(() => {
    if (typeof window === 'undefined' || !isHydrated) {
      return defaultValue
    }
    try {
      const raw = window.localStorage.getItem(key)
      if (raw === null) {
        return defaultValue
      }
      return deserialize(raw)
    } catch {
      return defaultValue
    }
  })

  const [rawValue, setRawValue] = useState<string | null>(() => {
    if (typeof window === 'undefined' || !isHydrated) {
      return null
    }
    return window.localStorage.getItem(key)
  })

  const [error, setError] = useState<Error | null>(null)

  const updateStorage = useCallback(
    (newValue: T) => {
      try {
        if (newValue === null || newValue === undefined) {
          window.localStorage.removeItem(key)
          setRawValue(null)
        } else {
          const serialized = serialize(newValue)
          window.localStorage.setItem(key, serialized)
          setRawValue(serialized)
        }
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('LocalStorage operation failed'))
      }
    },
    [key, serialize]
  )

  const setStoredValue = useCallback(
    (input: T | ((prev: T) => T)) => {
      const currentValue = value
      const newValue = input instanceof Function ? input(currentValue) : input
      setValue(newValue)
      updateStorage(newValue)
    },
    [value, updateStorage]
  )

  const removeStoredValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key)
      setValue(defaultValue)
      setRawValue(null)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to remove item'))
    }
  }, [key, defaultValue])

  useEffect(() => {
    if (!isHydrated) return

    const handleStorage = (event: StorageEvent) => {
      if (event.key === key) {
        try {
          if (event.newValue === null) {
            setValue(defaultValue)
            setRawValue(null)
          } else {
            setValue(deserialize(event.newValue))
            setRawValue(event.newValue)
          }
        } catch {
          setValue(defaultValue)
        }
      }
    }

    window.addEventListener('storage', handleStorage)
    return () => window.removeEventListener('storage', handleStorage)
  }, [key, defaultValue, deserialize, isHydrated])

  return {
    value,
    rawValue,
    setValue: setStoredValue,
    removeValue: removeStoredValue,
    error,
    isHydrated,
  }
}

export function useLocalStorageJSON<T extends object>(
  key: string,
  defaultValue: T
) {
  return useLocalStorage<T>(key, {
    defaultValue,
    serialize: (value) => JSON.stringify(value, null, 2),
    deserialize: (raw) => JSON.parse(raw),
  })
}

export function useLocalStorageNumber(key: string, defaultValue: number) {
  return useLocalStorage<number>(key, {
    defaultValue,
    serialize: String,
    deserialize: (raw) => {
      const parsed = parseFloat(raw)
      return isNaN(parsed) ? defaultValue : parsed
    },
  })
}

export function useLocalStorageBoolean(key: string, defaultValue: boolean) {
  return useLocalStorage<boolean>(key, {
    defaultValue,
    serialize: String,
    deserialize: (raw) => raw === 'true',
  })
}

export function useLocalStorageString(key: string, defaultValue: string) {
  return useLocalStorage<string>(key, {
    defaultValue,
    serialize: (value) => value,
    deserialize: (raw) => raw,
  })
}

export default useLocalStorage
