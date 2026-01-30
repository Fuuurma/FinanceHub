"use client"

import { useState } from 'react'
import { FileText, Download, ChevronDown, ChevronUp, Building2, DollarSign, TrendingUp, TrendingDown } from 'lucide-react'
import { cn, formatCurrency, formatNumber, formatPercent } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'

export interface FinancialStatement {
  period: string
  periodType: 'annual' | 'quarterly'
  fiscalYear: number
  fiscalQuarter?: number
  revenue: number
  revenueGrowth: number
  grossProfit: number
  grossMargin: number
  operatingIncome: number
  operatingMargin: number
  netIncome: number
  netMargin: number
  eps: number
  epsGrowth: number
  assets: number
  liabilities: number
  equity: number
  cashFlow: number
  freeCashFlow: number
}

export interface FinancialStatementsProps {
  statements?: FinancialStatement[]
  type?: 'income' | 'balance' | 'cashflow'
  symbol?: string
  loading?: boolean
  error?: string
  className?: string
}

type StatementPeriod = 'annual' | 'quarterly'

const METRIC_LABELS: Record<string, string> = {
  revenue: 'Revenue',
  grossProfit: 'Gross Profit',
  operatingIncome: 'Operating Income',
  netIncome: 'Net Income',
  eps: 'EPS',
  assets: 'Total Assets',
  liabilities: 'Total Liabilities',
  equity: 'Shareholders Equity',
  cashFlow: 'Operating Cash Flow',
  freeCashFlow: 'Free Cash Flow',
}

function IncomeStatementTable({ statements }: { statements: FinancialStatement[] }) {
  const latest = statements[0]

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-48">Metric</TableHead>
          <TableHead className="text-right">{latest?.period || 'Current'}</TableHead>
          <TableHead className="text-right">Prior</TableHead>
          <TableHead className="text-right">Change</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell className="font-medium">Revenue</TableCell>
          <TableCell className="text-right">{formatCurrency(latest?.revenue)}</TableCell>
          <TableCell className="text-right">{formatCurrency(statements[1]?.revenue)}</TableCell>
          <TableCell className="text-right">
            {latest?.revenueGrowth !== undefined && (
              <span className={cn(latest.revenueGrowth >= 0 ? 'text-green-500' : 'text-red-500')}>
                {latest.revenueGrowth >= 0 ? '+' : ''}{formatPercent(latest.revenueGrowth)}
              </span>
            )}
          </TableCell>
        </TableRow>
        <TableRow>
          <TableCell>Gross Profit</TableCell>
          <TableCell className="text-right">{formatCurrency(latest?.grossProfit)}</TableCell>
          <TableCell className="text-right">{formatCurrency(statements[1]?.grossProfit)}</TableCell>
          <TableCell className="text-right">
            {latest?.grossMargin !== undefined && (
              <span className="text-muted-foreground">{formatPercent(latest.grossMargin)}</span>
            )}
          </TableCell>
        </TableRow>
        <TableRow>
          <TableCell>Operating Income</TableCell>
          <TableCell className="text-right">{formatCurrency(latest?.operatingIncome)}</TableCell>
          <TableCell className="text-right">{formatCurrency(statements[1]?.operatingIncome)}</TableCell>
          <TableCell className="text-right">
            {latest?.operatingMargin !== undefined && (
              <span className="text-muted-foreground">{formatPercent(latest.operatingMargin)}</span>
            )}
          </TableCell>
        </TableRow>
        <TableRow>
          <TableCell>Net Income</TableCell>
          <TableCell className="text-right font-semibold">{formatCurrency(latest?.netIncome)}</TableCell>
          <TableCell className="text-right">{formatCurrency(statements[1]?.netIncome)}</TableCell>
          <TableCell className="text-right">
            {latest?.netMargin !== undefined && (
              <span className="text-muted-foreground">{formatPercent(latest.netMargin)}</span>
            )}
          </TableCell>
        </TableRow>
        <TableRow>
          <TableCell>EPS</TableCell>
          <TableCell className="text-right font-semibold">${latest?.eps?.toFixed(2) || '0.00'}</TableCell>
          <TableCell className="text-right">${statements[1]?.eps?.toFixed(2) || '0.00'}</TableCell>
          <TableCell className="text-right">
            {latest?.epsGrowth !== undefined && (
              <span className={cn(latest.epsGrowth >= 0 ? 'text-green-500' : 'text-red-500')}>
                {latest.epsGrowth >= 0 ? '+' : ''}{formatPercent(latest.epsGrowth)}
              </span>
            )}
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  )
}

