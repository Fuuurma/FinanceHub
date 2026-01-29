'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowDown, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'

interface DrawdownCardProps {
  maxDrawdown: number
  maxDrawdownDate?: string
  recoveryTime?: number
  className?: string
}

export function DrawdownCard({ maxDrawdown, maxDrawdownDate, recoveryTime, className }: DrawdownCardProps) {
  return (
    <Card className={cn('border-l-4 border-red-500', className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <ArrowDown className="h-4 w-4 text-red-500" />
          Max Drawdown
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-bold text-red-600">
          {maxDrawdown >= 0 ? '-' : ''}{Math.abs(maxDrawdown).toFixed(2)}%
        </p>
        {maxDrawdownDate && (
          <p className="text-xs text-muted-foreground mt-1">
            Largest drop on {new Date(maxDrawdownDate).toLocaleDateString()}
          </p>
        )}
        {recoveryTime !== undefined && recoveryTime > 0 && (
          <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>Recovered in {recoveryTime} days</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
