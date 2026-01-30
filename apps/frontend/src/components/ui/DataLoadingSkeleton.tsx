'use client'

import { cn } from '@/lib/utils'

interface DataLoadingSkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  radius?: string | number
  className?: string
  animation?: 'pulse' | 'wave' | 'none'
  lines?: number
  inline?: boolean
}

export function DataLoadingSkeleton({
  variant = 'text',
  width = '100%',
  height,
  radius = 4,
  className,
  animation = 'pulse',
  lines = 1,
  inline = false
}: DataLoadingSkeletonProps) {
  const baseStyles = 'bg-muted animate-pulse'

  const getAnimationClass = () => {
    switch (animation) {
      case 'wave':
        return 'animate-pulse'
      case 'none':
        return ''
      default:
        return 'animate-pulse'
    }
  }

  const renderSkeleton = (key?: number) => {
    const style: React.CSSProperties = {
      width: variant === 'text' ? undefined : width,
      height: variant === 'text' ? (height || 16) : height,
      borderRadius: variant === 'circular' ? '50%' : radius
    }

    return (
      <div
        key={key}
        className={cn(
          baseStyles,
          getAnimationClass(),
          variant === 'text' && 'h-4 rounded',
          inline && 'inline-block'
        )}
        style={style}
      />
    )
  }

  if (variant === 'text' && lines > 1) {
    return (
      <div className={cn('space-y-2', className)}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={cn(
              baseStyles,
              getAnimationClass(),
              'h-4 rounded',
              i === lines - 1 && 'w-3/4'
            )}
          />
        ))}
      </div>
    )
  }

  return renderSkeleton()
}

interface SkeletonCardProps {
  className?: string
  showHeader?: boolean
  showImage?: boolean
  imageHeight?: number
  showContent?: boolean
  contentLines?: number
  showFooter?: boolean
}

export function SkeletonCard({
  className,
  showHeader = true,
  showImage = true,
  imageHeight = 200,
  showContent = true,
  contentLines = 3,
  showFooter = true
}: SkeletonCardProps) {
  return (
    <div className={cn('border rounded-lg overflow-hidden', className)}>
      {showImage && (
        <DataLoadingSkeleton
          variant="rectangular"
          width="100%"
          height={imageHeight}
          className="w-full"
        />
      )}
      {(showHeader || showContent || showFooter) && (
        <div className="p-4 space-y-4">
          {showHeader && (
            <div className="space-y-2">
              <DataLoadingSkeleton variant="text" width="60%" height={20} />
              <DataLoadingSkeleton variant="text" width="40%" height={14} />
            </div>
          )}
          {showContent && (
            <div className="space-y-2">
              {Array.from({ length: contentLines }).map((_, i) => (
                <DataLoadingSkeleton
                  key={i}
                  variant="text"
                  width={i === contentLines - 1 ? '75%' : '100%'}
                  height={12}
                />
              ))}
            </div>
          )}
          {showFooter && (
            <div className="flex gap-2 pt-2">
              <DataLoadingSkeleton variant="circular" width={32} height={32} />
              <DataLoadingSkeleton variant="text" width="25%" height={16} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export function SkeletonTable({
  rows = 5,
  columns = 4,
  className
}: {
  rows?: number
  columns?: number
  className?: string
}) {
  return (
    <div className={cn('space-y-3', className)}>
      <div className="flex gap-4 border-b pb-2">
        {Array.from({ length: columns }).map((_, i) => (
          <DataLoadingSkeleton key={i} variant="text" width={100} height={16} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4 py-2 border-b last:border-0">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <DataLoadingSkeleton
              key={colIndex}
              variant="text"
              width={80}
              height={16}
            />
          ))}
        </div>
      ))}
    </div>
  )
}

export default DataLoadingSkeleton
