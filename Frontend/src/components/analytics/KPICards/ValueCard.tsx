'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DollarSign } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ValueCardProps {
  value: number
  change?: number
  className?: string
}

export function ValueCard({ value, change, className }: ValueCardProps) {
  const formattedValue = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)

  const formattedChange = change !== undefined 
    ? new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
      }).format(Math.abs(change))
    : null

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <DollarSign className="h-4 w-4" />
          Portfolio Value
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{formattedValue}</div>
        {change !== undefined && (
          <p className={cn(
            'text-xs mt-1',
            change > 0 ? 'text-green-600' : change < 0 ? 'text-red-600' : 'text-muted-foreground'
          )}>
            {change >= 0 ? '+' : ''}{formattedChange} from last period
          </p>
        )}
      </CardContent>
    </Card>
  )
}
