# FinanceHub - Feature Implementation Guides

**Created:** January 29, 2026
**Purpose:** Detailed implementation guides for each feature from FEATURES_SPECIFICATION.md
**Usage:** Pick one feature and follow the step-by-step guide

---

## Table of Contents

1. [Universal Screener](#1-universal-screener)
2. [Advanced Charting](#2-advanced-charting)
3. [Performance Analytics Dashboard](#3-performance-analytics-dashboard)
4. [Risk Management Dashboard](#4-risk-management-dashboard)
5. [Portfolio Rebalancing Tools](#5-portfolio-rebalancing-tools)
6. [Options Trading Interface](#6-options-trading-interface)
7. [Research Tools Dashboard](#7-research-tools-dashboard)
8. [Export & Reporting System](#8-export--reporting-system)
9. [Backtesting Engine](#9-backtesting-engine)
10. [AI-Powered Features](#10-ai-powered-features)

---

## 1. Universal Screener

### Status
- **Backend:** ✅ Complete (screener app exists with full filtering)
- **Frontend:** ❌ Missing (page exists but incomplete)
- **Priority:** HIGH
- **Estimated Effort:** 2-3 weeks

### Backend Status

**Existing Files:**
```
Backend/src/
├── screener/
│   ├── api.py              # Screener endpoints
│   ├── models.py           # ScreenerPreset model
│   ├── services.py         # ScreeningService
│   └── filters.py          # Filter classes
```

**Existing Endpoints:**
- `POST /api/screener/run/` - Run screener with filters
- `GET /api/screener/presets/` - Get available presets
- `POST /api/screener/presets/` - Create custom preset
- `GET /api/screener/sectors/` - Get sector list
- `GET /api/screener/industries/` - Get industry list

### Implementation Plan

#### Step 1: Review Backend APIs

**Check existing screener API:**
```bash
cd Backend/src
python manage.py shell

# Test screener endpoint
from screener.api import screener_router
# Review available endpoints and schemas
```

#### Step 2: Create Frontend API Client

**File:** `Frontend/src/lib/api/screener.ts`

```typescript
import { apiClient } from './client'

export interface ScreenerFilter {
  field: string
  operator: string
  value: string | number
}

export interface ScreenerRequest {
  filters: ScreenerFilter[]
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  limit?: number
  offset?: number
}

export interface ScreenerResult {
  symbol: string
  name: string
  asset_type: string
  price: number
  change_percent: number
  volume: number
  market_cap: number
  pe_ratio?: number
  dividend_yield?: number
  sector?: string
  industry?: string
}

export const screenerApi = {
  runScreener: async (request: ScreenerRequest): Promise<ScreenerResult[]> => {
    return apiClient.post('/screener/run/', request)
  },

  getPresets: async () => {
    return apiClient.get('/screener/presets/')
  },

  createPreset: async (name: string, filters: ScreenerFilter[]) => {
    return apiClient.post('/screener/presets/', { name, filters })
  },

  getSectors: async () => {
    return apiClient.get('/screener/sectors/')
  },

  getIndustries: async () => {
    return apiClient.get('/screener/industries/')
  }
}
```

#### Step 3: Create Types

**File:** `Frontend/src/lib/types/screener.ts`

```typescript
export interface ScreenerFilter {
  id: string
  field: string
  operator: string
  value: string | number
  label?: string
}

export interface ScreenerPreset {
  id: string
  name: string
  description?: string
  filters: ScreenerFilter[]
  is_public: boolean
  created_at: string
}

export interface ScreenerField {
  name: string
  label: string
  type: 'text' | 'number' | 'select' | 'multiselect'
  operators: string[]
  options?: { value: string; label: string }[]
  placeholder?: string
}

export interface ScreenerResult {
  symbol: string
  name: string
  asset_type: 'stock' | 'etf' | 'crypto' | 'index'
  price: number
  change_percent: number
  volume: number
  market_cap: number
  pe_ratio?: number
  pb_ratio?: number
  dividend_yield?: number
  eps?: number
  beta?: number
  sector?: string
  industry?: string
  country?: string
  exchange?: string
}
```

#### Step 4: Create Screener Store

**File:** `Frontend/src/stores/screenerStore.ts`

```typescript
import { create } from 'zustand'
import { ScreenerFilter, ScreenerResult, ScreenerPreset } from '@/lib/types/screener'
import { screenerApi } from '@/lib/api/screener'

interface ScreenerState {
  filters: ScreenerFilter[]
  results: ScreenerResult[]
  presets: ScreenerPreset[]
  loading: boolean
  error: string | null
  selectedPreset: string | null

  addFilter: (filter: ScreenerFilter) => void
  removeFilter: (filterId: string) => void
  updateFilter: (filterId: string, updates: Partial<ScreenerFilter>) => void
  clearFilters: () => void
  runScreener: () => Promise<void>
  loadPresets: () => Promise<void>
  savePreset: (name: string) => Promise<void>
  loadPreset: (presetId: string) => void
}

export const useScreenerStore = create<ScreenerState>((set, get) => ({
  filters: [],
  results: [],
  presets: [],
  loading: false,
  error: null,
  selectedPreset: null,

  addFilter: (filter) => {
    set((state) => ({
      filters: [...state.filters, { ...filter, id: crypto.randomUUID() }]
    }))
  },

  removeFilter: (filterId) => {
    set((state) => ({
      filters: state.filters.filter((f) => f.id !== filterId)
    }))
  },

  updateFilter: (filterId, updates) => {
    set((state) => ({
      filters: state.filters.map((f) =>
        f.id === filterId ? { ...f, ...updates } : f
      )
    }))
  },

  clearFilters: () => {
    set({ filters: [], results: [] })
  },

  runScreener: async () => {
    set({ loading: true, error: null })
    try {
      const { filters } = get()
      const request = {
        filters: filters.map(({ id, ...f }) => f),
        limit: 100
      }
      const results = await screenerApi.runScreener(request)
      set({ results, loading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to run screener',
        loading: false
      })
    }
  },

  loadPresets: async () => {
    try {
      const presets = await screenerApi.getPresets()
      set({ presets })
    } catch (error) {
      console.error('Failed to load presets:', error)
    }
  },

  savePreset: async (name) => {
    try {
      const { filters } = get()
      await screenerApi.createPreset(name, filters)
      await get().loadPresets()
    } catch (error) {
      console.error('Failed to save preset:', error)
    }
  },

  loadPreset: (presetId) => {
    const preset = get().presets.find((p) => p.id === presetId)
    if (preset) {
      set({
        filters: preset.filters.map((f) => ({ ...f, id: crypto.randomUUID() })),
        selectedPreset: presetId
      })
    }
  }
}))
```

#### Step 5: Create Screener Components

**File:** `Frontend/src/components/screener/ScreenerFilters.tsx`

```typescript
'use client'

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Trash2, Plus } from 'lucide-react'
import { useScreenerStore } from '@/stores/screenerStore'
import { SCREENER_FIELDS } from '@/lib/constants/screener'

export function ScreenerFilters() {
  const { filters, addFilter, removeFilter, updateFilter, clearFilters } = useScreenerStore()

  const addNewFilter = () => {
    addFilter({
      id: crypto.randomUUID(),
      field: '',
      operator: '',
      value: ''
    })
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Filters</h3>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={clearFilters}>
            Clear All
          </Button>
          <Button size="sm" onClick={addNewFilter}>
            <Plus className="w-4 h-4 mr-2" />
            Add Filter
          </Button>
        </div>
      </div>

      <div className="space-y-4">
        {filters.map((filter, index) => {
          const fieldConfig = SCREENER_FIELDS[filter.field]

          return (
            <div key={filter.id} className="flex gap-2 items-start">
              <div className="flex-1">
                <Label className="sr-only">Field</Label>
                <Select
                  value={filter.field}
                  onValueChange={(value) => updateFilter(filter.id, { field: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select field" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(SCREENER_FIELDS).map(([key, field]) => (
                      <SelectItem key={key} value={key}>
                        {field.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex-1">
                <Label className="sr-only">Operator</Label>
                <Select
                  value={filter.operator}
                  onValueChange={(value) => updateFilter(filter.id, { operator: value })}
                  disabled={!fieldConfig}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Operator" />
                  </SelectTrigger>
                  <SelectContent>
                    {fieldConfig?.operators.map((op) => (
                      <SelectItem key={op} value={op}>
                        {op}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex-1">
                <Label className="sr-only">Value</Label>
                {fieldConfig?.type === 'select' ? (
                  <Select
                    value={filter.value as string}
                    onValueChange={(value) => updateFilter(filter.id, { value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select value" />
                    </SelectTrigger>
                    <SelectContent>
                      {fieldConfig.options?.map((opt) => (
                        <SelectItem key={opt.value} value={opt.value}>
                          {opt.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Input
                    type={fieldConfig?.type === 'number' ? 'number' : 'text'}
                    value={filter.value as string}
                    onChange={(e) => updateFilter(filter.id, { value: e.target.value })}
                    placeholder={fieldConfig?.placeholder || 'Enter value'}
                    disabled={!fieldConfig}
                  />
                )}
              </div>

              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeFilter(filter.id)}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          )
        })}

        {filters.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <p>No filters added yet. Click "Add Filter" to get started.</p>
          </div>
        )}
      </div>
    </Card>
  )
}
```

**File:** `Frontend/src/lib/constants/screener.ts`

```typescript
export const SCREENER_FIELDS = {
  market_cap: {
    name: 'market_cap',
    label: 'Market Cap',
    type: 'select',
    operators: ['>', '<', '>=', '<=', '='],
    options: [
      { value: 'mega', label: 'Mega Cap ($200B+)' },
      { value: 'large', label: 'Large Cap ($10B-$200B)' },
      { value: 'mid', label: 'Mid Cap ($2B-$10B)' },
      { value: 'small', label: 'Small Cap ($300M-$2B)' },
      { value: 'micro', label: 'Micro Cap ($50M-$300M)' },
      { value: 'nano', label: 'Nano Cap (<$50M)' }
    ]
  },
  pe_ratio: {
    name: 'pe_ratio',
    label: 'P/E Ratio',
    type: 'number',
    operators: ['>', '<', '>=', '<=', '=', 'between'],
    placeholder: 'Enter P/E ratio'
  },
  dividend_yield: {
    name: 'dividend_yield',
    label: 'Dividend Yield',
    type: 'number',
    operators: ['>', '<', '>=', '<=', '='],
    placeholder: 'Enter yield %'
  },
  sector: {
    name: 'sector',
    label: 'Sector',
    type: 'select',
    operators: ['=', '!='],
    options: [
      { value: 'Technology', label: 'Technology' },
      { value: 'Healthcare', label: 'Healthcare' },
      { value: 'Financials', label: 'Financials' },
      { value: 'Consumer Discretionary', label: 'Consumer Discretionary' },
      { value: 'Consumer Staples', label: 'Consumer Staples' },
      { value: 'Energy', label: 'Energy' },
      { value: 'Utilities', label: 'Utilities' },
      { value: 'Real Estate', label: 'Real Estate' },
      { value: 'Materials', label: 'Materials' },
      { value: 'Industrials', label: 'Industrials' },
      { value: 'Communication Services', label: 'Communication Services' }
    ]
  },
  industry: {
    name: 'industry',
    label: 'Industry',
    type: 'select',
    operators: ['=', '!='],
    options: [] // Load dynamically from API
  },
  beta: {
    name: 'beta',
    label: 'Beta',
    type: 'number',
    operators: ['>', '<', '>=', '<=', '='],
    placeholder: 'Enter beta value'
  },
  volume: {
    name: 'volume',
    label: 'Volume',
    type: 'number',
    operators: ['>', '<', '>=', '<<='],
    placeholder: 'Enter volume'
  },
  price: {
    name: 'price',
    label: 'Price',
    type: 'number',
    operators: ['>', '<', '>=', '<<=', 'between'],
    placeholder: 'Enter price range'
  }
}
```

#### Step 6: Create Screener Results Component

**File:** `Frontend/src/components/screener/ScreenerResults.tsx`

```typescript
'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { useScreenerStore } from '@/stores/screenerStore'
import { useRouter } from 'next/navigation'
import { formatNumber, formatPercent } from '@/lib/utils/format'

export function ScreenerResults() {
  const { results, loading } = useScreenerStore()
  const router = useRouter()

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center py-8">Loading results...</div>
        </CardContent>
      </Card>
    )
  }

  if (results.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center py-8 text-muted-foreground">
            <p>No results yet. Add filters and run the screener.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Results ({results.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Symbol</TableHead>
              <TableHead>Name</TableHead>
              <TableHead className="text-right">Price</TableHead>
              <TableHead className="text-right">Change</TableHead>
              <TableHead className="text-right">Volume</TableHead>
              <TableHead className="text-right">Market Cap</TableHead>
              <TableHead className="text-right">P/E</TableHead>
              <TableHead>Sector</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {results.map((result) => (
              <TableRow
                key={result.symbol}
                className="cursor-pointer hover:bg-muted/50"
                onClick={() => router.push(`/assets/${result.symbol}`)}
              >
                <TableCell className="font-medium">{result.symbol}</TableCell>
                <TableCell>{result.name}</TableCell>
                <TableCell className="text-right">
                  ${result.price?.toFixed(2) || 'N/A'}
                </TableCell>
                <TableCell className="text-right">
                  <span className={result.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {formatPercent(result.change_percent)}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  {formatNumber(result.volume)}
                </TableCell>
                <TableCell className="text-right">
                  {formatNumber(result.market_cap)}
                </TableCell>
                <TableCell className="text-right">
                  {result.pe_ratio?.toFixed(2) || 'N/A'}
                </TableCell>
                <TableCell>
                  {result.sector && <Badge variant="secondary">{result.sector}</Badge>}
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm">
                    View
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
```

#### Step 7: Create Screener Page

**File:** `Frontend/src/app/(dashboard)/screener/page.tsx`

```typescript
'use client'

import { Suspense } from 'react'
import { ScreenerFilters } from '@/components/screener/ScreenerFilters'
import { ScreenerResults } from '@/components/screener/ScreenerResults'
import { Button } from '@/components/ui/button'
import { useScreenerStore } from '@/stores/screenerStore'
import { Loader2 } from 'lucide-react'

export default function ScreenerPage() {
  const { runScreener, loading, filters } = useScreenerStore()

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Stock Screener</h1>
          <p className="text-muted-foreground">
            Find stocks that match your investment criteria
          </p>
        </div>
        <Button
          onClick={runScreener}
          disabled={filters.length === 0 || loading}
          size="lg"
        >
          {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
          Run Screener
        </Button>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScreenerFilters />
        </div>
        <div className="lg:col-span-2">
          <Suspense fallback={<div>Loading...</div>}>
            <ScreenerResults />
          </Suspense>
        </div>
      </div>
    </div>
  )
}
```

#### Step 8: Add Presets Sidebar

**File:** `Frontend/src/components/screener/ScreenerPresets.tsx`

```typescript
'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Bookmark, Star, TrendingUp, TrendingDown } from 'lucide-react'
import { useScreenerStore } from '@/stores/screenerStore'

const PRESETS = [
  {
    id: 'value-stocks',
    name: 'Value Stocks',
    description: 'Low P/E, high dividend yield',
    icon: TrendingDown,
    filters: [
      { field: 'pe_ratio', operator: '<=', value: 15 },
      { field: 'dividend_yield', operator: '>=', value: 3 }
    ]
  },
  {
    id: 'growth-stocks',
    name: 'Growth Stocks',
    description: 'High P/E, high beta',
    icon: TrendingUp,
    filters: [
      { field: 'pe_ratio', operator: '>', value: 25 },
      { field: 'beta', operator: '>', value: 1.2 }
    ]
  },
  {
    id: 'dividend-aristocrats',
    name: 'Dividend Aristocrats',
    description: 'High dividend yield, stable',
    icon: Star,
    filters: [
      { field: 'dividend_yield', operator: '>=', value: 4 },
      { field: 'beta', operator: '<=', value: 0.8 }
    ]
  }
]

export function ScreenerPresets() {
  const { loadPreset, presets } = useScreenerStore()

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bookmark className="w-5 h-5" />
          Presets
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px]">
          <div className="space-y-2">
            {PRESETS.map((preset) => {
              const Icon = preset.icon
              return (
                <button
                  key={preset.id}
                  onClick={() => loadPreset(preset.id)}
                  className="w-full text-left p-3 rounded-lg hover:bg-muted transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <Icon className="w-5 h-5 mt-0.5 text-primary" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{preset.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {preset.description}
                      </p>
                    </div>
                  </div>
                </button>
              )
            })}

            {presets.map((preset) => (
              <button
                key={preset.id}
                onClick={() => loadPreset(preset.id)}
                className="w-full text-left p-3 rounded-lg hover:bg-muted transition-colors"
              >
                <div className="flex items-start gap-3">
                  <Bookmark className="w-5 h-5 mt-0.5 text-primary" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{preset.name}</p>
                    <p className="text-sm text-muted-foreground">
                      Custom preset
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
```

### Testing

```bash
# Frontend
cd Frontend/src
npm run dev

# Visit http://localhost:3000/screener

# Test:
1. Add filters (market cap, P/E ratio, sector)
2. Run screener
3. View results
4. Click on symbol to navigate to asset detail
5. Save custom preset
6. Load preset
```

---

## 2. Advanced Charting

### Status
- **Backend:** ✅ Complete (technical indicators API exists)
- **Frontend:** 🔄 Partial (RealTimeChart exists, needs enhancement)
- **Priority:** HIGH
- **Estimated Effort:** 3-4 weeks

### Backend Status

**Existing Files:**
```
Backend/src/
├── data/processing/
│   └── technical_indicators.py  # 10+ indicators implemented
├── assets/api.py                 # Historical prices endpoint
```

**Existing Endpoints:**
- `GET /api/assets/{symbol}/history/` - Historical OHLCV data
- `GET /api/market/{symbol}/indicators/` - Technical indicators

### Implementation Plan

#### Step 1: Upgrade Charting Library

**Install dependencies:**
```bash
cd Frontend/src
npm install lightweight-charts
npm install financial-charts  # If budget allows
npm install react-financial-charts
```

#### Step 2: Create Advanced Chart Component

**File:** `Frontend/src/components/charts/AdvancedChart.tsx`

```typescript
'use client'

import { useEffect, useRef, useState } from 'react'
import { createChart, IChartApi, ISeriesApi, ColorType } from 'lightweight-charts'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { Loader2 } from 'lucide-react'
import { assetsApi } from '@/lib/api/assets'

interface AdvancedChartProps {
  symbol: string
  height?: number
}

type ChartType = 'line' | 'candlestick' | 'bar' | 'area'
type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w' | '1M'

export function AdvancedChart({ symbol, height = 500 }: AdvancedChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | ISeriesApi<'Line'> | null>(null)

  const [chartType, setChartType] = useState<ChartType>('candlestick')
  const [timeframe, setTimeframe] = useState<Timeframe>('1d')
  const [loading, setLoading] = useState(true)
  const [showIndicators, setShowIndicators] = useState<string[]>([])

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height,
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#e1e1e1' },
        horzLines: { color: '#e1e1e1' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#cccccc',
      },
      timeScale: {
        borderColor: '#cccccc',
        timeVisible: true,
        secondsVisible: false,
      },
    })

    chartRef.current = chart

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [height])

  // Load data
  useEffect(() => {
    const loadData = async () => {
      if (!chartRef.current) return

      setLoading(true)
      try {
        const history = await assetsApi.getHistory(symbol, {
          timeframe,
          limit: 500
        })

        // Remove existing series
        if (seriesRef.current) {
          chartRef.current.removeSeries(seriesRef.current)
        }

        // Add new series based on chart type
        if (chartType === 'candlestick') {
          const candlestickSeries = chartRef.current.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
          })

          candlestickSeries.setData(
            history.map((d) => ({
              time: d.date as any,
              open: d.open,
              high: d.high,
              low: d.low,
              close: d.close,
            }))
          )

          seriesRef.current = candlestickSeries
        } else if (chartType === 'line' || chartType === 'area') {
          const lineSeries = chartRef.current.addLineSeries({
            color: '#2962ff',
            lineWidth: 2,
          })

          lineSeries.setData(
            history.map((d) => ({
              time: d.date as any,
              value: d.close,
            }))
          )

          seriesRef.current = lineSeries
        } else if (chartType === 'bar') {
          const barSeries = chartRef.current.addBarSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
          })

          barSeries.setData(
            history.map((d) => ({
              time: d.date as any,
              open: d.open,
              high: d.high,
              low: d.low,
              close: d.close,
            }))
          )

          seriesRef.current = barSeries
        }

        // Fit content
        chartRef.current.timeScale().fitContent()

        setLoading(false)
      } catch (error) {
        console.error('Failed to load chart data:', error)
        setLoading(false)
      }
    }

    loadData()
  }, [symbol, timeframe, chartType])

  // Add indicators
  useEffect(() => {
    const loadIndicators = async () => {
      if (!chartRef.current || showIndicators.length === 0) return

      try {
        const indicators = await assetsApi.getIndicators(symbol, {
          indicators: showIndicators,
          timeframe,
          limit: 500
        })

        // Add indicator series
        Object.entries(indicators).forEach(([name, data]) => {
          if (name === 'volume' && chartRef.current) {
            const volumeSeries = chartRef.current.addHistogramSeries({
              color: '#26a69a',
              priceFormat: {
                type: 'volume',
              },
              priceScaleId: '',
            })

            volumeSeries.priceScale().applyOptions({
              scaleMargins: {
                top: 0.8,
                bottom: 0,
              },
            })

            volumeSeries.setData(
              (data as any[]).map((d) => ({
                time: d.date as any,
                value: d.volume,
                color: d.close > d.open ? '#26a69a80' : '#ef535080',
              }))
            )
          } else if ((name === 'sma' || name === 'ema') && chartRef.current) {
            const maSeries = chartRef.current.addLineSeries({
              color: name === 'sma' ? '#ff9800' : '#2196f3',
              lineWidth: 1,
            })

            maSeries.setData(
              (data as any[]).map((d) => ({
                time: d.date as any,
                value: d.value,
              }))
            )
          }
        })
      } catch (error) {
        console.error('Failed to load indicators:', error)
      }
    }

    loadIndicators()
  }, [showIndicators, symbol, timeframe])

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center">
        <Select value={chartType} onValueChange={(v) => setChartType(v as ChartType)}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Chart type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="candlestick">Candlestick</SelectItem>
            <SelectItem value="line">Line</SelectItem>
            <SelectItem value="bar">Bar</SelectItem>
            <SelectItem value="area">Area</SelectItem>
          </SelectContent>
        </Select>

        <Select value={timeframe} onValueChange={(v) => setTimeframe(v as Timeframe)}>
          <SelectTrigger className="w-[120px]">
            <SelectValue placeholder="Timeframe" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1m">1 Min</SelectItem>
            <SelectItem value="5m">5 Min</SelectItem>
            <SelectItem value="15m">15 Min</SelectItem>
            <SelectItem value="1h">1 Hour</SelectItem>
            <SelectItem value="4h">4 Hour</SelectItem>
            <SelectItem value="1d">1 Day</SelectItem>
            <SelectItem value="1w">1 Week</SelectItem>
            <SelectItem value="1M">1 Month</SelectItem>
          </SelectContent>
        </Select>

        <ToggleGroup
          type="multiple"
          value={showIndicators}
          onValueChange={setShowIndicators}
        >
          <ToggleGroupItem value="sma">SMA</ToggleGroupItem>
          <ToggleGroupItem value="ema">EMA</ToggleGroupItem>
          <ToggleGroupItem value="volume">Volume</ToggleGroupItem>
          <ToggleGroupItem value="bb">Bollinger</ToggleGroupItem>
        </ToggleGroup>

        {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      </div>

      {/* Chart */}
      <div ref={chartContainerRef} className="rounded-lg border overflow-hidden" />
    </div>
  )
}
```

#### Step 3: Integrate into Asset Detail Page

**File:** `Frontend/src/app/(dashboard)/assets/[symbol]/page.tsx`

```typescript
'use client'

import { AdvancedChart } from '@/components/charts/AdvancedChart'
import { OrderBook } from '@/components/realtime/OrderBook'
import { TradeFeed } from '@/components/realtime/TradeFeed'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function AssetDetailPage({ params }: { params: { symbol: string } }) {
  const symbol = params.symbol.toUpperCase()

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{symbol}</h1>
        <p className="text-muted-foreground">Asset details and analysis</p>
      </div>

      <Tabs defaultValue="chart" className="space-y-4">
        <TabsList>
          <TabsTrigger value="chart">Chart</TabsTrigger>
          <TabsTrigger value="orderbook">Order Book</TabsTrigger>
          <TabsTrigger value="trades">Trades</TabsTrigger>
          <TabsTrigger value="fundamentals">Fundamentals</TabsTrigger>
        </TabsList>

        <TabsContent value="chart">
          <AdvancedChart symbol={symbol} />
        </TabsContent>

        <TabsContent value="orderbook">
          <OrderBook symbol={symbol} />
        </TabsContent>

        <TabsContent value="trades">
          <TradeFeed symbol={symbol} />
        </TabsContent>

        <TabsContent value="fundamentals">
          {/* Fundamentals content */}
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

### Testing

```bash
# Frontend
cd Frontend/src
npm run dev

# Visit http://localhost:3000/assets/AAPL

# Test:
1. Change chart types (candlestick, line, bar, area)
2. Change timeframes (1m, 5m, 1h, 1d, 1w)
3. Toggle indicators (SMA, EMA, Volume, Bollinger)
4. Verify data loads correctly
5. Check responsiveness
```

---

## 3. Performance Analytics Dashboard

### Status
- **Backend:** ✅ Complete (analytics API exists)
- **Frontend:** 🔄 Partial (components created, incomplete integration)
- **Priority:** HIGH
- **Estimated Effort:** 4-5 weeks

### Implementation Plan Summary

1. **Complete analytics dashboard** with all sections:
   - Performance metrics (total return, CAGR, Sharpe, Sortino)
   - Risk metrics (drawdown, volatility, beta)
   - Allocation breakdown (sector, asset class, geographic)
   - Attribution analysis

2. **Add export functionality** for all data formats

3. **Implement correlation matrix** visualization

4. **Create rolling returns** analysis

(See IMPLEMENTATION_ROADMAP.md for detailed breakdown)

---

## Summary

This document provides detailed implementation guides for the first 2 high-priority features. Each guide includes:

1. **Status assessment** - What exists vs what's needed
2. **Backend review** - Existing APIs and models
3. **Frontend implementation** - Step-by-step code
4. **Testing instructions** - How to verify

**Recommended starting order:**
1. ✅ **Universal Screener** (2-3 weeks) - High impact, backend ready
2. ✅ **Advanced Charting** (3-4 weeks) - Core feature, high demand
3. **Performance Analytics** (4-5 weeks) - Completes portfolio story
4. **Risk Management** (6-8 weeks) - Professional feature

---

**Next Steps:**
1. Choose feature to implement
2. Follow the detailed guide
3. Test thoroughly
4. Deploy to staging
5. Gather user feedback

**Last Updated:** January 29, 2026
