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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { TrendingUp, TrendingDown, Minus, ArrowUpDown } from 'lucide-react'
import { MarketPair } from '@/lib/types/coinmarketcap'

interface MarketPairsTableProps {
  pairs?: MarketPair[] | null
  loading?: boolean
  error?: string
  limit?: number
}

type SortField = 'volume_24h' | 'price' | 'percent_change_24h' | 'trust_score'
type SortOrder = 'asc' | 'desc'

export function MarketPairsTable({ pairs, loading, error, limit = 20 }: MarketPairsTableProps) {
  const [sortField, setSortField] = useState<SortField>('volume_24h')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
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

  if (error || !pairs || pairs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Market Pairs</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No market pairs available'}</p>
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
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(2)}%`
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  const sortedPairs = [...pairs]
    .sort((a, b) => {
      let aVal: number | undefined
      let bVal: number | undefined

      switch (sortField) {
        case 'volume_24h':
          aVal = a.volume_24h
          bVal = b.volume_24h
          break
        case 'price':
          aVal = a.price
          bVal = b.price
          break
        case 'percent_change_24h':
          aVal = a.price_quote?.USD
          bVal = b.price_quote?.USD
          break
        case 'trust_score':
          aVal = a.volume_percent && a.volume_percent >= 1 ? 1 : 0
          bVal = b.volume_percent && b.volume_percent >= 1 ? 1 : 0
          break
      }

      if (aVal === undefined || aVal === null) return 1
      if (bVal === undefined || bVal === null) return -1
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal
    })
    .slice(0, limit)

  const SortButton = ({ field }: { field: SortField }) => (
    <Button
      variant="ghost"
      size="sm"
      className="h-6 p-0 font-normal"
      onClick={() => handleSort(field)}
    >
      {sortField === field ? (
        sortOrder === 'asc' ? (
          <ArrowUpDown className="h-3 w-3" />
        ) : (
          <ArrowUpDown className="h-3 w-3 rotate-180" />
        )
      ) : (
        <Minus className="h-3 w-3 opacity-20" />
      )}
    </Button>
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Market Pairs</CardTitle>
        <CardDescription>Trading pairs across exchanges</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Exchange</TableHead>
                <TableHead>Pair</TableHead>
                <TableHead className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    Price
                    <SortButton field="price" />
                  </div>
                </TableHead>
                <TableHead className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    Volume (24h)
                    <SortButton field="volume_24h" />
                  </div>
                </TableHead>
                <TableHead className="text-center">
                  <div className="flex items-center justify-center gap-1">
                    Trust
                    <SortButton field="trust_score" />
                  </div>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedPairs.map((pair) => (
                <TableRow key={pair.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{pair.exchange.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{pair.pair}</Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    ${formatNumber(pair.price, 6)}
                  </TableCell>
                  <TableCell className="text-right">{formatNumber(pair.volume_24h)}</TableCell>
                  <TableCell className="text-center">
                    <Badge
                      variant={pair.volume_percent && pair.volume_percent >= 1 ? 'default' : 'secondary'}
                      className={
                        pair.volume_percent && pair.volume_percent >= 1
                          ? 'bg-green-500 hover:bg-green-600'
                          : ''
                      }
                    >
                      {pair.volume_percent && pair.volume_percent >= 1 ? 'High' : 'Low'}
                    </Badge>
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
