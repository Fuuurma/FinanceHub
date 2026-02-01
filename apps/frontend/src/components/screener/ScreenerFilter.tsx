'use client'

import { useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { X, Filter, ChevronDown, ChevronUp } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useScreenerStore } from '@/stores/screenerStore'
import type { ScreenerRequest } from '@/lib/types/screener'

const MARKET_CAP_RANGES = [
  { label: 'Micro Cap (<$300M)', min: 0, max: 300000000 },
  { label: 'Small Cap ($300M-$2B)', min: 300000000, max: 2000000000 },
  { label: 'Mid Cap ($2B-$10B)', min: 2000000000, max: 10000000000 },
  { label: 'Large Cap ($10B-$200B)', min: 10000000000, max: 200000000000 },
  { label: 'Mega Cap (>$200B)', min: 200000000000, max: Infinity },
]

const PRESETS = [
  { key: 'high_dividend', name: 'High Dividend', description: 'Yield > 4%, Cap > $1B' },
  { key: 'growth_stocks', name: 'Growth Stocks', description: 'P/E < 30, Cap > $500M' },
  { key: 'value_stocks', name: 'Value Stocks', description: 'P/E < 15, P/B < 1.5' },
  { key: 'momentum', name: 'Momentum', description: 'RSI < 30, Above 50-day MA' },
  { key: 'small_cap_growth', name: 'Small Cap Growth', description: 'Cap $100M-$2B' },
]

interface FilterSectionProps {
  title: string
  children: React.ReactNode
  defaultOpen?: boolean
}

function FilterSection({ title, children, defaultOpen = true }: FilterSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="border-b pb-4 last:border-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full py-2 text-left font-semibold hover:text-primary transition-colors"
      >
        <span>{title}</span>
        {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
      {isOpen && <div className="pt-2 space-y-3">{children}</div>}
    </div>
  )
}

