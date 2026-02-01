'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  TrendingUp, TrendingDown, Minus, Twitter, MessageCircle, Hash
} from 'lucide-react'

interface SentimentGaugeProps {
  score: number
  label: 'bullish' | 'bearish' | 'neutral'
  mentionCount: number
  source: 'twitter' | 'reddit' | 'aggregated'
  className?: string
}

export function SentimentGauge({
  score,
  label,
  mentionCount,
  source,
  className
}: SentimentGaugeProps) {
  const percentage = Math.abs(score) * 100
  const isBullish = score > 0
  const isBearish = score < 0

  const getColor = () => {
    if (isBullish) return 'bg-green-500'
    if (isBearish) return 'bg-red-500'
    return 'bg-yellow-500'
  }

  const getIcon = () => {
    if (source === 'twitter') return <Twitter className="h-4 w-4" />
    if (source === 'reddit') return <MessageCircle className="h-4 w-4" />
    return <Hash className="h-4 w-4" />
  }

  return (
    <Card className={cn('rounded-none border-2 border-foreground', className)}>
      <CardHeader className="border-b-2 border-foreground">
        <div className="flex items-center justify-between">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            {getIcon()}
            {source === 'aggregated' ? 'Aggregated' : source.charAt(0).toUpperCase() + source.slice(1)} Sentiment
          </CardTitle>
          <span className="font-mono text-sm text-muted-foreground">
            {mentionCount.toLocaleString()} mentions
          </span>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div className="flex items-center gap-6">
          <div className="flex-1">
            <div className="relative h-8 bg-muted rounded-full overflow-hidden border-2 border-foreground">
              <div
                className={cn(
                  'absolute top-0 bottom-0 transition-all duration-500',
                  getColor()
                )}
                style={{
                  left: isBullish ? '50%' : '0%',
                  width: isBullish ? `${percentage / 2}%` : `${percentage}%`
                }}
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-1 h-6 bg-foreground" />
              </div>
            </div>
            <div className="flex justify-between mt-2 text-xs font-bold uppercase">
              <span className="text-red-600">Bearish</span>
              <span className="text-yellow-600">Neutral</span>
              <span className="text-green-600">Bullish</span>
            </div>
          </div>

          <div className="text-center">
            <div className={cn(
              'text-4xl font-black uppercase tracking-tight',
              isBullish ? 'text-green-600' : isBearish ? 'text-red-600' : 'text-yellow-600'
            )}>
              {label}
            </div>
            <div className="text-2xl font-mono font-bold mt-1">
              {score >= 0 ? '+' : ''}{score.toFixed(3)}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

interface SentimentGaugeSkeletonProps {
  className?: string
}

export function SentimentGaugeSkeleton({ className }: SentimentGaugeSkeletonProps) {
  return (
    <Card className={cn('rounded-none border-2 border-foreground', className)}>
      <CardHeader className="border-b-2 border-foreground">
        <Skeleton className="h-6 w-48" />
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          <Skeleton className="h-8 w-full" />
          <div className="flex justify-between text-xs">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-16" />
          </div>
          <Skeleton className="h-10 w-32 mx-auto" />
        </div>
      </CardContent>
    </Card>
  )
}
