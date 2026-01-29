'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts'
import { format } from 'date-fns'

interface IndicatorChartProps {
  data: Array<{
    timestamp: string
    value: number
    upper?: number
    middle?: number
    lower?: number
    signal?: string
    histogram?: number
    macd?: number
    signalLine?: number
    k?: number
    d?: number
  }>
  title: string
  color?: string
  showPrice?: boolean
  priceData?: Array<{ timestamp: string; close: number }>
  type?: 'line' | 'area' | 'bar'
  referenceLines?: Array<{ value: number; label: string; color: string }>
  height?: number
  loading?: boolean
  error?: string
}

export function IndicatorChart({
  data,
  title,
  color = '#3b82f6',
  showPrice = false,
  priceData,
  type = 'line',
  referenceLines,
  height = 300,
  loading,
  error,
}: IndicatorChartProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="w-full" style={{ height }} />
        </CardContent>
      </Card>
    )
  }

  if (error || !data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No data available'}</p>
        </CardContent>
      </Card>
    )
  }

  const chartData = data.map((d, i) => {
    const base: Record<string, any> = {
      timestamp: d.timestamp,
      value: d.value,
    }
    if (d.upper !== undefined) {
      base.upper = d.upper
      base.middle = d.middle
      base.lower = d.lower
    }
    if (d.histogram !== undefined) {
      base.histogram = d.histogram
    }
    if (d.macd !== undefined) {
      base.macd = d.macd
      base.signalLine = d.signal
    }
    if (d.k !== undefined) {
      base.k = d.k
      base.d = d.d
    }
    if (showPrice && priceData?.[i]) {
      base.price = priceData[i].close
    }
    return base
  })

  const formatXAxis = (timestamp: string) => {
    try {
      return format(new Date(timestamp), 'MMM dd')
    } catch {
      return ''
    }
  }

  const formatTooltip = (timestamp: string) => {
    try {
      return format(new Date(timestamp), 'MMM dd, yyyy HH:mm')
    } catch {
      return timestamp
    }
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded-lg p-3 shadow-lg">
          <p className="text-sm font-medium mb-2">{formatTooltip(label)}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value?.toFixed(4)}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  const getSignalBadge = (value: number | undefined, overbought: number, oversold: number) => {
    if (value === undefined) return null
    if (value > overbought) return <Badge variant="destructive">Overbought</Badge>
    if (value < oversold) return <Badge variant="default">Oversold</Badge>
    return <Badge variant="secondary">Neutral</Badge>
  }

  const latestValue = data[data.length - 1]?.value

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{title}</CardTitle>
          {latestValue !== undefined && (
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">{latestValue.toFixed(4)}</span>
              {title.includes('RSI') && getSignalBadge(latestValue, 70, 30)}
              {title.includes('Stochastic') && getSignalBadge(latestValue, 80, 20)}
              {title.includes('CCI') && getSignalBadge(latestValue, 100, -100)}
              {title.includes('MFI') && getSignalBadge(latestValue, 80, 20)}
              {title.includes('Williams') && getSignalBadge(latestValue, -20, -80)}
            </div>
          )}
        </div>
        {data.length > 0 && (
          <CardDescription>
            Last updated: {format(new Date(data[data.length - 1]?.timestamp), 'MMM dd, yyyy HH:mm')}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={formatXAxis}
              className="text-xs"
              tick={{ fill: 'muted-foreground' }}
            />
            <YAxis
              className="text-xs"
              tick={{ fill: 'muted-foreground' }}
              domain={['auto', 'auto']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />

            {showPrice && (
              <Line
                type="monotone"
                dataKey="price"
                stroke="#8884d8"
                strokeWidth={1}
                dot={false}
                name="Price"
              />
            )}

            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={false}
              name={title}
              connectNulls
            />

            {data[0]?.upper !== undefined && (
              <>
                <Line
                  type="monotone"
                  dataKey="upper"
                  stroke="#ef4444"
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Upper"
                />
                <Line
                  type="monotone"
                  dataKey="middle"
                  stroke={color}
                  strokeWidth={1}
                  dot={false}
                  name="Middle"
                />
                <Line
                  type="monotone"
                  dataKey="lower"
                  stroke="#22c55e"
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Lower"
                />
              </>
            )}

            {data[0]?.histogram !== undefined && (
              <>
                <Line
                  type="monotone"
                  dataKey="macd"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  name="MACD"
                />
                <Line
                  type="monotone"
                  dataKey="signalLine"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={false}
                  name="Signal"
                />
              </>
            )}

            {data[0]?.k !== undefined && (
              <>
                <Line
                  type="monotone"
                  dataKey="k"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  name="%K"
                />
                <Line
                  type="monotone"
                  dataKey="d"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={false}
                  name="%D"
                />
              </>
            )}

            {referenceLines?.map((ref, index) => (
              <ReferenceLine
                key={index}
                y={ref.value}
                stroke={ref.color}
                strokeDasharray="3 3"
                label={{ value: ref.label, fill: ref.color, fontSize: 12 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
