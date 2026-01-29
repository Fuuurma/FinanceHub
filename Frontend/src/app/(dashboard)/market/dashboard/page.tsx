'use client'

import { useEffect } from 'react'
import { useMarketStore } from '@/stores/marketStore'
import { useWatchlistStore } from '@/stores/watchlistStore'
import { useRealtimeStore } from '@/stores/realtimeStore'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ConnectionStatus } from '@/components/realtime/ConnectionStatus'
import { LivePriceTicker } from '@/components/realtime/LivePriceTicker'

export default function MarketDashboardPage() {
  const { marketData, fetchMarketData } = useMarketStore()
  const { watchlists, fetchWatchlists } = useWatchlistStore()
  const { connectionState, connect } = useRealtimeStore()

  useEffect(() => {
    fetchMarketData('stock')
    fetchWatchlists()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Market Dashboard</h1>
          <p className="text-muted-foreground">Real-time market data and analytics</p>
        </div>
        <ConnectionStatus />
      </div>
      <LivePriceTicker />
      <div className="text-2xl font-bold">Market Dashboard Content</div>
    </div>
  )
}
