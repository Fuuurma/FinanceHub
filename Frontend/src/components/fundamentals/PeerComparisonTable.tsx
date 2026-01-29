'use client'

import React, { useState } from 'react'
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
import { Button } from '@/components/ui/button'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Peer } from '@/lib/types/iex-cloud'

interface PeerComparisonTableProps {
  peers?: Peer[]
  symbol?: string
  loading?: boolean
  error?: string
}

type SortField = 'symbol' | 'marketCap' | 'peRatio' | 'dividendYield' | 'beta'
type SortOrder = 'asc' | 'desc'

export function PeerComparisonTable({ peers, symbol, loading, error }: PeerComparisonTableProps) {
  const [sortField, setSortField] = useState<SortField>('marketCap')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !peers || peers.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Peer Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No peer data available'}</p>
        </CardContent>
      </Card>
    )
  }

  const formatNumber = (value: number | undefined, decimals = 2) => {
    if (value === undefined || value === null) return 'N/A'
    if (Math.abs(value) >= 1e9) return `${(value / 1e9).toFixed(decimals)}B`
    if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(decimals)}M`
    if (Math.abs(value) >= 1e3) return `${(value / 1e3).toFixed(decimals)}K`
    return value.toFixed(decimals)
  }

  const formatPercent = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A'
    return `${value.toFixed(2)}%`
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  const sortedPeers = [...peers].sort((a, b) => {
    let aVal: number | undefined
    let bVal: number | undefined

    switch (sortField) {
      case 'symbol':
        return sortOrder === 'asc'
          ? a.symbol.localeCompare(b.symbol)
          : b.symbol.localeCompare(a.symbol)
      case 'marketCap':
        aVal = a.marketCap
        bVal = b.marketCap
        break
      case 'peRatio':
        aVal = a.peRatio
        bVal = b.peRatio
        break
      case 'dividendYield':
        aVal = a.dividendYield
        bVal = b.dividendYield
        break
      case 'beta':
        aVal = a.beta
        bVal = b.beta
        break
    }

    if (aVal === undefined || aVal === null) return 1
    if (bVal === undefined || bVal === null) return -1
    return sortOrder === 'asc' ? aVal - bVal : bVal - aVal
  })

  const SortButton = ({ field }: { field: SortField }) => (
    <Button
      variant="ghost"
      size="sm"
      className="h-6 p-0 font-normal"
      onClick={() => handleSort(field)}
    >
      {sortField === field && (
        sortOrder === 'asc' ? (
          <TrendingUp className="h-3 w-3" />
        ) : (
          <TrendingDown className="h-3 w-3" />
        )
      )}
      {sortField !== field && <Minus className="h-3 w-3 opacity-20" />}
    </Button>
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Peer Comparison</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    Market Cap
                    <SortButton field="marketCap" />
                  </div>
                </TableHead>
                <TableHead className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    P/E Ratio
                    <SortButton field="peRatio" />
                  </div>
                </TableHead>
                <TableHead className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    Dividend Yield
                    <SortButton field="dividendYield" />
                  </div>
                </TableHead>
                <TableHead className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    Beta
                    <SortButton field="beta" />
                  </div>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedPeers.map((peer) => (
                <TableRow key={peer.symbol}>
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      {peer.symbol}
                      {peer.symbol === symbol && (
                        <Badge variant="secondary" className="text-xs">
                          You
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">{formatNumber(peer.marketCap)}</TableCell>
                  <TableCell className="text-right">
                    {peer.peRatio?.toFixed(2) || 'N/A'}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatPercent(peer.dividendYield)}
                  </TableCell>
                  <TableCell className="text-right">
                    {peer.beta?.toFixed(2) || 'N/A'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
