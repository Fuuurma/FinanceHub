'use client'

import React from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Earnings } from '@/lib/types/iex-cloud'

interface EarningsTableProps {
  earnings?: Earnings[] | null
  loading?: boolean
  error?: string
}

export function EarningsTable({ earnings, loading, error }: EarningsTableProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !earnings || earnings.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Earnings</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No earnings data available'}</p>
        </CardContent>
      </Card>
    )
  }

  const formatNumber = (value: number | undefined, decimals = 2) => {
    if (value === undefined || value === null) return 'N/A'
    return value.toFixed(decimals)
  }

  const formatPercent = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A'
    return `${value.toFixed(2)}%`
  }

  const getSurpriseIcon = (surprisePercent: number | undefined) => {
    if (surprisePercent === undefined || surprisePercent === null || surprisePercent === 0) {
      return <Minus className="h-4 w-4 text-muted-foreground" />
    }
    if (surprisePercent > 0) {
      return <TrendingUp className="h-4 w-4 text-green-500" />
    }
    return <TrendingDown className="h-4 w-4 text-red-500" />
  }

  const getSurpriseBadge = (surprisePercent: number | undefined) => {
    if (surprisePercent === undefined || surprisePercent === null) {
      return <Badge variant="secondary">N/A</Badge>
    }
    if (surprisePercent > 5) {
      return <Badge variant="default" className="bg-green-500">Beat</Badge>
    }
    if (surprisePercent < -5) {
      return <Badge variant="destructive">Miss</Badge>
    }
    return <Badge variant="secondary">In-line</Badge>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Earnings</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Fiscal Period</TableHead>
              <TableHead className="text-right">EPS Estimate</TableHead>
              <TableHead className="text-right">EPS Actual</TableHead>
              <TableHead className="text-right">Surprise (%)</TableHead>
              <TableHead className="text-right">Result</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {earnings.map((earning, index) => (
              <TableRow key={index}>
                <TableCell className="font-medium">{earning.fiscalPeriod}</TableCell>
                <TableCell className="text-right">${formatNumber(earning.estimatedEPS)}</TableCell>
                <TableCell className="text-right">${formatNumber(earning.actualEPS)}</TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-2">
                    {getSurpriseIcon(earning.surprisePercent)}
                    <span>{formatPercent(earning.surprisePercent)}</span>
                  </div>
                </TableCell>
                <TableCell className="text-right">
                  {getSurpriseBadge(earning.surprisePercent)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
