'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Minus, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { cn } from '@/lib/utils'

interface HoldingPerformance {
  symbol: string
  name: string
  weight: number
  return: number
  contribution: number
  value: number
  sector: string
}

interface PerformanceBreakdownProps {
  holdings: HoldingPerformance[]
  className?: string
}

export function PerformanceBreakdown({ holdings, className }: PerformanceBreakdownProps) {
  const sortedByContribution = [...holdings].sort((a, b) => b.contribution - a.contribution)
  const topContributors = sortedByContribution.slice(0, 5)
  const bottomContributors = sortedByContribution.slice(-5).reverse()

  const getReturnBadge = (returnValue: number) => {
    if (returnValue > 0) {
      return (
        <Badge className="bg-green-100 text-green-700 hover:bg-green-200">
          <ArrowUpRight className="h-3 w-3 mr-1" />
          +{returnValue.toFixed(2)}%
        </Badge>
      )
    }
    if (returnValue < 0) {
      return (
        <Badge variant="destructive" className="bg-red-100 text-red-700 hover:bg-red-200">
          <ArrowDownRight className="h-3 w-3 mr-1" />
          {returnValue.toFixed(2)}%
        </Badge>
      )
    }
    return (
      <Badge variant="secondary">
        <Minus className="h-3 w-3 mr-1" />
        {returnValue.toFixed(2)}%
      </Badge>
    )
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Performance Breakdown</CardTitle>
        <CardDescription>Contribution to portfolio return by holding</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              Top Contributors
            </h4>
            <div className="space-y-2">
              {topContributors.map((holding, index) => (
                <div key={holding.symbol} className="flex items-center justify-between p-2 rounded-lg bg-green-50 dark:bg-green-900/20">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-muted-foreground">{index + 1}</span>
                    <div>
                      <p className="font-medium text-sm">{holding.symbol}</p>
                      <p className="text-xs text-muted-foreground truncate max-w-[120px]">{holding.name}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-green-600">+{holding.contribution.toFixed(2)}%</p>
                    <p className="text-xs text-muted-foreground">{holding.weight.toFixed(1)}% weight</p>
                  </div>
                </div>
              ))}
              {topContributors.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">No positive contributors</p>
              )}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-500" />
              Bottom Contributors
            </h4>
            <div className="space-y-2">
              {bottomContributors.map((holding, index) => (
                <div key={holding.symbol} className="flex items-center justify-between p-2 rounded-lg bg-red-50 dark:bg-red-900/20">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-muted-foreground">{holdings.length - index}</span>
                    <div>
                      <p className="font-medium text-sm">{holding.symbol}</p>
                      <p className="text-xs text-muted-foreground truncate max-w-[120px]">{holding.name}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-red-600">{holding.contribution.toFixed(2)}%</p>
                    <p className="text-xs text-muted-foreground">{holding.weight.toFixed(1)}% weight</p>
                  </div>
                </div>
              ))}
              {bottomContributors.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">No negative contributors</p>
              )}
            </div>
          </div>
        </div>

        <div className="mt-6">
          <h4 className="text-sm font-medium mb-3">All Holdings</h4>
          <div className="border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Symbol</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead className="text-right">Weight</TableHead>
                  <TableHead className="text-right">Return</TableHead>
                  <TableHead className="text-right">Contribution</TableHead>
                  <TableHead className="text-right">Value</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {holdings.map((holding) => (
                  <TableRow key={holding.symbol}>
                    <TableCell className="font-medium">{holding.symbol}</TableCell>
                    <TableCell className="text-muted-foreground truncate max-w-[150px]">{holding.name}</TableCell>
                    <TableCell className="text-right">{holding.weight.toFixed(1)}%</TableCell>
                    <TableCell className="text-right">{getReturnBadge(holding.return)}</TableCell>
                    <TableCell className={cn(
                      'text-right font-medium',
                      holding.contribution > 0 ? 'text-green-600' : holding.contribution < 0 ? 'text-red-600' : ''
                    )}>
                      {holding.contribution >= 0 ? '+' : ''}{holding.contribution.toFixed(2)}%
                    </TableCell>
                    <TableCell className="text-right">{formatCurrency(holding.value)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
