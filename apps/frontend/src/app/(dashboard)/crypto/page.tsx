'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { CryptoOverviewCard } from '@/components/crypto/CryptoOverviewCard'
import { GlobalMetricsPanel } from '@/components/crypto/GlobalMetricsPanel'
import { TokenomicsPanel } from '@/components/crypto/TokenomicsPanel'
import { MarketPairsTable } from '@/components/crypto/MarketPairsTable'
import { coinmarketcapApi } from '@/lib/api/coinmarketcap'
import type { CryptoInfo, GlobalMetrics, MarketPair } from '@/lib/types/coinmarketcap'
import { Search, RefreshCw, TrendingUp, Coins, BarChart3 } from 'lucide-react'

export default function CryptoPage() {
  const searchParams = useSearchParams()
  const [symbol, setSymbol] = useState(searchParams.get('symbol') || 'BTC')
  const [searchInput, setSearchInput] = useState(symbol)
  const [crypto, setCrypto] = useState<CryptoInfo | null>(null)
  const [globalMetrics, setGlobalMetrics] = useState<GlobalMetrics | null>(null)
  const [marketPairs, setMarketPairs] = useState<MarketPair[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [trending, setTrending] = useState<any[]>([])

  const fetchAllData = async (sym: string) => {
    setLoading(true)
    setError('')

    try {
      const [cryptoResponse, metricsResponse, trendingResponse] = await Promise.all([
        coinmarketcapApi.getCryptoInfo(sym.toUpperCase()),
        coinmarketcapApi.getGlobalMetrics(),
        coinmarketcapApi.getTrending(),
      ])

      // Extract crypto info from response object
      const cryptoInfoData = cryptoResponse?.data
      const firstCryptoKey = cryptoInfoData ? Object.keys(cryptoInfoData)[0] : null
      const cryptoInfo = firstCryptoKey ? cryptoInfoData[firstCryptoKey] : null

      setCrypto(cryptoInfo)
      setGlobalMetrics(metricsResponse?.data || null)
      setTrending(trendingResponse?.data?.slice(0, 10) || [])

      // Fetch market pairs if we have a crypto
      if (cryptoInfo) {
        const pairsResponse = await coinmarketcapApi.getMarketPairs(sym.toUpperCase())
        setMarketPairs(pairsResponse?.data || [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (symbol) {
      fetchAllData(symbol)
    }
  }, [symbol])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchInput.trim()) {
      setSymbol(searchInput.toUpperCase())
    }
  }

  const handleRefresh = () => {
    if (symbol) {
      fetchAllData(symbol)
    }
  }

  const handleTrendingClick = (coinSymbol: string) => {
    setSymbol(coinSymbol)
    setSearchInput(coinSymbol)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Cryptocurrency</h1>
          <p className="text-muted-foreground">
            Real-time crypto prices, market data, and analytics from CoinMarketCap
          </p>
        </div>
        <Button onClick={handleRefresh} disabled={loading} variant="outline">
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Enter crypto symbol (e.g., BTC, ETH)..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
            className="pl-9"
          />
        </div>
        <Button type="submit" disabled={loading}>
          Search
        </Button>
      </form>

      {error && (
        <Card className="border-red-500">
          <CardContent className="pt-6">
            <p className="text-sm text-red-500">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Trending */}
      {trending.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Trending Cryptocurrencies
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {trending.map((coin, index) => (
                <Button
                  key={index}
                  variant={symbol === coin.symbol ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleTrendingClick(coin.symbol)}
                >
                  {coin.symbol}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      {crypto && !loading && (
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">
              <Coins className="mr-2 h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="tokenomics">
              <BarChart3 className="mr-2 h-4 w-4" />
              Tokenomics
            </TabsTrigger>
            <TabsTrigger value="pairs">
              <TrendingUp className="mr-2 h-4 w-4" />
              Market Pairs
            </TabsTrigger>
            <TabsTrigger value="global">
              <Globe className="mr-2 h-4 w-4" />
              Global Metrics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-6 md:grid-cols-2">
              <CryptoOverviewCard crypto={crypto} loading={loading} />
              <GlobalMetricsPanel metrics={globalMetrics} loading={loading} />
            </div>
          </TabsContent>

          <TabsContent value="tokenomics" className="space-y-4">
            <TokenomicsPanel crypto={crypto} loading={loading} />
          </TabsContent>

          <TabsContent value="pairs" className="space-y-4">
            <MarketPairsTable pairs={marketPairs} loading={loading} />
          </TabsContent>

          <TabsContent value="global" className="space-y-4">
            <GlobalMetricsPanel metrics={globalMetrics} loading={loading} />
          </TabsContent>
        </Tabs>
      )}

      {loading && (
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="grid gap-4 md:grid-cols-3">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <Skeleton key={i} className="h-24 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

function Globe({ className }: { className?: string }) {
  return <Search className={className} />
}
