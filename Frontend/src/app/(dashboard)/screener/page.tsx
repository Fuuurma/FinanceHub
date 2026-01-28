'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Search,
  Filter,
  TrendingUp,
  TrendingDown,
  X,
  Loader2
} from 'lucide-react'
import { screenerApi } from '@/lib/api/screener'
import type {
  ScreenerFilter,
  ScreenerFiltersOut,
  ScreenerResult,
} from '@/lib/types/screener'

export default function ScreenerPage() {
  const [filtersData, setFiltersData] = useState<ScreenerFiltersOut | null>(null)
  const [results, setResults] = useState<ScreenerResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState('relevance')
  const [sortOrder, setSortOrder] = useState('desc')
  const [limit, setLimit] = useState(20)
  const [selectedFilters, setSelectedFilters] = useState<ScreenerFilter[]>([])

  useEffect(() => {
    loadFilters()
  }, [])

  const loadFilters = async () => {
    try {
      setLoading(true)
      const data = await screenerApi.getFilters()
      setFiltersData(data)
      setSelectedFilters(data.active_filters.map(f => ({
        key: f.key,
        value: f.value,
        operator: f.operator
      })))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load filters')
    } finally {
      setLoading(false)
    }
  }

  const runScreen = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await screenerApi.screenAssets(
        selectedFilters.length > 0 ? selectedFilters : undefined,
        selectedPreset,
        limit,
        sortBy,
        sortOrder
      )
      setResults(response.results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to screen assets')
    } finally {
      setLoading(false)
    }
  }

  const applyPreset = async (presetKey: string) => {
    try {
      setLoading(true)
      setError('')
      await screenerApi.applyPreset(presetKey)
      setSelectedPreset(presetKey)
      await runScreen()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply preset')
    } finally {
      setLoading(false)
    }
  }

  const clearFilters = async () => {
    try {
      setLoading(true)
      await screenerApi.clearFilters()
      setSelectedFilters([])
      setSelectedPreset(null)
      setResults([])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear filters')
    } finally {
      setLoading(false)
    }
  }

  const removeFilter = (index: number) => {
    setSelectedFilters(selectedFilters.filter((_, i) => i !== index))
  }

  const filteredResults = results.filter(result =>
    result.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    result.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Stock Screener</h1>
          <p className="text-muted-foreground mt-2">
            Find stocks and assets that match your investment criteria
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={clearFilters} disabled={loading}>
            <X className="h-4 w-4 mr-2" />
            Clear All
          </Button>
          <Button onClick={runScreen} disabled={loading}>
            {loading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Filter className="h-4 w-4 mr-2" />
            )}
            Run Screener
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Presets</CardTitle>
              <CardDescription>Quick start with common filters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {filtersData?.presets.map(preset => (
                <Button
                  key={preset.key}
                  variant={selectedPreset === preset.key ? "default" : "outline"}
                  className="w-full justify-start"
                  onClick={() => applyPreset(preset.key)}
                  disabled={loading}
                >
                  <Filter className="h-4 w-4 mr-2" />
                  <div className="text-left">
                    <div className="font-medium">{preset.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {preset.description}
                    </div>
                  </div>
                </Button>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Results Limit</Label>
                <Select value={limit.toString()} onValueChange={(v) => setLimit(parseInt(v))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="10">10 results</SelectItem>
                    <SelectItem value="20">20 results</SelectItem>
                    <SelectItem value="50">50 results</SelectItem>
                    <SelectItem value="100">100 results</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Sort By</Label>
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="relevance">Relevance</SelectItem>
                    <SelectItem value="price">Price</SelectItem>
                    <SelectItem value="volume">Volume</SelectItem>
                    <SelectItem value="change">Change</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Sort Order</Label>
                <Select value={sortOrder} onValueChange={setSortOrder}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="desc">Descending</SelectItem>
                    <SelectItem value="asc">Ascending</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-3 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Filters</CardTitle>
              {selectedFilters.length > 0 && (
                <CardDescription>{selectedFilters.length} filter{selectedFilters.length > 1 ? 's' : ''} applied</CardDescription>
              )}
            </CardHeader>
            <CardContent>
              {selectedFilters.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  No filters applied. Select a preset or add filters below.
                </p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {selectedFilters.map((filter, index) => (
                    <Badge key={index} variant="secondary" className="gap-1">
                      {filter.key}: {filter.value}
                      <button
                        onClick={() => removeFilter(index)}
                        className="ml-1 hover:text-destructive"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Results</CardTitle>
                <div className="relative w-64">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search results..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>
              </div>
              <CardDescription>
                Showing {filteredResults.length} of {results.length} results
                {results.length > 0 && ` • Screened ${results.length} assets`}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : filteredResults.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  {searchTerm ? 'No results match your search' : 'No results. Run the screener to see matching assets.'}
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredResults.map((result) => (
                    <div
                      key={result.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <div>
                            <p className="font-semibold text-lg">{result.symbol}</p>
                            <p className="text-sm text-muted-foreground">{result.name}</p>
                          </div>
                          <Badge variant="outline">{result.asset_type}</Badge>
                        </div>
                      </div>

                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <p className="font-semibold tabular-nums">
                            ${result.price?.toFixed(2) || 'N/A'}
                          </p>
                          <div className="flex items-center gap-1 justify-end">
                            {result.change_percent !== null && result.change_percent !== 0 ? (
                              result.change_percent > 0 ? (
                                <TrendingUp className="h-4 w-4 text-green-600" />
                              ) : (
                                <TrendingDown className="h-4 w-4 text-red-600" />
                              )
                            ) : null}
                            <p className={`text-sm font-medium tabular-nums ${
                              result.change_percent > 0 ? 'text-green-600' :
                              result.change_percent < 0 ? 'text-red-600' :
                              'text-muted-foreground'
                            }`}>
                              {result.change_percent !== null ? `${result.change_percent >= 0 ? '+' : ''}${result.change_percent.toFixed(2)}%` : 'N/A'}
                            </p>
                          </div>
                        </div>

                        {result.volume && (
                          <div className="text-right min-w-[100px]">
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
                          <div className="text-right min-w-[80px]">
                            <p className="text-xs text-muted-foreground">P/E Ratio</p>
                            <p className="font-medium tabular-nums">{result.pe_ratio.toFixed(2)}</p>
                          </div>
                        )}

                        <Button variant="ghost" size="sm">
                          View
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
