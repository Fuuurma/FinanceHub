'use client'

import { useState, useCallback } from 'react'
import { RefreshCw, AlertCircle, Home, Mail } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

export interface RetryFallbackProps {
  error: Error | null
  resetErrorBoundary?: () => void
  message?: string
  title?: string
  className?: string
  showHome?: boolean
  showContact?: boolean
  onHome?: () => void
  onContact?: () => void
}

export function RetryFallback({
  error,
  resetErrorBoundary,
  message = 'Something went wrong',
  title = 'Oops! An error occurred',
  className,
  showHome = false,
  showContact = false,
  onHome,
  onContact,
}: RetryFallbackProps) {
  const [isRetrying, setIsRetrying] = useState(false)

  const handleRetry = useCallback(async () => {
    if (!resetErrorBoundary) return
    setIsRetrying(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      resetErrorBoundary()
    } finally {
      setIsRetrying(false)
    }
  }, [resetErrorBoundary])

  const errorMessage = error?.message || message

  return (
    <Card className={cn('max-w-md mx-auto mt-8', className)}>
      <CardHeader className="text-center">
        <div className="mx-auto w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mb-4">
          <AlertCircle className="h-6 w-6 text-red-600" />
        </div>
        <CardTitle className="text-lg">{title}</CardTitle>
        <CardDescription className="text-sm text-muted-foreground">
          {errorMessage}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {resetErrorBoundary && (
          <Button
            onClick={handleRetry}
            disabled={isRetrying}
            className="w-full"
            variant="default"
          >
            <RefreshCw className={cn('h-4 w-4 mr-2', isRetrying && 'animate-spin')} />
            {isRetrying ? 'Retrying...' : 'Try Again'}
          </Button>
        )}
        
        {showHome && (
          <Button
            onClick={onHome}
            variant="outline"
            className="w-full"
          >
            <Home className="h-4 w-4 mr-2" />
            Go to Homepage
          </Button>
        )}
        
        {showContact && (
          <Button
            onClick={onContact}
            variant="ghost"
            className="w-full"
          >
            <Mail className="h-4 w-4 mr-2" />
            Contact Support
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

interface ErrorCardProps {
  title?: string
  description?: string
  onRetry?: () => void
  retryLabel?: string
  className?: string
}

export function ErrorCard({
  title = 'Error',
  description = 'An unexpected error occurred',
  onRetry,
  retryLabel = 'Retry',
  className,
}: ErrorCardProps) {
  return (
    <Card className={cn('border-red-200 bg-red-50', className)}>
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          <div className="p-2 rounded-full bg-red-100">
            <AlertCircle className="h-5 w-5 text-red-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-red-800">{title}</h3>
            <p className="text-sm text-red-600 mt-1">{description}</p>
            {onRetry && (
              <Button
                size="sm"
                variant="outline"
                onClick={onRetry}
                className="mt-3 border-red-300 text-red-700 hover:bg-red-100"
              >
                <RefreshCw className="h-3 w-3 mr-2" />
                {retryLabel}
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

interface LoadingRetryProps {
  isLoading: boolean
  error: Error | null
  onRetry: () => void
  children: React.ReactNode
  loadingLabel?: string
  retryLabel?: string
  className?: string
}

export function LoadingRetry({
  isLoading,
  error,
  onRetry,
  children,
  loadingLabel = 'Loading...',
  retryLabel = 'Retry',
  className,
}: LoadingRetryProps) {
  if (isLoading) {
    return (
      <div className={cn('flex items-center justify-center py-8', className)}>
        <div className="flex flex-col items-center gap-2">
          <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">{loadingLabel}</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={cn('py-8', className)}>
        <ErrorCard
          description={error.message}
          onRetry={onRetry}
          retryLabel={retryLabel}
        />
      </div>
    )
  }

  return <>{children}</>
}

export default RetryFallback
