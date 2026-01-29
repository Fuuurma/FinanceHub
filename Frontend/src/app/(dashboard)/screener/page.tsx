'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, RotateCcw, Play } from 'lucide-react'
import { FilterPanel } from '@/components/screener/FilterPanel'
import { ResultsPanel } from '@/components/screener/ResultsPanel'
import { useScreenerStore } from '@/stores/screenerStore'

export default function ScreenerPage() {
  const {
    runScreener,
    clearFilters,
    loading,
    error,
    selectedFilters,
    selectedPreset
  } = useScreenerStore()

  useEffect(() => {
    runScreener()
  }, [])

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Stock Screener</h1>
          <p className="text-muted-foreground mt-1">
            Find stocks and assets that match your investment criteria
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={clearFilters}
            disabled={loading || (selectedFilters.length === 0 && !selectedPreset)}
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
