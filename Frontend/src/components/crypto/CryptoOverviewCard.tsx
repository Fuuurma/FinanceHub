'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { CryptoInfo } from '@/lib/types/coinmarketcap'

interface CryptoOverviewCardProps {
  crypto?: CryptoInfo | null
  loading?: boolean
}

export function CryptoOverviewCard({ crypto, loading }: CryptoOverviewCardProps) {
  if (loading || !crypto) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{crypto.name} ({crypto.symbol})</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{crypto.description?.slice(0, 500)}...</p>
      </CardContent>
    </Card>
  )
}
