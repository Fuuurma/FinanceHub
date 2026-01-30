'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface RiskCardProps {
  volatility: number
  beta: number
  sharpeRatio: number
  className?: string
}

export function RiskCard({ volatility, beta, sharpeRatio, className }: RiskCardProps) {
  const getRiskLevel = (vol: number) => {
    if (vol < 10) return { level: 'Low', color: 'text-green-600', bg: 'bg-green-100' }
    if (vol < 20) return { level: 'Medium', color: 'text-yellow-600', bg: 'bg-yellow-100' }
    return { level: 'High', color: 'text-red-600', bg: 'bg-red-100' }
  }

  const risk = getRiskLevel(volatility)

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <Activity className="h-4 w-4" />
          Risk Metrics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-muted-foreground">Volatility</p>
            <p className="text-xl font-bold">{volatility.toFixed(2)}%</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Beta</p>
            <p className="text-xl font-bold">{beta.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Sharpe</p>
            <p className={cn(
              'text-xl font-bold',
              sharpeRatio >= 1 ? 'text-green-600' : sharpeRatio >= 0 ? 'text-yellow-600' : 'text-red-600'
            )}>
              {sharpeRatio.toFixed(2)}
            </p>
          </div>
        </div>
        <div className="mt-3 pt-3 border-t">
          <span className={cn('text-xs px-2 py-1 rounded-full', risk.bg, risk.color)}>
            {risk.level} Risk
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
