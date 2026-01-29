'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { TrendingUp, TrendingDown, Globe, PieChart, DollarSign, Activity } from 'lucide-react'
import { GlobalMetrics } from '@/lib/types/coinmarketcap'

interface GlobalMetricsPanelProps {
  metrics?: GlobalMetrics | null
  loading?: boolean
  error?: string
}

export function GlobalMetricsPanel({ metrics, loading, error }: GlobalMetricsPanelProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !metrics) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Global Crypto Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No data available'}</p>
        </CardContent>
      </Card>
    )
  }

  const formatNumber = (value: number | undefined, decimals = 2) => {
    if (value === undefined || value === null) return 'N/A'
    if (Math.abs(value) >= 1e12) return `$${(value / 1e12).toFixed(decimals)}T`
    if (Math.abs(value) >= 1e9) return `$${(value / 1e9).toFixed(decimals)}B`
    if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(decimals)}M`
    return `$${value.toFixed(decimals)}`
  }

  const formatPercent = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A'
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(2)}%`
  }

  const metricsItems = [
    {
      label: 'Total Market Cap',
      value: formatNumber(metrics.quote?.USD?.totalMarketCap),
      change: metrics.quote?.USD?.totalMarketCap24hPercentChange,
      icon: PieChart,
      color: 'text-blue-500',
    },
    {
      label: '24h Volume',
      value: formatNumber(metrics.quote?.USD?.totalVolume24h),
      change: null,
      icon: Activity,
      color: 'text-purple-500',
    },
    {
      label: 'BTC Dominance',
      value: `${metrics.quote?.USD?.bitcoinDominance?.toFixed(2)}%`,
      change: metrics.quote?.USD?.bitcoinDominance24hPercentChange,
      icon: DollarSign,
      color: 'text-orange-500',
    },
    {
      label: 'ETH Dominance',
      value: `${metrics.quote?.USD?.ethereumDominance?.toFixed(2)}%`,
      change: metrics.quote?.USD?.ethereumDominance24hPercentChange,
      icon: Globe,
      color: 'text-indigo-500',
    },
    {
      label: 'Market Cap Change (24h)',
      value: formatPercent(metrics.quote?.USD?.totalMarketCap24hPercentChange),
      change: null,
      icon: TrendingUp,
      color: (metrics.quote?.USD?.totalMarketCap24hPercentChange ?? 0) >= 0 
        ? 'text-green-500' 
        : 'text-red-500',
    },
    {
      label: 'Cryptocurrencies',
      value: metrics.activeCryptocurrencies?.toLocaleString() || 'N/A',
      change: null,
      icon: Globe,
      color: 'text-cyan-500',
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5" />
          Global Crypto Metrics
        </CardTitle>
        <CardDescription>Real-time overview of the cryptocurrency market</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {metricsItems.map((item, index) => (
            <div
              key={index}
              className="flex flex-col p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">{item.label}</span>
                <item.icon className={`h-4 w-4 ${typeof item.color === 'string' ? item.color : ''}`} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xl font-bold">{item.value}</span>
                {item.change !== null && item.change !== undefined && (
                  <div className="flex items-center gap-1">
                    {item.change >= 0 ? (
                      <TrendingUp className="h-3 w-3 text-green-500" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-red-500" />
                    )}
                    <span
                      className={`text-xs font-medium ${
                        item.change >= 0 ? 'text-green-500' : 'text-red-500'
                      }`}
                    >
                      {formatPercent(item.change)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">
            Last updated: {new Date().toLocaleString()}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
