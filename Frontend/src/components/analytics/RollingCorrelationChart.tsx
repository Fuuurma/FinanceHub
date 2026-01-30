'use client'

import { useMemo, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { cn, formatPercent } from '@/lib/utils'
import { TrendingUp, TrendingDown, Activity, Calendar } from 'lucide-react'

export interface RollingCorrelationData {
  date: Date
  correlation: number
}

export interface RollingCorrelationChartProps {
  symbol1: string
  symbol2: string
  data?: RollingCorrelationData[]
  loading?: boolean
  className?: string
}

export function RollingCorrelationChart({
  symbol1,
  symbol2,
  data: propData,
  loading = false,
  className,
}: RollingCorrelationChartProps) {
  const [period, setPeriod] = useState('30')
  const [view, setView] = useState('chart')

  const defaultData: RollingCorrelationData[] = useMemo(() => {
    const points: RollingCorrelationData[] = []
    const days = parseInt(period)
    const now = new Date()
    let correlation = 0.5 + Math.random() * 0.3

    for (let i = days; i >= 0; i--) {
      const date = new Date(now)
      date.setDate(date.getDate() - i)

      correlation += (Math.random() - 0.5) * 0.2
      correlation = Math.max(-1, Math.min(1, correlation))

      points.push({
        date,
        correlation,
      })
    }
    return points
  }, [period])

  const data = propData || defaultData

  const avgCorrelation = useMemo(() => {
    if (data.length === 0) return 0
    return data.reduce((sum, d) => sum + d.correlation, 0) / data.length
  }, [data])

  const maxCorrelation = useMemo(() => Math.max(...data.map((d) => d.correlation)), [data])
  const minCorrelation = useMemo(() => Math.min(...data.map((d) => d.correlation)), [data])

  const correlationLevel = useMemo(() => {
    const avg = Math.abs(avgCorrelation)
    if (avg >= 0.7) return 'strong'
    if (avg >= 0.4) return 'moderate'
    return 'weak'
  }, [avgCorrelation])

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const chartPath = useMemo(() => {
    if (data.length === 0) return ''

    const width = 600
    const height = 200
    const padding = 30

    const minDate = data[0].date.getTime()
    const maxDate = data[data.length - 1].date.getTime()
    const dateRange = maxDate - minDate || 1

    const minCorr = -1
    const maxCorr = 1
    const corrRange = maxCorr - minCorr || 1

    const xScale = (date: Date) => {
      return padding + ((date.getTime() - minDate) / dateRange) * (width - 2 * padding)
    }

    const yScale = (corr: number) => {
      return height - padding - ((corr - minCorr) / corrRange) * (height - 2 * padding)
    }

    let path = `M ${xScale(data[0].date)} ${yScale(data[0].correlation)}`
    data.slice(1).forEach((point) => {
      path += ` L ${xScale(point.date)} ${yScale(point.correlation)}`
    })
    return path
  }, [data])

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-48 w-full" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Rolling Correlation
            </CardTitle>
            <CardDescription>
              {symbol1} vs {symbol2} • {period}-day rolling window
            </CardDescription>
          </div>
          <Select value={period} onValueChange={setPeriod}>
            <SelectTrigger className="w-28">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10 days</SelectItem>
              <SelectItem value="30">30 days</SelectItem>
              <SelectItem value="60">60 days</SelectItem>
              <SelectItem value="90">90 days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={view} onValueChange={setView}>
          <TabsList>
            <TabsTrigger value="chart">Chart</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
          </TabsList>

          <TabsContent value="chart" className="mt-4">
            <div className="relative h-48 bg-muted/30 rounded-lg border overflow-hidden">
              <svg viewBox="0 0 600 200" className="w-full h-full">
                <defs>
                  <linearGradient id="corrGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="rgba(59, 130, 246, 0.3)" />
                    <stop offset="50%" stopColor="rgba(156, 163, 175, 0.1)" />
                    <stop offset="100%" stopColor="rgba(239, 68, 68, 0.3)" />
                  </linearGradient>
                </defs>

                <line x1="30" y1="100" x2="570" y2="100" stroke="currentColor" strokeOpacity="0.3" strokeWidth="1" strokeDasharray="4" />

                <line x1="30" y1="35" x2="570" y2="35" stroke="currentColor" strokeOpacity="0.2" strokeWidth="1" />
                <line x1="30" y1="165" x2="570" y2="165" stroke="currentColor" strokeOpacity="0.2" strokeWidth="1" />

                <path d={chartPath} fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />

                {data.filter((_, i) => i % Math.ceil(data.length / 5) === 0).map((point, i) => (
                  <circle
                    key={i}
                    cx={30 + (i * Math.ceil(data.length / 5) / data.length) * 540}
                    cy={100 - point.correlation * 65}
                    r="4"
                    fill={point.correlation > 0 ? '#22c55e' : '#ef4444'}
                    stroke="white"
                    strokeWidth="1"
                  />
                ))}
              </svg>

              <div className="absolute bottom-2 left-2 text-xs text-muted-foreground">
                Time →
              </div>
              <div className="absolute top-1/2 left-2 text-xs text-muted-foreground transform -rotate-90 origin-left" style={{ top: '40%' }}>
                Correlation
              </div>

              <div className="absolute top-2 right-2 flex gap-3 text-xs">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span>+1.0</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-gray-400" />
                  <span>0.0</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-red-500" />
                  <span>-1.0</span>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="analysis" className="mt-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="p-4 border rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">Average Correlation</p>
                <p className={cn('text-2xl font-bold', avgCorrelation > 0 ? 'text-green-600' : 'text-red-600')}>
                  {avgCorrelation >= 0 ? '+' : ''}{avgCorrelation.toFixed(3)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {correlationLevel === 'strong' && 'Strong correlation'}
                  {correlationLevel === 'moderate' && 'Moderate correlation'}
                  {correlationLevel === 'weak' && 'Weak correlation'}
                </p>
              </div>

              <div className="p-4 border rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">Range</p>
                <p className="text-2xl font-bold">
                  {minCorrelation.toFixed(2)} to {maxCorrelation.toFixed(2)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Min to Max over period
                </p>
              </div>

              <div className="p-4 border rounded-lg">
                <p className="text-xs text-muted-foreground mb-1">Interpretation</p>
                <div className="space-y-1">
                  {avgCorrelation > 0.7 && (
                    <p className="text-sm font-medium text-green-600">High positive correlation - assets move together</p>
                  )}
                  {avgCorrelation > 0.3 && avgCorrelation <= 0.7 && (
                    <p className="text-sm font-medium text-yellow-600">Moderate positive correlation</p>
                  )}
                  {avgCorrelation > -0.3 && avgCorrelation <= 0.3 && (
                    <p className="text-sm font-medium">Low correlation - good diversification</p>
                  )}
                  {avgCorrelation <= -0.3 && (
                    <p className="text-sm font-medium text-red-600">Negative correlation - inverse relationship</p>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-4 p-4 bg-muted rounded-lg">
              <h4 className="font-semibold mb-2">Understanding Correlation</h4>
              <p className="text-sm text-muted-foreground">
                Correlation measures how two assets move relative to each other.
                A correlation of +1.0 means they move perfectly together, while -1.0 means they move inversely.
                Values near 0 indicate little relationship. Diversification benefits increase when correlation is low.
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default RollingCorrelationChart
