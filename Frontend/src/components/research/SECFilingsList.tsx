'use client'

import { useState, useMemo, useCallback } from 'react'
import { FileText, Download, Calendar, Building, ExternalLink, Filter, RefreshCw, Search } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { cn, formatDate } from '@/lib/utils'

export type FilingType = '10-K' | '10-Q' | '8-K' | '4' | 'S-1' | 'DEF 14A' | '13F' | 'all'

export interface SECFiling {
  id: string
  formType: string
  companyName: string
  symbol: string
  filedDate: string
  acceptedDate: string
  description: string
  documentUrl: string
  size: string
  isAmd: boolean
}

export interface SECFilingsSummary {
  totalFilings: number
  recent10K: number
  recent10Q: number
  recent8K: number
}

export interface SECFilingsListProps {
  symbol?: string
  filings?: SECFiling[]
  summary?: SECFilingsSummary
  loading?: boolean
  className?: string
}

const FORM_TYPE_LABELS: Record<string, string> = {
  '10-K': 'Annual Report',
  '10-Q': 'Quarterly Report',
  '8-K': 'Current Report',
  '4': 'Insider Transaction',
  'S-1': 'IPO Registration',
  'DEF 14A': 'Proxy Statement',
  '13F': 'Institutional Holdings',
}

const FORM_TYPE_COLORS: Record<string, string> = {
  '10-K': 'bg-blue-100 text-blue-700 border-blue-200',
  '10-Q': 'bg-cyan-100 text-cyan-700 border-cyan-200',
  '8-K': 'bg-orange-100 text-orange-700 border-orange-200',
  '4': 'bg-purple-100 text-purple-700 border-purple-200',
  'S-1': 'bg-pink-100 text-pink-700 border-pink-200',
  'DEF 14A': 'bg-indigo-100 text-indigo-700 border-indigo-200',
  '13F': 'bg-teal-100 text-teal-700 border-teal-200',
}

function generateMockFilings(symbol: string, count: number = 30): SECFiling[] {
  const forms = ['10-K', '10-Q', '8-K', '4', 'DEF 14A', '13F']
  const descriptions: Record<string, string[]> = {
    '10-K': ['Annual report with audited financial statements', 'Annual report pursuant to Section 13', 'Annual report for fiscal year ended'],
    '10-Q': ['Quarterly report with unaudited financial statements', 'Quarterly report for quarter ended', 'Form 10-Q quarterly filing'],
    '8-K': ['Current report - material event', 'Current report - entry into material agreement', 'Current report - regulation FD disclosure', 'Current report - earnings release'],
    '4': ['Statement of changes in beneficial ownership', 'Form 4 insider trading filing', 'Securities exchange act Section 16'],
    'DEF 14A': ['Definitive proxy statement', 'Proxy statement filed with SEC', 'Annual meeting proxy materials'],
    '13F': ['Quarterly institutional investment manager report', 'Form 13F holdings report', 'Institutional investment manager disclosure'],
  }

  return Array.from({ length: count }, (_, i) => {
    const formType = forms[Math.floor(Math.random() * forms.length)]
    return {
      id: `filing-${i}`,
      formType,
      companyName: `${symbol} Inc.`,
      symbol,
      filedDate: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      acceptedDate: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
      description: `${descriptions[formType][Math.floor(Math.random() * descriptions[formType].length)]} ${symbol}`,
      documentUrl: `https://www.sec.gov/Archives/edgar/data/${Math.floor(Math.random() * 1000000)}/${symbol}-${formType.toLowerCase().replace('-', '')}-${Date.now()}.htm`,
      size: `${(Math.random() * 10 + 0.1).toFixed(1)} MB`,
      isAmd: Math.random() > 0.9,
    }
  }).sort((a, b) => new Date(b.filedDate).getTime() - new Date(a.filedDate).getTime())
}

function SECFilingsListSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-32" />
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-16 w-full" />)}
        </div>
        <Skeleton className="h-64 w-full" />
      </CardContent>
    </Card>
  )
}

function FilingRow({ filing }: { filing: SECFiling }) {
  const colorClass = FORM_TYPE_COLORS[filing.formType] || 'bg-gray-100'

  return (
    <div className="flex items-center gap-4 p-4 border-b hover:bg-muted/30 transition-colors">
      <div className={cn('px-3 py-1 rounded text-xs font-semibold border', colorClass)}>
        {filing.formType}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate">{filing.description}</p>
        <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
          <Calendar className="h-3 w-3" />
          <span>{formatDate(filing.filedDate)}</span>
          {filing.isAmd && (
            <Badge variant="outline" className="text-[10px]">Amd</Badge>
          )}
        </div>
      </div>
      <div className="text-xs text-muted-foreground">{filing.size}</div>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
              <ExternalLink className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p className="text-xs">View on SEC.gov</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
              <Download className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p className="text-xs">Download filing</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  )
}

