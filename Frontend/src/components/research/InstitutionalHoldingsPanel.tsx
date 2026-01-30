'use client'

import { useState, useMemo, useCallback } from 'react'
import { Building2, TrendingUp, TrendingDown, Users, DollarSign, RefreshCw, Download, Filter, BarChart3, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { cn, formatCurrency, formatNumber, formatPercent, formatDate } from '@/lib/utils'
import type { InstitutionalOwner, FundOwner, InstitutionalHolder } from '@/lib/types/iex-cloud'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, PieChart, Pie, Cell } from 'recharts'

export type HolderType = 'all' | 'institutional' | 'fund'

export interface InstitutionalHoldingData {
  symbol: string
  companyName: string
  institutionalOwners: InstitutionalOwner[]
  fundOwners: FundOwner[]
  insiderHolders: InstitutionalHolder[]
  summary: {
    totalInstitutionalShares: number
    totalInstitutionalValue: number
    totalFundShares: number
    totalFundValue: number
    institutionalOwnership: number
    fundOwnership: number
    insiderOwnership: number
    topHolderPercent: number
    holderCount: number
    changeFromLastQuarter: number
  }
  lastUpdated: string
}

interface InstitutionalHoldingsPanelProps {
  data: InstitutionalHoldingData
  isLoading?: boolean
  onRefresh?: () => void
  onExport?: () => void
  className?: string
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#ff7300']

const OWNER_COLORS: Record<string, string> = {
  'BlackRock': '#000000',
  'Vanguard': '#C41230',
  'State Street': '#003087',
  'JP Morgan': '#1166CB',
  'Goldman Sachs': '#003087',
  'Morgan Stanley': '#E31E24',
  'Bank of America': '#012169',
  'Citadel': '#003399',
}

function OwnerRow({ owner, rank, showValue }: { owner: InstitutionalOwner | FundOwner; rank: number; showValue?: boolean }) {
  const isPositive = (owner as InstitutionalOwner).shares !== undefined && (owner as InstitutionalOwner).shares > 0
  
  return (
    <div className="flex items-center justify-between p-3 border-b last:border-0 hover:bg-muted/50 transition-colors">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-bold">
          {rank}
        </div>
        <div>
          <p className="font-medium text-sm">{owner.ownerName || (owner as FundOwner).fundName}</p>
          <p className="text-xs text-muted-foreground">
            {owner.positionPct ? formatPercent(owner.positionPct / 100) : 'N/A'} of company
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-medium text-sm">{formatNumber(owner.shares)} shares</p>
        {showValue && owner.value && (
          <p className="text-xs text-muted-foreground">{formatCurrency(owner.value)}</p>
        )}
      </div>
    </div>
  )
}

function OwnershipChart({ data, type }: { data: InstitutionalHoldingData; type: 'institutional' | 'fund' }) {
  const chartData = useMemo(() => {
    const owners = type === 'institutional' ? data.institutionalOwners : data.fundOwners
    const totalShares = type === 'institutional' ? data.summary.totalInstitutionalShares : data.summary.totalFundShares
    
    return owners.slice(0, 10).map(owner => ({
      name: owner.ownerName || (owner as FundOwner).fundName,
      value: owner.shares,
      pct: (owner.shares / totalShares) * 100,
    }))
  }, [data, type])

  if (chartData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-muted-foreground">
        No ownership data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
          label={({ name, pct }) => `${name.split(' ')[0]}: ${pct.toFixed(1)}%`}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={OWNER_COLORS[entry.name] || COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <RechartsTooltip
          formatter={(value: number, name: string) => [formatNumber(value), name]}
          contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

function OwnershipTrendChart({ data }: { data: InstitutionalHoldingData }) {
  const chartData = useMemo(() => {
    return [
      { name: 'Institutions', value: data.summary.totalInstitutionalShares, pct: data.summary.institutionalOwnership },
      { name: 'Funds', value: data.summary.totalFundShares, pct: data.summary.fundOwnership },
      { name: 'Insiders', value: data.summary.totalInstitutionalShares * (data.summary.insiderOwnership / 100), pct: data.summary.insiderOwnership },
      { name: 'Retail', value: 0, pct: 100 - data.summary.institutionalOwnership - data.summary.fundOwnership - data.summary.insiderOwnership },
    ]
  }, [data])

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={chartData} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis type="number" tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`} />
        <YAxis dataKey="name" type="category" width={80} tick={{ fontSize: 12 }} />
        <RechartsTooltip
          formatter={(value: number, name: string) => name === 'Retail' ? [value, name] : [formatNumber(value), name]}
          contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
        />
        <Bar dataKey="value" fill="#0088FE" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

function OwnershipSummaryCards({ summary }: { summary: InstitutionalHoldingData['summary'] }) {
  const ownershipChange = summary.changeFromLastQuarter
  const changeColor = ownershipChange >= 0 ? 'text-green-600' : 'text-red-600'
  
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4 text-blue-600" />
            <span className="text-xs text-muted-foreground">Institutional Own.</span>
          </div>
          <p className="text-2xl font-bold mt-2">{formatPercent(summary.institutionalOwnership / 100)}</p>
          <p className="text-xs text-muted-foreground">{formatNumber(summary.totalInstitutionalShares)} shares</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-purple-600" />
            <span className="text-xs text-muted-foreground">Fund Own.</span>
          </div>
          <p className="text-2xl font-bold mt-2">{formatPercent(summary.fundOwnership / 100)}</p>
          <p className="text-xs text-muted-foreground">{formatNumber(summary.totalFundShares)} shares</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-green-600" />
            <span className="text-xs text-muted-foreground">Total Value</span>
          </div>
          <p className="text-2xl font-bold mt-2">{formatCurrency(summary.totalInstitutionalValue + summary.totalFundValue)}</p>
          <p className="text-xs text-muted-foreground">{summary.holderCount} holders</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2">
            {ownershipChange >= 0 ? <ArrowUpRight className="h-4 w-4 text-green-600" /> : <ArrowDownRight className="h-4 w-4 text-red-600" />}
            <span className="text-xs text-muted-foreground">Quarterly Change</span>
          </div>
          <p className={cn('text-2xl font-bold mt-2', changeColor)}>
            {ownershipChange >= 0 ? '+' : ''}{formatPercent(ownershipChange / 100)}
          </p>
          <p className="text-xs text-muted-foreground">vs last quarter</p>
        </CardContent>
      </Card>
    </div>
  )
}

function HoldersList({ holders, title, showValue }: { holders: (InstitutionalOwner | FundOwner)[]; title: string; showValue?: boolean }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-0">
          {holders.slice(0, 10).map((owner, index) => (
            <OwnerRow key={index} owner={owner} rank={index + 1} showValue={showValue} />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export function InstitutionalHoldingsPanel({ data, isLoading = false, onRefresh, onExport, className }: InstitutionalHoldingsPanelProps) {
  const [holderType, setHolderType] = useState<HolderType>('all')
  const [sortBy, setSortBy] = useState<string>('shares')

  const sortedInstitutional = useMemo(() => {
    return [...data.institutionalOwners].sort((a, b) => b.shares - a.shares)
  }, [data.institutionalOwners])

  const sortedFunds = useMemo(() => {
    return [...data.fundOwners].sort((a, b) => b.shares - a.shares)
  }, [data.fundOwners])

  const handleRefresh = useCallback(() => {
    onRefresh?.()
  }, [onRefresh])

  const handleExport = useCallback(() => {
    onExport?.()
  }, [onExport])

  if (isLoading) {
    return (
      <Card className={cn('', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24" />)}
          </div>
          <Skeleton className="h-64" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Institutional Holdings
            </CardTitle>
            <CardDescription>{data.companyName} ({data.symbol}) - Ownership breakdown by institutional investors and funds</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline" size="sm" onClick={handleRefresh}>
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Refresh data</TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline" size="sm" onClick={handleExport}>
                    <Download className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Export data</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <OwnershipSummaryCards summary={data.summary} />

        <div className="mt-6">
          <Tabs defaultValue="all" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all" onClick={() => setHolderType('all')}>All Holders</TabsTrigger>
              <TabsTrigger value="institutional" onClick={() => setHolderType('institutional')}>Institutions</TabsTrigger>
              <TabsTrigger value="funds" onClick={() => setHolderType('fund')}>Funds</TabsTrigger>
              <TabsTrigger value="chart" onClick={() => setHolderType('chart')}>Charts</TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="mt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <HoldersList holders={sortedInstitutional} title="Top Institutional Holders" showValue />
                <HoldersList holders={sortedFunds} title="Top Fund Holders" showValue />
              </div>
            </TabsContent>

            <TabsContent value="institutional" className="mt-4">
              <HoldersList holders={sortedInstitutional} title="All Institutional Holders" showValue />
            </TabsContent>

            <TabsContent value="funds" className="mt-4">
              <HoldersList holders={sortedFunds} title="All Fund Holders" showValue />
            </TabsContent>

            <TabsContent value="chart" className="mt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">Institutional Ownership</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <OwnershipChart data={data} type="institutional" />
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">Fund Ownership</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <OwnershipChart data={data} type="fund" />
                  </CardContent>
                </Card>
                <Card className="md:col-span-2">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">Ownership Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <OwnershipTrendChart data={data} />
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </CardContent>
    </Card>
  )
}
