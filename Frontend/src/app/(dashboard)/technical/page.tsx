'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Search, TrendingUp, BarChart2, Activity, LineChart as LineChartIcon } from 'lucide-react'

const POPULAR_SYMBOLS = [
  { symbol: 'AAPL', name: 'Apple Inc.', type: 'Stock' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', type: 'Stock' },
  { symbol: 'MSFT', name: 'Microsoft Corp.', type: 'Stock' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', type: 'Stock' },
  { symbol: 'TSLA', name: 'Tesla Inc.', type: 'Stock' },
  { symbol: 'NVDA', name: 'NVIDIA Corp.', type: 'Stock' },
  { symbol: 'META', name: 'Meta Platforms', type: 'Stock' },
  { symbol: 'BTC', name: 'Bitcoin', type: 'Crypto' },
  { symbol: 'ETH', name: 'Ethereum', type: 'Crypto' },
  { symbol: 'SOL', name: 'Solana', type: 'Crypto' },
]

export default function TechnicalPage() {
  const router = useRouter()
  const [searchInput, setSearchInput] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchInput.trim()) {
      router.push(`/technical/${searchInput.toUpperCase()}`)
    }
  }

  const handleSymbolClick = (symbol: string) => {
    router.push(`/technical/${symbol}`)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Technical Analysis</h1>
        <p className="text-muted-foreground">
          Advanced technical indicators and chart analysis for any asset
        </p>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Enter stock or crypto symbol..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
            className="pl-9"
          />
        </div>
        <Button type="submit">
          <BarChart2 className="mr-2 h-4 w-4" />
          Analyze
        </Button>
      </form>

      {/* Features */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-500" />
              Trend Indicators
            </CardTitle>
            <CardDescription>
              SMA, EMA, WMA, VWAP, Ichimoku
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Identify trends and trend reversals with moving averages and cloud indicators
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-orange-500" />
              Momentum Indicators
            </CardTitle>
            <CardDescription>
              RSI, MACD, Stochastic, CCI, MFI
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Measure overbought/oversold conditions and momentum strength
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <LineChartIcon className="h-5 w-5 text-purple-500" />
              Volatility Indicators
            </CardTitle>
            <CardDescription>
              Bollinger Bands, ATR, Parabolic SAR
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Analyze price volatility and set stop-loss levels
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Available Indicators */}
      <Card>
        <CardHeader>
          <CardTitle>Available Indicators</CardTitle>
          <CardDescription>
            15+ technical indicators with customizable parameters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">SMA</Badge>
            <Badge variant="outline">EMA</Badge>
            <Badge variant="outline">WMA</Badge>
            <Badge variant="outline">VWAP</Badge>
            <Badge variant="outline">Ichimoku</Badge>
            <Badge variant="outline">Parabolic SAR</Badge>
            <Badge variant="outline">RSI</Badge>
            <Badge variant="outline">MACD</Badge>
            <Badge variant="outline">Stochastic</Badge>
            <Badge variant="outline">CCI</Badge>
            <Badge variant="outline">MFI</Badge>
            <Badge variant="outline">Williams %R</Badge>
            <Badge variant="outline">Bollinger Bands</Badge>
            <Badge variant="outline">ATR</Badge>
            <Badge variant="outline">OBV</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Popular Symbols */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Access</CardTitle>
          <CardDescription>
            Click a symbol to start technical analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-5">
            {POPULAR_SYMBOLS.map((item) => (
              <button
                key={item.symbol}
                onClick={() => handleSymbolClick(item.symbol)}
                className="flex flex-col items-start p-3 rounded-lg border hover:bg-accent hover:border-primary transition-colors text-left"
              >
                <div className="flex items-center justify-between w-full">
                  <span className="font-medium">{item.symbol}</span>
                  <Badge variant={item.type === 'Crypto' ? 'default' : 'secondary'} className="text-xs">
                    {item.type}
                  </Badge>
                </div>
                <span className="text-sm text-muted-foreground truncate w-full">
                  {item.name}
                </span>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* How to Use */}
      <Card>
        <CardHeader>
          <CardTitle>How to Use</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-2 text-sm text-muted-foreground">
            <li>1. Enter a stock symbol (e.g., AAPL) or crypto symbol (e.g., BTC) above</li>
            <li>2. Click "Analyze" to view technical indicators</li>
            <li>3. Toggle indicators on/off using the selector</li>
            <li>4. Adjust time periods (30, 60, 90, 180, 365 days)</li>
            <li>5. View reference lines for overbought/oversold levels</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  )
}
