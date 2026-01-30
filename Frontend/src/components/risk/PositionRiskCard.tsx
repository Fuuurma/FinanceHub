'use client'

import { useMemo } from 'react'
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Target,
  DollarSign,
  Percent,
  BarChart3,
} from 'lucide-react'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

export interface PositionRiskData {
  symbol: string
  name: string
  quantity: number
  avgPrice: number
  currentPrice: number
  marketValue: number
  unrealizedPnL: number
  unrealizedPnLPercent: number
  weight: number
  beta: number
  correlationSP500: number
  volatility: number
  var95: number
  var99: number
  contributionVaR: number
  stopLoss?: number
  takeProfit?: number
  riskRewardRatio?: number
  liquidityScore: number
  sector: string
}

interface PositionRiskCardProps {
  position: PositionRiskData
  portfolioVaR?: number
  maxWeight?: number
  onSetStopLoss?: (symbol: string, price: number) => void
  onSetTakeProfit?: (symbol: string, price: number) => void
  className?: string
}

function getRiskLevel(value: number, thresholds: { low: number; medium: number; high: number }): RiskLevel {
  if (value <= thresholds.low) return 'low'
  if (value <= thresholds.medium) return 'medium'
  if (value <= thresholds.high) return 'high'
  return 'critical'
}

function getRiskColor(level: RiskLevel): string {
  switch (level) {
    case 'low': return 'text-green-600 bg-green-100 border-green-200'
    case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-200'
    case 'high': return 'text-orange-600 bg-orange-100 border-orange-200'
    case 'critical': return 'text-red-600 bg-red-100 border-red-200'
  }
}

function formatCurrencyCompact(value: number): string {
  if (Math.abs(value) >= 1000000) {
    return `$${(value / 1000000).toFixed(2)}M`
  }
  if (Math.abs(value) >= 1000) {
    return `$${(value / 1000).toFixed(1)}K`
  }
  return formatCurrency(value)
}

