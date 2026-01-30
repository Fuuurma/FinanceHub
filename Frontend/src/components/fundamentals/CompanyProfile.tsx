'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Download, ExternalLink, MapPin, Building2, Users, TrendingUp, Star, Target, TrendingDown } from 'lucide-react'
import { cn, formatCurrency, formatNumber, formatPercent } from '@/lib/utils'

export interface CompanyOfficer {
  name: string
  title: string
  pay?: number
  exercised?: number
  born?: number
  yearBorn?: number
}

export interface CompanyPeer {
  symbol: string
  companyName: string
  marketCap?: number
  price?: number
  changePercent?: number
}

export interface CompanyMarket {
  marketCap: number
  sharesOutstanding: number
  eps: number
  peRatio?: number
  week52High?: number
  week52Low?: number
  dividendYield?: number
  beta?: number
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
  tags?: string[]
  founded?: number
  officers?: CompanyOfficer[]
  peers?: CompanyPeer[]
  targets?: Array<{
    analystName: string
    targetLow?: number
    targetHigh?: number
    targetMedian?: number
    rating?: string
    ratingScore?: number
    updatedDate?: string
  }>
  market?: CompanyMarket
  sustainability?: {
    esgScore?: number
    environmentScore?: number
    socialScore?: number
    governanceScore?: number
  }
}

interface CompanyProfileProps {
  data?: CompanyProfileData | null
  loading?: boolean
  error?: string
  onExport?: (data: CompanyProfileData) => void
}

