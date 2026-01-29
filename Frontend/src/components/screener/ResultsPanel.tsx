'use client'

import { useEffect } from 'react'
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
  } = useScreenerStore()

  useEffect(() => {
    if (results.length === 0 && !loading) {
      runScreener()
    }
  }, [])

  const filteredResults = results.filter(result =>
    result.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    result.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const totalPages = Math.ceil(filteredResults.length / limit)

  const handleExport = (format: 'csv' | 'json') => {
    if (filteredResults.length === 0) return

    if (format === 'json') {
      const data = JSON.stringify(filteredResults, null, 2)
      const blob = new Blob([data], { type: 'application/json' })
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
      const rows = filteredResults.map(r => [
        r.symbol,
        r.name,
        r.asset_type,
        r.price?.toFixed(2) || 'N/A',
        r.change_percent !== null ? `${r.change_percent >= 0 ? '+' : ''}${r.change_percent.toFixed(2)}%` : 'N/A',
        r.volume ? (r.volume / 1000000).toFixed(2) + 'M' : 'N/A',
        r.market_cap ? `$${(r.market_cap / 1000000000).toFixed(2)}B` : 'N/A',
        r.pe_ratio !== null ? r.pe_ratio.toFixed(2) : 'N/A'
      ])

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
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Results</CardTitle>
            <div className="flex items-center gap-2">
              <div className="relative w-48">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search results..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8 h-9"
                />
              </div>
              <Select value={limit.toString()} onValueChange={(v) => setLimit(parseInt(v))}>
                <SelectTrigger className="w-24 h-9">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="20">20</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-32 h-9">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="relevance">Relevance</SelectItem>
                  <SelectItem value="price">Price</SelectItem>
                  <SelectItem value="volume">Volume</SelectItem>
                  <SelectItem value="change">Change</SelectItem>
                </SelectContent>
              </Select>
              <Select value={sortOrder} onValueChange={(v) => setSortOrder(v as 'asc' | 'desc')}>
                <SelectTrigger className="w-24 h-9">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="desc">Desc</SelectItem>
                  <SelectItem value="asc">Asc</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <CardDescription>
            Showing {filteredResults.length > 0 ? ((currentPage - 1) * limit) + 1 : 0}-{Math.min(currentPage * limit, filteredResults.length)} of {filteredResults.length} results
            {results.length > 0 && ` • Screened ${results.length} assets`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="text-center py-12 text-destructive">
              <p>{error}</p>
              <Button variant="outline" size="sm" onClick={runScreener} className="mt-2">
                Retry
              </Button>
            </div>
          ) : filteredResults.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p>No results match your criteria.</p>
              <p className="text-sm mt-1">Try adjusting your filters or running without filters.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredResults.slice((currentPage - 1) * limit, currentPage * limit).map((result) => (
                <div
                  key={result.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => router.push(`/assets/${result.symbol}`)}
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
                        <div className="flex items-center justify-end gap-1">
                          {result.change_percent > 0 ? (
                            <TrendingUp className="h-3 w-3 text-green-600" />
                          ) : (
                            <TrendingDown className="h-3 w-3 text-red-600" />
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
                          {(result.volume / 1000000).toFixed(2)}M
                        </p>
                      </div>
                    )}

                    {result.market_cap && (
                      <div className="text-right min-w-[100px]">
                        <p className="text-xs text-muted-foreground">Market Cap</p>
                        <p className="font-medium tabular-nums">
                          ${(result.market_cap / 1000000000).toFixed(2)}B
                        </p>
                      </div>
                    )}

                    {result.pe_ratio !== null && (
                      <div className="text-right min-w-[60px]">
                        <p className="text-xs text-muted-foreground">P/E</p>
                        <p className="font-medium tabular-nums">{result.pe_ratio.toFixed(2)}</p>
                      </div>
                    )}

                    <Button variant="ghost" size="sm">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {filteredResults.length > limit && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <div className="text-sm text-muted-foreground">
                Page {currentPage} of {totalPages}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          )}

          {filteredResults.length > 0 && (
            <div className="flex gap-2 mt-4 pt-4 border-t">
              <Label className="text-sm text-muted-foreground self-center">Export:</Label>
              <Button variant="outline" size="sm" onClick={() => handleExport('csv')}>
                CSV
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleExport('json')}>
                JSON
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
