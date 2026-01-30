'use client'

import { useState, useCallback, useEffect, useMemo } from 'react'
import { Search, Building2, BarChart3, RefreshCw, ArrowUpDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { type Sector, type Industry } from '@/lib/api/market-overview'

type SortField = 'name' | 'change' | 'marketCap'

interface SectorWithPerformance extends Sector {
  avgChange: number
  totalMarketCap: number
  symbolCount: number
}

interface IndustryWithPerformance extends Industry {
  change: number
  marketCap: number
  symbolCount: number
}

interface SectorIndustryBrowserProps {
  onSectorSelect?: (sector: Sector) => void
  onIndustrySelect?: (industry: Industry) => void
  className?: string
}

function formatNumber(num: number): string {
  if (num >= 1e12) return `${(num / 1e12).toFixed(2)}T`
  if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`
  if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`
  return num.toFixed(2)
}

function formatPercent(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

function getPerformanceColor(value: number): string {
  if (value > 2) return 'text-green-600'
  if (value > 0) return 'text-green-500'
  if (value === 0) return 'text-gray-500'
  if (value > -2) return 'text-red-500'
  return 'text-red-600'
}

function generateMockSectors(): SectorWithPerformance[] {
  return [
    { id: 'XLK', code: 'XLK', name: 'Technology', industry_count: 6, avgChange: 2.3, totalMarketCap: 12.5e12, symbolCount: 350 },
    { id: 'XLF', code: 'XLF', name: 'Financials', industry_count: 5, avgChange: 1.1, totalMarketCap: 8.2e12, symbolCount: 280 },
    { id: 'XLV', code: 'XLV', name: 'Healthcare', industry_count: 6, avgChange: -0.4, totalMarketCap: 7.8e12, symbolCount: 420 },
    { id: 'XLY', code: 'XLY', name: 'Consumer Discretionary', industry_count: 6, avgChange: 1.8, totalMarketCap: 6.5e12, symbolCount: 290 },
    { id: 'XLE', code: 'XLE', name: 'Energy', industry_count: 4, avgChange: -1.2, totalMarketCap: 4.2e12, symbolCount: 180 },
    { id: 'XLI', code: 'XLI', name: 'Industrials', industry_count: 5, avgChange: 0.7, totalMarketCap: 5.8e12, symbolCount: 250 },
    { id: 'XLP', code: 'XLP', name: 'Consumer Staples', industry_count: 5, avgChange: 0.3, totalMarketCap: 4.1e12, symbolCount: 200 },
    { id: 'XLU', code: 'XLU', name: 'Utilities', industry_count: 4, avgChange: -0.2, totalMarketCap: 2.3e12, symbolCount: 150 },
    { id: 'XLB', code: 'XLB', name: 'Materials', industry_count: 4, avgChange: 0.9, totalMarketCap: 2.1e12, symbolCount: 120 },
    { id: 'XLRE', code: 'XLRE', name: 'Real Estate', industry_count: 3, avgChange: -0.8, totalMarketCap: 2.5e12, symbolCount: 180 },
    { id: 'XLC', code: 'XLC', name: 'Communication Services', industry_count: 4, avgChange: 1.5, totalMarketCap: 5.2e12, symbolCount: 160 },
  ]
}

function generateMockIndustries(sectorCode?: string): IndustryWithPerformance[] {
  const industries = [
    { id: 'semi-1', code: 'semiconductors', name: 'Semiconductors', sector_id: 'XLK', sector_name: 'Technology', sector_code: 'XLK', change: 3.2, marketCap: 4.5e12, symbolCount: 45 },
    { id: 'soft-1', code: 'software', name: 'Software', sector_id: 'XLK', sector_name: 'Technology', sector_code: 'XLK', change: 2.1, marketCap: 3.8e12, symbolCount: 120 },
    { id: 'hw-1', code: 'hardware', name: 'Tech Hardware', sector_id: 'XLK', sector_name: 'Technology', sector_code: 'XLK', change: 1.5, marketCap: 2.1e12, symbolCount: 85 },
    { id: 'int-1', code: 'internet', name: 'Internet', sector_id: 'XLK', sector_name: 'Technology', sector_code: 'XLK', change: 2.8, marketCap: 2.8e12, symbolCount: 60 },
    { id: 'bank-1', code: 'banks', name: 'Banks', sector_id: 'XLF', sector_name: 'Financials', sector_code: 'XLF', change: 1.2, marketCap: 2.8e12, symbolCount: 90 },
    { id: 'ins-1', code: 'insurance', name: 'Insurance', sector_id: 'XLF', sector_name: 'Financials', sector_code: 'XLF', change: 0.8, marketCap: 2.1e12, symbolCount: 75 },
    { id: 'pharm-1', code: 'pharma', name: 'Pharmaceuticals', sector_id: 'XLV', sector_name: 'Healthcare', sector_code: 'XLV', change: -0.3, marketCap: 3.2e12, symbolCount: 80 },
    { id: 'bio-1', code: 'biotech', name: 'Biotechnology', sector_id: 'XLV', sector_name: 'Healthcare', sector_code: 'XLV', change: -0.8, marketCap: 1.5e12, symbolCount: 180 },
    { id: 'retail-1', code: 'retail', name: 'Retail', sector_id: 'XLY', sector_name: 'Consumer Discretionary', sector_code: 'XLY', change: 1.9, marketCap: 2.8e12, symbolCount: 110 },
    { id: 'media-1', code: 'media', name: 'Media', sector_id: 'XLC', sector_name: 'Communication Services', sector_code: 'XLC', change: 1.6, marketCap: 2.1e12, symbolCount: 65 },
  ]
  if (sectorCode) {
    return industries.filter(i => i.sector_code === sectorCode)
  }
  return industries
}

export function SectorIndustryBrowser({ onSectorSelect, onIndustrySelect, className }: SectorIndustryBrowserProps) {
  const [activeTab, setActiveTab] = useState<'sectors' | 'industries'>('sectors')
  const [sectors, setSectors] = useState<SectorWithPerformance[]>([])
  const [industries, setIndustries] = useState<IndustryWithPerformance[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedSector, setSelectedSector] = useState<SectorWithPerformance | null>(null)
  const [selectedIndustry, setSelectedIndustry] = useState<IndustryWithPerformance | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [sortField, setSortField] = useState<SortField>('change')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')

  useEffect(() => {
    setLoading(true)
    const mockSectors = generateMockSectors()
    const mockIndustries = generateMockIndustries()
    setSectors(mockSectors)
    setIndustries(mockIndustries)
    setLoading(false)
  }, [])

  const handleSort = useCallback((field: SortField) => {
    if (sortField === field) {
      setSortDir(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDir('desc')
    }
  }, [sortField])

  const handleSectorClick = useCallback((sector: SectorWithPerformance) => {
    setSelectedSector(sector)
    setSelectedIndustry(null)
    onSectorSelect?.({ id: sector.id, code: sector.code, name: sector.name, industry_count: sector.industry_count })
    setIndustries(generateMockIndustries(sector.code))
    setActiveTab('industries')
  }, [onSectorSelect])

  const handleIndustryClick = useCallback((industry: IndustryWithPerformance) => {
    setSelectedIndustry(industry)
    onIndustrySelect?.({ id: industry.id, code: industry.code, name: industry.name, sector_id: industry.sector_id, sector_name: industry.sector_name, sector_code: industry.sector_code })
  }, [onIndustrySelect])

  const filteredSectors = useMemo(() => {
    let filtered = searchQuery 
      ? sectors.filter(s => s.name.toLowerCase().includes(searchQuery.toLowerCase()) || s.code.toLowerCase().includes(searchQuery.toLowerCase()))
      : sectors
    return filtered.sort((a, b) => {
      const aVal = sortField === 'name' ? a[sortField].toLowerCase() : a[sortField]
      const bVal = sortField === 'name' ? b[sortField].toLowerCase() : b[sortField]
      return sortDir === 'asc' ? (aVal > bVal ? 1 : -1) : (aVal < bVal ? 1 : -1)
    })
  }, [sectors, searchQuery, sortField, sortDir])

  const filteredIndustries = useMemo(() => {
    let filtered = searchQuery
      ? industries.filter(i => i.name.toLowerCase().includes(searchQuery.toLowerCase()) || i.code.toLowerCase().includes(searchQuery.toLowerCase()))
      : industries
    return filtered.sort((a, b) => {
      const aVal = sortField === 'name' ? a[sortField].toLowerCase() : a[sortField]
      const bVal = sortField === 'name' ? b[sortField].toLowerCase() : b[sortField]
      return sortDir === 'asc' ? (aVal > bVal ? 1 : -1) : (aVal < bVal ? 1 : -1)
    })
  }, [industries, searchQuery, sortField, sortDir])

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader><CardTitle>Sector & Industry Browser</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-32" />)}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Sector & Industry Browser
          </CardTitle>
          <Button variant="outline" size="sm" onClick={() => { setSectors(generateMockSectors()); setIndustries(generateMockIndustries()) }}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search sectors or industries..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button variant="outline" size="sm" onClick={() => handleSort(sortField === 'change' ? 'name' : 'change')}>
            <ArrowUpDown className="h-4 w-4 mr-2" />
            Sort: {sortField}
          </Button>
        </div>

        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'sectors' | 'industries')}>
          <TabsList>
            <TabsTrigger value="sectors">Sectors ({filteredSectors.length})</TabsTrigger>
            <TabsTrigger value="industries">Industries ({filteredIndustries.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="sectors" className="mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredSectors.map((sector) => (
                <div
                  key={sector.id}
                  onClick={() => handleSectorClick(sector)}
                  className={cn(
                    'cursor-pointer rounded-lg border p-4 transition-all duration-200 hover:shadow-md',
                    selectedSector?.id === sector.id ? 'border-primary bg-primary/5 shadow-md' : 'border-border bg-card hover:border-primary/50'
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold">{sector.name}</h3>
                      <p className="text-xs text-muted-foreground">{sector.industry_count} Industries</p>
                    </div>
                    <Badge variant="outline">{sector.code}</Badge>
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
                    <div>
                      <p className="text-xs text-muted-foreground">Change</p>
                      <p className={cn('font-semibold', getPerformanceColor(sector.avgChange))}>{formatPercent(sector.avgChange)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Market Cap</p>
                      <p className="font-semibold">{formatNumber(sector.totalMarketCap)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Symbols</p>
                      <p className="font-semibold">{sector.symbolCount}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="industries" className="mt-4">
            {selectedSector && (
              <div className="mb-4 p-3 bg-muted/50 rounded-lg flex items-center gap-2">
                <Building2 className="h-4 w-4" />
                <span className="text-sm">Filtering: <strong>{selectedSector.name}</strong></span>
                <Button variant="ghost" size="sm" className="ml-auto" onClick={() => { setSelectedSector(null); setIndustries(generateMockIndustries()) }}>
                  Clear
                </Button>
              </div>
            )}
            <div className="space-y-2">
              {filteredIndustries.map((industry) => (
                <div
                  key={industry.id}
                  onClick={() => handleIndustryClick(industry)}
                  className={cn(
                    'flex cursor-pointer items-center gap-4 rounded-lg border p-3 transition-all hover:bg-muted/50',
                    selectedIndustry?.id === industry.id ? 'border-primary bg-primary/5' : 'border-border bg-card'
                  )}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <BarChart3 className="h-4 w-4 text-muted-foreground shrink-0" />
                      <h4 className="font-medium truncate">{industry.name}</h4>
                    </div>
                    <p className="text-xs text-muted-foreground">{industry.sector_name}</p>
                  </div>
                  <div className="flex items-center gap-6 shrink-0">
                    <div className="w-20 text-right">
                      <p className={cn('text-sm font-semibold', getPerformanceColor(industry.change))}>{formatPercent(industry.change)}</p>
                    </div>
                    <div className="w-24 text-right">
                      <p className="text-sm font-semibold">{formatNumber(industry.marketCap)}</p>
                    </div>
                    <div className="w-16 text-right text-sm text-muted-foreground">{industry.symbolCount}</div>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
