"use client"

import { useState } from 'react'
import { Building2, MapPin, Globe, Calendar, FileText, DollarSign, TrendingUp, Users, Factory } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export interface CompanyProfileData {
  symbol: string
  name: string
  description: string
  sector: string
  industry: string
  ceo: string
  employees: number
  headquarters: string
  website: string
  founded: number
  exchange: string
  currency: string
  fiscalYearEnd: string
  marketCap: number
  enterpriseValue: number
  sharesOutstanding: number
  avgVolume: number
  peRatio: number
  eps: number
  dividendYield: number
  beta: number
  lastUpdated: string
}

export interface CompanyProfileProps {
  data?: CompanyProfileData
  symbol?: string
  loading?: boolean
  error?: string
  className?: string
}

function formatLargeNumber(num: number): string {
  if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`
  if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`
  if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`
  return `$${(num / 1e3).toFixed(0)}K`
}

function InfoRow({ icon: Icon, label, value, href }: { icon: typeof Building2; label: string; value?: string; href?: string }) {
  if (!value) return null
  return (
    <div className="flex items-center gap-3 py-2">
      <Icon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
      <span className="text-sm text-muted-foreground w-24 flex-shrink-0">{label}</span>
      {href ? (
        <a href={href} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline">
          {value}
        </a>
      ) : (
        <span className="text-sm font-medium">{value}</span>
      )}
    </div>
  )
}

export function CompanyProfile({
  data,
  symbol,
  loading = false,
  error,
  className,
}: CompanyProfileProps) {
  const [activeTab, setActiveTab] = useState('overview')

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-48 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !data) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Company Profile
          </CardTitle>
          <CardDescription>Company information and business description</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No company data available'}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              {data.name}
              {symbol && <Badge variant="outline">{symbol}</Badge>}
            </CardTitle>
            <CardDescription>{data.sector} · {data.industry}</CardDescription>
          </div>
          <Button variant="outline" size="sm">
            <FileText className="h-4 w-4 mr-2" />
            SEC Filings
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="statistics">Statistics</TabsTrigger>
            <TabsTrigger value="management">Management</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-4 space-y-4">
            <p className="text-sm text-muted-foreground leading-relaxed">
              {data.description || 'No company description available.'}
            </p>

            <Separator />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <InfoRow icon={MapPin} label="Headquarters" value={data.headquarters} />
                <InfoRow icon={Globe} label="Website" value={data.website} href={data.website} />
                <InfoRow icon={Calendar} label="Founded" value={data.founded ? String(data.founded) : undefined} />
                <InfoRow icon={Factory} label="Industry" value={data.industry} />
              </div>
              <div className="space-y-1">
                <InfoRow icon={DollarSign} label="Exchange" value={data.exchange} />
                <InfoRow icon={DollarSign} label="Currency" value={data.currency} />
                <InfoRow icon={Calendar} label="Fiscal Year" value={data.fiscalYearEnd} />
                <InfoRow icon={Users} label="Employees" value={data.employees ? `${data.employees.toLocaleString()}` : undefined} />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="statistics" className="mt-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-muted/30 rounded-lg">
                <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
                  <DollarSign className="h-4 w-4" />
                  <span className="text-xs">Market Cap</span>
                </div>
                <div className="text-lg font-semibold">{formatLargeNumber(data.marketCap)}</div>
              </div>

              <div className="text-center p-4 bg-muted/30 rounded-lg">
                <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
                  <DollarSign className="h-4 w-4" />
                  <span className="text-xs">P/E Ratio</span>
                </div>
                <div className="text-lg font-semibold">{data.peRatio?.toFixed(2) || 'N/A'}</div>
              </div>

              <div className="text-center p-4 bg-muted/30 rounded-lg">
                <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
                  <TrendingUp className="h-4 w-4" />
                  <span className="text-xs">Dividend Yield</span>
                </div>
                <div className="text-lg font-semibold">
                  {data.dividendYield ? `${data.dividendYield.toFixed(2)}%` : 'N/A'}
                </div>
              </div>

              <div className="text-center p-4 bg-muted/30 rounded-lg">
                <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
                  <TrendingUp className="h-4 w-4" />
                  <span className="text-xs">Beta</span>
                </div>
                <div className="text-lg font-semibold">{data.beta?.toFixed(2) || 'N/A'}</div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="management" className="mt-4">
            <div className="flex items-center gap-4 p-4 bg-muted/30 rounded-lg">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Users className="h-6 w-6 text-primary" />
              </div>
              <div>
                <div className="font-semibold">{data.ceo || 'CEO'}</div>
                <div className="text-sm text-muted-foreground">Chief Executive Officer</div>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">
            Last updated: {data.lastUpdated || 'N/A'}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
