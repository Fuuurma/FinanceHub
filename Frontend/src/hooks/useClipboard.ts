import { useState, useCallback } from 'react'

interface UseClipboardOptions {
  timeout?: number
}

interface UseClipboardReturn {
  copy: (text: string) => Promise<boolean>
  copied: boolean
  error: Error | null
  reset: () => void
}

export function useClipboard(options: UseClipboardOptions = {}): UseClipboardReturn {
  const { timeout = 2000 } = options
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const copy = useCallback(async (text: string): Promise<boolean> => {
    setError(null)
    setCopied(false)

    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text)
      } else {
        const textArea = document.createElement('textarea')
        textArea.value = text
        textArea.style.position = 'fixed'
        textArea.style.left = '-999999px'
        textArea.style.top = '-999999px'
        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()

        const successful = document.execCommand('copy')
        document.body.removeChild(textArea)

        if (!successful) {
          throw new Error('Failed to copy to clipboard')
        }
      }

      setCopied(true)

      if (timeout > 0) {
        setTimeout(() => setCopied(false), timeout)
      }

      return true
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to copy')
      setError(error)
      return false
    }
  }, [timeout])

  const reset = useCallback(() => {
    setCopied(false)
    setError(null)
  }, [])

  return { copy, copied, error, reset }
}
