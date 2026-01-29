'use client'

import { useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Filter, Loader2, Plus, RotateCcw, Play } from 'lucide-react'
import { FilterRow } from './FilterRow'
import { useScreenerStore } from '@/stores/screenerStore'

export function FilterPanel() {
  const {
    selectedFilters,
    addFilter,
    clearFilters,
    runScreener,
    loading,
    loadPresets,
    applyPreset,
  } = useScreenerStore()

  useEffect(() => {
    loadPresets()
  }, [loadPresets])

  const handleAddFilter = useCallback(() => {
    addFilter({
      key: '',
      value: '',
      operator: '='
    })
  }, [addFilter])

  const handleClearFilters = useCallback(async () => {
    await clearFilters()
  }, [clearFilters])

  const handleRunScreener = useCallback(async () => {
    await runScreener()
  }, [runScreener])

  const handleKeydown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleRunScreener()
    }
  }, [handleRunScreener])

  useEffect(() => {
    window.addEventListener('keydown', handleKeydown)
    return () => window.removeEventListener('keydown', handleKeydown)
  }, [handleKeydown])

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Filter className="h-4 w-4" aria-hidden="true" />
            Active Filters
          </CardTitle>
          {selectedFilters.length > 0 && (
            <CardDescription>{selectedFilters.length} filter(s) applied</CardDescription>
          )}
        </CardHeader>
        <CardContent className="space-y-3">
          {selectedFilters.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No filters applied. Add filters or select a preset below.
            </p>
          ) : (
            <ScrollArea className="h-[300px] pr-3">
              <div className="space-y-2" role="list" aria-label="Active filters">
                {selectedFilters.map((filter, index) => (
                  <FilterRow key={index} index={index} filter={filter} />
                ))}
              </div>
            </ScrollArea>
          )}
          <div className="flex gap-2 pt-2" role="group" aria-label="Filter actions">
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearFilters}
              disabled={loading || selectedFilters.length === 0}
              aria-label="Clear all filters"
            >
              <RotateCcw className="h-3 w-3 mr-1" aria-hidden="true" />
              Clear All
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleAddFilter}
              disabled={loading}
              aria-label="Add new filter"
            >
              <Plus className="h-3 w-3 mr-1" aria-hidden="true" />
              Add Filter
            </Button>
            <Button
              size="sm"
              onClick={handleRunScreener}
              disabled={loading || selectedFilters.length === 0}
              className="ml-auto"
              aria-label="Run screener with current filters"
            >
              {loading ? (
                <Loader2 className="h-3 w-3 mr-1 animate-spin" aria-hidden="true" />
              ) : (
                <Play className="h-3 w-3 mr-1" aria-hidden="true" />
              )}
              Run
            </Button>
          </div>
        </CardContent>
      </Card>

      <Separator />

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Quick Presets</CardTitle>
          <CardDescription>Common screening criteria</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-2" role="list" aria-label="Filter presets">
            {[
              { id: 'undervalued', name: 'Undervalued', desc: 'Low P/E, low P/B' },
              { id: 'growth', name: 'Growth', desc: 'High earnings growth' },
              { id: 'dividend', name: 'Dividend', desc: 'High dividend yield' },
              { id: 'momentum', name: 'Momentum', desc: 'Strong performance' },
              { id: 'smallCap', name: 'Small Cap', desc: 'Undervalued small caps' },
              { id: 'techLeaders', name: 'Tech Leaders', desc: 'Large tech companies' },
            ].map(preset => (
              <Button
                key={preset.id}
                variant="outline"
                size="sm"
                className="justify-start h-auto py-2"
                onClick={() => applyPreset(preset.id)}
                disabled={loading}
                role="listitem"
                aria-label={`Apply ${preset.name} preset: ${preset.desc}`}
              >
                <div className="text-left">
                  <div className="font-medium">{preset.name}</div>
                  <div className="text-xs text-muted-foreground">{preset.desc}</div>
                </div>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
