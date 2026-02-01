'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart
} from 'recharts'
import { format, parseISO, subHours } from 'date-fns'

interface SentimentHistoryDataPoint {
  timestamp: string
  score: number
  mentions: number
}

interface SentimentHistoryChartProps {
  data: SentimentHistoryDataPoint[]
  timeframe?: '24h' | '7d' | '30d'
  onTimeframeChange?: (timeframe: '24h' | '7d' | '30d') => void
  className?: string
}

const TIMEFRAMES = ['24h', '7d', '30d'] as const

export function SentimentHistoryChart({
  data,
  timeframe = '24h',
  onTimeframeChange,
  className
}: SentimentHistoryChartProps) {
  const chartData = React.useMemo(() => {
    return data.map(point => ({
      ...point,
      formattedTime: format(parseISO(point.timestamp), timeframe === '24h' ? 'HH:mm' : 'MMM dd')
    }))
  }, [data, timeframe])

  const formatYAxis = (value: number) => {
    return value.toFixed(1)
  }

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number; payload: SentimentHistoryDataPoint }>; label?: string }) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-none border-2 border-foreground bg-background p-3 shadow-lg">
          <p className="font-mono text-xs text-muted-foreground mb-1">
            {label}
          </p>
          <p className="font-bold">
            Sentiment: <span className={cn(
              payload[0].value >= 0 ? 'text-success' : 'text-destructive'
            )}>
              {payload[0].value >= 0 ? '+' : ''}{payload[0].value.toFixed(3)}
            </span>
          </p>
          <p className="font-mono text-xs text-muted-foreground">
            {payload[0].payload.mentions.toLocaleString()} mentions
          </p>
        </div>
      )
    }
    return null
  }

  const gradientOffset = () => {
    const dataMax = Math.max(...chartData.map((i) => i.score))
    const dataMin = Math.min(...chartData.map((i) => i.score))
  
    if (dataMax <= 0) return 0
    if (dataMin >= 0) return 1
  
    return dataMax / (dataMax - dataMin)
  }

  const off = gradientOffset()

  return (
    <Card className={cn('rounded-none border-1', className)}>
      <CardHeader className="border-b-1 pb-0">
        <div className="flex items-center justify-between">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            Sentiment History
          </CardTitle>
          
          {onTimeframeChange && (
            <div className="flex gap-1" role="tablist" aria-label="Time period">
              {TIMEFRAMES.map((tf) => (
                <Button
                  key={tf}
                  variant={timeframe === tf ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => onTimeframeChange(tf)}
                  className={cn(
                    'rounded-none px-3 py-1 font-black uppercase text-xs',
                    timeframe === tf ? '' : 'border-2'
                  )}
                  role="tab"
                  aria-selected={timeframe === tf}
                >
                  {tf}
                </Button>
              ))}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <div 
          className="h-[300px]" 
          role="img"
          aria-label={`Sentiment history chart showing sentiment score over the ${timeframe}`}
        >
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="sentimentGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(var(--foreground))" stopOpacity={0.3} />
                  <stop offset={off} stopColor="hsl(var(--foreground))" stopOpacity={0.1} />
                  <stop offset={off} stopColor="hsl(var(--foreground))" stopOpacity={0.1} />
                  <stop offset="100%" stopColor="hsl(var(--foreground))" stopOpacity={0.3} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="formattedTime"
                tick={{ fontSize: 11, fontFamily: 'var(--font-mono)' }}
                tickLine={false}
                axisLine={{ stroke: 'hsl(var(--border))' }}
                className="text-muted-foreground"
              />
              <YAxis
                domain={[-1, 1]}
                tickFormatter={formatYAxis}
                tick={{ fontSize: 11, fontFamily: 'var(--font-mono)' }}
                tickLine={false}
                axisLine={{ stroke: 'hsl(var(--border))' }}
                className="text-muted-foreground"
              />
              <ReferenceLine y={0} stroke="hsl(var(--muted-foreground))" strokeDasharray="3 3" />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="score"
                stroke="hsl(var(--foreground))"
                strokeWidth={2}
                fill="url(#sentimentGradient)"
                dot={false}
                activeDot={{ r: 4, fill: 'hsl(var(--foreground))' }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        
        <div className="flex items-center justify-center gap-6 mt-4 pt-4 border-t-1">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-none bg-success" aria-hidden="true" />
            <span className="text-xs font-mono text-muted-foreground">Bullish (+0.5 to +1.0)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-none bg-muted" aria-hidden="true" />
            <span className="text-xs font-mono text-muted-foreground">Neutral (-0.5 to +0.5)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-none bg-destructive" aria-hidden="true" />
            <span className="text-xs font-mono text-muted-foreground">Bearish (-0.5 to -1.0)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
