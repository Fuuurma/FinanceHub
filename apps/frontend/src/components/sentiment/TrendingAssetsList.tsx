'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface TrendingAsset {
  symbol: string
  name: string
  mentions: number
  sentiment: number
  sentimentLabel: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
  change24h: number
}

interface TrendingAssetsListProps {
  assets: TrendingAsset[]
  onAssetClick?: (symbol: string) => void
  onAssetHover?: (symbol: string | null) => void
  className?: string
}

const SENTIMENT_ICONS = {
  BULLISH: TrendingUp,
  BEARISH: TrendingDown,
  NEUTRAL: Minus
}

const SENTIMENT_COLORS = {
  BULLISH: 'text-success',
  BEARISH: 'text-destructive',
  NEUTRAL: 'text-muted-foreground'
}

const SENTIMENT_BG = {
  BULLISH: 'bg-success/10',
  BEARISH: 'bg-destructive/10',
  NEUTRAL: 'bg-muted/50'
}

export function TrendingAssetsList({ 
  assets, 
  onAssetClick, 
  onAssetHover,
  className 
}: TrendingAssetsListProps) {
  const sortedAssets = React.useMemo(() => {
    return [...assets].sort((a, b) => b.mentions - a.mentions)
  }, [assets])

  return (
    <Card className={cn('rounded-none border-1', className)}>
      <CardHeader className="border-b-1 pb-0">
        <CardTitle className="font-black uppercase flex items-center gap-2">
          <TrendingUp className="h-5 w-5" aria-hidden="true" />
          Trending Assets
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y-1" role="list" aria-label="Trending assets">
          {sortedAssets.length === 0 ? (
            <div className="p-8 text-center">
              <p className="font-mono text-sm text-muted-foreground">
                No trending assets
              </p>
            </div>
          ) : (
            sortedAssets.map((asset, index) => {
              const Icon = SENTIMENT_ICONS[asset.sentimentLabel]
              const colorClass = SENTIMENT_COLORS[asset.sentimentLabel]
              const bgClass = SENTIMENT_BG[asset.sentimentLabel]
              
              return (
                <article
                  key={asset.symbol}
                  role="listitem"
                  className="p-4 hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => onAssetClick?.(asset.symbol)}
                  onMouseEnter={() => onAssetHover?.(asset.symbol)}
                  onMouseLeave={() => onAssetHover?.(null)}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      onAssetClick?.(asset.symbol)
                    }
                  }}
                  aria-label={`${asset.symbol}: ${asset.mentions} mentions, ${asset.sentimentLabel}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono text-muted-foreground w-4">
                        #{index + 1}
                      </span>
                      <div>
                        <p className="font-black uppercase">{asset.symbol}</p>
                        <p className="text-xs text-muted-foreground truncate max-w-[120px]">
                          {asset.name}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className={cn('flex items-center gap-1 px-2 py-1 rounded-none border-1', bgClass)}>
                        <Icon className={cn('h-3 w-3', colorClass)} aria-hidden="true" />
                        <span className={cn('font-mono text-xs font-bold', colorClass)}>
                          {asset.sentiment >= 0 ? '+' : ''}{asset.sentiment.toFixed(2)}
                        </span>
                      </div>
                      
                      <div className="text-right">
                        <p className="font-mono text-xs font-medium">
                          {asset.mentions.toLocaleString()}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          mentions
                        </p>
                      </div>
                      
                      <div className={cn(
                        'flex items-center gap-1 font-mono text-xs',
                        asset.change24h >= 0 ? 'text-success' : 'text-destructive'
                      )}>
                        {asset.change24h >= 0 ? (
                          <TrendingUp className="h-3 w-3" aria-hidden="true" />
                        ) : (
                          <TrendingDown className="h-3 w-3" aria-hidden="true" />
                        )}
                        {asset.change24h >= 0 ? '+' : ''}{asset.change24h.toFixed(2)}%
                      </div>
                    </div>
                  </div>
                </article>
              )
            })
          )}
        </div>
      </CardContent>
    </Card>
  )
}
