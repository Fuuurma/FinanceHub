'use client'

import { useEffect, useRef, useCallback, useState } from 'react'
import { Lock, Unlock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface FocusTrapProps {
  children: React.ReactNode
  active?: boolean
  className?: string
  showToggle?: boolean
  initialFocus?: boolean
  returnFocus?: boolean
}

export function FocusTrap({
  children,
  active = true,
  className,
  showToggle = false,
  initialFocus = true,
  returnFocus = true
}: FocusTrapProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const previousActiveElement = useRef<HTMLElement | null>(null)
  const [isActive, setIsActive] = useState(active)

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (!isActive || e.key !== 'Tab') return

    const focusableElements = containerRef.current?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )

    if (!focusableElements || focusableElements.length === 0) {
      e.preventDefault()
      return
    }

    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        e.preventDefault()
        lastElement.focus()
      }
    } else {
      if (document.activeElement === lastElement) {
        e.preventDefault()
        firstElement.focus()
      }
    }
  }, [isActive])

  useEffect(() => {
    if (!isActive) return

    previousActiveElement.current = document.activeElement as HTMLElement

    const focusableElements = containerRef.current?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )

    if (initialFocus && focusableElements && focusableElements.length > 0) {
      focusableElements[0].focus()
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      if (returnFocus && previousActiveElement.current) {
        previousActiveElement.current.focus()
      }
    }
  }, [isActive, handleKeyDown, initialFocus, returnFocus])

  if (!isActive) {
    return <div className={className}>{children}</div>
  }

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      {children}
      {showToggle && (
        <div className="absolute top-2 right-2 z-50">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsActive(!isActive)}
            className="text-xs"
            aria-label={isActive ? 'Disable focus trap' : 'Enable focus trap'}
          >
            {isActive ? <Lock className="w-3 h-3" /> : <Unlock className="w-3 h-3" />}
          </Button>
        </div>
      )}
    </div>
  )
}

export default FocusTrap
