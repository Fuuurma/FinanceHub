/**
 * Similar Assets Card Component
 * Displays assets similar to the current one based on sector/industry
 */

'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, ArrowUpRight } from 'lucide-react'

interface SimilarAsset {
  symbol: string
  name: string
  correlation: number
  change?: number
  changePercent?: number
}

interface SimilarAssetsProps {
  assets: SimilarAsset[]
  currentAssetSymbol: string
}

export function SimilarAssetsCard({ assets, currentAssetSymbol }: SimilarAssetsProps) {
  if (!assets || assets.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Similar Assets</CardTitle>
        <CardDescription>
          Related {(assets.length > 0 && assets[0]?.symbol?.includes('-')) ? 'cryptocurrencies' : 'stocks'} based on sector and industry
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {assets.map((asset) => (
            <a
              key={asset.symbol}
              href={`/assets/${asset.symbol}`}
              className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors group"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{asset.symbol}</span>
                  <Badge variant="outline" className="text-xs">
                    {Math.round(asset.correlation * 100)}% match
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-1">{asset.name}</p>
              </div>
              
              {asset.changePercent !== undefined && (
                <div className="text-right">
                  <div className={`flex items-center gap-1 font-semibold ${
                    asset.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {asset.changePercent >= 0 ? (
                      <TrendingUp className="h-4 w-4" />
                    ) : (
                      <TrendingDown className="h-4 w-4" />
                    )}
                    <span>{asset.changePercent >= 0 ? '+' : ''}{asset.changePercent.toFixed(2)}%</span>
                  </div>
                </div>
              )}
              
              <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors ml-2" />
            </a>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
