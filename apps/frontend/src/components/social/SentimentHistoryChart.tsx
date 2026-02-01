'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { RefreshCw, LineChart as LineChartIcon } from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

interface SentimentHistoryPoint {
  timestamp: string
  sentiment_score: number
  mention_count: number
}

interface SentimentHistoryChartProps {
  symbol: string
  data: SentimentHistoryPoint[]
  isLoading: boolean
  period: string
  onPeriodChange: (period: string) => void
  onRefresh?: () => void
  className?: string
}

export function SentimentHistoryChart({
  symbol,
  data,
  isLoading,
  period,
  onPeriodChange,
  onRefresh,
  className
}: SentimentHistoryChartProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    if (period === '24h') {
      return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    }
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const formatScore = (score: number) => {
    if (score > 0) return `+${score.toFixed(2)}`
    return score.toFixed(2)
  }

  const getLineColor = (score: number) => {
    if (score > 0.3) return '#16a34a'
    if (score < -0.3) return '#dc2626'
    return '#ca8a04'
  }

  if (isLoading) {
    return (
      <Card className={cn('rounded-none border-2 border-foreground', className)}>
        <CardHeader className="border-b-2 border-foreground">
          <Skeleton className="h-8 w-48" />
        </CardHeader>
        <CardContent className="p-6">
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('rounded-none border-2 border-foreground', className)}>
      <CardHeader className="border-b-2 border-foreground">
        <div className="flex items-center justify-between">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            <LineChartIcon className="h-5 w-5" />
            Sentiment History
          </CardTitle>
          <div className="flex items-center gap-2">
            <Select value={period} onValueChange={onPeriodChange}>
              <SelectTrigger className="w-24 rounded-none border-2 font-bold uppercase text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="24h">24H</SelectItem>
                <SelectItem value="7d">7D</SelectItem>
                <SelectItem value="30d">30D</SelectItem>
              </SelectContent>
            </Select>
            {onRefresh && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRefresh}
                className="rounded-none border-2 font-bold uppercase"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        {data.length === 0 ? (
          <div className="h-64 flex items-center justify-center">
            <div className="text-center">
              <LineChartIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="font-black uppercase text-lg mb-2">No History Data</h3>
              <p className="text-muted-foreground font-mono text-sm">
                Sentiment history will appear here
              </p>
            </div>
          </div>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatTime}
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  domain={[-1, 1]}
                  tickFormatter={(value) => formatScore(value)}
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  width={50}
                />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="border-2 border-foreground bg-background p-3 shadow-lg">
                          <p className="font-mono text-xs font-bold mb-1">
                            {formatTime(label)}
                          </p>
                          <p className="font-mono text-sm">
                            Score: <span className={cn(
                              'font-bold',
                              data.sentiment_score > 0.3 ? 'text-green-600' :
                                data.sentiment_score < -0.3 ? 'text-red-600' : 'text-yellow-600'
                            )}>
                              {formatScore(data.sentiment_score)}
                            </span>
                          </p>
                          <p className="font-mono text-xs text-muted-foreground">
                            {data.mention_count.toLocaleString()} mentions
                          </p>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <ReferenceLine y={0} stroke="hsl(var(--foreground))" strokeWidth={1} />
                <ReferenceLine y={0.3} stroke="#16a34a" strokeDasharray="3 3" strokeWidth={1} />
                <ReferenceLine y={-0.3} stroke="#dc2626" strokeDasharray="3 3" strokeWidth={1} />
                <Line
                  type="monotone"
                  dataKey="sentiment_score"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="flex items-center justify-center gap-6 mt-4 text-xs font-bold uppercase">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-600" />
            <span className="text-muted-foreground">Bullish (&gt;0.3)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-600" />
            <span className="text-muted-foreground">Neutral</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-600" />
            <span className="text-muted-foreground">Bearish (&lt;-0.3)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
