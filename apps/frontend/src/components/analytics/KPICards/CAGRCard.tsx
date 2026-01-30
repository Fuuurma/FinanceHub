'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

interface CAGRProps {
  cagr: number
  annualizedReturn: number
  className?: string
}

export function CAGRCard({ cagr, annualizedReturn, className }: CAGRProps) {
  const displayValue = cagr || annualizedReturn || 0
  const isPositive = displayValue > 0

  return (
    <Card className={cn('border-l-4 border-green-500', className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <TrendingUp className="h-4 w-4" />
          CAGR / Annual Return
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className={cn(
          'text-3xl font-bold',
          isPositive ? 'text-green-600' : 'text-red-600'
        )}>
          {displayValue >= 0 ? '+' : ''}{displayValue.toFixed(2)}%
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          Compound Annual Growth Rate
        </p>
      </CardContent>
    </Card>
  )
}