export function CompanyProfile({ data, loading, error, onExport }: CompanyProfileProps) {
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

   const handleExport = () => {
     if (!profileData) return
     const exportData = {
       symbol: profileData.symbol,
       companyName: profileData.companyName,
       exchange: profileData.exchange,
       sector: profileData.sector,
       industry: profileData.industry,
       ceo: profileData.ceo,
       employees: profileData.employees,
       city: profileData.city,
       state: profileData.state,
       country: profileData.country,
       url: profileData.url,
       marketCap: profileData.market?.marketCap,
       sharesOutstanding: profileData.market?.sharesOutstanding,
       eps: profileData.market?.eps,
       peRatio: profileData.market?.peRatio,
       week52High: profileData.market?.week52High,
       week52Low: profileData.market?.week52Low,
       dividendYield: profileData.market?.dividendYield,
       beta: profileData.market?.beta,
     }

     const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
     const url = URL.createObjectURL(blob)
     const a = document.createElement('a')
     a.href = url
     a.download = `${profileData.symbol}-profile.json`
     a.click()
     URL.revokeObjectURL(url)

     onExport?.(profileData)
   }

  const getRatingBadge = (rating?: string, score?: number) => {
    if (!rating && !score) return null
    const label = rating || (score ? `${(score * 100).toFixed(0)}%` : 'N/A')
    const variant = score && score >= 0.6 ? 'default' : score && score >= 0.4 ? 'secondary' : 'destructive'
    return <Badge variant={variant as 'default' | 'secondary' | 'destructive' | 'outline'}>{label}</Badge>
  }

  const currentPrice = 0
  const targets = data?.targets || []
  const medianTarget = targets.length > 0 ? targets.reduce((acc, t) => acc + (t.targetMedian || 0), 0) / targets.length : 0
  const upside = medianTarget && currentPrice ? ((medianTarget - currentPrice) / currentPrice) * 100 : 0

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex justify-between">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-20" />
            </div>
          ))}
        </CardContent>
      </Card>
    )
  }

  if (!data) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">{error || 'No data available'}</p>
        </CardContent>
      </Card>
    )
  }

  const profileData = data!

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-4">
           <Avatar className="h-16 w-16">
             <AvatarImage src={profileData.image} alt={profileData.companyName} />
             <AvatarFallback>{profileData.symbol.slice(0, 2).toUpperCase()}</AvatarFallback>
           </Avatar>
          <div className="flex-1">
             <div className="flex items-center gap-3">
               <CardTitle className="text-xl">{profileData.companyName}</CardTitle>
               <Badge variant="secondary">{profileData.exchange}</Badge>
               {profileData.sector && <Badge variant="outline">{profileData.sector}</Badge>}
               {profileData.tags?.map((tag, i) => (
                 <Badge key={i} variant="secondary" className="text-xs">{tag}</Badge>
               ))}
             </div>
             <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
               <span className="font-mono font-medium">{profileData.symbol}</span>
               {profileData.industry && <span>• {profileData.industry}</span>}
               {profileData.founded && <span>• Founded {profileData.founded}</span>}
             </div>
          </div>
             <div className="flex items-center gap-2">
             {profileData.url && (
               <Button variant="ghost" size="sm" asChild>
                 <a href={profileData.url} target="_blank" rel="noopener noreferrer">
                   <ExternalLink className="h-4 w-4 mr-2" />
                   Website
                 </a>
               </Button>
             )}
             <Button variant="outline" size="sm" onClick={handleExport}>
               <Download className="h-4 w-4 mr-2" />
               Export
             </Button>
           </div>
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
             <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
               {profileData.description && (
                 <div className="md:col-span-2 lg:col-span-3">
                   <h4 className="text-sm font-medium mb-2">Description</h4>
                   <p className="text-sm text-muted-foreground leading-relaxed">{profileData.description}</p>
                 </div>
               )}
               <div className="space-y-3">
                 <h4 className="text-sm font-medium">Company Details</h4>
                 <div className="grid gap-2 text-sm">
                   <div className="flex items-center gap-2">
                     <MapPin className="h-4 w-4 text-muted-foreground" />
                     <span className="text-muted-foreground">CEO:</span>
                     <span className="font-medium">{profileData.ceo || 'N/A'}</span>
                   </div>
                   <div className="flex items-center gap-2">
                     <Building2 className="h-4 w-4 text-muted-foreground" />
                     <span className="text-muted-foreground">Employees:</span>
                     <span className="font-medium">{formatNumber(profileData.employees)}</span>
                   </div>
                   <div className="flex items-center gap-2">
                     <Users className="h-4 w-4 text-muted-foreground" />
                     <span className="text-muted-foreground">Headquarters:</span>
                     <span className="font-medium">{[profileData.city, profileData.state, profileData.country].filter(Boolean).join(', ') || 'N/A'}</span>
                   </div>
                   {profileData.founded && (
                     <div className="flex items-center gap-2">
                       <Star className="h-4 w-4 text-muted-foreground" />
                       <span className="text-muted-foreground">Founded:</span>
                       <span className="font-medium">{profileData.founded}</span>
                     </div>
                   )}
                 </div>
               </div>
               {profileData.market && (
                 <div className="space-y-3">
                   <h4 className="text-sm font-medium">Market Data</h4>
                   <div className="grid grid-cols-2 gap-2 text-sm">
                     <div className="flex items-center gap-2">
                       <TrendingUp className="h-4 w-4 text-muted-foreground" />
                       <span className="text-muted-foreground">Market Cap:</span>
                       <span className="font-medium">{formatCurrency(profileData.market.marketCap)}</span>
                     </div>
                     <div className="flex items-center gap-2">
                       <span className="text-muted-foreground">Shares:</span>
                       <span className="font-medium">{formatNumber(profileData.market.sharesOutstanding)}</span>
                     </div>
                     <div className="flex items-center gap-2">
                       <span className="text-muted-foreground">EPS:</span>
                       <span className="font-medium">{formatCurrency(profileData.market.eps)}</span>
                     </div>
                     <div className="flex items-center gap-2">
                       <span className="text-muted-foreground">P/E:</span>
                       <span className="font-medium">{profileData.market.peRatio?.toFixed(2) || 'N/A'}</span>
                     </div>
                     <div className="flex items-center gap-2">
                       <span className="text-muted-foreground">52W High:</span>
                       <span className="font-medium text-green-600">{formatCurrency(profileData.market.week52High)}</span>
                     </div>
                     <div className="flex items-center gap-2">
                       <span className="text-muted-foreground">52W Low:</span>
                       <span className="font-medium text-red-600">{formatCurrency(profileData.market.week52Low)}</span>
                     </div>
                     <div className="flex items-center gap-2">
                       <span className="text-muted-foreground">Div Yield:</span>
                       <span className="font-medium">{profileData.market.dividendYield ? formatPercent(profileData.market.dividendYield) : 'N/A'}</span>
                     </div>
                     <div className="flex items-center gap-2">
                       <span className="text-muted-foreground">Beta:</span>
                       <span className="font-medium">{profileData.market.beta?.toFixed(2) || 'N/A'}</span>
                     </div>
                   </div>
                 </div>
               )}
               {profileData.sustainability && (
                 <div className="space-y-3">
                   <h4 className="text-sm font-medium">Sustainability</h4>
                   <div className="grid grid-cols-2 gap-2 text-sm">
                     <div className="p-2 bg-muted rounded">
                       <p className="text-xs text-muted-foreground">ESG Score</p>
                       <p className="font-semibold">{profileData.sustainability.esgScore?.toFixed(1) || 'N/A'}</p>
                     </div>
                     <div className="p-2 bg-muted rounded">
                       <p className="text-xs text-muted-foreground">Environment</p>
                       <p className="font-semibold">{profileData.sustainability.environmentScore?.toFixed(1) || 'N/A'}</p>
                     </div>
                     <div className="p-2 bg-muted rounded">
                       <p className="text-xs text-muted-foreground">Social</p>
                       <p className="font-semibold">{profileData.sustainability.socialScore?.toFixed(1) || 'N/A'}</p>
                     </div>
                     <div className="p-2 bg-muted rounded">
                       <p className="text-xs text-muted-foreground">Governance</p>
                       <p className="font-semibold">{profileData.sustainability.governanceScore?.toFixed(1) || 'N/A'}</p>
                     </div>
                   </div>
                 </div>
               )}
              {medianTarget > 0 && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium">Analyst Targets</h4>
                  <div className="p-4 bg-muted rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-muted-foreground">Median Target</span>
                      <span className="text-lg font-bold">{formatCurrency(medianTarget)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Upside</span>
                      <Badge variant={upside > 0 ? 'default' : 'destructive'}>
                        {upside > 0 ? '+' : ''}{upside.toFixed(1)}%
                      </Badge>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

           <TabsContent value="officers" className="mt-4">
             {profileData.officers && profileData.officers.length > 0 ? (
               <div className="space-y-3">
                 {profileData.officers.map((officer: CompanyOfficer, index: number) => (
                   <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                     <div className="flex items-center gap-4">
                       <Avatar className="h-12 w-12">
                         <AvatarFallback className="text-sm font-medium">
                           {officer.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                         </AvatarFallback>
                       </Avatar>
                       <div>
                         <p className="font-medium">{officer.name}</p>
                         <p className="text-sm text-muted-foreground">{officer.title}</p>
                         {officer.yearBorn && (
                           <p className="text-xs text-muted-foreground">Born {officer.yearBorn}</p>
                         )}
                       </div>
                     </div>
                     <div className="text-right">
                       {officer.pay && (
                         <p className="font-medium">{formatCurrency(officer.pay)}</p>
                       )}
                       {officer.exercised && (
                         <p className="text-xs text-muted-foreground">Exercised: {formatCurrency(officer.exercised)}</p>
                       )}
                     </div>
                   </div>
                 ))}
               </div>
             ) : (
               <div className="text-center py-12 text-muted-foreground">
                 <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                 <p>No officer data available</p>
               </div>
             )}
           </TabsContent>

           <TabsContent value="peers" className="mt-4">
             {profileData.peers && profileData.peers.length > 0 ? (
               <div className="grid gap-2">
                 {profileData.peers.map((peer: CompanyPeer, index: number) => (
                   <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
                     <div className="flex items-center gap-4">
                       <Avatar className="h-10 w-10">
                         <AvatarFallback className="text-sm font-medium">{peer.symbol.slice(0, 2).toUpperCase()}</AvatarFallback>
                       </Avatar>
                       <div>
                         <p className="font-medium">{peer.companyName}</p>
                         <p className="text-sm text-muted-foreground">{peer.symbol}</p>
                       </div>
                     </div>
                     <div className="flex items-center gap-4">
                       {peer.price && (
                         <div className="text-right">
                           <p className="font-medium">{formatCurrency(peer.price)}</p>
                         </div>
                       )}
                       {peer.changePercent !== undefined && (
                         <Badge variant={peer.changePercent >= 0 ? 'default' : 'destructive'}>
                           {peer.changePercent >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                           {formatPercent(Math.abs(peer.changePercent))}
                         </Badge>
                       )}
                       {peer.marketCap && (
                         <Badge variant="outline">{formatCurrency(peer.marketCap)}</Badge>
                       )}
                     </div>
                   </div>
                 ))}
               </div>
             ) : (
               <p className="text-sm text-muted-foreground">No peer data available</p>
             )}
           </TabsContent>

           <TabsContent value="targets" className="mt-4">
             {profileData.targets && profileData.targets.length > 0 ? (
               <div className="space-y-4">
                 <div className="grid gap-4 md:grid-cols-4">
                   <div className="p-4 bg-muted rounded-lg">
                     <p className="text-sm text-muted-foreground">Analysts</p>
                     <p className="text-2xl font-bold">{profileData.targets.length}</p>
                   </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">Median Target</p>
                    <p className="text-2xl font-bold">{formatCurrency(medianTarget)}</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">High Target</p>
                    <p className="text-2xl font-bold text-green-600">{formatCurrency(Math.max(...profileData.targets.map((t) => t.targetHigh || 0)))}</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">Low Target</p>
                    <p className="text-2xl font-bold text-red-600">{formatCurrency(Math.min(...profileData.targets.map((t) => t.targetLow || Infinity)))}</p>
                  </div>
                </div>
                 <div className="space-y-2">
                   {profileData.targets.map((target, index: number) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{target.analystName}</p>
                          {getRatingBadge(target.rating, target.ratingScore)}
                        </div>
                        <p className="text-sm text-muted-foreground">{target.updatedDate}</p>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <p className="text-xs text-muted-foreground">Range</p>
                          <p className="text-sm font-medium">{formatCurrency(target.targetLow || 0)} - {formatCurrency(target.targetHigh || 0)}</p>
                        </div>
                        <div className="text-right min-w-[80px]">
                          <p className="text-xs text-muted-foreground">Target</p>
                          <p className="font-semibold">{formatCurrency(target.targetMedian)}</p>
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

export default CompanyProfile