export function ScreenerFilter() {
  const {
    filters,
    setFilter,
    removeFilter,
    clearFilters,
    runScreener,
    loading,
    selected_presets,
  } = useScreenerStore()

  const [localFilters, setLocalFilters] = useState<Partial<ScreenerRequest>>(filters)

  const updateFilter = useCallback((key: keyof ScreenerRequest, value: any) => {
    setLocalFilters((prev) => ({ ...prev, [key]: value }))
  }, [])

  const applyFilters = useCallback(() => {
    Object.entries(localFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        setFilter(key as keyof ScreenerRequest, value)
      }
    })
    runScreener()
  }, [localFilters, setFilter, runScreener])

  const activeFilterCount = Object.values(filters).filter(
    (v) => v !== undefined && v !== null && v !== ''
  ).length

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Filters
              {activeFilterCount > 0 && (
                <Badge variant="secondary">{activeFilterCount}</Badge>
              )}
            </CardTitle>
            <CardDescription>Screen stocks by criteria</CardDescription>
          </div>
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            Clear All
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 overflow-y-auto max-h-[calc(100vh-200px)]">
        {/* Quick Presets */}
        <div>
          <Label className="text-sm font-semibold mb-2 block">Quick Presets</Label>
          <div className="flex flex-wrap gap-2">
            {PRESETS.map((preset) => (
              <Badge
                key={preset.key}
                variant={selected_presets.includes(preset.key) ? 'default' : 'outline'}
                className="cursor-pointer hover:opacity-80 transition-opacity"
                title={preset.description}
              >
                {preset.name}
              </Badge>
            ))}
          </div>
        </div>

        {/* Market Cap */}
        <FilterSection title="Market Cap">
          <div className="space-y-2">
            <div className="flex gap-2">
              <Input
                type="number"
                placeholder="Min"
                value={localFilters.market_cap_min || ''}
                onChange={(e) => updateFilter('market_cap_min', e.target.value ? Number(e.target.value) : undefined)}
                aria-label="Minimum market cap"
              />
              <Input
                type="number"
                placeholder="Max"
                value={localFilters.market_cap_max || ''}
                onChange={(e) => updateFilter('market_cap_max', e.target.value ? Number(e.target.value) : undefined)}
                aria-label="Maximum market cap"
              />
            </div>
            <div className="flex flex-wrap gap-1">
              {MARKET_CAP_RANGES.slice(0, 3).map((range) => (
                <Button
                  key={range.label}
                  variant="outline"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => {
                    updateFilter('market_cap_min', range.min)
                    updateFilter('market_cap_max', range.max)
                  }}
                >
                  {range.label.split('(')[0].trim()}
                </Button>
              ))}
            </div>
          </div>
        </FilterSection>

        {/* Price */}
        <FilterSection title="Price">
          <div className="flex gap-2">
            <Input
              type="number"
              placeholder="Min"
              value={localFilters.price_min || ''}
              onChange={(e) => updateFilter('price_min', e.target.value ? Number(e.target.value) : undefined)}
              aria-label="Minimum price"
            />
            <Input
              type="number"
              placeholder="Max"
              value={localFilters.price_max || ''}
              onChange={(e) => updateFilter('price_max', e.target.value ? Number(e.target.value) : undefined)}
              aria-label="Maximum price"
            />
          </div>
        </FilterSection>

        {/* Volume */}
        <FilterSection title="Volume">
          <div className="space-y-2">
            <div className="flex gap-2">
              <Input
                type="number"
                placeholder="Min Volume"
                value={localFilters.volume_min || ''}
                onChange={(e) => updateFilter('volume_min', e.target.value ? Number(e.target.value) : undefined)}
              />
              <Input
                type="number"
                placeholder="Avg Volume"
                value={localFilters.volume_avg_min || ''}
                onChange={(e) => updateFilter('volume_avg_min', e.target.value ? Number(e.target.value) : undefined)}
              />
            </div>
          </div>
        </FilterSection>

        {/* Valuation */}
        <FilterSection title="Valuation (P/E)">
          <div className="flex gap-2">
            <Input
              type="number"
              placeholder="Min P/E"
              value={localFilters.pe_min || ''}
              onChange={(e) => updateFilter('pe_min', e.target.value ? Number(e.target.value) : undefined)}
            />
            <Input
              type="number"
              placeholder="Max P/E"
              value={localFilters.pe_max || ''}
              onChange={(e) => updateFilter('pe_max', e.target.value ? Number(e.target.value) : undefined)}
            />
          </div>
        </FilterSection>

        {/* P/B Ratio */}
        <FilterSection title="P/B Ratio">
          <div className="flex gap-2">
            <Input
              type="number"
              placeholder="Min P/B"
              value={localFilters.pb_min || ''}
              onChange={(e) => updateFilter('pb_min', e.target.value ? Number(e.target.value) : undefined)}
            />
            <Input
              type="number"
              placeholder="Max P/B"
              value={localFilters.pb_max || ''}
              onChange={(e) => updateFilter('pb_max', e.target.value ? Number(e.target.value) : undefined)}
            />
          </div>
        </FilterSection>

        {/* Dividend Yield */}
        <FilterSection title="Dividend Yield">
          <div className="space-y-2">
            <Label>Minimum Yield: {localFilters.dividend_yield_min || 0}%</Label>
            <Slider
              value={[localFilters.dividend_yield_min || 0]}
              onValueChange={([value]) => updateFilter('dividend_yield_min', value)}
              max={10}
              step={0.5}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>0%</span>
              <span>5%</span>
              <span>10%</span>
            </div>
          </div>
        </FilterSection>

        {/* Technical Indicators */}
        <FilterSection title="Technical Indicators" defaultOpen={false}>
          <div className="space-y-3">
            <div className="space-y-2">
              <Label>RSI Range</Label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  placeholder="Min"
                  min={0}
                  max={100}
                  value={localFilters.rsi_min || ''}
                  onChange={(e) => updateFilter('rsi_min', e.target.value ? Number(e.target.value) : undefined)}
                />
                <Input
                  type="number"
                  placeholder="Max"
                  min={0}
                  max={100}
                  value={localFilters.rsi_max || ''}
                  onChange={(e) => updateFilter('rsi_max', e.target.value ? Number(e.target.value) : undefined)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="above_ma_20"
                  checked={localFilters.above_ma_20 || false}
                  onCheckedChange={(checked) => updateFilter('above_ma_20', checked)}
                />
                <Label htmlFor="above_ma_20" className="text-sm cursor-pointer">
                  Above 20-day MA
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="above_ma_50"
                  checked={localFilters.above_ma_50 || false}
                  onCheckedChange={(checked) => updateFilter('above_ma_50', checked)}
                />
                <Label htmlFor="above_ma_50" className="text-sm cursor-pointer">
                  Above 50-day MA
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="above_ma_200"
                  checked={localFilters.above_ma_200 || false}
                  onCheckedChange={(checked) => updateFilter('above_ma_200', checked)}
                />
                <Label htmlFor="above_ma_200" className="text-sm cursor-pointer">
                  Above 200-day MA
                </Label>
              </div>
            </div>
          </div>
        </FilterSection>

        {/* Sector */}
        <FilterSection title="Sector" defaultOpen={false}>
          <Input
            placeholder="Enter sector..."
            value={localFilters.sector || ''}
            onChange={(e) => updateFilter('sector', e.target.value)}
          />
        </FilterSection>

        {/* Apply Button */}
        <div className="pt-4 space-y-2">
          <Button onClick={applyFilters} className="w-full" disabled={loading}>
            {loading ? 'Screening...' : 'Apply Filters'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
