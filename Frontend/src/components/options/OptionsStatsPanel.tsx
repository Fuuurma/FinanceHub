'use client'

import { useState, useMemo } from 'react'
import { TrendingUp, TrendingDown, Activity, Target, Percent, BarChart3, Zap } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

export interface OptionsStats {
  ivRank: number
  ivPercentile: number
  putCallRatio: number
  totalVolume: number
  totalOpenInterest: number
  maxPain: number
  supportLevels: number[]
  resistanceLevels: number[]
  impliedMove: number
  deltaNeutral: number
  gammaNeutral: number
  thetaNeutral: number
}

export interface OptionsStatsPanelProps {
  symbol: string
  currentPrice: number
  stats?: OptionsStats
  loading?: boolean
  className?: string
}

function generateMockStats(currentPrice: number): OptionsStats {
  return {
    ivRank: Math.random() * 100,
    ivPercentile: Math.random() * 100,
    putCallRatio: 0.5 + Math.random() * 1.5,
    totalVolume: Math.floor(Math.random() * 1000000) + 100000,
    totalOpenInterest: Math.floor(Math.random() * 5000000) + 1000000,
    maxPain: currentPrice * (0.95 + Math.random() * 0.1),
    supportLevels: [currentPrice * 0.95, currentPrice * 0.90, currentPrice * 0.85],
    resistanceLevels: [currentPrice * 1.05, currentPrice * 1.10, currentPrice * 1.15],
    impliedMove: currentPrice * (Math.random() * 0.05 + 0.02),
    deltaNeutral: currentPrice,
    gammaNeutral: currentPrice,
    thetaNeutral: currentPrice,
  }
}

function OptionsStatsPanelSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-32" />
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-20 w-full" />)}
        </div>
        <Skeleton className="h-48 w-full" />
      </CardContent>
    </Card>
  )
}

function StatCard({ title, value, subtitle, trend, icon: Icon }: { title: string; value: string; subtitle?: string; trend?: 'up' | 'down' | 'neutral'; icon: any }) {
  return (
    <div className="p-4 border rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-muted-foreground">{title}</span>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </div>
      <p className="text-xl font-bold">{value}</p>
      {subtitle && (
        <p className={cn('text-xs', trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-muted-foreground')}>
          {subtitle}
        </p>
      )}
    </div>
  )
}

export function OptionsStatsPanel({ symbol, currentPrice, stats: propStats, loading = false, className }: OptionsStatsPanelProps) {
  const stats = useMemo(() => propStats || generateMockStats(currentPrice), [propStats, currentPrice])

  const ivStatus = stats.ivRank > 50 ? 'high' : stats.ivRank > 25 ? 'normal' : 'low'
  const pcrStatus = stats.putCallRatio > 1 ? 'bearish' : stats.putCallRatio > 0.7 ? 'neutral' : 'bullish'

  if (loading) return <OptionsStatsPanelSkeleton />

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Options Statistics
            </CardTitle>
            <CardDescription>{symbol} - Key options metrics and levels</CardDescription>
          </div>
          <Badge variant={ivStatus === 'high' ? 'destructive' : ivStatus === 'normal' ? 'secondary' : 'outline'}>
            IV Rank: {stats.ivRank.toFixed(0)}
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatCard
            title="Put/Call Ratio"
            value={stats.putCallRatio.toFixed(2)}
            subtitle={pcrStatus === 'bullish' ? 'Bullish signal' : pcrStatus === 'bearish' ? 'Bearish signal' : 'Neutral'}
            trend={pcrStatus === 'bullish' ? 'up' : pcrStatus === 'bearish' ? 'down' : 'neutral'}
            icon={BarChart3}
          />
          <StatCard
            title="Implied Move"
            value={formatCurrency(stats.impliedMove)}
            subtitle={`±${formatPercent(stats.impliedMove / currentPrice)}`}
            icon={Zap}
          />
          <StatCard
            title="Max Pain"
            value={formatCurrency(stats.maxPain)}
            subtitle={`${((stats.maxPain - currentPrice) / currentPrice * 100).toFixed(1)}% from spot`}
            icon={Target}
          />
          <StatCard
            title="IV Percentile"
            value={`${stats.ivPercentile.toFixed(0)}%`}
            subtitle={`Rank: ${stats.ivRank.toFixed(0)}`}
            icon={Percent}
          />
        </div>

        <Tabs defaultValue="levels" className="space-y-4">
          <TabsList>
            <TabsTrigger value="levels">Key Levels</TabsTrigger>
            <TabsTrigger value="greeks">Greeks Neutral</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
          </TabsList>

          <TabsContent value="levels" className="space-y-4">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="font-semibold flex items-center gap-2">
                  <TrendingDown className="h-4 w-4 text-green-600" />
                  Support Levels
                </h4>
                {stats.supportLevels.map((level, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                    <span className="font-medium">Level {i + 1}</span>
                    <div className="text-right">
                      <p className="font-bold text-green-700">{formatCurrency(level)}</p>
                      <p className="text-xs text-green-600">
                        {((currentPrice - level) / currentPrice * 100).toFixed(1)}% below
                      </p>
                    </div>
                    <Progress value={100 - (i + 1) * 25} className="w-16 h-2" />
                  </div>
                ))}
              </div>
              <div className="space-y-3">
                <h4 className="font-semibold flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-red-600" />
                  Resistance Levels
                </h4>
                {stats.resistanceLevels.map((level, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                    <span className="font-medium">Level {i + 1}</span>
                    <div className="text-right">
                      <p className="font-bold text-red-700">{formatCurrency(level)}</p>
                      <p className="text-xs text-red-600">
                        {((level - currentPrice) / currentPrice * 100).toFixed(1)}% above
                      </p>
                    </div>
                    <Progress value={(i + 1) * 25} className="w-16 h-2" />
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="greeks" className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 border rounded-lg text-center">
                <p className="text-xs text-muted-foreground mb-2">Delta Neutral</p>
                <p className="text-2xl font-bold">{formatCurrency(stats.deltaNeutral)}</p>
                <p className="text-xs text-muted-foreground mt-1">Where delta = 0</p>
              </div>
              <div className="p-4 border rounded-lg text-center">
                <p className="text-xs text-muted-foreground mb-2">Gamma Neutral</p>
                <p className="text-2xl font-bold">{formatCurrency(stats.gammaNeutral)}</p>
                <p className="text-xs text-muted-foreground mt-1">Where gamma = 0</p>
              </div>
              <div className="p-4 border rounded-lg text-center">
                <p className="text-xs text-muted-foreground mb-2">Theta Neutral</p>
                <p className="text-2xl font-bold">{formatCurrency(stats.thetaNeutral)}</p>
                <p className="text-xs text-muted-foreground mt-1">Where theta = 0</p>
              </div>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-semibold mb-2">Understanding Neutral Points</h4>
              <p className="text-sm text-muted-foreground">
                Delta neutral: Stock price where long and short delta positions balance.
                Gamma neutral: Price where gamma exposure is neutralized.
                Theta neutral: Price where time decay impact is balanced.
              </p>
            </div>
          </TabsContent>

          <TabsContent value="activity" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Total Volume</span>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </div>
                <p className="text-2xl font-bold">{stats.totalVolume.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">Contracts traded today</p>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Open Interest</span>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </div>
                <p className="text-2xl font-bold">{stats.totalOpenInterest.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">Total outstanding contracts</p>
              </div>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-semibold mb-2">Volume Analysis</h4>
              <p className="text-sm text-muted-foreground">
                High volume with increasing open interest suggests new money entering the market.
                High volume with decreasing open interest indicates position closing.
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default OptionsStatsPanel
