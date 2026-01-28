'use client'

import { useState, useEffect } from 'react'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js/auto'
import { Bar } from 'react-chartjs-2'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useRealtimeStore } from '@/stores/realtimeStore'
import { ORDERBOOK_CONFIG } from '@/lib/constants/realtime'
import type { OrderBookDepth } from '@/lib/constants/realtime'
import type { OrderBook as OrderBookType } from '@/lib/types/realtime'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

interface OrderBookProps {
  symbol: string
  depth?: OrderBookDepth
}

export function OrderBook({ symbol, depth = ORDERBOOK_CONFIG.DEFAULT_DEPTH }: OrderBookProps) {
  const { orderBooks, subscribeSingle, unsubscribeSingle } = useRealtimeStore()
  const [localDepth, setLocalDepth] = useState<OrderBookDepth>(depth)
  const [updateTimer, setUpdateTimer] = useState<NodeJS.Timeout | null>(null)

  useEffect(() => {
    subscribeSingle(symbol, ['orderbook'])

    return () => {
      unsubscribeSingle(symbol, ['orderbook'])
    }
  }, [symbol, subscribeSingle, unsubscribeSingle])

  const orderBook = orderBooks[symbol]

  useEffect(() => {
    setUpdateTimer(null)

    const timer = setTimeout(() => {
      setUpdateTimer(null)
    }, ORDERBOOK_CONFIG.UPDATE_DEBOUNCE_MS)

    setUpdateTimer(timer)

    return () => {
      if (timer) {
        clearTimeout(timer)
      }
    }
  }, [orderBook])

  if (!orderBook || orderBook.levels.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 border rounded-lg bg-background">
        <p className="text-muted-foreground">No order book data available</p>
      </div>
    )
  }

  const levels = orderBook.levels.slice(0, localDepth)
  const midPrice = orderBook.midPrice || (orderBook.levels.reduce((sum, level) => sum + level.price, 0) / orderBook.levels.length)

  const bids = levels.filter((level) => level.price < midPrice).reverse()
  const asks = levels.filter((level) => level.price > midPrice)

  const bidPrices = bids.map((l) => l.price)
  const bidVolumes = bids.map((l) => l.volume)

  const askPrices = asks.map((l) => l.price)
  const askVolumes = asks.map((l) => l.volume)

  const depthChartData = {
    labels: [...bidPrices.reverse(), ...askPrices],
    datasets: [
      {
        label: 'Bids',
        data: [...bidVolumes.reverse()],
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1,
        borderRadius: 4,
      },
      {
        label: 'Asks',
        data: askVolumes,
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderColor: 'rgb(239, 68, 68)',
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  }

  const depthChartOptions = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: (context: any) => {
            const dataset = context.dataset
            const price = context.label
            const volume = context.parsed.x

            return `${dataset.label}: ${volume?.toLocaleString()} @ $${price?.toFixed(2)}`
          },
        },
      },
    },
    scales: {
      x: {
        stacked: true,
        grid: {
          color: 'rgba(148, 163, 184, 0.1)',
        },
        ticks: {
          color: 'rgba(148, 163, 184, 0.5)',
          callback: (value: any) => value?.toLocaleString(),
        },
      },
      y: {
        grid: {
          color: 'rgba(148, 163, 184, 0.1)',
        },
        ticks: {
          color: 'rgba(148, 163, 184, 0.5)',
          callback: (value: any) => `$${value?.toFixed(2)}`,
        },
      },
    },
  }

  const handleDepthChange = (newDepth: OrderBookDepth) => {
    setLocalDepth(newDepth)
  }

  const maxVolume = Math.max(
    ...bids.map((b) => b.volume),
    ...asks.map((a) => a.volume)
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Order Book - {symbol}</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Depth:</span>
          <Select value={String(localDepth)} onValueChange={(v) => handleDepthChange(v as OrderBookDepth)}>
            <SelectTrigger className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ORDERBOOK_CONFIG.DEPTH_OPTIONS.map((option) => (
                <SelectItem key={option} value={String(option)}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <Tabs defaultValue="depth" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="depth">Depth Chart</TabsTrigger>
          <TabsTrigger value="ladder">Bid/Ask Ladder</TabsTrigger>
        </TabsList>

        <TabsContent value="depth">
          <div className="h-96">
            <Bar data={depthChartData} options={depthChartOptions} />
          </div>
        </TabsContent>

        <TabsContent value="ladder" className="h-96 overflow-auto">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <div className="text-xs font-semibold text-center text-green-600 p-2 border-b">
                BIDS
              </div>
              {bids.map((bid, index) => (
                <div
                  key={`bid-${index}`}
                  className="flex items-center justify-between p-2 hover:bg-muted/50"
                >
                  <span className="text-sm font-mono text-green-600">
                    ${bid.price.toFixed(2)}
                  </span>
                  <div className="flex items-center gap-2 flex-1 justify-end">
                    <div
                      className="h-4 bg-green-600/20 rounded"
                      style={{ width: `${(bid.volume / maxVolume) * 100}%` }}
                    />
                    <span className="text-sm font-mono">
                      {bid.volume.toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="space-y-1">
              <div className="text-xs font-semibold text-center text-red-600 p-2 border-b">
                ASKS
              </div>
              {asks.map((ask, index) => (
                <div
                  key={`ask-${index}`}
                  className="flex items-center justify-between p-2 hover:bg-muted/50"
                >
                  <div className="flex items-center gap-2 flex-1">
                    <div
                      className="h-4 bg-red-600/20 rounded"
                      style={{ width: `${(ask.volume / maxVolume) * 100}%` }}
                    />
                    <span className="text-sm font-mono">
                      {ask.volume.toLocaleString()}
                    </span>
                  </div>
                  <span className="text-sm font-mono text-red-600">
                    ${ask.price.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {midPrice && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-background border-2 border-primary px-4 py-2 rounded-lg shadow-lg">
              <div className="text-center">
                <div className="text-xs text-muted-foreground">Mid Price</div>
                <div className="text-lg font-bold font-mono">${midPrice.toFixed(2)}</div>
                <div className="text-xs text-muted-foreground">
                  Spread: ${orderBook.spread.toFixed(2)}
                </div>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
