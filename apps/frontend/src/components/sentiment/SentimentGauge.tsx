'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, MessageSquare } from 'lucide-react'

interface SentimentGaugeProps {
  score: number
  label: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
  mentions: number
  source?: 'twitter' | 'reddit' | 'all'
  className?: string
}

const SENTIMENT_CONFIG = {
  BULLISH: {
    color: 'text-success',
    bgColor: 'bg-success/10',
    borderColor: 'border-success',
    icon: TrendingUp,
    gradient: 'from-green-500/20 to-green-500/5'
  },
  BEARISH: {
    color: 'text-destructive',
    bgColor: 'bg-destructive/10',
    borderColor: 'border-destructive',
    icon: TrendingDown,
    gradient: 'from-red-500/20 to-red-500/5'
  },
  NEUTRAL: {
    color: 'text-muted-foreground',
    bgColor: 'bg-muted/50',
    borderColor: 'border-border',
    icon: MessageSquare,
    gradient: 'from-muted/30 to-muted/10'
  }
}

export function SentimentGauge({ score, label, mentions, source = 'all', className }: SentimentGaugeProps) {
  const config = SENTIMENT_CONFIG[label]
  const Icon = config.icon

  const normalizedScore = Math.max(-1, Math.min(1, score))
  const percentage = ((normalizedScore + 1) / 2) * 100

  return (
    <Card className={cn('rounded-none border-1', className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
          Sentiment Score
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className={cn('relative rounded-none border-1 p-6 text-center', config.bgColor, config.borderColor)}>
          <div className="absolute inset-0 bg-gradient-to-br opacity-50" />
          
          <Icon className={cn('h-12 w-12 mx-auto mb-3', config.color)} aria-hidden="true" />
          
          <p className={cn('text-4xl font-black tracking-tight', config.color)}>
            {score >= 0 ? '+' : ''}{score.toFixed(2)}
          </p>
          
          <p className={cn('text-lg font-black uppercase tracking-widest mt-1', config.color)}>
            {label}
          </p>
          
          <div className="flex items-center justify-center gap-2 mt-4 pt-4 border-t border-border/50">
            <MessageSquare className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <span className="font-mono text-sm font-medium">
              {mentions.toLocaleString()} mentions
            </span>
            <Badge variant="outline" className="rounded-none text-xs font-mono uppercase">
              {source}
            </Badge>
          </div>
        </div>
        
        <div className="mt-4" role="progressbar" aria-valuenow={percentage} aria-valuemin={0} aria-valuemax={100} aria-label={`Sentiment polarity: ${percentage.toFixed(0)}% positive`}>
          <div className="h-2 rounded-none bg-muted overflow-hidden">
            <div 
              className={cn('h-full transition-all duration-500', config.color.replace('text', 'bg'))}
              style={{ width: `${percentage}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground mt-1 font-mono">
            <span>Bearish</span>
            <span>Neutral</span>
            <span>Bullish</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
