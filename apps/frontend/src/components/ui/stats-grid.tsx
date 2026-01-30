'use client'

import { Icon, LucideIcon } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface StatsGridProps {
  stats: {
    title: string
    value: string | number
    change?: number
    changeLabel?: string
    icon?: LucideIcon
    iconColor?: string
    description?: string
  }[]
  columns?: 2 | 3 | 4 | 5
  className?: string
}

export function StatsGrid({
  stats,
  columns = 4,
  className,
}: StatsGridProps) {
  const gridCols = {
    2: 'md:grid-cols-2',
    3: 'md:grid-cols-3',
    4: 'md:grid-cols-4',
    5: 'md:grid-cols-5',
  }

  const formatValue = (value: string | number): string => {
    if (typeof value === 'number') {
      if (Math.abs(value) >= 1e12) {
        return `$${(value / 1e12).toFixed(2)}T`
      }
      if (Math.abs(value) >= 1e9) {
        return `$${(value / 1e9).toFixed(2)}B`
      }
      if (Math.abs(value) >= 1e6) {
        return `$${(value / 1e6).toFixed(2)}M`
      }
      if (Math.abs(value) >= 1000) {
        return value.toLocaleString('en-US', {
          style: 'currency',
          currency: 'USD',
          maximumFractionDigits: 0,
        })
      }
      return value.toLocaleString()
    }
    return value
  }

  const formatChange = (change: number): string => {
    const prefix = change >= 0 ? '+' : ''
    return `${prefix}${change.toFixed(2)}%`
  }

  return (
    <div className={cn('grid gap-4', gridCols[columns], className)}>
      {stats.map((stat, index) => (
        <Card key={index}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {stat.title}
            </CardTitle>
            {stat.icon && (
              <stat.icon className={cn('h-4 w-4', stat.iconColor || 'text-muted-foreground')} />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatValue(stat.value)}</div>
            {(stat.change !== undefined || stat.description) && (
              <div className="flex items-center gap-2 mt-1">
                {stat.change !== undefined && (
                  <span
                    className={cn(
                      'text-sm font-medium',
                      stat.change >= 0 ? 'text-green-600' : 'text-red-600'
                    )}
                  >
                    {formatChange(stat.change)}
                  </span>
                )}
                {stat.changeLabel && (
                  <span className="text-xs text-muted-foreground">{stat.changeLabel}</span>
                )}
                {stat.description && !stat.change && (
                  <span className="text-xs text-muted-foreground">{stat.description}</span>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
