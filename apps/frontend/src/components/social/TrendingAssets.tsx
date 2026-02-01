'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { TrendingUp, TrendingDown, RefreshCw, Hash, ArrowUpRight } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

interface TrendingAsset {
  symbol: string
  sentiment_score: number
  sentiment_label: 'bullish' | 'bearish' | 'neutral'
  mention_count: number
  volume_change: number | null
}

interface TrendingAssetsProps {
  assets: TrendingAsset[]
  isLoading: boolean
  onRefresh?: () => void
  onSelectAsset?: (symbol: string) => void
  className?: string
}

export function TrendingAssets({
  assets,
  isLoading,
  onRefresh,
  onSelectAsset,
  className
}: TrendingAssetsProps) {
  const formatChange = (change: number | null) => {
    if (change === null) return '-'
    return `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`
  }

  const getChangeColor = (change: number | null) => {
    if (change === null) return 'text-muted-foreground'
    return change >= 0 ? 'text-green-600' : 'text-red-600'
  }

  const getSentimentColor = (label: string) => {
    switch (label) {
      case 'bullish': return 'bg-green-100 text-green-800'
      case 'bearish': return 'bg-red-100 text-red-800'
      default: return 'bg-yellow-100 text-yellow-800'
    }
  }

  if (isLoading) {
    return (
      <Card className={cn('rounded-none border-2 border-foreground', className)}>
        <CardHeader className="border-b-2 border-foreground">
          <Skeleton className="h-8 w-48" />
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-3">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('rounded-none border-2 border-foreground', className)}>
      <CardHeader className="border-b-2 border-foreground">
        <div className="flex items-center justify-between">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Trending Assets
          </CardTitle>
          {onRefresh && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRefresh}
              className="rounded-none border-2 font-bold uppercase"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {assets.length === 0 ? (
          <div className="p-8 text-center">
            <Hash className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-black uppercase text-lg mb-2">No Trending Assets</h3>
            <p className="text-muted-foreground font-mono text-sm">
              Social media activity will appear here
            </p>
          </div>
        ) : (
          <div className="divide-y-2 divide-border">
            {assets.map((asset, index) => (
              <div
                key={asset.symbol}
                className="p-4 hover:bg-muted/30 transition-colors cursor-pointer"
                onClick={() => onSelectAsset?.(asset.symbol)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-lg font-black">{index + 1}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-black uppercase text-lg">{asset.symbol}</span>
                        <Badge className={cn('text-xs', getSentimentColor(asset.sentiment_label))}>
                          {asset.sentiment_label}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground font-mono">
                        {asset.mention_count.toLocaleString()} mentions
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className={cn('font-mono font-bold', getChangeColor(asset.volume_change))}>
                        {formatChange(asset.volume_change)}
                      </p>
                      <p className="text-xs text-muted-foreground">vs yesterday</p>
                    </div>
                    <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
