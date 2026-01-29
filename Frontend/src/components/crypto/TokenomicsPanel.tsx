'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Coins, CircleDollarSign, Lock, Unlock } from 'lucide-react'
import { CryptoInfo } from '@/lib/types/coinmarketcap'

interface TokenomicsPanelProps {
  crypto?: CryptoInfo | null
  loading?: boolean
  error?: string
}

export function TokenomicsPanel({ crypto, loading, error }: TokenomicsPanelProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    )
  }

  if (error || !crypto) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tokenomics</CardTitle>
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

  const platform = crypto.platform
  const maxSupply = crypto.maxSupply
  const circulatingSupply = crypto.circulatingSupply
  const totalSupply = crypto.totalSupply

  const circulatingPercent = maxSupply
    ? ((circulatingSupply ?? 0) / maxSupply) * 100
    : null

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Coins className="h-5 w-5" />
          Tokenomics
        </CardTitle>
        <CardDescription>Supply and token distribution details</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2 mb-1">
              <CircleDollarSign className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Circulating Supply</span>
            </div>
            <p className="text-lg font-semibold">{formatNumber(circulatingSupply, 0)}</p>
            <p className="text-xs text-muted-foreground">{crypto.symbol}</p>
          </div>

          <div className="p-3 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2 mb-1">
              <Unlock className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Total Supply</span>
            </div>
            <p className="text-lg font-semibold">{formatNumber(totalSupply, 0)}</p>
            <p className="text-xs text-muted-foreground">{crypto.symbol}</p>
          </div>

          <div className="p-3 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2 mb-1">
              <Lock className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Max Supply</span>
            </div>
            <p className="text-lg font-semibold">
              {maxSupply ? formatNumber(maxSupply, 0) : 'Infinite'}
            </p>
            <p className="text-xs text-muted-foreground">{crypto.symbol}</p>
          </div>

          <div className="p-3 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2 mb-1">
              <Coins className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">CMC Rank</span>
            </div>
            <p className="text-lg font-semibold">#{crypto.cmcRank}</p>
            <p className="text-xs text-muted-foreground">Global Rank</p>
          </div>
        </div>

        {circulatingPercent !== null && (
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Circulation Progress</span>
              <span className="text-sm text-muted-foreground">
                {circulatingPercent.toFixed(2)}% of max supply
              </span>
            </div>
            <Progress value={circulatingPercent} className="h-2" />
          </div>
        )}

        {platform && (
          <div className="pt-4 border-t">
            <span className="text-sm font-medium mb-2 block">Platform Information</span>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{platform.name}</Badge>
              <span className="text-xs text-muted-foreground">
                Contract: {platform.tokenAddress?.slice(0, 10)}...
              </span>
            </div>
          </div>
        )}

        {crypto.dateLaunched && (
          <div className="pt-4 border-t">
            <span className="text-sm font-medium">Launch Date</span>
            <p className="text-sm text-muted-foreground">
              {new Date(crypto.dateLaunched).toLocaleDateString()}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
