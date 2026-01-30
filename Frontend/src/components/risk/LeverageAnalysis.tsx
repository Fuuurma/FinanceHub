"use client"

import { useState, useMemo } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Area, ComposedChart } from 'recharts'
import { TrendingUp, TrendingDown, Activity, AlertTriangle, BarChart3, Target, Zap } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

export interface LeverageData {
  date: string
  grossLeverage: number
  netLeverage: number
  exposure: number
  marginUsed: number
}

export interface LeverageMetrics {
  avgGrossLeverage: number
  avgNetLeverage: number
  maxGrossLeverage: number
  minGrossLeverage: number
  currentExposure: number
  availableMargin: number
  marginUtilization: number
  leverageWarning: number
  leverageDanger: number
}

export interface LeverageAnalysisProps {
  data?: LeverageData[]
  metrics?: LeverageMetrics
  symbol?: string
  loading?: boolean
  error?: string
  className?: string
}

const LEVERAGE_COLORS = {
  gross: '#3b82f6',
  net: '#22c55e',
  exposure: '#f59e0b',
  warning: '#ef4444',
  danger: '#dc2626',
}

function LeverageChart({ data, warning, danger }: { data: LeverageData[]; warning: number; danger: number }) {
  const maxLeverage = Math.max(...data.map(d => Math.max(d.grossLeverage, d.netLeverage)), danger * 1.2, 2)

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="exposureGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis dataKey="date" tickFormatter={(v) => v.slice(5)} tick={{ fontSize: 10 }} />
        <YAxis domain={[0, maxLeverage]} tickFormatter={(v) => `${v.toFixed(1)}x`} tick={{ fontSize: 10 }} />
        <Tooltip
          formatter={(value: number, name: string) => [`${value.toFixed(2)}x`, name === 'grossLeverage' ? 'Gross' : 'Net']}
          contentStyle={{ backgroundColor: 'hsl(var(--background))', border: '1px solid hsl(var(--border))' }}
        />
        <ReferenceLine y={warning} stroke="#ef4444" strokeDasharray="5 5" label={{ value: 'Warning', position: 'insideTopRight', fill: '#ef4444', fontSize: 10 }} />
        <ReferenceLine y={danger} stroke="#dc2626" strokeDasharray="5 5" label={{ value: 'Danger', position: 'insideTopRight', fill: '#dc2626', fontSize: 10 }} />
        <ReferenceLine y={1} stroke="#94a3b8" />
        <Area type="monotone" dataKey="exposure" fill="url(#exposureGradient)" stroke="none" />
        <Line type="monotone" dataKey="grossLeverage" stroke={LEVERAGE_COLORS.gross} strokeWidth={2} dot={false} name="Gross Leverage" />
        <Line type="monotone" dataKey="netLeverage" stroke={LEVERAGE_COLORS.net} strokeWidth={2} dot={false} name="Net Leverage" />
      </ComposedChart>
    </ResponsiveContainer>
  )
}

function MetricsGrid({ metrics }: { metrics: LeverageMetrics }) {
  const isWarning = metrics.avgGrossLeverage >= metrics.leverageWarning
  const isDanger = metrics.avgGrossLeverage >= metrics.leverageDanger

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-muted/30 rounded-lg">
      <div className="text-center">
        <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
          <Activity className="h-4 w-4" />
          <span className="text-xs">Avg Gross</span>
        </div>
        <div className={cn('text-lg font-semibold', isDanger ? 'text-red-500' : isWarning ? 'text-amber-500' : 'text-green-500')}>
          {metrics.avgGrossLeverage.toFixed(2)}x
        </div>
      </div>

      <div className="text-center">
        <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
          <Target className="h-4 w-4" />
          <span className="text-xs">Avg Net</span>
        </div>
        <div className="text-lg font-semibold">{metrics.avgNetLeverage.toFixed(2)}x</div>
      </div>

      <div className="text-center">
        <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
          <Zap className="h-4 w-4" />
          <span className="text-xs">Margin Used</span>
        </div>
        <div className="text-lg font-semibold">{formatPercent(metrics.marginUtilization)}</div>
        <Progress value={metrics.marginUtilization * 100} className="h-1 mt-1" />
      </div>

      <div className="text-center">
        <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-xs">Available</span>
        </div>
        <div className="text-lg font-semibold">{formatCurrency(metrics.availableMargin)}</div>
      </div>
    </div>
  )
}

