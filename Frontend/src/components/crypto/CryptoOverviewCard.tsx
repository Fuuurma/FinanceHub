'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, DollarSign, Globe, Coins } from 'lucide-react'
import { CryptoInfo } from '@/lib/types/coinmarketcap'

interface CryptoOverviewCardProps {
  crypto?: CryptoInfo | null
  loading?: boolean
  error?: string
}

export function CryptoOverviewCard({ crypto, loading, error }: CryptoOverviewCardProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-24 w-full" />
        </CardContent>
      </Card>
    )
  }

  if (error || !crypto) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Crypto Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No data available'}</p>
        </CardContent>
      </Card>
    )
  }

  const formatNumber = (value: number | undefined, decimals = 2) => {
    if (value === undefined || value === null) return 'N/A'
    if (Math.abs(value) >= 1e9) return `$${(value / 1e9).toFixed(decimals)}B`
    if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(decimals)}M`
    if (Math.abs(value) >= 1e3) return `$${(value / 1e3).toFixed(decimals)}K`
    return `$${value.toFixed(decimals)}`
  }

  const formatPercent = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A'
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(2)}%`
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Coins className="h-5 w-5" />
            {crypto.name}
          </CardTitle>
          <Badge variant="secondary">Rank #{crypto.cmcRank}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Symbol</span>
          <span className="font-medium">{crypto.symbol}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Price</span>
          <span className="text-2xl font-bold">{formatNumber(crypto.quote?.USD?.price)}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">24h Change</span>
          <div className="flex items-center gap-2">
            {(crypto.quote?.USD?.percentChange24h ?? 0) >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
            <span
              className={`font-medium ${
                (crypto.quote?.USD?.percentChange24h ?? 0) >= 0
                  ? 'text-green-500'
                  : 'text-red-500'
              }`}
            >
              {formatPercent(crypto.quote?.USD?.percentChange24h)}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div>
            <span className="text-xs text-muted-foreground">Market Cap</span>
            <p className="text-lg font-semibold">{formatNumber(crypto.quote?.USD?.marketCap)}</p>
          </div>
          <div>
            <span className="text-xs text-muted-foreground">Volume (24h)</span>
            <p className="text-lg font-semibold">{formatNumber(crypto.quote?.USD?.volume24h)}</p>
          </div>
        </div>

        {crypto.description && (
          <div className="pt-4 border-t">
            <p className="text-sm text-muted-foreground line-clamp-3">{crypto.description}</p>
          </div>
        )}

        {crypto.urls?.website && crypto.urls.website.length > 0 && (
          <div className="flex items-center gap-2 pt-2">
            <Globe className="h-4 w-4 text-muted-foreground" />
            <a
              href={crypto.urls.website[0]}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-500 hover:underline"
            >
              Official Website
            </a>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
