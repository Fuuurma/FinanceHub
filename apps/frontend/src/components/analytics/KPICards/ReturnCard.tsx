'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ReturnCardProps {
  value: number
  percent?: boolean
  className?: string
}

export function ReturnCard({ value, percent = true, className }: ReturnCardProps) {
  const isPositive = value > 0
  const isNeutral = value === 0
  
  const formattedValue = percent 
    ? `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
    : `$${value.toLocaleString()}`

  return (
    <Card className={cn('border-l-4', className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          Total Return
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2">
          {isPositive && <TrendingUp className="h-5 w-5 text-green-500" />}
          {isNeutral && <Minus className="h-5 w-5 text-gray-500" />}
          {!isPositive && !isNeutral && <TrendingDown className="h-5 w-5 text-red-500" />}
          <span className={cn(
            'text-3xl font-bold',
            isPositive && 'text-green-600',
            isNeutral && 'text-gray-600',
            !isPositive && !isNeutral && 'text-red-600'
          )}>
            {formattedValue}
          </span>
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          {value >= 0 ? 'Profit' : value === 0 ? 'Break even' : 'Loss'}
        </p>
      </CardContent>
    </Card>
  )
}