function LeverageGauge({ value, max, warning, danger }: { value: number; max: number; warning: number; danger: number }) {
  const percentage = Math.min((value / max) * 100, 100)
  const getColor = () => {
    if (value >= danger) return 'bg-red-500'
    if (value >= warning) return 'bg-amber-500'
    return 'bg-green-500'
  }

  return (
    <div className="flex items-center gap-4">
      <div className="flex-1">
        <div className="h-3 bg-muted rounded-full overflow-hidden">
          <div className={cn('h-full transition-all', getColor())} style={{ width: `${percentage}%` }} />
        </div>
        <div className="flex justify-between text-xs text-muted-foreground mt-1">
          <span>0x</span>
          <span>{max}x</span>
        </div>
      </div>
      <div className="text-lg font-semibold w-20 text-right">{value.toFixed(2)}x</div>
    </div>
  )
}

export function LeverageAnalysis({
  data = [],
  metrics,
  symbol,
  loading = false,
  error,
  className,
}: LeverageAnalysisProps) {
  const [view, setView] = useState<'chart' | 'gauge'>('chart')
  const [timeframe, setTimeframe] = useState('1M')

  const warningLevel = metrics?.leverageWarning || 2.0
  const dangerLevel = metrics?.leverageDanger || 3.0

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-48 mt-2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-72 w-full" />
        </CardContent>
      </Card>
    )
  }

  if (error || (!data.length && !metrics)) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Leverage Analysis
          </CardTitle>
          <CardDescription>Portfolio leverage and margin utilization</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No leverage data available'}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Leverage Analysis
              {symbol && <Badge variant="outline">{symbol}</Badge>}
            </CardTitle>
            <CardDescription>Portfolio leverage and margin utilization</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={timeframe} onValueChange={setTimeframe}>
              <SelectTrigger className="w-24 h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1W">1W</SelectItem>
                <SelectItem value="1M">1M</SelectItem>
                <SelectItem value="3M">3M</SelectItem>
                <SelectItem value="1Y">1Y</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {metrics && <MetricsGrid metrics={metrics} />}

        <Tabs value={view} onValueChange={(v) => setView(v as 'chart' | 'gauge')} className="mt-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="chart">Leverage Chart</TabsTrigger>
            <TabsTrigger value="gauge">Current Levels</TabsTrigger>
          </TabsList>

          <TabsContent value="chart" className="mt-4">
            {data.length > 0 ? (
              <LeverageChart data={data} warning={warningLevel} danger={dangerLevel} />
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No historical leverage data</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="gauge" className="mt-4">
            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Gross Leverage</span>
                  <span className="font-medium">{metrics?.avgGrossLeverage.toFixed(2) || 0}x</span>
                </div>
                <LeverageGauge value={metrics?.avgGrossLeverage || 0} max={dangerLevel * 1.5} warning={warningLevel} danger={dangerLevel} />
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Net Leverage</span>
                  <span className="font-medium">{metrics?.avgNetLeverage.toFixed(2) || 0}x</span>
                </div>
                <LeverageGauge value={metrics?.avgNetLeverage || 0} max={dangerLevel * 1.5} warning={warningLevel} danger={dangerLevel} />
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Margin Utilization</span>
                  <span className="font-medium">{formatPercent(metrics?.marginUtilization || 0)}</span>
                </div>
                <Progress value={(metrics?.marginUtilization || 0) * 100} className="h-3" />
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span>Safe (&lt;{warningLevel}x)</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-amber-500" />
              <span>Warning ({warningLevel}-{dangerLevel}x)</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span>Danger (&gt;{dangerLevel}x)</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
