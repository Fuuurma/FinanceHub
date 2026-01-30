'use client'

import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

interface LoadingOverlayProps {
  isLoading: boolean
  children: React.ReactNode
  message?: string
  className?: string
  overlayClassName?: string
}

export function LoadingOverlay({
  isLoading,
  children,
  message = 'Loading...',
  className,
  overlayClassName,
}: LoadingOverlayProps) {
  return (
    <div className={cn('relative', className)}>
      {children}
      {isLoading && (
        <div
          className={cn(
            'absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50',
            overlayClassName
          )}
        >
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            {message && (
              <p className="text-sm text-muted-foreground">{message}</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

interface FullScreenLoaderProps {
  message?: string
  className?: string
}

export function FullScreenLoader({
  message = 'Loading...',
  className,
}: FullScreenLoaderProps) {
  return (
    <div
      className={cn(
        'fixed inset-0 bg-background flex items-center justify-center z-50',
        className
      )}
    >
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="h-6 w-6 rounded-full border-2 border-primary/30 animate-pulse" />
          </div>
        </div>
        {message && (
          <p className="text-lg text-muted-foreground animate-pulse">{message}</p>
        )}
      </div>
    </div>
  )
}

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  }

  return (
    <Loader2
      className={cn('animate-spin text-primary', sizeClasses[size], className)}
    />
  )
}

interface LoadingDotsProps {
  className?: string
}

export function LoadingDots({ className }: LoadingDotsProps) {
  return (
    <div className={cn('flex items-center gap-1', className)}>
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
        <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
      </span>
      <span className="relative flex h-2 w-2 delay-75">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
        <span className="relative inline-flex rounded-full h-2 w-2 bg-primary delay-75"></span>
      </span>
      <span className="relative flex h-2 w-2 delay-150">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
        <span className="relative inline-flex rounded-full h-2 w-2 bg-primary delay-150"></span>
      </span>
    </div>
  )
}

interface SkeletonLoaderProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  style?: React.CSSProperties
}

export function SkeletonLoader({
  className,
  variant = 'text',
  style,
}: SkeletonLoaderProps) {
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  }

  return (
    <div
      className={cn(
        'animate-pulse bg-muted',
        variantClasses[variant],
        className
      )}
      style={style}
    />
  )
}

interface CardSkeletonProps {
  showHeader?: boolean
  showContent?: boolean
  showFooter?: boolean
  className?: string
}

export function CardSkeleton({
  showHeader = true,
  showContent = true,
  showFooter = false,
  className,
}: CardSkeletonProps) {
  return (
    <div className={cn('space-y-4 p-4 border rounded-lg', className)}>
      {showHeader && (
        <div className="space-y-2">
          <SkeletonLoader className="h-5 w-3/4" variant="text" />
          <SkeletonLoader className="h-4 w-1/2" variant="text" />
        </div>
      )}
      {showContent && (
        <div className="space-y-2">
          <SkeletonLoader className="h-20 w-full" variant="rectangular" />
          <div className="flex gap-2">
            <SkeletonLoader className="h-8 w-20" variant="rectangular" />
            <SkeletonLoader className="h-8 w-20" variant="rectangular" />
          </div>
        </div>
      )}
      {showFooter && (
        <div className="flex justify-end gap-2 pt-2 border-t">
          <SkeletonLoader className="h-8 w-20" variant="rectangular" />
          <SkeletonLoader className="h-8 w-20" variant="rectangular" />
        </div>
      )}
    </div>
  )
}

interface TableRowSkeletonProps {
  columns: number
  showActions?: boolean
  className?: string
}

export function TableRowSkeleton({
  columns,
  showActions = false,
  className,
}: TableRowSkeletonProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-4 p-3 border-b last:border-0 animate-pulse',
        className
      )}
    >
      {Array.from({ length: columns }).map((_, i) => (
        <SkeletonLoader key={i} className="h-4 flex-1" variant="text" />
      ))}
      {showActions && <SkeletonLoader className="h-8 w-20" variant="rectangular" />}
    </div>
  )
}

interface ChartSkeletonProps {
  height?: number
  className?: string
}

export function ChartSkeleton({ height = 250, className }: ChartSkeletonProps) {
  return (
    <div className={cn('space-y-3', className)}>
      <div className="flex justify-between items-center">
        <SkeletonLoader className="h-5 w-32" variant="text" />
        <div className="flex gap-2">
          <SkeletonLoader className="h-6 w-16" variant="rectangular" />
          <SkeletonLoader className="h-6 w-16" variant="rectangular" />
        </div>
      </div>
      <SkeletonLoader className="w-full" style={{ height }} variant="rectangular" />
    </div>
  )
}

interface ListSkeletonProps {
  items?: number
  itemHeight?: number
  className?: string
}

export function ListSkeleton({
  items = 5,
  itemHeight = 48,
  className,
}: ListSkeletonProps) {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: items }).map((_, i) => (
        <SkeletonLoader
          key={i}
          className="w-full"
          style={{ height: itemHeight }}
          variant="rectangular"
        />
      ))}
    </div>
  )
}

export default LoadingOverlay
