'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ExternalLink, MapPin, Building2, Users, TrendingUp } from 'lucide-react'

export interface CompanyOfficer {
  name: string
  title: string
  pay?: number
  exercised?: number
  born?: number
}

export interface CompanyPeer {
  symbol: string
  companyName: string
  marketCap?: number
}

export interface CompanyMarket {
  marketCap: number
  sharesOutstanding: number
  eps: number
}

export interface CompanyProfileData {
  symbol: string
  companyName: string
  exchange: string
  sector?: string
  industry?: string
  description?: string
  ceo?: string
  employees?: number
  city?: string
  state?: string
  country?: string
  url?: string
  image?: string
  officers?: CompanyOfficer[]
  peers?: CompanyPeer[]
  targets?: Array<{
    analystName: string
    targetLow?: number
    targetHigh?: number
    targetMedian?: number
    rating?: string
    updatedDate?: string
  }>
  market?: CompanyMarket
}

interface CompanyProfileProps {
  data?: CompanyProfileData | null
  loading?: boolean
  error?: string
}

export function CompanyProfile({ data, loading, error }: CompanyProfileProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <Skeleton className="h-16 w-16 rounded-full" />
            <div className="space-y-2">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-32" />
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-4 w-full" />
          ))}
        </CardContent>
      </Card>
    )
  }

  if (error || !data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Company Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No data available'}</p>
        </CardContent>
      </Card>
    )
  }

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(value)
  }

  const formatNumber = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A'
    return new Intl.NumberFormat('en-US').format(value)
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-4">
          <Avatar className="h-16 w-16">
            <AvatarImage src={data.image} alt={data.companyName} />
            <AvatarFallback>{data.symbol.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <CardTitle className="text-xl">{data.companyName}</CardTitle>
              <Badge variant="secondary">{data.exchange}</Badge>
              <Badge variant="outline">{data.sector}</Badge>
            </div>
            <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
              <span className="font-mono font-medium">{data.symbol}</span>
              {data.industry && <span>• {data.industry}</span>}
            </div>
          </div>
          {data.url && (
            <Button variant="ghost" size="sm" asChild>
              <a href={data.url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-2" />
                Website
              </a>
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="officers">Officers</TabsTrigger>
            <TabsTrigger value="peers">Peers</TabsTrigger>
            <TabsTrigger value="targets">Price Targets</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-4">
            <div className="grid gap-4 md:grid-cols-2">
              {data.description && (
                <div className="md:col-span-2">
                  <h4 className="text-sm font-medium mb-2">Description</h4>
                  <p className="text-sm text-muted-foreground">{data.description}</p>
                </div>
              )}
              <div className="space-y-3">
                <h4 className="text-sm font-medium">Details</h4>
                <div className="grid gap-2 text-sm">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">CEO:</span>
                    <span className="font-medium">{data.ceo || 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Building2 className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Employees:</span>
                    <span className="font-medium">{formatNumber(data.employees)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Headquarters:</span>
                    <span className="font-medium">{data.city}, {data.state} {data.country}</span>
                  </div>
                </div>
              </div>
              {data.market && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium">Market</h4>
                  <div className="grid gap-2 text-sm">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">Market Cap:</span>
                      <span className="font-medium">{formatCurrency(data.market.marketCap)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Shares Outstanding:</span>
                      <span className="font-medium">{formatNumber(data.market.sharesOutstanding)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">EPS:</span>
                      <span className="font-medium">{formatCurrency(data.market.eps)}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="officers" className="mt-4">
            {data.officers && data.officers.length > 0 ? (
              <div className="space-y-3">
                {data.officers.map((officer: CompanyOfficer, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">{officer.name}</p>
                      <p className="text-sm text-muted-foreground">{officer.title}</p>
                    </div>
                    {officer.pay && (
                      <p className="text-sm font-medium">{formatCurrency(officer.pay)}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No officer data available</p>
            )}
          </TabsContent>

          <TabsContent value="peers" className="mt-4">
            {data.peers && data.peers.length > 0 ? (
              <div className="grid gap-2">
                {data.peers.map((peer: CompanyPeer, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="text-xs">{peer.symbol.slice(0, 2).toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{peer.companyName}</p>
                        <p className="text-sm text-muted-foreground">{peer.symbol}</p>
                      </div>
                    </div>
                    {peer.marketCap && (
                      <Badge variant="secondary">{formatCurrency(peer.marketCap)}</Badge>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No peer data available</p>
            )}
          </TabsContent>

          <TabsContent value="targets" className="mt-4">
            {data.targets && data.targets.length > 0 ? (
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">Number of Analysts</p>
                    <p className="text-2xl font-bold">{data.targets.length}</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">Median Target</p>
                    <p className="text-2xl font-bold">{formatCurrency(data.targets.reduce((acc, t) => acc + (t.targetMedian || 0), 0) / data.targets.length)}</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">High Target</p>
                    <p className="text-2xl font-bold text-green-600">{formatCurrency(Math.max(...data.targets.map((t) => t.targetHigh || 0)))}</p>
                  </div>
                </div>
                <div className="space-y-2">
                  {data.targets.map((target, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{target.analystName}</p>
                        <p className="text-sm text-muted-foreground">{target.updatedDate}</p>
                      </div>
                      <div className="flex gap-4">
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground">Target</p>
                          <p className="font-medium">{formatCurrency(target.targetMedian)}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground">Rating</p>
                          <p className="font-medium">{target.rating}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No price target data available</p>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