export function PositionRiskCard({
  position,
  portfolioVaR,
  maxWeight = 10,
  onSetStopLoss,
  onSetTakeProfit,
  className,
}: PositionRiskCardProps) {
  const weightRiskLevel = useMemo(() => 
    getRiskLevel(position.weight, { low: 3, medium: 5, high: maxWeight }),
  [position.weight, maxWeight])

  const varRiskLevel = useMemo(() => {
    if (!portfolioVaR || portfolioVaR === 0) return 'low' as RiskLevel
    const contributionPercent = (Math.abs(position.contributionVaR) / portfolioVaR) * 100
    return getRiskLevel(contributionPercent, { low: 5, medium: 10, high: 15 }) as RiskLevel
  }, [position.contributionVaR, portfolioVaR])

  const liquidityRiskLevel = useMemo(() =>
    getRiskLevel(position.liquidityScore, { low: 70, medium: 40, high: 20 }),
  [position.liquidityScore])

  const isLong = position.unrealizedPnL >= 0
  const riskRewardRatio = position.riskRewardRatio || 
    (position.stopLoss && position.takeProfit 
      ? Math.abs(position.takeProfit - position.currentPrice) / Math.abs(position.stopLoss - position.currentPrice)
      : undefined)

  return (
    <Card className={cn('overflow-hidden', className)}>
      <CardHeader className="pb-3 space-y-1">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold">{position.symbol}</CardTitle>
            <CardDescription className="text-xs">{position.name}</CardDescription>
          </div>
          <Badge variant="outline" className="text-xs">
            {position.sector}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <DollarSign className="h-3 w-3" />
              Market Value
            </p>
            <p className="text-sm font-semibold">{formatCurrencyCompact(position.marketValue)}</p>
          </div>
          
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <Percent className="h-3 w-3" />
              Portfolio Weight
            </p>
            <div className="flex items-center gap-2">
              <p className={cn(
                'text-sm font-semibold',
                weightRiskLevel === 'critical' ? 'text-red-600' :
                weightRiskLevel === 'high' ? 'text-orange-600' : ''
              )}>
                {position.weight.toFixed(2)}%
              </p>
              <Progress 
                value={(position.weight / maxWeight) * 100} 
                className="h-1.5 flex-1" 
              />
            </div>
          </div>
        </div>

        <div className={cn(
          'flex items-center gap-2 p-2 rounded-lg border',
          isLong ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
        )}>
          {isLong ? (
            <TrendingUp className="h-4 w-4 text-green-600" />
          ) : (
            <TrendingDown className="h-4 w-4 text-red-600" />
          )}
          <span className={cn(
            'text-sm font-semibold',
            isLong ? 'text-green-700' : 'text-red-700'
          )}>
            {formatCurrency(position.unrealizedPnL)} ({formatPercent(position.unrealizedPnLPercent)})
          </span>
        </div>

        <div className="grid grid-cols-3 gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className={cn(
                  'p-2 rounded-lg border text-center cursor-help',
                  getRiskColor(varRiskLevel)
                )}>
                  <p className="text-xs font-medium">VaR Contrib.</p>
                  <p className="text-sm font-bold">{position.contributionVaR.toFixed(2)}%</p>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p className="text-xs">Contribution to Portfolio VaR</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className={cn(
                  'p-2 rounded-lg border text-center cursor-help',
                  getRiskColor(liquidityRiskLevel)
                )}>
                  <p className="text-xs font-medium">Liquidity</p>
                  <p className="text-sm font-bold">{position.liquidityScore.toFixed(0)}</p>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p className="text-xs">Liquidity Score (0-100)</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <div className="p-2 rounded-lg border text-center bg-gray-50">
            <p className="text-xs font-medium text-muted-foreground">Beta</p>
            <p className="text-sm font-bold">{position.beta.toFixed(2)}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Beta:</span>
            <span className="font-medium">{position.beta.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Volatility:</span>
            <span className="font-medium">{position.volatility.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">VaR 95%:</span>
            <span className="font-medium">{formatCurrency(position.var95)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Corr. S&P:</span>
            <span className="font-medium">{position.correlationSP500.toFixed(2)}</span>
          </div>
        </div>

        {(position.stopLoss || position.takeProfit || riskRewardRatio) && (
          <div className="pt-3 border-t space-y-2">
            <p className="text-xs font-medium text-muted-foreground flex items-center gap-1">
              <Target className="h-3 w-3" />
              Risk Management
            </p>
            <div className="grid grid-cols-3 gap-2">
              {position.stopLoss && (
                <div className="text-center">
                  <p className="text-xs text-red-600 font-medium">Stop Loss</p>
                  <p className="text-sm font-bold">{formatCurrency(position.stopLoss)}</p>
                  <p className="text-xs text-muted-foreground">
                    {((position.stopLoss - position.avgPrice) / position.avgPrice * 100).toFixed(1)}%
                  </p>
                </div>
              )}
              {position.currentPrice && (
                <div className="text-center">
                  <p className="text-xs text-blue-600 font-medium">Current</p>
                  <p className="text-sm font-bold">{formatCurrency(position.currentPrice)}</p>
                </div>
              )}
              {position.takeProfit && (
                <div className="text-center">
                  <p className="text-xs text-green-600 font-medium">Take Profit</p>
                  <p className="text-sm font-bold">{formatCurrency(position.takeProfit)}</p>
                  <p className="text-xs text-muted-foreground">
                    {((position.takeProfit - position.avgPrice) / position.avgPrice * 100).toFixed(1)}%
                  </p>
                </div>
              )}
            </div>
            {riskRewardRatio && (
              <div className="flex items-center justify-center gap-2 text-xs">
                <span className="text-muted-foreground">Risk/Reward:</span>
                <Badge variant={riskRewardRatio >= 2 ? 'default' : 'secondary'}>
                  1:{riskRewardRatio.toFixed(1)}
                </Badge>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default PositionRiskCard
