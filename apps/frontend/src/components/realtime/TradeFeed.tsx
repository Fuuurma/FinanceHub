'use client'

import { useState, useEffect, useRef } from 'react'
import { ArrowUp, ArrowDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useRealtimeStore } from '@/stores/realtimeStore'
import { WS_CONFIG } from '@/lib/constants/realtime'
import type { TradeFilter } from '@/lib/constants/realtime'
import type { RealTimeTrade as TradeType } from '@/lib/types/realtime'

interface TradeFeedProps {
  symbol: string
  limit?: number
}

export function TradeFeed({ symbol, limit = WS_CONFIG.TRADE_FEED_LIMIT }: TradeFeedProps) {
  const { trades, subscribeSingle, unsubscribeSingle } = useRealtimeStore()
  const [filter, setFilter] = useState<TradeFilter>('all')
  const [autoScroll, setAutoScroll] = useState(true)
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const [flashingTrades, setFlashingTrades] = useState<Set<number>>(new Set())

  useEffect(() => {
    subscribeSingle(symbol, ['trades'])

    return () => {
      unsubscribeSingle(symbol, ['trades'])
    }
  }, [symbol, subscribeSingle, unsubscribeSingle])

  const symbolTrades = (trades[symbol] || []).slice(0, limit)

  useEffect(() => {
    const timer = setTimeout(() => {
      setFlashingTrades(new Set())
    }, 500)

    return () => clearTimeout(timer)
  }, [symbolTrades])

  useEffect(() => {
    if (autoScroll && scrollContainerRef.current && symbolTrades.length > 0) {
      scrollContainerRef.current.scrollTop = 0
    }
  }, [symbolTrades, autoScroll])

  const filteredTrades = symbolTrades.filter((trade) => {
    if (filter === 'all') return true
    if (filter === 'buys') return trade.isBuy
    if (filter === 'sells') return !trade.isBuy
    return true
  })

  const filterOptions: { value: TradeFilter; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'buys', label: 'Buys' },
    { value: 'sells', label: 'Sells' },
  ]

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })
  }

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`
  }

  const isTradeFlashing = (trade: TradeType) => {
    return flashingTrades.has(parseInt(trade.tradeId))
  }

  if (symbolTrades.length === 0) {
    return (
      <div className="flex flex-col h-96 border rounded-lg bg-background">
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">Trade Feed - {symbol}</h3>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <p className="text-muted-foreground">No trades available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-96 border rounded-lg bg-background">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-lg font-semibold">Trade Feed - {symbol}</h3>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Filter:</span>
            <div className="flex">
              {filterOptions.map((option) => (
                <Button
                  key={option.value}
                  size="sm"
                  variant={filter === option.value ? 'default' : 'outline'}
                  onClick={() => setFilter(option.value)}
                  className="rounded-none rounded-l-none first:rounded-l-l first:rounded-r-none last:rounded-r-l last:rounded-r-none"
                >
                  {option.label}
                </Button>
              ))}
            </div>
          </div>

          <Button
            size="sm"
            variant="outline"
            onClick={() => setAutoScroll(!autoScroll)}
            className="text-xs"
          >
            {autoScroll ? 'Auto-scroll: On' : 'Auto-scroll: Off'}
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-auto" ref={scrollContainerRef}>
        <table className="w-full">
          <thead className="sticky top-0 bg-background">
            <tr className="text-xs text-muted-foreground">
              <th className="p-3 text-left">Time</th>
              <th className="p-3 text-right">Price</th>
              <th className="p-3 text-right">Size</th>
              <th className="p-3 text-left">Type</th>
              <th className="p-3 text-left">Exchange</th>
            </tr>
          </thead>
          <tbody>
            {filteredTrades.map((trade, index) => (
              <tr
                key={trade.tradeId}
                className={`
                  border-b hover:bg-muted/50 transition-colors
                  ${isTradeFlashing(trade) ? 'bg-muted/30' : ''}
                `}
              >
                <td className="p-3 text-sm font-mono text-muted-foreground">
                  {formatTime(trade.timestamp)}
                </td>
                <td className="p-3 text-sm font-mono text-right">
                  {formatPrice(trade.price)}
                </td>
                <td className="p-3 text-sm font-mono text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div
                      className="h-1 bg-foreground/30 rounded"
                      style={{ width: `${(trade.quantity / Math.max(...symbolTrades.map((t) => t.quantity))) * 100}px` }}
                    />
                    <span>{trade.quantity.toLocaleString()}</span>
                  </div>
                </td>
                <td className="p-3">
                  <div className={`
                    inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold
                    ${trade.isBuy ? 'bg-green-500/10 text-green-600' : 'bg-red-500/10 text-red-600'}
                  `}>
                    {trade.isBuy ? (
                      <ArrowUp className="h-3 w-3" />
                    ) : (
                      <ArrowDown className="h-3 w-3" />
                    )}
                    <span>{trade.tradeType}</span>
                  </div>
                </td>
                <td className="p-3 text-sm text-muted-foreground">
                  {trade.exchange}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="p-2 border-t bg-muted/20">
        <p className="text-xs text-muted-foreground text-center">
          Showing {filteredTrades.length} of {symbolTrades.length} trades
          {filter !== 'all' && ` (${filter})`}
        </p>
      </div>
    </div>
  )
}
