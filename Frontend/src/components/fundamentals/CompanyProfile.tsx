'use client'

import { useState, useMemo } from 'react'
import { Building2, MapPin, Globe, Calendar, TrendingUp, TrendingDown, DollarSign, Users, PieChart, Download, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import { cn, formatCurrency, formatNumber, formatPercent } from '@/lib/utils'

export interface CompanyProfileData {
  symbol: string
  companyName: string
  shortName: string
  sector: string
  industry: string
  description: string
  website: string
  headquarters: string
  employees: number
  ceo: string
  founded: number
  marketCap: number
  enterpriseValue: number
  peRatio: number
  eps: number
  dividend: number
  dividendYield: number
  beta: number
  high52Week: number
  low52Week: number
  volume: number
  avgVolume: number
  sharesOutstanding: number
  floatShares: number
  insiderOwnership: number
  institutionalOwnership: number
}

export interface CompanyProfileProps {
  symbol?: string
  profile?: CompanyProfileData
  loading?: boolean
  className?: string
}

function generateMockProfile(symbol: string): CompanyProfileData {
  return {
    symbol,
    companyName: `${symbol} Inc.`,
    shortName: symbol,
    sector: 'Technology',
    industry: 'Software - Infrastructure',
    description: `${symbol} Inc. is a leading technology company that develops innovative software solutions for enterprises worldwide. The company was founded in 2010 and has grown to become a key player in the cloud computing and artificial intelligence markets.`,
    website: `https://www.${symbol.toLowerCase()}.com`,
    headquarters: 'San Francisco, CA',
    employees: Math.floor(Math.random() * 50000) + 1000,
    ceo: 'John Smith',
    founded: 2010,
    marketCap: Math.random() * 500000000000 + 50000000000,
    enterpriseValue: Math.random() * 600000000000 + 60000000000,
    peRatio: Math.random() * 50 + 10,
    eps: Math.random() * 10 + 1,
    dividend: Math.random() * 2,
    dividendYield: Math.random() * 3,
    beta: Math.random() * 2,
    high52Week: 200 + Math.random() * 100,
    low52Week: 100 + Math.random() * 50,
    volume: Math.floor(Math.random() * 50000000) + 1000000,
    avgVolume: Math.floor(Math.random() * 30000000) + 1000000,
    sharesOutstanding: Math.floor(Math.random() * 1000000000) + 100000000,
    floatShares: Math.floor(Math.random() * 800000000) + 100000000,
    insiderOwnership: Math.random() * 10,
    institutionalOwnership: Math.random() * 80 + 20,
  }
}

function CompanyProfileSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-32" />
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-20 w-full" />)}
        </div>
        <Skeleton className="h-32 w-full" />
      </CardContent>
    </Card>
  )
}

