'use client'

import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import type { ReactNode } from 'react'

interface ChartWrapperProps {
  children: ReactNode
  fallback?: ReactNode
  className?: string
}

export function ChartWrapper({ children, fallback, className }: ChartWrapperProps) {
  return (
    <ErrorBoundary fallback={fallback} className={className}>
      {children}
    </ErrorBoundary>
  )
}
