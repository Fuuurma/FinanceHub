'use client'

import { useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Loader2, RotateCcw, Play, RefreshCw, Clock } from 'lucide-react'
import { FilterPanel } from '@/components/screener/FilterPanel'
import { ResultsPanel } from '@/components/screener/ResultsPanel'
import { useScreenerStore } from '@/stores/screenerStore'

function formatLastUpdated(dateString: string | null): string {
  if (!dateString) return 'Never'
  const date = new Date(dateString)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

export default function ScreenerPage() {
  const {
    runScreener,
    clearFilters,
    loading,
    error,
    selectedFilters,
    selectedPreset,
    autoRefresh,
    lastUpdated
  } = useScreenerStore()

  const handleRunScreener = useCallback(() => {
    runScreener()
  }, [runScreener])

  const handleClearFilters = useCallback(() => {
    clearFilters()
  }, [clearFilters])

  useEffect(() => {
    runScreener()
  }, [runScreener])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      runScreener()
    }, 30000)

    return () => clearInterval(interval)
  }, [autoRefresh, runScreener])

  const filtersCount = selectedFilters.length
  const isFiltered = filtersCount > 0 || selectedPreset !== null

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Stock Screener</h1>
          <p className="text-muted-foreground mt-1">
            Find stocks and assets that match your investment criteria
          </p>
          <div className="flex items-center gap-3 mt-2 text-sm">
            {isFiltered && (
              <Badge variant="secondary">
                {filtersCount} filter{filtersCount !== 1 ? 's' : ''} applied
              </Badge>
            )}
            {autoRefresh ? (
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                Auto-refresh
              </Badge>
            ) : (
              <span className="text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Last updated: {formatLastUpdated(lastUpdated)}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={clearFilters}
            disabled={loading || !isFiltered}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Clear All
          </Button>
          <Button
            onClick={runScreener}
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
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
        <div className="lg:col-span-1">
          <FilterPanel />
        </div>
        <div className="lg:col-span-3">
          <ResultsPanel />
        </div>
      </div>
    </div>
  )
}
