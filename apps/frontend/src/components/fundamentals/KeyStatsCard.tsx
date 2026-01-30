'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { KeyStats } from '@/lib/types/iex-cloud'

interface KeyStatsCardProps {
  stats?: KeyStats | null
  loading?: boolean
  error?: string
}

export function KeyStatsCard({ stats, loading, error }: KeyStatsCardProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="flex justify-between">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-20" />
            </div>
          ))}
        </CardContent>
      </Card>
    )
  }

  if (error || !stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Key Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No data available'}</p>
        </CardContent>
      </Card>
    )
  }

  const formatNumber = (value: number | undefined, decimals = 2) => {
    if (value === undefined || value === null) return 'N/A'
    if (Math.abs(value) >= 1e9) return `${(value / 1e9).toFixed(decimals)}B`
    if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(decimals)}M`
    if (Math.abs(value) >= 1e3) return `${(value / 1e3).toFixed(decimals)}K`
    return value.toFixed(decimals)
  }

  const formatPercent = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A'
    return `${value.toFixed(2)}%`
  }

  const renderChange = (value: number | undefined) => {
    if (value === undefined || value === null || value === 0) {
      return <Minus className="h-3 w-3 text-muted-foreground" />
    }
    if (value > 0) {
      return <TrendingUp className="h-3 w-3 text-green-500" />
    }
    return <TrendingDown className="h-3 w-3 text-red-500" />
  }

  const statItems = [
    { label: 'Market Cap', value: formatNumber(stats.marketCap), change: undefined },
    { label: 'PE Ratio', value: stats.peRatio?.toFixed(2) || 'N/A', change: undefined },
    { label: 'Forward PE', value: stats.forwardPE?.toFixed(2) || 'N/A', change: undefined },
    { label: 'EPS', value: formatNumber(stats.eps), change: undefined },
    { label: 'Dividend Yield', value: formatPercent(stats.dividendYield), change: undefined },
    { label: 'Beta', value: stats.beta?.toFixed(2) || 'N/A', change: undefined },
    { label: '52W High', value: formatNumber(stats.week52High, 2), change: undefined },
    { label: '52W Low', value: formatNumber(stats.week52Low, 2), change: undefined },
    { label: 'Avg Volume', value: formatNumber(stats.avgTotalVolume), change: undefined },
    { label: 'Shares Outstanding', value: formatNumber(stats.sharesOutstanding), change: undefined },
    { label: 'Price to Book', value: stats.priceToBook?.toFixed(2) || 'N/A', change: undefined },
    { label: 'EV to EBITDA', value: stats.evToEbitda?.toFixed(2) || 'N/A', change: undefined },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Key Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {statItems.map((item, index) => (
            <div key={index} className="flex items-center justify-between py-2 border-b last:border-0">
              <span className="text-sm text-muted-foreground">{item.label}</span>
              <div className="flex items-center gap-2">
                {item.change !== undefined && renderChange(item.change)}
                <span className="text-sm font-medium">{item.value}</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
