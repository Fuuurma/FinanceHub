'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { GlobalMetrics } from '@/lib/types/coinmarketcap'

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

  return (
    <Card>
      <CardHeader>
        <CardTitle>Global Crypto Metrics</CardTitle>
        <CardDescription>Real-time overview of the cryptocurrency market</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <div className="p-4 rounded-lg border">
            <p className="text-sm text-muted-foreground">Total Market Cap</p>
            <p className="text-xl font-bold">{formatNumber(metrics.quote?.USD?.total_market_cap)}</p>
          </div>
          <div className="p-4 rounded-lg border">
            <p className="text-sm text-muted-foreground">24h Volume</p>
            <p className="text-xl font-bold">{formatNumber(metrics.quote?.USD?.total_volume_24h)}</p>
          </div>
          <div className="p-4 rounded-lg border">
            <p className="text-sm text-muted-foreground">BTC Dominance</p>
            <p className="text-xl font-bold">{metrics.bitcoin_dominance?.toFixed(2)}%</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
