'use client'

import { Component, ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { RefreshCw, AlertTriangle, Home, Bug } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: { componentStack: string }) => void
  className?: string
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: { componentStack: string } | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: { componentStack: string }) {
    this.setState({ errorInfo })
    this.props.onError?.(error, errorInfo)
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <DefaultErrorFallback
          error={this.state.error}
          onRetry={this.handleRetry}
          className={this.props.className}
        />
      )
    }

    return this.props.children
  }
}

interface DefaultErrorFallbackProps {
  error: Error | null
  onRetry: () => void
  className?: string
}

function DefaultErrorFallback({ error, onRetry, className }: DefaultErrorFallbackProps) {
  const errorMessage = error?.message || 'An unknown error occurred'
  const errorStack = error?.stack || ''

  return (
    <div className={cn('p-4 md:p-6', className)}>
      <Card className="max-w-lg mx-auto border-destructive/50">
        <CardHeader className="bg-destructive/10 border-b border-destructive/20">
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Something went wrong
          </CardTitle>
          <CardDescription>
            An error occurred while rendering this component.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-4 space-y-4">
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm font-medium text-foreground">{errorMessage}</p>
          </div>

          {process.env.NODE_ENV === 'development' && errorStack && (
            <details className="p-3 bg-muted rounded-lg">
              <summary className="text-sm font-medium cursor-pointer text-muted-foreground">
                Error Stack Trace
              </summary>
              <pre className="mt-2 p-2 bg-background rounded text-xs overflow-auto max-h-40">
                {errorStack}
              </pre>
            </details>
          )}

          <div className="flex flex-col sm:flex-row gap-2">
            <Button onClick={onRetry} className="flex-1">
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
            <Button variant="outline" onClick={() => window.location.href = '/'} className="flex-1">
              <Home className="h-4 w-4 mr-2" />
              Go Home
            </Button>
          </div>

          <p className="text-xs text-muted-foreground text-center">
            If this problem persists, please contact support or report this issue.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

interface AsyncErrorBoundaryProps {
  children: ReactNode
  loading?: ReactNode
  error?: ReactNode
  onRetry?: () => void
  className?: string
}

export function AsyncErrorBoundary({
  children,
  loading,
  error,
  onRetry,
  className,
}: AsyncErrorBoundaryProps) {
  return (
    <ErrorBoundary
      fallback={
        error || (
          <DefaultErrorFallback
            error={null}
            onRetry={onRetry || (() => window.location.reload())}
            className={className}
          />
        )
      }
    >
      {children}
    </ErrorBoundary>
  )
}

interface SuspenseErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  className?: string
}

export function SuspenseErrorBoundary({
  children,
  fallback = <LoadingSkeleton />,
  className,
}: SuspenseErrorBoundaryProps) {
  return (
    <ErrorBoundary
      fallback={
        <Card className={cn('max-w-md mx-auto', className)}>
          <CardContent className="py-8 text-center">
            <AlertTriangle className="h-8 w-8 mx-auto text-destructive mb-2" />
            <p className="text-muted-foreground">Failed to load content</p>
            <Button variant="outline" onClick={() => window.location.reload()} className="mt-4">
              <RefreshCw className="h-4 w-4 mr-2" />
              Reload Page
            </Button>
          </CardContent>
        </Card>
      }
    >
      {children}
    </ErrorBoundary>
  )
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-4 bg-muted rounded w-3/4" />
      <div className="h-4 bg-muted rounded w-1/2" />
      <div className="h-32 bg-muted rounded" />
      <div className="h-4 bg-muted rounded w-5/6" />
    </div>
  )
}

export default ErrorBoundary
