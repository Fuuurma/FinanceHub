'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { iexCloudApi } from '@/lib/api/iex-cloud'
import type { MarketMover } from '@/lib/types/iex-cloud'
import { TrendingUp, TrendingDown, Activity, RefreshCw, ExternalLink } from 'lucide-react'
import Link from 'next/link'

type MoverType = 'gainers' | 'losers' | 'mostactive'

export default function MarketMoversPage() {
  const [gainers, setGainers] = useState<MarketMover[]>([])
  const [losers, setLosers] = useState<MarketMover[]>([])
  const [mostActive, setMostActive] = useState<MarketMover[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<MoverType>('gainers')

  const fetchMarketMovers = async () => {
    setLoading(true)
    setError('')

    try {
      const [gainersData, losersData, mostActiveData] = await Promise.all([
        iexCloudApi.getMarketMovers('gainers'),
        iexCloudApi.getMarketMovers('losers'),
        iexCloudApi.getMarketMovers('mostactive'),
      ])

      setGainers(gainersData)
      setLosers(losersData)
      setMostActive(mostActiveData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch market movers')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMarketMovers()
  }, [])

  const formatNumber = (value: number | undefined, decimals = 2) => {
    if (value === undefined || value === null) return 'N/A'
    if (Math.abs(value) >= 1e9) return `${(value / 1e9).toFixed(decimals)}B`
    if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(decimals)}M`
    if (Math.abs(value) >= 1e3) return `${(value / 1e3).toFixed(decimals)}K`
    return value.toFixed(decimals)
  }

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(2)}%`
  }

  const MoversTable = ({ data, type }: { data: MarketMover[]; type: MoverType }) => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {type === 'gainers' && <TrendingUp className="h-5 w-5 text-green-500" />}
          {type === 'losers' && <TrendingDown className="h-5 w-5 text-red-500" />}
          {type === 'mostactive' && <Activity className="h-5 w-5 text-blue-500" />}
          {type === 'gainers' && 'Top Gainers'}
          {type === 'losers' && 'Top Losers'}
          {type === 'mostactive' && 'Most Active'}
        </CardTitle>
        <CardDescription>
          {type === 'gainers' && 'Stocks with the highest price increases'}
          {type === 'losers' && 'Stocks with the largest price declines'}
          {type === 'mostactive' && 'Stocks with the highest trading volume'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="text-sm text-muted-foreground">No data available</p>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Symbol</TableHead>
                  <TableHead>Company Name</TableHead>
                  <TableHead className="text-right">Price</TableHead>
                  <TableHead className="text-right">Change</TableHead>
                  <TableHead className="text-right">% Change</TableHead>
                  <TableHead className="text-right">Volume</TableHead>
                  <TableHead className="text-right">Market Cap</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((mover) => (
                  <TableRow key={mover.symbol}>
                    <TableCell className="font-medium">
                      <Link
                        href={`/fundamentals/iex?symbol=${mover.symbol}`}
                        className="flex items-center gap-1 hover:underline"
                      >
                        {mover.symbol}
                        <ExternalLink className="h-3 w-3 text-muted-foreground" />
                      </Link>
                    </TableCell>
                    <TableCell>{mover.companyName}</TableCell>
                    <TableCell className="text-right">${mover.price?.toFixed(2)}</TableCell>
                    <TableCell className="text-right">
                      <span
                        className={
                          mover.change && mover.change >= 0 ? 'text-green-500' : 'text-red-500'
                        }
                      >
                        {mover.change !== undefined ? mover.change.toFixed(2) : 'N/A'}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge
                        variant={mover.changePercent && mover.changePercent >= 0 ? 'default' : 'destructive'}
                        className={
                          mover.changePercent && mover.changePercent >= 0
                            ? 'bg-green-500 hover:bg-green-600'
                            : ''
                        }
                      >
                        {mover.changePercent !== undefined
                          ? formatPercent(mover.changePercent)
                          : 'N/A'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {formatNumber(mover.volume)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatNumber(mover.marketCap)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Market Movers</h1>
          <p className="text-muted-foreground">
            Top gainers, losers, and most active stocks in the market
          </p>
        </div>
        <Button onClick={fetchMarketMovers} disabled={loading} variant="outline">
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <Card className="border-red-500">
          <CardContent className="pt-6">
            <p className="text-sm text-red-500">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Tabs for different mover types */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as MoverType)} className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="gainers">
            <TrendingUp className="mr-2 h-4 w-4" />
            Gainers
          </TabsTrigger>
          <TabsTrigger value="losers">
            <TrendingDown className="mr-2 h-4 w-4" />
            Losers
          </TabsTrigger>
          <TabsTrigger value="mostactive">
            <Activity className="mr-2 h-4 w-4" />
            Most Active
          </TabsTrigger>
        </TabsList>

        <TabsContent value="gainers">
          <MoversTable data={gainers} type="gainers" />
        </TabsContent>

        <TabsContent value="losers">
          <MoversTable data={losers} type="losers" />
        </TabsContent>

        <TabsContent value="mostactive">
          <MoversTable data={mostActive} type="mostactive" />
        </TabsContent>
      </Tabs>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Top Gainer</CardTitle>
          </CardHeader>
          <CardContent>
            {gainers.length > 0 ? (
              <div>
                <p className="text-2xl font-bold">{gainers[0].symbol}</p>
                <p className="text-sm text-green-500">
                  {gainers[0].changePercent !== undefined
                    ? formatPercent(gainers[0].changePercent)
                    : 'N/A'}
                </p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No data</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Top Loser</CardTitle>
          </CardHeader>
          <CardContent>
            {losers.length > 0 ? (
              <div>
                <p className="text-2xl font-bold">{losers[0].symbol}</p>
                <p className="text-sm text-red-500">
                  {losers[0].changePercent !== undefined
                    ? formatPercent(losers[0].changePercent)
                    : 'N/A'}
                </p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No data</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Most Active</CardTitle>
          </CardHeader>
          <CardContent>
            {mostActive.length > 0 ? (
              <div>
                <p className="text-2xl font-bold">{mostActive[0].symbol}</p>
                <p className="text-sm text-muted-foreground">
                  Vol: {formatNumber(mostActive[0].volume)}
                </p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No data</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