export function SECFilingsList({ symbol = 'AAPL', filings: propFilings, summary: propSummary, loading = false, className }: SECFilingsListProps) {
  const [filter, setFilter] = useState<FilingType>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'date' | 'form'>('date')

  const filings = useMemo(() => propFilings || generateMockFilings(symbol, 50), [propFilings, symbol])
  const summary = useMemo(() => propSummary || { totalFilings: filings.length, recent10K: filings.filter(f => f.formType === '10-K').length, recent10Q: filings.filter(f => f.formType === '10-Q').length, recent8K: filings.filter(f => f.formType === '8-K').length }, [propSummary, filings])

  const filteredFilings = useMemo(() => {
    let result = filings.filter(f => filter === 'all' || f.formType === filter)
    if (searchQuery) {
      result = result.filter(f => f.description.toLowerCase().includes(searchQuery.toLowerCase()))
    }
    result.sort((a, b) => {
      if (sortBy === 'date') return new Date(b.filedDate).getTime() - new Date(a.filedDate).getTime()
      return a.formType.localeCompare(b.formType)
    })
    return result
  }, [filings, filter, searchQuery, sortBy])

  const handleExport = useCallback(() => {
    const csvData = filteredFilings.map(f => ({
      Form: f.formType,
      Company: f.companyName,
      Symbol: f.symbol,
      Filed: f.filedDate,
      Description: f.description,
      Size: f.size,
    }))
    const csv = ['Form,Company,Symbol,Filed,Description,Size', ...csvData.map(row => Object.values(row).join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${symbol}_sec_filings.csv`
    a.click()
  }, [filteredFilings, symbol])

  if (loading) return <SECFilingsListSkeleton />

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <FileText className="h-5 w-5" />
              SEC Filings
            </CardTitle>
            <CardDescription>{symbol} - SEC filings and regulatory reports</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={filter} onValueChange={(v: FilingType) => setFilter(v)}>
              <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Forms</SelectItem>
                <SelectItem value="10-K">10-K (Annual)</SelectItem>
                <SelectItem value="10-Q">10-Q (Quarterly)</SelectItem>
                <SelectItem value="8-K">8-K (Current)</SelectItem>
                <SelectItem value="4">Form 4</SelectItem>
                <SelectItem value="DEF 14A">DEF 14A</SelectItem>
                <SelectItem value="13F">13F</SelectItem>
              </SelectContent>
            </Select>
            <Button size="sm" variant="outline" onClick={handleExport}>
              <Download className="h-4 w-4 mr-1" />Export
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Total Filings</span>
            </div>
            <p className="text-2xl font-bold">{summary.totalFilings}</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="h-4 w-4 text-blue-600" />
              <span className="text-xs text-blue-700">10-K (Annual)</span>
            </div>
            <p className="text-2xl font-bold text-blue-700">{summary.recent10K}</p>
          </div>
          <div className="p-4 bg-cyan-50 rounded-lg border border-cyan-200">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="h-4 w-4 text-cyan-600" />
              <span className="text-xs text-cyan-700">10-Q (Quarterly)</span>
            </div>
            <p className="text-2xl font-bold text-cyan-700">{summary.recent10Q}</p>
          </div>
          <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="h-4 w-4 text-orange-600" />
              <span className="text-xs text-orange-700">8-K (Current)</span>
            </div>
            <p className="text-2xl font-bold text-orange-700">{summary.recent8K}</p>
          </div>
        </div>

        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search filings..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
            <SelectTrigger className="w-32"><SelectValue placeholder="Sort by" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="date">Most Recent</SelectItem>
              <SelectItem value="form">Form Type</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Tabs defaultValue="list" className="space-y-4">
          <TabsList>
            <TabsTrigger value="list">Filing List</TabsTrigger>
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
          </TabsList>

          <TabsContent value="list">
            <div className="border rounded-lg bg-card">
              <div className="flex items-center gap-4 p-3 border-b bg-muted/50 text-xs font-medium text-muted-foreground">
                <div className="w-20">Form</div>
                <div className="flex-1">Description</div>
                <div className="w-20">Size</div>
                <div className="w-20">Action</div>
              </div>
              <div className="divide-y max-h-96 overflow-y-auto">
                {filteredFilings.map((filing) => (
                  <FilingRow key={filing.id} filing={filing} />
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="timeline">
            <div className="space-y-2">
              {filteredFilings.slice(0, 10).map((filing, i) => (
                <div key={filing.id} className="flex items-start gap-4">
                  <div className="flex flex-col items-center">
                    <div className={cn('w-3 h-3 rounded-full mt-1', FORM_TYPE_COLORS[filing.formType]?.split(' ')[0].replace('bg-', 'bg-').replace('-100', '-500'))} />
                    {i < 9 && <div className="w-0.5 h-full bg-border mt-1" />}
                  </div>
                  <div className="flex-1 pb-4">
                    <div className={cn('inline-block px-2 py-0.5 rounded text-xs font-medium border', FORM_TYPE_COLORS[filing.formType])}>
                      {filing.formType}
                    </div>
                    <p className="text-sm mt-1">{filing.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">{formatDate(filing.filedDate)}</p>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default SECFilingsList
