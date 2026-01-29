'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'

interface IndicatorCardProps {
  title: string
  value: string | number
  unit?: string
  change?: number
  changeType?: 'positive' | 'negative' | 'neutral'
  date?: string
  description?: string
  icon?: React.ReactNode
  className?: string
  loading?: boolean
}

export function IndicatorCard({
  title,
  value,
  unit,
  change,
  changeType = 'neutral',
  date,
  description,
  icon,
  className,
  loading = false,
}: IndicatorCardProps) {
  if (loading) {
    return (
      <Card className={className}>
        <CardHeader className="pb-2">
          <Skeleton className="h-4 w-24" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-32 mb-2" />
          <Skeleton className="h-3 w-20" />
        </CardContent>
      </Card>
    )
  }

  const getChangeIcon = () => {
    if (changeType === 'positive') return <TrendingUp className="h-3 w-3" />
    if (changeType === 'negative') return <TrendingDown className="h-3 w-3" />
    return <Minus className="h-3 w-3" />
  }

  const getChangeColor = () => {
    if (changeType === 'positive') return 'text-green-600 dark:text-green-400'
    if (changeType === 'negative') return 'text-red-600 dark:text-red-400'
    return 'text-muted-foreground'
  }

  return (
    <Card className={cn('hover:shadow-md transition-shadow', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardDescription className="text-xs font-medium">{title}</CardDescription>
          {icon && <div className="text-muted-foreground">{icon}</div>}
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2">
          <div className="text-2xl font-bold">{value}</div>
          {unit && <span className="text-xs text-muted-foreground">{unit}</span>}
        </div>
        {change !== undefined && (
          <div className={cn('flex items-center gap-1 text-xs mt-1', getChangeColor())}>
            {getChangeIcon()}
            <span>{change > 0 ? '+' : ''}{change}%</span>
            <span className="text-muted-foreground ml-1">from last period</span>
          </div>
        )}
        {date && (
          <div className="text-xs text-muted-foreground mt-1">
            Updated: {new Date(date).toLocaleDateString()}
          </div>
        )}
        {description && (
          <p className="text-xs text-muted-foreground mt-2">{description}</p>
        )}
      </CardContent>
    </Card>
  )
}
