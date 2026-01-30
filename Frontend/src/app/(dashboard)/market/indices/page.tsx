'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { PageHeader } from '@/components/ui/page-header'
import { StatsGrid } from '@/components/ui/stats-grid'
import { PageErrorBoundary } from '@/components/ui/PageErrorBoundary'
import {
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Target,
} from 'lucide-react'

const INDICES = [
  { symbol: 'SPX', name: 'S&P 500', price: 4875.43, change: 1.23, volume: 2.3, region: 'US' },
  { symbol: 'NDX', name: 'NASDAQ-100', price: 15234.56, change: 2.45, volume: 1.8, region: 'US' },
  { symbol: 'DJI', name: 'DOW JONES', price: 38234.12, change: 0.89, volume: 0.9, region: 'US' },
  { symbol: 'UKX', name: 'FTSE 100', price: 7567.89, change: -0.34, volume: 0.7, region: 'UK' },
  { symbol: 'DAX', name: 'DAX 40', price: 16789.23, change: 1.56, volume: 1.2, region: 'EU' },
  { symbol: 'NKY', name: 'Nikkei 225', price: 34567.89, change: 0.12, volume: 1.5, region: 'Asia' },
  { symbol: 'SHANGHAI', name: 'Shanghai Composite', price: 2890.45, change: -0.67, volume: 2.1, region: 'Asia' },
  { symbol: 'RTS', name: 'MOEX Russia', price: 3421.56, change: 0.45, volume: 0.5, region: 'EU' },
  { symbol: 'BSE', name: 'BSE Sensex', price: 71234.56, change: 0.89, volume: 1.1, region: 'Asia' },
  { symbol: 'TSX', name: 'S&P/TSX', price: 19876.34, change: 0.34, volume: 0.8, region: 'US' },
]

function MarketIndicesPageContent() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 600)
    return () => clearTimeout(timer)
  }, [])

  const stats = [
    { title: 'Indices Tracked', value: INDICES.length, description: 'global indices' },
    { title: 'Top Gainer', value: 'NDX', change: 2.45, changeLabel: 'NASDAQ-100' },
    { title: 'Top Loser', value: 'SHANGHAI', change: -0.67, changeLabel: 'Shanghai' },
    { title: 'Avg Change', value: '0.59%', change: 0.59, changeLabel: 'all indices' },
  ]

  const formatChange = (change: number): string => {
    const prefix = change >= 0 ? '+' : ''
    return `${prefix}${change.toFixed(2)}%`
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Market Indices"
        description="Global market indices and performance"
        loading={loading}
        onRefresh={() => setLoading(true)}
      />

      {error && (
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : (
        <StatsGrid stats={stats} />
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            All Indices
          </CardTitle>
          <CardDescription>Real-time performance of global market indices</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-20" />
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {INDICES.map((index) => (
                <div
                  key={index.symbol}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <Badge variant="outline">{index.symbol}</Badge>
                    <div>
                      <div className="font-semibold">{index.name}</div>
                      <div className="text-sm text-muted-foreground">
                        Volume: {index.volume}B • {index.region}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{index.price.toFixed(2)}</div>
                    <div className={`flex items-center justify-end gap-1 text-sm ${index.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {index.change >= 0 ? (
                        <ArrowUpRight className="h-4 w-4" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4" />
                      )}
                      <span className="font-semibold">{formatChange(index.change)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-600">
              <TrendingUp className="h-5 w-5" />
              Top Gainers
            </CardTitle>
            <CardDescription>Best performing indices today</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {INDICES.filter(i => i.change > 0).sort((a, b) => b.change - a.change).slice(0, 5).map((index) => (
                <div key={index.symbol} className="flex items-center justify-between p-3 rounded-lg bg-green-50 dark:bg-green-950">
                  <div>
                    <div className="font-semibold">{index.symbol}</div>
                    <div className="text-sm text-muted-foreground">{index.name}</div>
                  </div>
                  <div className="text-green-600 font-semibold">+{index.change.toFixed(2)}%</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <TrendingDown className="h-5 w-5" />
              Top Losers
            </CardTitle>
            <CardDescription>Worst performing indices today</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {INDICES.filter(i => i.change < 0).sort((a, b) => a.change - b.change).slice(0, 5).map((index) => (
                <div key={index.symbol} className="flex items-center justify-between p-3 rounded-lg bg-red-50 dark:bg-red-950">
                  <div>
                    <div className="font-semibold">{index.symbol}</div>
                    <div className="text-sm text-muted-foreground">{index.name}</div>
                  </div>
                  <div className="text-red-600 font-semibold">{index.change.toFixed(2)}%</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default function MarketIndicesPage() {
  return (
    <PageErrorBoundary
      onError={(error, errorInfo) => {
        console.error('Market Indices page error:', error, errorInfo)
      }}
    >
      <MarketIndicesPageContent />
    </PageErrorBoundary>
  )
}
