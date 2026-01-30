'use client'

import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import type { ReactNode } from 'react'

interface PageErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: { componentStack: string }) => void
}

export function PageErrorBoundary({ children, fallback, onError }: PageErrorBoundaryProps) {
  return (
    <ErrorBoundary
      fallback={fallback}
      onError={onError}
    >
      {children}
    </ErrorBoundary>
  )
}
