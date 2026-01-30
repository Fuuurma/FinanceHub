'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { CryptoInfo } from '@/lib/types/coinmarketcap'

interface TokenomicsPanelProps {
  crypto?: CryptoInfo | null
  loading?: boolean
}

export function TokenomicsPanel({ crypto, loading }: TokenomicsPanelProps) {
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

  const supply = crypto.supply

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tokenomics - {crypto.symbol}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="p-4 rounded-lg border">
            <p className="text-sm text-muted-foreground">Circulating Supply</p>
            <p className="text-xl font-bold">{supply?.circulating?.toLocaleString() || 'N/A'}</p>
          </div>
          <div className="p-4 rounded-lg border">
            <p className="text-sm text-muted-foreground">Total Supply</p>
            <p className="text-xl font-bold">{supply?.total?.toLocaleString() || 'N/A'}</p>
          </div>
          <div className="p-4 rounded-lg border">
            <p className="text-sm text-muted-foreground">Max Supply</p>
            <p className="text-xl font-bold">{supply?.max?.toLocaleString() || 'Unlimited'}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
