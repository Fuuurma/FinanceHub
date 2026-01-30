"use client"

import { useState, useMemo } from 'react'
import { FileText, Download, ExternalLink, Filter, Calendar, Building, RefreshCw } from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import type { SECFiling, FilingsSummary } from '@/lib/types/sec-filings'

export interface SECFilingsListProps {
  filings?: SECFiling[]
  summary?: FilingsSummary
  symbol?: string
  loading?: boolean
  error?: string
  className?: string
}

type FilingType = 'all' | '10-K' | '10-Q' | '8-K' | '4' | 'DEF 14A' | 'S-1' | 'S-3'

export type { FilingType as FilingType, SECFiling, FilingsSummary }

const FORM_TYPE_LABELS: Record<string, string> = {
  '10-K': 'Annual Report',
  '10-Q': 'Quarterly Report',
  '8-K': 'Current Report',
  '4': 'Insider Statement',
  'DEF 14A': 'Proxy Statement',
  'S-1': 'Registration Statement',
  'S-3': 'Registration Statement',
}

const FORM_TYPE_COLORS: Record<string, string> = {
  '10-K': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  '10-Q': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  '8-K': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
  '4': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
  'DEF 14A': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300',
  'S-1': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-300',
  'S-3': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-300',
}

function getFormTypeColor(formType: string): string {
  return FORM_TYPE_COLORS[formType] || 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
}

function FilingRow({ filing }: { filing: SECFiling }) {
  const formLabel = FORM_TYPE_LABELS[filing.form_type] || filing.form_type

  return (
    <TableRow className="hover:bg-muted/50">
      <TableCell className="py-3">
        <Badge className={cn('font-medium', getFormTypeColor(filing.form_type))}>
          {filing.form_type}
        </Badge>
      </TableCell>
      <TableCell className="py-3">
        <div className="flex flex-col">
          <span className="font-medium">{formLabel}</span>
          <span className="text-xs text-muted-foreground">
            Filed: {formatDate(filing.filed_at)}
          </span>
        </div>
      </TableCell>
      <TableCell className="py-3 hidden md:table-cell">
        <span className="text-muted-foreground">
          Period: {formatDate(filing.report_date)}
        </span>
      </TableCell>
      <TableCell className="py-3">
        <div className="flex items-center justify-end gap-2">
          {filing.document_url && (
            <Button variant="ghost" size="icon" asChild>
              <a href={filing.document_url} target="_blank" rel="noopener noreferrer" title="View Document">
                <ExternalLink className="h-4 w-4" />
              </a>
            </Button>
          )}
        </div>
      </TableCell>
    </TableRow>
  )
}

function FilingsSummaryCard({ summary }: { summary: FilingsSummary }) {
  const counts = summary.filing_counts

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 p-4 bg-muted/30 rounded-lg">
      <div className="flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-bold">{counts['10-K'] || 0}</span>
        <span className="text-xs text-muted-foreground">10-K</span>
      </div>
      <div className="flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-bold">{counts['10-Q'] || 0}</span>
        <span className="text-xs text-muted-foreground">10-Q</span>
      </div>
      <div className="flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-bold">{counts['8-K'] || 0}</span>
        <span className="text-xs text-muted-foreground">8-K</span>
      </div>
      <div className="flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-bold">{counts['4'] || 0}</span>
        <span className="text-xs text-muted-foreground">Insider</span>
      </div>
      <div className="flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-bold">{counts.other || 0}</span>
        <span className="text-xs text-muted-foreground">Other</span>
      </div>
    </div>
  )
}

export function SECFilingsList({
  filings = [],
  summary,
  symbol,
  loading = false,
  error,
  className,
}: SECFilingsListProps) {
  const [filter, setFilter] = useState<FilingType>('all')
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc')

  const filteredFilings = useMemo(() => {
    let result = [...filings]

    if (filter !== 'all') {
      result = result.filter(f => f.form_type === filter)
    }

    result.sort((a, b) => {
      const dateA = new Date(a.filed_at).getTime()
      const dateB = new Date(b.filed_at).getTime()
      return sortOrder === 'desc' ? dateB - dateA : dateA - dateB
    })

    return result
  }, [filings, filter, sortOrder])

  const handleRefresh = () => {
    console.log('Refresh SEC filings')
  }

  const handleExport = () => {
    const csvContent = [
      ['Form Type', 'Filed Date', 'Report Date', 'Accession Number', 'Document URL'].join(','),
      ...filteredFilings.map(f => [
        f.form_type,
        f.filed_at,
        f.report_date,
        f.accession_number || '',
        f.document_url || '',
      ].join(',')),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${symbol || 'sec'}-filings.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-4 w-48 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || (!filings.length && !summary)) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            SEC Filings
          </CardTitle>
          <CardDescription>SEC Edgar filings and regulatory documents</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No filings data available'}</p>
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
              <FileText className="h-5 w-5" />
              SEC Filings
              {symbol && <Badge variant="outline">{symbol}</Badge>}
            </CardTitle>
            <CardDescription>SEC Edgar filings and regulatory documents</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={filter} onValueChange={(v) => setFilter(v as FilingType)}>
              <SelectTrigger className="w-36">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Filings</SelectItem>
                <SelectItem value="10-K">10-K (Annual)</SelectItem>
                <SelectItem value="10-Q">10-Q (Quarterly)</SelectItem>
                <SelectItem value="8-K">8-K (Current)</SelectItem>
                <SelectItem value="4">Form 4 (Insider)</SelectItem>
                <SelectItem value="DEF 14A">DEF 14A (Proxy)</SelectItem>
                <SelectItem value="S-1">S-1 (IPO)</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortOrder} onValueChange={(v) => setSortOrder(v as 'desc' | 'asc')}>
              <SelectTrigger className="w-28">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">Newest</SelectItem>
                <SelectItem value="asc">Oldest</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" onClick={handleRefresh}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleExport}>
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {summary && <FilingsSummaryCard summary={summary} />}

        <Tabs defaultValue="filings" className="mt-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="filings">All Filings</TabsTrigger>
            <TabsTrigger value="annual">Annual Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="filings" className="mt-4">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-24">Type</TableHead>
                    <TableHead>Filing Details</TableHead>
                    <TableHead className="hidden md:table-cell">Period</TableHead>
                    <TableHead className="w-24 text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredFilings.map((filing, index) => (
                    <FilingRow key={filing.id || index} filing={filing} />
                  ))}
                </TableBody>
              </Table>
            </div>

            {filteredFilings.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No filings match your filters</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="annual" className="mt-4">
            <div className="text-center py-8 text-muted-foreground">
              <Building className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>Annual and quarterly report summaries would go here</p>
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">
            Data from SEC Edgar · {summary?.total_filings || filings.length} filings ·
            Last updated: {summary?.last_updated || 'N/A'}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
