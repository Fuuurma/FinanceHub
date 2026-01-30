'use client'

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, X, ExternalLink } from 'lucide-react'
import { cn, formatCurrency } from '@/lib/utils'
import type { WatchlistItem as WatchlistItemType } from './WatchlistManager'

interface WatchlistItemProps {
  item: WatchlistItemType
  onRemove?: () => void
}

export function WatchlistItem({ item, onRemove }: WatchlistItemProps) {
  const isPositive = item.change >= 0

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-0">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg">{item.symbol}</span>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
              <span className="text-sm text-muted-foreground">{item.companyName}</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="font-bold text-lg">{formatCurrency(item.price)}</p>
              <div className="flex items-center gap-1 justify-end">
                {isPositive ? (
                  <TrendingUp className="h-3 w-3 text-green-600" />
                ) : (
                  <TrendingDown className="h-3 w-3 text-red-600" />
                )}
                <span
                  className={cn(
                    'text-sm font-medium',
                    isPositive ? 'text-green-600' : 'text-red-600'
                  )}
                >
                  {isPositive ? '+' : ''}{item.change.toFixed(2)} ({item.changePercent.toFixed(2)}%)
                </span>
              </div>
            </div>

            {onRemove && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onRemove}
                className="text-muted-foreground hover:text-red-600"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>

        {item.notes && (
          <div className="px-4 pb-3">
            <Badge variant="outline" className="text-xs">
              {item.notes}
            </Badge>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default WatchlistItem
