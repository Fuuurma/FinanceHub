'use client'

import { useState, useEffect, useCallback } from 'react'
import { SkipForward } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface SkipLinkProps {
  targetId?: string
  targetRef?: React.RefObject<HTMLElement>
  label?: string
  className?: string
}

export function SkipLink({
  targetId = 'main-content',
  targetRef,
  label = 'Skip to main content',
  className
}: SkipLinkProps) {
  const [isFocused, setIsFocused] = useState(false)

  const handleClick = useCallback(() => {
    const target = targetRef?.current || document.getElementById(targetId)
    if (target) {
      target.tabIndex = -1
      target.focus()
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [targetId, targetRef])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && isFocused) {
        handleClick()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isFocused, handleClick])

  return (
    <a
      href={`#${targetId}`}
      onClick={(e) => {
        e.preventDefault()
        handleClick()
      }}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      className={cn(
        'sr-only focus:not-sr-only',
        'focus:absolute focus:top-4 focus:left-4 focus:z-50',
        'focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground',
        'focus:rounded-md focus:font-medium focus:shadow-lg',
        'transition-all focus:translate-y-0 focus:opacity-100',
        '-translate-y-2 opacity-0',
        className
      )}
      aria-label={label}
    >
      <SkipForward className="w-4 h-4 mr-2 inline" />
      {label}
    </a>
  )
}

export default SkipLink
