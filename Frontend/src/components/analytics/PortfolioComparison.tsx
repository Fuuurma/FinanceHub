'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Trophy, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface PortfolioComparisonProps {
  portfolios: {
    id: string
    name: string
    return: number
    volatility: number
    sharpeRatio: number
    maxDrawdown: number
  }[]
  selectedId: string
  onSelect: (id: string) => void
  className?: string
}

export function PortfolioComparison({
  portfolios,
  selectedId,
  onSelect,
  className,
}: PortfolioComparisonProps) {
  const sortedByReturn = [...portfolios].sort((a, b) => b.return - a.return)
  const bestPerformer = sortedByReturn[0]?.id
  const worstPerformer = sortedByReturn[sortedByReturn.length - 1]?.id

  const getRank = (id: string) => {
    return sortedByReturn.findIndex((p) => p.id === id) + 1
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Trophy className="h-5 w-5 text-yellow-500" />
          Portfolio Comparison
        </CardTitle>
        <CardDescription>Compare performance across your portfolios</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {portfolios.map((portfolio) => {
            const rank = getRank(portfolio.id)
            const isBest = portfolio.id === bestPerformer
            const isWorst = portfolio.id === worstPerformer

            return (
              <div
                key={portfolio.id}
                onClick={() => onSelect(portfolio.id)}
                className={cn(
                  'p-4 border rounded-lg cursor-pointer transition-all',
                  selectedId === portfolio.id
                    ? 'border-primary bg-primary/5'
                    : 'hover:border-muted-foreground/50',
                  isBest && 'bg-green-50 border-green-200 dark:bg-green-900/20',
                  isWorst && 'bg-red-50 border-red-200 dark:bg-red-900/20'
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">#{rank}</span>
                      {isBest && <Trophy className="h-4 w-4 text-yellow-500" />}
                    </div>
                    <div>
                      <p className="font-medium">{portfolio.name}</p>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span>Vol: {portfolio.volatility.toFixed(1)}%</span>
                        <span>•</span>
                        <span>Sharpe: {portfolio.sharpeRatio.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={cn(
                      'flex items-center gap-1 font-semibold',
                      portfolio.return >= 0 ? 'text-green-600' : 'text-red-600'
                    )}>
                      {portfolio.return >= 0 ? (
                        <TrendingUp className="h-4 w-4" />
                      ) : (
                        <TrendingDown className="h-4 w-4" />
                      )}
                      {portfolio.return >= 0 ? '+' : ''}{portfolio.return.toFixed(2)}%
                    </div>
                  </div>
                </div>

                <div className="mt-2 flex items-center gap-4 text-xs">
                  <span className="text-muted-foreground">
                    Max Drawdown: <span className="text-red-600">-{Math.abs(portfolio.maxDrawdown).toFixed(2)}%</span>
                  </span>
                  {isBest && (
                    <Badge variant="secondary" className="bg-green-100 text-green-700">
                      Best Performer
                    </Badge>
                  )}
                  {isWorst && portfolios.length > 1 && (
                    <Badge variant="secondary" className="bg-red-100 text-red-700">
                      Worst Performer
                    </Badge>
                  )}
                </div>
              </div>
            )
          })}

          {portfolios.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No portfolios to compare</p>
              <p className="text-sm">Create multiple portfolios to see comparison</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
