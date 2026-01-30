'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import type { YieldCurvePoint } from '@/lib/types'

interface YieldCurveChartProps {
  data: YieldCurvePoint[]
  loading?: boolean
  showSpreads?: boolean
  className?: string
}

export function YieldCurveChart({ data, loading = false, showSpreads = false, className }: YieldCurveChartProps) {
  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    )
  }

  const chartData = data.map((point) => ({
    maturity: point.maturity,
    rate: point.rate,
  }))

  const avgRate = data.reduce((sum, d) => sum + d.rate, 0) / data.length

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>US Treasury Yield Curve</CardTitle>
        <CardDescription>
          {showSpreads ? 'Yield curve with spread analysis' : 'Current yields by maturity'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8} />
                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="maturity"
              className="text-xs"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
            />
            <YAxis
              className="text-xs"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
              domain={['dataMin - 0.5', 'dataMax + 0.5']}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--background))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '6px',
              }}
              labelStyle={{ color: 'hsl(var(--foreground))' }}
              formatter={(value: number) => [`${value.toFixed(2)}%`, 'Yield']}
            />
            <ReferenceLine
              y={avgRate}
              label="Avg"
              stroke="hsl(var(--muted-foreground))"
              strokeDasharray="3 3"
            />
            <Area
              type="monotone"
              dataKey="rate"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorRate)"
            />
          </AreaChart>
        </ResponsiveContainer>
        {showSpreads && (
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {data.find((d) => d.maturity === '10y')?.rate.toFixed(2) || '-'}%
              </div>
              <div className="text-xs text-muted-foreground">10-Year</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {data.find((d) => d.maturity === '2y')?.rate.toFixed(2) || '-'}%
              </div>
              <div className="text-xs text-muted-foreground">2-Year</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {data.find((d) => d.maturity === '3m')?.rate.toFixed(2) || '-'}%
              </div>
              <div className="text-xs text-muted-foreground">3-Month</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
