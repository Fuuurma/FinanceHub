'use client'

import { useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts'
import { cn } from '@/lib/utils'
import type { ScreenerResult } from '@/lib/types/screener'

interface ScreenerChartProps {
  results: ScreenerResult[]
  chartType: 'price' | 'marketCap' | 'peRatio'
  className?: string
}

type ChartData = {
  name: string
  value: number
  count: number
}

const PRICE_RANGES = [
  { label: '$0-10', min: 0, max: 10 },
  { label: '$10-25', min: 10, max: 25 },
  { label: '$25-50', min: 25, max: 50 },
  { label: '$50-100', min: 50, max: 100 },
  { label: '$100-200', min: 100, max: 200 },
  { label: '$200+', min: 200, max: Infinity },
]

const MARKET_CAP_RANGES = [
  { label: 'Small (<$2B)', min: 0, max: 2e9 },
  { label: 'Mid ($2-10B)', min: 2e9, max: 10e9 },
  { label: 'Large ($10-50B)', min: 10e9, max: 50e9 },
  { label: 'Mega ($50-200B)', min: 50e9, max: 200e9 },
  { label: 'Huge ($200B+)', min: 200e9, max: Infinity },
]

const PE_RANGES = [
  { label: 'Loss', min: -Infinity, max: 0 },
  { label: '0-15', min: 0, max: 15 },
  { label: '15-25', min: 15, max: 25 },
  { label: '25-40', min: 25, max: 40 },
  { label: '40+', min: 40, max: Infinity },
]

function generateChartData(results: ScreenerResult[], ranges: typeof PRICE_RANGES, valueExtractor: (r: ScreenerResult) => number | null): ChartData[] {
  const data = ranges.map(range => ({
    name: range.label,
    value: 0,
    count: 0,
  }))

  results.forEach(result => {
    const value = valueExtractor(result)
    if (value === null || value === undefined) return

    const rangeIndex = ranges.findIndex(range => value >= range.min && value < range.max)
    if (rangeIndex !== -1) {
      data[rangeIndex].count++
      data[rangeIndex].value += value
    }
  })

  return data.filter(d => d.count > 0)
}

function formatValue(value: number, type: 'price' | 'marketCap' | 'peRatio'): string {
  if (type === 'marketCap') {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`
    if (value >= 1e9) return `$${(value / 1e9).toFixed(0)}B`
    return `$${(value / 1e6).toFixed(0)}M`
  }
  if (type === 'price') return `$${value.toFixed(2)}`
  return value.toFixed(1)
}

function formatCount(value: number): string {
  return value === 1 ? '1 stock' : `${value} stocks`
}

const COLORS = [
  'hsl(var(--chart-1))',
  'hsl(var(--chart-2))',
  'hsl(var(--chart-3))',
  'hsl(var(--chart-4))',
  'hsl(var(--chart-5))',
]

export function ScreenerChart({ results, chartType, className }: ScreenerChartProps) {
  const data = useMemo(() => {
    if (chartType === 'price') {
      return generateChartData(results, PRICE_RANGES, r => r.price)
    }
    if (chartType === 'marketCap') {
      return generateChartData(results, MARKET_CAP_RANGES, r => r.market_cap)
    }
    return generateChartData(results, PE_RANGES, r => r.pe_ratio)
  }, [results, chartType])

  const chartTitle = useMemo(() => {
    switch (chartType) {
      case 'price': return 'Price Distribution'
      case 'marketCap': return 'Market Cap Distribution'
      case 'peRatio': return 'P/E Ratio Distribution'
    }
  }, [chartType])

  const xAxisLabel = useMemo(() => {
    switch (chartType) {
      case 'price': return 'Price Range'
      case 'marketCap': return 'Market Cap'
      case 'peRatio': return 'P/E Ratio'
    }
  }, [chartType])

  if (results.length === 0) {
    return (
      <Card className={cn('h-full flex items-center justify-center', className)}>
        <CardContent className="text-center text-muted-foreground py-8">
          <p>No results to visualize</p>
          <p className="text-sm mt-1">Run a screener to see charts</p>
        </CardContent>
      </Card>
    )
  }

  if (data.length === 0) {
    return (
      <Card className={cn('h-full flex items-center justify-center', className)}>
        <CardContent className="text-center text-muted-foreground py-8">
          <p>No data in selected ranges</p>
          <p className="text-sm mt-1">Try adjusting your filters</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('h-full', className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">{chartTitle}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              label={{ value: xAxisLabel, position: 'insideBottom', offset: -5, fontSize: 11 }}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => value === 0 ? '' : value.toString()}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: 'var(--radius)',
              }}
              formatter={(value: number, name: string) => {
                if (name === 'count') {
                  return [formatCount(value), 'Stocks']
                }
                const avgValue = value / (data.find(d => d.name === (data.find(d => d.count > 0) || data[0]).name)?.count || 1)
                return [formatValue(avgValue, chartType), 'Avg Value']
              }}
              labelFormatter={(label) => label}
            />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-2 text-center text-xs text-muted-foreground">
          Showing {results.length} stocks across {data.length} ranges
        </div>
      </CardContent>
    </Card>
  )
}