export function CompanyProfile({ symbol = 'AAPL', profile: propProfile, loading = false, className }: CompanyProfileProps) {
  const [activeTab, setActiveTab] = useState('overview')

  const profile = useMemo(() => propProfile || generateMockProfile(symbol), [propProfile, symbol])

  const metrics = useMemo(() => [
    { label: 'Market Cap', value: formatCurrency(profile.marketCap), icon: DollarSign },
    { label: 'P/E Ratio', value: profile.peRatio.toFixed(2), icon: PieChart },
    { label: 'EPS', value: formatCurrency(profile.eps), icon: TrendingUp },
    { label: 'Dividend Yield', value: formatPercent(profile.dividendYield / 100), icon: Calendar },
    { label: 'Beta', value: profile.beta.toFixed(2), icon: TrendingDown },
    { label: '52W High', value: formatCurrency(profile.high52Week), icon: TrendingUp },
    { label: '52W Low', value: formatCurrency(profile.low52Week), icon: TrendingDown },
    { label: 'Volume', value: formatNumber(profile.volume), icon: Users },
  ], [profile])

  if (loading) return <CompanyProfileSkeleton />

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-lg bg-primary/10 flex items-center justify-center">
              <Building2 className="h-8 w-8 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold">{profile.companyName}</CardTitle>
              <CardDescription>{profile.sector} • {profile.industry}</CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline">
              <ExternalLink className="h-4 w-4 mr-1" />
              SEC Filings
            </Button>
            <Button size="sm" variant="outline">
              <Globe className="h-4 w-4 mr-1" />
              Website
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="key-metrics">Key Metrics</TabsTrigger>
            <TabsTrigger value="ownership">Ownership</TabsTrigger>
            <TabsTrigger value="competitors">Competitors</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-3 gap-6">
              <div className="col-span-2 space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">About</h4>
                  <p className="text-sm text-muted-foreground">{profile.description}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                    <MapPin className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">Headquarters</p>
                      <p className="font-medium">{profile.headquarters}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                    <Globe className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">Website</p>
                      <a href={profile.website} className="font-medium text-primary hover:underline">{profile.website}</a>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                    <Users className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">Employees</p>
                      <p className="font-medium">{formatNumber(profile.employees)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                    <Calendar className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">Founded</p>
                      <p className="font-medium">{profile.founded}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <h4 className="font-semibold">Leadership</h4>
                <div className="p-4 border rounded-lg">
                  <p className="font-medium">{profile.ceo}</p>
                  <p className="text-sm text-muted-foreground">Chief Executive Officer</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground">Sector</p>
                  <Badge variant="outline">{profile.sector}</Badge>
                </div>
                <div className="p-4 border rounded-lg">
                  <p className="text-sm text-muted-foreground">Industry</p>
                  <Badge variant="outline">{profile.industry}</Badge>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="key-metrics" className="space-y-4">
            <div className="grid grid-cols-4 gap-4">
              {metrics.map((metric, i) => (
                <div key={i} className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <metric.icon className="h-4 w-4 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">{metric.label}</span>
                  </div>
                  <p className="text-xl font-bold">{metric.value}</p>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="font-semibold">Valuation</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Market Cap</span>
                    <span className="font-medium">{formatCurrency(profile.marketCap)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Enterprise Value</span>
                    <span className="font-medium">{formatCurrency(profile.enterpriseValue)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>P/E Ratio</span>
                    <span className="font-medium">{profile.peRatio.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>EPS</span>
                    <span className="font-medium">{formatCurrency(profile.eps)}</span>
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <h4 className="font-semibold">Dividends</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Annual Dividend</span>
                    <span className="font-medium">{formatCurrency(profile.dividend)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Dividend Yield</span>
                    <span className="font-medium">{formatPercent(profile.dividendYield / 100)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Payout Ratio</span>
                    <span className="font-medium">{((profile.dividend / profile.eps) * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="ownership" className="space-y-4">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="font-semibold">Ownership Structure</h4>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Insider Ownership</span>
                      <span className="font-medium">{profile.insiderOwnership.toFixed(1)}%</span>
                    </div>
                    <Progress value={profile.insiderOwnership} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Institutional Ownership</span>
                      <span className="font-medium">{profile.institutionalOwnership.toFixed(1)}%</span>
                    </div>
                    <Progress value={profile.institutionalOwnership} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Public Ownership</span>
                      <span className="font-medium">{(100 - profile.insiderOwnership - profile.institutionalOwnership).toFixed(1)}%</span>
                    </div>
                    <Progress value={100 - profile.insiderOwnership - profile.institutionalOwnership} className="h-2" />
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <h4 className="font-semibold">Share Statistics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Shares Outstanding</span>
                    <span className="font-medium">{formatNumber(profile.sharesOutstanding)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Float Shares</span>
                    <span className="font-medium">{formatNumber(profile.floatShares)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Avg. Volume</span>
                    <span className="font-medium">{formatNumber(profile.avgVolume)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Today's Volume</span>
                    <span className="font-medium">{formatNumber(profile.volume)}</span>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="competitors" className="space-y-4">
            <div className="text-center py-12 text-muted-foreground">
              <PieChart className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Competitor data not available</p>
              <p className="text-sm">This feature requires a premium data subscription</p>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default CompanyProfile
