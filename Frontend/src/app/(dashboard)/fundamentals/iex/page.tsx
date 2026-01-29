'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { use } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { KeyStatsCard } from '@/components/fundamentals/KeyStatsCard'
import { EarningsTable } from '@/components/fundamentals/EarningsTable'
import { OwnershipChart } from '@/components/fundamentals/OwnershipChart'
import { PeerComparisonTable } from '@/components/fundamentals/PeerComparisonTable'
import { iexCloudApi } from '@/lib/api/iex-cloud'
import type { KeyStats, Earnings, Ownership, Peer, CompanyInfo } from '@/lib/types/iex-cloud'
import { Search, TrendingUp, Building2, DollarSign, BarChart3, RefreshCw, Building } from 'lucide-react'

export default function IEXFundamentalsPage() {
  const params = useParams()
  const [symbol, setSymbol] = useState((params.symbol as string) || 'AAPL')
  const [searchInput, setSearchInput] = useState(symbol)
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null)
  const [keyStats, setKeyStats] = useState<KeyStats | null>(null)
  const [earnings, setEarnings] = useState<Earnings[]>([])
  const [ownership, setOwnership] = useState<Ownership | null>(null)
  const [peers, setPeers] = useState<Peer[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchAllData = async (sym: string) => {
    setLoading(true)
    setError('')

    try {
      const [info, stats, earningsData, ownershipData, peersData] = await Promise.all([
        iexCloudApi.getCompanyInfo(sym),
        iexCloudApi.getKeyStats(sym),
        iexCloudApi.getEarnings(sym),
        iexCloudApi.getOwnership(sym),
        iexCloudApi.getPeers(sym),
      ])

      setCompanyInfo(info)
      setKeyStats(stats)

      // Transform earnings data to match component expectations
      const transformedEarnings: Earnings[] = earningsData.map((e) => ({
        ...e,
        fiscalPeriod: e.fiscalPeriod?.toString() || 'N/A',
        surprisePercent: e.EPSSurprisePercent,
      }))
      setEarnings(transformedEarnings)

      setOwnership(ownershipData)
      setPeers(peersData)
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">IEX Cloud Fundamentals</h1>
          <p className="text-muted-foreground">
            Comprehensive stock fundamentals, earnings, ownership, and peer analysis
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
            placeholder="Enter stock symbol..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
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

      {companyInfo && !loading && (
        <>
          {/* Company Info Card */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Building2 className="h-5 w-5" />
                    {companyInfo.companyName}
                  </CardTitle>
                  <CardDescription className="mt-2">
                    <Badge variant="secondary" className="mr-2">
                      {companyInfo.symbol}
                    </Badge>
                    {companyInfo.industry} • {companyInfo.sector}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{companyInfo.description}</p>
              <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">CEO:</span> {companyInfo.CEO}
                </div>
                <div>
                  <span className="font-medium">Employees:</span>{' '}
                  {companyInfo.employees?.toLocaleString()}
                </div>
                <div>
                  <span className="font-medium">Website:</span>{' '}
                  <a
                    href={companyInfo.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:underline"
                  >
                    {companyInfo.website}
                  </a>
                </div>
                <div>
                  <span className="font-medium">Exchange:</span> {companyInfo.exchange}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tabs for different data sections */}
          <Tabs defaultValue="keystats" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="keystats">
                <BarChart3 className="mr-2 h-4 w-4" />
                Key Stats
              </TabsTrigger>
              <TabsTrigger value="earnings">
                <DollarSign className="mr-2 h-4 w-4" />
                Earnings
              </TabsTrigger>
              <TabsTrigger value="ownership">
                <Building className="mr-2 h-4 w-4" />
                Ownership
              </TabsTrigger>
              <TabsTrigger value="peers">
                <TrendingUp className="mr-2 h-4 w-4" />
                Peers
              </TabsTrigger>
            </TabsList>

            <TabsContent value="keystats" className="space-y-4">
              <KeyStatsCard stats={keyStats} loading={loading} />
            </TabsContent>

            <TabsContent value="earnings" className="space-y-4">
              <EarningsTable earnings={earnings} loading={loading} />
            </TabsContent>

            <TabsContent value="ownership" className="space-y-4">
              <OwnershipChart ownership={ownership} loading={loading} />
            </TabsContent>

            <TabsContent value="peers" className="space-y-4">
              <PeerComparisonTable peers={peers} symbol={symbol} loading={loading} />
            </TabsContent>
          </Tabs>
        </>
      )}

      {loading && (
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-12 w-full animate-pulse rounded bg-muted" />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
