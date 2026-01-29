'use client'

import { useEffect, useMemo, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Search,
  TrendingUp,
  TrendingDown,
  ChevronLeft,
  ChevronRight,
  Loader2,
  ExternalLink,
  FileSpreadsheet,
  FileJson,
  Clock,
} from 'lucide-react'
import { useScreenerStore } from '@/stores/screenerStore'
import { formatNumber, formatPercent } from '@/lib/utils/formatters'

export function ResultsPanel() {
  const router = useRouter()
  const {
    results,
    loading,
    error,
    searchTerm,
    sortBy,
    sortOrder,
    limit,
    currentPage,
    setSearchTerm,
    setSortBy,
    setSortOrder,
    setLimit,
    setCurrentPage,
    runScreener,
    lastUpdated,
  } = useScreenerStore()

  useEffect(() => {
    if (results.length === 0 && !loading) {
      runScreener()
    }
  }, [results.length, loading, runScreener])

  const filteredResults = useMemo(() => {
    if (!searchTerm.trim()) return results
    const term = searchTerm.toLowerCase()
    return results.filter(result =>
      result.symbol.toLowerCase().includes(term) ||
      result.name.toLowerCase().includes(term)
    )
  }, [results, searchTerm])

  const sortedResults = useMemo(() => {
    const sorted = [...filteredResults]
    if (sortBy === 'price') {
      sorted.sort((a, b) => {
        const priceA = a.price ?? 0
        const priceB = b.price ?? 0
        return sortOrder === 'asc' ? priceA - priceB : priceB - priceA
      })
    } else if (sortBy === 'volume') {
      sorted.sort((a, b) => {
        const volA = a.volume ?? 0
        const volB = b.volume ?? 0
        return sortOrder === 'asc' ? volA - volB : volB - volA
      })
    } else if (sortBy === 'change') {
      sorted.sort((a, b) => {
        const changeA = a.change_percent ?? 0
        const changeB = b.change_percent ?? 0
        return sortOrder === 'asc' ? changeA - changeB : changeB - changeA
      })
    }
    return sorted
  }, [filteredResults, sortBy, sortOrder])

  const totalPages = useMemo(() =>
    Math.ceil(sortedResults.length / limit),
  [sortedResults.length, limit])

  const paginatedResults = useMemo(() =>
    sortedResults.slice((currentPage - 1) * limit, currentPage * limit),
  [sortedResults, currentPage, limit])

  const handleExport = useCallback((format: 'csv' | 'json') => {
    if (sortedResults.length === 0) return

    const exportData = sortedResults.map(r => ({
      symbol: r.symbol,
      name: r.name,
      type: r.asset_type,
      price: r.price?.toFixed(2) || 'N/A',
      change: r.change_percent !== null ? `${r.change_percent >= 0 ? '+' : ''}${r.change_percent.toFixed(2)}%` : 'N/A',
      volume: r.volume ? formatNumber(r.volume) : 'N/A',
      marketCap: r.market_cap ? `$${formatNumber(r.market_cap)}` : 'N/A',
      peRatio: r.pe_ratio?.toFixed(2) || 'N/A'
    }))

    if (format === 'json') {
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `screener-results-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } else {
      const headers = ['Symbol', 'Name', 'Type', 'Price', 'Change %', 'Volume', 'Market Cap', 'P/E']
      const rows = exportData.map(r => Object.values(r))

      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `screener-results-${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }, [sortedResults])

  const handlePageChange = useCallback((newPage: number) => {
    setCurrentPage(Math.max(1, Math.min(newPage, totalPages)))
  }, [totalPages, setCurrentPage])

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Results</CardTitle>
            <div className="flex items-center gap-2" role="search" aria-label="Filter and sort results">
              <div className="relative w-48">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                <Input
                  placeholder="Search results..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8 h-9"
                  aria-label="Search within results"
                />
              </div>
              <Label htmlFor="results-limit" className="sr-only">Results per page</Label>
              <Select value={limit.toString()} onValueChange={(v) => setLimit(parseInt(v))}>
                <SelectTrigger id="results-limit" className="w-24 h-9" aria-label="Results per page">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="20">20</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
              <Label htmlFor="sort-by" className="sr-only">Sort by</Label>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger id="sort-by" className="w-32 h-9" aria-label="Sort by">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="relevance">Relevance</SelectItem>
                  <SelectItem value="price">Price</SelectItem>
                  <SelectItem value="volume">Volume</SelectItem>
                  <SelectItem value="change">Change</SelectItem>
                </SelectContent>
              </Select>
              <Label htmlFor="sort-order" className="sr-only">Sort order</Label>
              <Select value={sortOrder} onValueChange={(v) => setSortOrder(v as 'asc' | 'desc')}>
                <SelectTrigger id="sort-order" className="w-24 h-9" aria-label="Sort order">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="desc">Desc</SelectItem>
                  <SelectItem value="asc">Asc</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <CardDescription aria-live="polite">
            Showing {paginatedResults.length > 0 ? ((currentPage - 1) * limit) + 1 : 0}-{Math.min(currentPage * limit, sortedResults.length)} of {sortedResults.length} results
            {results.length > 0 && ` • ${results.length} assets`}
            {lastUpdated && (
              <span className="ml-2 text-muted-foreground flex items-center gap-1 inline-flex">
                <Clock className="h-3 w-3" />
                Updated {new Date(lastUpdated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12" role="status" aria-label="Loading results">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" aria-hidden="true" />
              <span className="sr-only">Loading...</span>
            </div>
          ) : error ? (
            <div className="text-center py-12 text-destructive" role="alert">
              <p>{error}</p>
              <Button variant="outline" size="sm" onClick={runScreener} className="mt-2">
                Retry
              </Button>
            </div>
          ) : sortedResults.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p>No results match your criteria.</p>
              <p className="text-sm mt-1">Try adjusting your filters or running without filters.</p>
            </div>
          ) : (
            <div className="space-y-2" role="list" aria-label="Screened assets">
              {paginatedResults.map((result) => (
                <div
                  key={result.id}
                  role="listitem"
                  tabIndex={0}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-ring"
                  onClick={() => router.push(`/assets/${result.symbol}`)}
                  onKeyDown={(e) => e.key === 'Enter' && router.push(`/assets/${result.symbol}`)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <div>
                        <p className="font-semibold text-lg">{result.symbol}</p>
                        <p className="text-sm text-muted-foreground truncate">{result.name}</p>
                      </div>
                      <Badge variant="outline" className="capitalize">
                        {result.asset_type}
                      </Badge>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="text-right min-w-[100px]">
                      <p className="font-semibold tabular-nums">
                        ${result.price?.toFixed(2) || 'N/A'}
                      </p>
                      {result.change_percent !== null && (
                        <div className="flex items-center justify-end gap-1" aria-label={`Change: ${formatPercent(result.change_percent)}`}>
                          {result.change_percent > 0 ? (
                            <TrendingUp className="h-3 w-3 text-green-600" aria-hidden="true" />
                          ) : (
                            <TrendingDown className="h-3 w-3 text-red-600" aria-hidden="true" />
                          )}
                          <span className={`text-sm font-medium tabular-nums ${
                            result.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {formatPercent(result.change_percent)}
                          </span>
                        </div>
                      )}
                    </div>

                    {result.volume && (
                      <div className="text-right min-w-[80px]">
                        <p className="text-xs text-muted-foreground">Volume</p>
                        <p className="font-medium tabular-nums">
                          {formatNumber(result.volume)}
                        </p>
                      </div>
                    )}

                    {result.market_cap && (
                      <div className="text-right min-w-[100px]">
                        <p className="text-xs text-muted-foreground">Market Cap</p>
                        <p className="font-medium tabular-nums">
                          ${formatNumber(result.market_cap)}
                        </p>
                      </div>
                    )}

                    {result.pe_ratio !== null && (
                      <div className="text-right min-w-[60px]">
                        <p className="text-xs text-muted-foreground">P/E</p>
                        <p className="font-medium tabular-nums">{result.pe_ratio.toFixed(2)}</p>
                      </div>
                    )}

                    <Button
                      variant="ghost"
                      size="sm"
                      aria-label={`View ${result.symbol} details`}
                    >
                      <ExternalLink className="h-4 w-4" aria-hidden="true" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {sortedResults.length > limit && (
            <nav className="flex items-center justify-between mt-4 pt-4 border-t" aria-label="Pagination">
              <div className="text-sm text-muted-foreground">
                Page {currentPage} of {totalPages}
              </div>
              <div className="flex gap-2" role="navigation" aria-label="Pagination controls">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  aria-label="Previous page"
                >
                  <ChevronLeft className="h-4 w-4 mr-1" aria-hidden="true" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  aria-label="Next page"
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" aria-hidden="true" />
                </Button>
              </div>
            </nav>
          )}

          {sortedResults.length > 0 && (
            <div className="flex gap-2 mt-4 pt-4 border-t">
              <Label className="text-sm text-muted-foreground self-center">Export:</Label>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport('csv')}
                aria-label="Export results as CSV"
              >
                <FileSpreadsheet className="h-4 w-4 mr-1" aria-hidden="true" />
                CSV
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport('json')}
                aria-label="Export results as JSON"
              >
                <FileJson className="h-4 w-4 mr-1" aria-hidden="true" />
                JSON
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