function BalanceSheetTable({ statements }: { statements: FinancialStatement[] }) {
  const latest = statements[0]

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-48">Metric</TableHead>
          <TableHead className="text-right">{latest?.period || 'Current'}</TableHead>
          <TableHead className="text-right">Prior</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell className="font-medium">Total Assets</TableCell>
          <TableCell className="text-right">{formatCurrency(latest?.assets)}</TableCell>
          <TableCell className="text-right">{formatCurrency(statements[1]?.assets)}</TableCell>
        </TableRow>
        <TableRow>
          <TableCell>Total Liabilities</TableCell>
          <TableCell className="text-right">{formatCurrency(latest?.liabilities)}</TableCell>
          <TableCell className="text-right">{formatCurrency(statements[1]?.liabilities)}</TableCell>
        </TableRow>
        <TableRow>
          <TableCell>Shareholders Equity</TableCell>
          <TableCell className="text-right font-semibold">{formatCurrency(latest?.equity)}</TableCell>
          <TableCell className="text-right">{formatCurrency(statements[1]?.equity)}</TableCell>
        </TableRow>
        <TableRow>
          <TableCell>Debt/Equity Ratio</TableCell>
          <TableCell className="text-right">
            {latest?.equity ? (latest.liabilities / latest.equity).toFixed(2) : 'N/A'}
          </TableCell>
          <TableCell className="text-right">
            {statements[1]?.equity ? (statements[1].liabilities / statements[1].equity).toFixed(2) : 'N/A'}
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  )
}

function CashFlowTable({ statements }: { statements: FinancialStatement[] }) {
  const latest = statements[0]

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-48">Metric</TableHead>
          <TableHead className="text-right">{latest?.period || 'Current'}</TableHead>
          <TableHead className="text-right">Prior</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell className="font-medium">Operating Cash Flow</TableCell>
          <TableCell className="text-right">{formatCurrency(latest?.cashFlow)}</TableCell>
          <TableCell className="text-right">{formatCurrency(statements[1]?.cashFlow)}</TableCell>
        </TableRow>
        <TableRow>
          <TableCell>Free Cash Flow</TableCell>
          <TableCell className="text-right font-semibold">{formatCurrency(latest?.freeCashFlow)}</TableCell>
          <TableCell className="text-right">{formatCurrency(statements[1]?.freeCashFlow)}</TableCell>
        </TableRow>
        <TableRow>
          <TableCell>FCF per Share</TableCell>
          <TableCell className="text-right">
            {latest?.freeCashFlow && latest?.eps ? `$${(latest.freeCashFlow / 1000000 / latest.eps).toFixed(2)}` : 'N/A'}
          </TableCell>
          <TableCell className="text-right">
            {statements[1]?.freeCashFlow && statements[1]?.eps ? `$${(statements[1].freeCashFlow / 1000000 / statements[1].eps).toFixed(2)}` : 'N/A'}
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  )
}

export function FinancialStatements({
  statements = [],
  type = 'income',
  symbol,
  loading = false,
  error,
  className,
}: FinancialStatementsProps) {
  const [period, setPeriod] = useState<StatementPeriod>('annual')
  const [expanded, setExpanded] = useState(false)

  const filteredStatements = statements.filter(s => s.periodType === period).slice(0, 4)
  const latest = filteredStatements[0]

  const handleExport = () => {
    const csvContent = [
      ['Period', 'Revenue', 'Gross Profit', 'Operating Income', 'Net Income', 'EPS', 'Assets', 'Liabilities', 'Equity'].join(','),
      ...filteredStatements.map(s => [
        s.period,
        s.revenue,
        s.grossProfit,
        s.operatingIncome,
        s.netIncome,
        s.eps,
        s.assets,
        s.liabilities,
        s.equity,
      ].join(',')),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${symbol || 'company'}-financials-${period}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-32 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-48 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || (!statements.length && !latest)) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Financial Statements
          </CardTitle>
          <CardDescription>Income statement, balance sheet, and cash flow</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No financial data available'}</p>
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
              Financial Statements
              {symbol && <Badge variant="outline">{symbol}</Badge>}
            </CardTitle>
            <CardDescription>Income statement, balance sheet, and cash flow</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={period} onValueChange={(v) => setPeriod(v as StatementPeriod)}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="annual">Annual</SelectItem>
                <SelectItem value="quarterly">Quarterly</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" onClick={handleExport}>
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="income" className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="income">Income Statement</TabsTrigger>
            <TabsTrigger value="balance">Balance Sheet</TabsTrigger>
            <TabsTrigger value="cashflow">Cash Flow</TabsTrigger>
          </TabsList>

          <TabsContent value="income" className="mt-4">
            <IncomeStatementTable statements={filteredStatements} />
          </TabsContent>

          <TabsContent value="balance" className="mt-4">
            <BalanceSheetTable statements={filteredStatements} />
          </TabsContent>

          <TabsContent value="cashflow" className="mt-4">
            <CashFlowTable statements={filteredStatements} />
          </TabsContent>
        </Tabs>

        <Collapsible open={expanded} onOpenChange={setExpanded} className="mt-4">
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="w-full justify-between">
              <span>Historical Data ({filteredStatements.length} periods)</span>
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-2">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Period</TableHead>
                    <TableHead className="text-right">Revenue</TableHead>
                    <TableHead className="text-right">Net Income</TableHead>
                    <TableHead className="text-right">EPS</TableHead>
                    <TableHead className="text-right">FCF</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredStatements.map((s, i) => (
                    <TableRow key={i}>
                      <TableCell>{s.period}</TableCell>
                      <TableCell className="text-right">{formatCurrency(s.revenue)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(s.netIncome)}</TableCell>
                      <TableCell className="text-right">${s.eps.toFixed(2)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(s.freeCashFlow)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CollapsibleContent>
        </Collapsible>

        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">
            Data from company filings · {period === 'annual' ? 'Annual' : 'Quarterly'} reporting
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
