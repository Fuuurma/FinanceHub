'use client'

import { useState, useEffect } from 'react'
import { ArrowUp, ArrowDown } from 'lucide-react'
import { useRealtimeStore } from '@/stores/realtimeStore'
import { useWatchlistStore } from '@/stores/watchlistStore'
import { TICKER_CONFIG } from '@/lib/constants/realtime'
import type { RealTimePrice } from '@/lib/types/realtime'

export function LivePriceTicker() {
  const { prices } = useRealtimeStore()
  const { watchlists } = useWatchlistStore()
  const [isPaused, setIsPaused] = useState(false)
  const [flashingSymbols, setFlashingSymbols] = useState<Set<string>>(new Set())

  const symbols = Object.keys(prices)
  const displaySymbols = symbols.slice(0, TICKER_CONFIG.MAX_SYMBOLS)

  useEffect(() => {
    const interval = setInterval(() => {
      setFlashingSymbols(new Set())
    }, TICKER_CONFIG.FLASH_DURATION)

    return () => clearInterval(interval)
  }, [prices])

  useEffect(() => {
    const prevPrices = new Map<string, number>()
    symbols.forEach((symbol) => {
      if (prices[symbol]) {
        prevPrices.set(symbol, prices[symbol].price)
      }
    })

    return () => {
      symbols.forEach((symbol) => {
        const currentPrice = prices[symbol]?.price
        const previousPrice = prevPrices.get(symbol)

        if (currentPrice !== undefined && previousPrice !== undefined && currentPrice !== previousPrice) {
          setFlashingSymbols((prev) => new Set(prev).add(symbol))
        }
      })
    }
  }, [prices, symbols])

  const getPriceColor = (symbol: string): string => {
    if (flashingSymbols.has(symbol)) {
      const price = prices[symbol]
      if (price && price.changePercent > 0) {
        return 'text-green-500'
      } else if (price && price.changePercent < 0) {
        return 'text-red-500'
      }
    }
    return 'text-foreground'
  }

  const getChangeIcon = (price: RealTimePrice) => {
    if (price.changePercent > 0) {
      return <ArrowUp className="h-3 w-3 text-green-500" />
    } else if (price.changePercent < 0) {
      return <ArrowDown className="h-3 w-3 text-red-500" />
    }
    return null
  }

  if (displaySymbols.length === 0) {
    return (
      <div className="p-4 border rounded-lg bg-background">
        <p className="text-sm text-muted-foreground">No real-time data available. Connect to start streaming.</p>
      </div>
    )
  }

  return (
    <div 
      className="relative overflow-hidden border rounded-lg bg-background"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div 
        className="flex gap-8 whitespace-nowrap py-3 px-4"
        style={{
          animation: `scroll ${TICKER_CONFIG.SCROLL_SPEED}s linear infinite`,
          animationPlayState: isPaused ? 'paused' : 'running',
        }}
      >
        {[...displaySymbols, ...displaySymbols].map((symbol, index) => {
          const price = prices[symbol]
          if (!price) return null

          return (
            <div 
              key={`${symbol}-${index}`} 
              className="flex items-center gap-3 shrink-0"
            >
              <span className="text-xs font-mono font-bold text-muted-foreground">
                {symbol}
              </span>
              <span className={`text-sm font-mono font-bold ${getPriceColor(symbol)}`}>
                ${price.price.toFixed(2)}
              </span>
              <div className="flex items-center gap-1">
                {getChangeIcon(price)}
                <span className="text-xs font-mono">
                  {price.changePercent > 0 ? '+' : ''}{price.changePercent.toFixed(2)}%
                </span>
              </div>
              <span className="text-xs text-muted-foreground">
                Vol: {price.volume.toLocaleString()}
              </span>
            </div>
          )
        })}
      </div>

      <style jsx>{`
        @keyframes scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
      `}</style>
    </div>
  )
}
