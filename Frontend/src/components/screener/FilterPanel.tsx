'use client'

import { useEffect, useCallback, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Filter,
  Loader2,
  Plus,
  RotateCcw,
  Play,
  RefreshCw,
  Star,
  Save,
  Download,
  Upload,
  Trash2,
  Edit2,
  Check,
  X,
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  BarChart3,
  Zap,
  Building2,
  Percent,
  Cpu,
  TrendingUpIcon,
  ArrowUpDown,
  Share2,
  LineChart,
  Leaf,
  Search,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import { FilterRow } from './FilterRow'
import { useScreenerStore } from '@/stores/screenerStore'
import { SCREENER_CATEGORIES, SCREENER_PRESETS, type FilterCategory, type FilterDefinition } from '@/lib/constants/screener'
import { cn } from '@/lib/utils'

const SECTOR_QUICK_FILTERS = [
  'Technology', 'Healthcare', 'Financials', 'Consumer Discretionary',
  'Communication Services', 'Industrials', 'Consumer Staples',
  'Energy', 'Utilities', 'Real Estate', 'Materials'
]

const TECHNICAL_QUICK_FILTERS = [
  { label: 'RSI Oversold', key: 'rsi', value: 30, operator: '<' },
  { label: 'RSI Overbought', key: 'rsi', value: 70, operator: '>' },
  { label: 'MA Golden Cross', key: 'ma_50_200', value: 'above', operator: '=' },
  { label: 'High Volume', key: 'volume', value: 2000000, operator: '>' },
  { label: 'Near 52W High', key: 'price_vs_52w_high', value: 95, operator: '>' },
  { label: 'Near 52W Low', key: 'price_vs_52w_low', value: 105, operator: '<' },
]

interface SavePresetDialogProps {
  onSave: (name: string) => void
  existingPresets: { id: string; name: string }[]
}

function SavePresetDialog({ onSave, existingPresets }: SavePresetDialogProps) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [error, setError] = useState('')

  const handleSave = () => {
    if (!name.trim()) {
      setError('Please enter a preset name')
      return
    }
    if (existingPresets.some(p => p.name.toLowerCase() === name.toLowerCase())) {
      setError('A preset with this name already exists')
      return
    }
    onSave(name)
    setOpen(false)
    setName('')
    setError('')
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="w-full">
          <Save className="h-3 w-3 mr-1" />
          Save Current as Preset
        </Button>
      </DialogTrigger>
      <DialogContent className="border-2 border-foreground rounded-none shadow-[8px_8px_0px_0px_var(--foreground)]">
        <DialogHeader>
          <DialogTitle className="font-black uppercase italic">Save_Preset</DialogTitle>
          <DialogDescription>Save your current filter configuration as a preset</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="preset-name" className="font-bold uppercase text-xs">Preset Name</Label>
            <Input
              id="preset-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My Custom Filter"
              className="border-foreground"
            />
            {error && <p className="text-red-600 text-xs font-bold">{error}</p>}
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)} className="border-foreground">
            <X className="h-4 w-4 mr-1" />
            Cancel
          </Button>
          <Button onClick={handleSave} className="bg-foreground text-background hover:bg-foreground/90">
            <Check className="h-4 w-4 mr-1" />
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export function FilterPanel() {
  const {
    selectedFilters,
    addFilter,
    clearFilters,
    runScreener,
    loading,
    loadPresets,
    applyPreset,
    autoRefresh,
    setAutoRefresh,
    saveCustomPreset,
    customPresets,
    deleteCustomPreset,
    sortBy,
    sortOrder,
    setSort,
  } = useScreenerStore()

  const [showAdvanced, setShowAdvanced] = useState(false)
  const [activeTab, setActiveTab] = useState('filters')

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

  const handleSavePreset = useCallback((name: string) => {
    saveCustomPreset(name, selectedFilters)
  }, [saveCustomPreset, selectedFilters])

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

  const handleTechnicalQuickFilter = useCallback((filter: { key: string; value: any; operator: string }) => {
    const exists = selectedFilters.some(f => f.key === filter.key && f.value === filter.value)
    if (!exists) {
      addFilter(filter)
    }
  }, [addFilter, selectedFilters])

  return (
    <div className="space-y-4">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="w-full border-2 border-foreground bg-background grid grid-cols-4">
          <TabsTrigger
            value="filters"
            className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs"
          >
            <Filter className="h-4 w-4 mr-1" />
            Filters
          </TabsTrigger>
          <TabsTrigger
            value="browse"
            className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs"
          >
            <Search className="h-4 w-4 mr-1" />
            Browse
          </TabsTrigger>
          <TabsTrigger
            value="presets"
            className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs"
          >
            <Star className="h-4 w-4 mr-1" />
            Presets
          </TabsTrigger>
          <TabsTrigger
            value="quick"
            className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs"
          >
            <Zap className="h-4 w-4 mr-1" />
            Quick
          </TabsTrigger>
        </TabsList>

        <TabsContent value="filters" className="space-y-4">
          <Card className="border-2 border-foreground">
            <CardHeader className="pb-3 border-b-2 border-foreground bg-muted/30">
              <CardTitle className="text-base flex items-center gap-2">
                <Filter className="h-4 w-4" aria-hidden="true" />
                Active Filters
              </CardTitle>
              {selectedFilters.length > 0 && (
                <CardDescription>{selectedFilters.length} filter(s) applied</CardDescription>
              )}
            </CardHeader>
            <CardContent className="space-y-3 pt-4">
              {selectedFilters.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4 font-medium">
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
                  className="border-foreground/20 hover:bg-destructive/10"
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
                  className="border-foreground/20"
                >
                  <Plus className="h-3 w-3 mr-1" aria-hidden="true" />
                  Add Filter
                </Button>
                <Button
                  size="sm"
                  onClick={handleRunScreener}
                  disabled={loading || selectedFilters.length === 0}
                  className="ml-auto bg-foreground text-background hover:bg-foreground/90"
                  aria-label="Run screener with current filters"
                >
                  {loading ? (
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" aria-hidden="true" />
                  ) : (
                    <Play className="h-3 w-3 mr-1" aria-hidden="true" />
                  )}
                  Run Screener
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-foreground">
            <CardHeader className="pb-3 border-b-2 border-foreground bg-muted/30">
              <CardTitle className="text-base">Sort Results</CardTitle>
              <CardDescription>Order your screening results</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="flex gap-2">
                <div className="flex-1 space-y-2">
                  <Label className="text-xs font-bold uppercase">Sort By</Label>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { key: 'market_cap', label: 'Market Cap', icon: BarChart3 },
                      { key: 'price', label: 'Price', icon: Activity },
                      { key: 'change_percent', label: 'Change %', icon: TrendingUp },
                      { key: 'pe_ratio', label: 'P/E', icon: Percent },
                      { key: 'dividend_yield', label: 'Dividend', icon: Target },
                      { key: 'volume', label: 'Volume', icon: Zap },
                    ].map(option => (
                      <Button
                        key={option.key}
                        variant={sortBy === option.key ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setSort(option.key, sortOrder)}
                        className={cn(
                          'text-xs font-bold uppercase',
                          sortBy === option.key && 'bg-foreground text-background'
                        )}
                      >
                        <option.icon className="h-3 w-3 mr-1" />
                        {option.label}
                      </Button>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs font-bold uppercase">Order</Label>
                  <div className="flex flex-col gap-2">
                    <Button
                      variant={sortOrder === 'desc' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSort(sortBy, 'desc')}
                      className={cn(sortOrder === 'desc' && 'bg-foreground text-background')}
                    >
                      <TrendingDown className="h-3 w-3 mr-1" />
                      Descending
                    </Button>
                    <Button
                      variant={sortOrder === 'asc' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSort(sortBy, 'asc')}
                      className={cn(sortOrder === 'asc' && 'bg-foreground text-background')}
                    >
                      <TrendingUp className="h-3 w-3 mr-1" />
                      Ascending
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="presets" className="space-y-4">
          <Card className="border-2 border-foreground">
            <CardHeader className="pb-3 border-b-2 border-foreground bg-muted/30">
              <CardTitle className="text-base flex items-center gap-2">
                <Star className="h-4 w-4" />
                Built-in Presets
              </CardTitle>
              <CardDescription>Common screening criteria</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="grid grid-cols-1 gap-2" role="list" aria-label="Filter presets">
                {SCREENER_PRESETS.map(preset => (
                  <Button
                    key={preset.id}
                    variant="outline"
                    size="sm"
                    className="justify-start h-auto py-3 border-foreground/20 hover:bg-primary/10 hover:border-foreground"
                    onClick={() => applyPreset(preset.id)}
                    disabled={loading}
                    role="listitem"
                    aria-label={`Apply ${preset.name}: ${preset.description}`}
                  >
                    <div className="flex items-center gap-3 w-full">
                      <div className="h-8 w-8 bg-primary/10 flex items-center justify-center border border-foreground/20">
                        <Cpu className="h-4 w-4" />
                      </div>
                      <div className="text-left flex-1">
                        <div className="font-black uppercase text-sm">{preset.name}</div>
                        <div className="text-xs text-muted-foreground font-mono">{preset.description}</div>
                      </div>
                      <ArrowUpDown className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-foreground">
            <CardHeader className="pb-3 border-b-2 border-foreground bg-muted/30">
              <CardTitle className="text-base flex items-center gap-2">
                <Save className="h-4 w-4" />
                Custom Presets
              </CardTitle>
              <CardDescription>Your saved filter configurations</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              {customPresets.length === 0 ? (
                <div className="text-center py-8">
                  <Save className="h-12 w-12 mx-auto text-muted-foreground/50 mb-2" />
                  <p className="font-black uppercase text-muted-foreground text-sm">No Custom Presets</p>
                  <p className="text-xs text-muted-foreground font-mono mt-1">Save your filters to access them quickly</p>
                </div>
              ) : (
                <div className="space-y-2" role="list" aria-label="Custom presets">
                  {customPresets.map(preset => (
                    <div
                      key={preset.id}
                      className="flex items-center justify-between p-3 border-2 border-foreground/20 hover:border-foreground transition-all"
                    >
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => applyPreset(preset.id)}
                          className="justify-start h-auto py-1 font-bold uppercase text-sm"
                        >
                          <Star className="h-4 w-4 mr-1" />
                          {preset.name}
                        </Button>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteCustomPreset(preset.id)}
                        className="text-destructive hover:bg-destructive/10"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
              <div className="mt-4 pt-4 border-t-2 border-foreground/20">
                <SavePresetDialog
                  onSave={handleSavePreset}
                  existingPresets={customPresets}
                />
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-foreground">
            <CardHeader className="pb-3 border-b-2 border-foreground bg-muted/30">
              <CardTitle className="text-base flex items-center gap-2">
                <Download className="h-4 w-4" />
                Export / Import
              </CardTitle>
              <CardDescription>Save or share your filter configurations</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="grid grid-cols-2 gap-2">
                <Button variant="outline" size="sm" className="border-foreground/20">
                  <Download className="h-3 w-3 mr-1" />
                  Export Filters
                </Button>
                <Button variant="outline" size="sm" className="border-foreground/20">
                  <Upload className="h-3 w-3 mr-1" />
                  Import Filters
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="browse" className="space-y-4">
          <Card className="border-2 border-foreground">
            <CardHeader className="pb-3 border-b-2 border-foreground bg-muted/30">
              <CardTitle className="text-base flex items-center gap-2">
                <Search className="h-4 w-4" />
                Browse All Filters
              </CardTitle>
              <CardDescription>Click to add filters from any category</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <ScrollArea className="h-[500px] pr-3">
                <div className="space-y-4">
                  {SCREENER_CATEGORIES.map((category) => {
                    const categoryFilters = SCREENER_CATEGORIES.find(c => c.id === category.id)?.filters || []
                    return (
                      <div key={category.id} className="border-2 border-foreground/20 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-3">
                          <Badge variant="outline" className="border-foreground">
                            {category.name}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {categoryFilters.length} filter{categoryFilters.length !== 1 ? 's' : ''}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          {categoryFilters.map((filter) => {
                            const isActive = selectedFilters.some(f => f.key === filter.key)
                            return (
                              <Button
                                key={filter.key}
                                variant={isActive ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => {
                                  if (isActive) {
                                    const idx = selectedFilters.findIndex(f => f.key === filter.key)
                                    if (idx >= 0) {
                                      const { removeFilter } = useScreenerStore.getState()
                                      removeFilter(idx)
                                    }
                                  } else {
                                    addFilter({
                                      key: filter.key,
                                      value: '',
                                      operator: filter.operators[0] || '=',
                                      label: filter.label
                                    })
                                  }
                                }}
                                className={cn(
                                  'justify-start h-auto py-2 px-3 text-xs',
                                  isActive && 'bg-foreground text-background'
                                )}
                              >
                                <Filter className="h-3 w-3 mr-2" />
                                {filter.label}
                                {isActive && <Check className="h-3 w-3 ml-auto" />}
                              </Button>
                            )
                          })}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="quick" className="space-y-4">
          <Card className="border-2 border-foreground">
            <CardHeader className="pb-3 border-b-2 border-foreground bg-muted/30">
              <CardTitle className="text-base flex items-center gap-2">
                <Zap className="h-4 w-4" />
                Technical Quick Filters
              </CardTitle>
              <CardDescription>Click to apply common technical criteria</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="grid grid-cols-2 gap-2" role="list" aria-label="Technical quick filters">
                {TECHNICAL_QUICK_FILTERS.map((filter, idx) => {
                  const isActive = selectedFilters.some(f => f.key === filter.key && f.value === filter.value)
                  return (
                    <Badge
                      key={idx}
                      variant={isActive ? 'default' : 'outline'}
                      className={cn(
                        'cursor-pointer justify-start py-3 px-4 border-2 transition-all hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[4px_4px_0px_0px_var(--foreground)]',
                        isActive ? 'bg-foreground text-background' : 'border-foreground/40 hover:bg-primary/5'
                      )}
                      role="listitem"
                      onClick={() => handleTechnicalQuickFilter(filter)}
                    >
                      <Activity className="h-4 w-4 mr-2" />
                      <span className="font-bold uppercase text-xs">{filter.label}</span>
                    </Badge>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-foreground">
            <CardHeader className="pb-3 border-b-2 border-foreground bg-muted/30">
              <CardTitle className="text-base">Sector Quick Filter</CardTitle>
              <CardDescription>Click to add sector filter</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="flex flex-wrap gap-2" role="list" aria-label="Sector filters">
                {SECTOR_QUICK_FILTERS.map(sector => {
                  const isActive = selectedFilters.some(f => f.key === 'sector' && f.value === sector)
                  return (
                    <Badge
                      key={sector}
                      variant={isActive ? 'default' : 'outline'}
                      className={cn(
                        'cursor-pointer py-2 px-3 border-2 transition-all hover:translate-x-[-1px] hover:translate-y-[-1px] hover:shadow-[2px_2px_0px_0px_var(--foreground)]',
                        isActive ? 'bg-foreground text-background border-foreground' : 'border-foreground/40 hover:bg-primary/5'
                      )}
                      role="listitem"
                      onClick={() => {
                        if (isActive) {
                          const idx = selectedFilters.findIndex(f => f.key === 'sector' && f.value === sector)
                          if (idx >= 0) {
                            const { removeFilter } = useScreenerStore.getState()
                            removeFilter(idx)
                          }
                        } else {
                          addFilter({ key: 'sector', value: sector, operator: '=' })
                        }
                      }}
                    >
                      <Building2 className="h-3 w-3 mr-1" />
                      {sector}
                    </Badge>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-foreground">
            <CardHeader className="pb-3 border-b-2 border-foreground bg-muted/30">
              <CardTitle className="text-base flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Strategy Templates
              </CardTitle>
              <CardDescription>Popular investment strategies</CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-2">
                {[
                  { name: 'CAN SLIM', desc: 'Growth investing with IBD methodology', icon: TrendingUp },
                  { name: 'Warren Buffett', desc: 'Quality value investing', icon: Building2 },
                  { name: 'Peter Lynch', desc: 'Growth at reasonable price', icon: Cpu },
                  { name: 'Greenblatt', desc: 'Magic formula investing', icon: Target },
                ].map((strategy, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    className="justify-start h-auto py-3 border-foreground/20 hover:bg-primary/10"
                    onClick={() => {
                      clearFilters()
                      addFilter({ key: 'roe', operator: '>', value: 15 })
                      addFilter({ key: 'debt_to_equity', operator: '<', value: 0.5 })
                    }}
                  >
                    <div className="h-8 w-8 bg-primary/10 flex items-center justify-center border border-foreground/20 mr-3">
                      <strategy.icon className="h-4 w-4" />
                    </div>
                    <div className="text-left">
                      <div className="font-black uppercase text-sm">{strategy.name}</div>
                      <div className="text-xs text-muted-foreground font-mono">{strategy.desc}</div>
                    </div>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Separator />

      <Card className="border-2 border-foreground">
        <CardHeader className="pb-3 border-b-2 border-foreground bg-muted/30 py-3">
          <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Auto-Refresh Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Switch
                id="auto-refresh"
                checked={autoRefresh}
                onCheckedChange={setAutoRefresh}
                className="border-2 border-foreground"
              />
              <Label htmlFor="auto-refresh" className="font-bold uppercase text-sm">
                Auto-refresh every 30 seconds
              </Label>
            </div>
            {autoRefresh && (
              <Badge variant="secondary" className="animate-pulse bg-foreground text-background">
                <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                LIVE
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
