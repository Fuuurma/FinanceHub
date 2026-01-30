'use client'

import { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import {
  ChevronLeft,
  Filter,
  Search,
  Plus,
  Download,
  X,
  Settings2,
  Activity,
  TrendingUp,
  TrendingDown,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { cn } from '@/lib/utils'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js/auto'
import { Line } from 'react-chartjs-2'

// Initialize Chart.js
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export interface OptionType {
  id: string
  symbol: string
  name: string
  option_type: 'call' | 'put'
  underlying_symbol: string
  strike_price: number
  expiration_date: string
  bid: number
  ask: number
  last_price: number
  volume: number
  open_interest: number
  change: number
  change_percent: number
}

export interface OptionChainData {
  symbol: string
  name: string
  current_price: number
  bid: number
  ask: number
  change: number
  change_percent: number
  last_updated: string
  options: {
    calls: OptionType[]
    puts: OptionType[]
  }
  greeks: {
    iv: number
    delta_call: number
    delta_put: number
    gamma: number
    theta: number
    vega: number
  }
}

export interface FilterState {
  option_type: string
  strike_range_min: number
  strike_range_max: number
  bid_min: number
  bid_max: number
  volume_min: number
  expiration: string
  search: string
}

export interface SortState {
  field: string
  direction: 'asc' | 'desc'
}

const DEFAULT_FILTERS: FilterState = {
  option_type: 'all',
  strike_range_min: 0,
  strike_range_max: 999999,
  bid_min: 0,
  bid_max: 999999,
  volume_min: 0,
  expiration: 'all',
  search: '',
}

const TIMEFRAMES: string[] = ['1D', '1W', '1M', '3M', '6M', '1Y']

export function OptionsChain() {
  const params = useParams()
  const router = useRouter()
  const symbol = (params.symbol as string) || 'AAPL'

  const [selectedOptionChain, setSelectedOptionChain] = useState<OptionChainData | null>(null)
  const [selectedExpiry, setSelectedExpiry] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'overview' | 'calls' | 'puts'>('overview')
  const [loading, setLoading] = useState(true)

  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS)
  const [sort, setSort] = useState<SortState>({ field: 'strike_price', direction: 'asc' })

  const [showFilters, setShowFilters] = useState(false)
  const [selectedDate, setSelectedDate] = useState<string>('')

  useEffect(() => {
    fetchOptionChainData(symbol)
  }, [symbol])

  const fetchOptionChainData = async (ticker: string) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/options/${ticker}`)
      if (response.ok) {
        const data = await response.json()
        setSelectedOptionChain(data)
        if (data.options.calls.length > 0) {
          setSelectedExpiry(data.options.calls[0].expiration_date)
          setSelectedDate(data.options.calls[0].expiration_date)
        }
      }
    } catch (error) {
      console.error('Failed to fetch option chain:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value: number, decimals = 2): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value)
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const formatNumber = (value: number): string => {
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`
    return value.toFixed(0)
  }

  const filterOptions = useMemo(() => {
    if (!selectedOptionChain) return { calls: [], puts: [] }

    let calls = [...selectedOptionChain.options.calls]
    let puts = [...selectedOptionChain.options.puts]

    // Filter by option type
    if (filters.option_type === 'call') {
      puts = []
    } else if (filters.option_type === 'put') {
      calls = []
    }

    // Filter by strike range
    calls = calls.filter(opt => opt.strike_price >= filters.strike_range_min && opt.strike_price <= filters.strike_range_max)
    puts = puts.filter(opt => opt.strike_price >= filters.strike_range_min && opt.strike_price <= filters.strike_range_max)

    // Filter by bid range
    calls = calls.filter(opt => opt.bid >= filters.bid_min && opt.bid <= filters.bid_max)
    puts = puts.filter(opt => opt.bid >= filters.bid_min && opt.bid <= filters.bid_max)

    // Filter by volume
    calls = calls.filter(opt => opt.volume >= filters.volume_min)
    puts = puts.filter(opt => opt.volume >= filters.volume_min)

    // Filter by expiration
    if (filters.expiration !== 'all') {
      const now = new Date()
      const expiryDate = new Date(filters.expiration)
      calls = calls.filter(opt => {
        const optDate = new Date(opt.expiration_date)
        return optDate <= expiryDate
      })
      puts = puts.filter(opt => {
        const optDate = new Date(opt.expiration_date)
        return optDate <= expiryDate
      })
    }

    // Sort
    calls.sort((a, b) => {
      const aVal = a[sort.field as keyof OptionType] as number
      const bVal = b[sort.field as keyof OptionType] as number
      return sort.direction === 'asc' ? aVal - bVal : bVal - aVal
    })

    puts.sort((a, b) => {
      const aVal = a[sort.field as keyof OptionType] as number
      const bVal = b[sort.field as keyof OptionType] as number
      return sort.direction === 'asc' ? aVal - bVal : bVal - aVal
    })

    return { calls, puts }
  }, [selectedOptionChain, filters, sort])

  const sortedCalls = filterOptions.calls
  const sortedPuts = filterOptions.puts

  const activeOptions = activeTab === 'calls' ? sortedCalls : activeTab === 'puts' ? sortedPuts : [...sortedCalls, ...sortedPuts]

  const maxStrike = selectedOptionChain ? Math.max(...selectedOptionChain.options.calls.map(o => o.strike_price), ...selectedOptionChain.options.puts.map(o => o.strike_price)) : 0
  const minStrike = selectedOptionChain ? Math.min(...selectedOptionChain.options.calls.map(o => o.strike_price), ...selectedOptionChain.options.puts.map(o => o.strike_price)) : 0

  const handleFilterChange = (field: keyof FilterState, value: string | number) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleResetFilters = () => {
    setFilters(DEFAULT_FILTERS)
  }

  const handleSortChange = (field: string) => {
    setSort(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc',
    }))
  }

  const getStrikeColumnClass = (strikePrice: number): string => {
    if (!selectedOptionChain) return ''
    const currentPrice = selectedOptionChain.current_price
    const isATM = Math.abs(strikePrice - currentPrice) < (currentPrice * 0.01)
    const isITM = strikePrice < currentPrice
    return cn(
      'font-semibold',
      isATM ? 'bg-muted/30' : '',
      isITM ? 'text-green-600 dark:text-green-400' : '',
    )
  }

  const chartData = useMemo(() => {
    if (!selectedOptionChain || !selectedExpiry) return null

    const selectedDate = selectedOptionChain.options.calls.find(c => c.expiration_date === selectedExpiry)
    if (!selectedDate) return null

    const calls = selectedOptionChain.options.calls.filter(c => c.expiration_date === selectedExpiry)
    const puts = selectedOptionChain.options.puts.filter(p => p.expiration_date === selectedExpiry)

    const labels = calls.map(c => `$${c.strike_price.toFixed(0)}`)
    const callData = calls.map(c => c.bid)
    const putData = puts.map(p => p.bid)

    return {
      labels,
      datasets: [
        {
          label: 'Call Bids',
          data: callData,
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          tension: 0.1,
          fill: true,
        },
        {
          label: 'Put Bids',
          data: putData,
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.1,
          fill: true,
        },
      ],
    }
  }, [selectedOptionChain, selectedExpiry])

  const getGreeksCard = () => {
    if (!selectedOptionChain) return null
    const greeks = selectedOptionChain.greeks

    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Greeks Overview
          </CardTitle>
          <CardDescription>Current option greeks for {symbol}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="p-4 bg-muted/30 rounded-lg">
              <p className="text-sm text-muted-foreground mb-1">Implied Volatility</p>
              <p className="text-2xl font-bold">{greeks.iv.toFixed(2)}%</p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <p className="text-sm text-muted-foreground mb-1">Call Delta</p>
              <p className="text-2xl font-bold">{greeks.delta_call.toFixed(3)}</p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <p className="text-sm text-muted-foreground mb-1">Put Delta</p>
              <p className="text-2xl font-bold">{greeks.delta_put.toFixed(3)}</p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <p className="text-sm text-muted-foreground mb-1">Gamma</p>
              <p className="text-2xl font-bold">{greeks.gamma.toFixed(4)}</p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <p className="text-sm text-muted-foreground mb-1">Theta</p>
              <p className="text-2xl font-bold">{greeks.theta.toFixed(4)}</p>
            </div>
            <div className="p-4 bg-muted/30 rounded-lg">
              <p className="text-sm text-muted-foreground mb-1">Vega</p>
              <p className="text-2xl font-bold">{greeks.vega.toFixed(4)}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/market/stocks')}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Options Chain</h1>
            <p className="text-muted-foreground">
              {selectedOptionChain?.name || symbol} - Option Chain Data
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="space-y-4">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-96 w-full" />
        </div>
      ) : (
        <>
          {selectedOptionChain && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">{selectedOptionChain.name}</CardTitle>
                  <CardDescription>
                    Current Price: {formatCurrency(selectedOptionChain.current_price)}
                    {' '}
                    {selectedOptionChain.change >= 0 ? (
                      <span className="text-green-600">
                        {selectedOptionChain.change >= 0 ? '+' : ''}{selectedOptionChain.change.toFixed(2)}
                        {' '}
                        ({selectedOptionChain.change_percent >= 0 ? '+' : ''}{selectedOptionChain.change_percent.toFixed(2)}%)
                      </span>
                    ) : (
                      <span className="text-red-600">
                        {selectedOptionChain.change.toFixed(2)}
                        {' '}
                        ({selectedOptionChain.change_percent.toFixed(2)}%)
                      </span>
                    )}
                  </CardDescription>
                </CardHeader>
              </Card>

              {getGreeksCard()}

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Available Expirations</CardTitle>
                  <CardDescription>Select an expiration date to view options</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {TIMEFRAMES.map((tf) => (
                      <Button
                        key={tf}
                        variant={selectedDate === tf ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setSelectedDate(tf)}
                      >
                        {tf}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Option Pricer</CardTitle>
                  <CardDescription>
                    {selectedDate && `Expiring: ${formatDate(selectedDate)}`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {chartData && (
                    <div className="h-[400px]">
                      <Line data={chartData} />
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          )}

          {showFilters && (
            <Card>
              <CardHeader>
                <CardTitle>Filters</CardTitle>
                <CardDescription>Refine your option chain view</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Option Type</label>
                    <Select
                      value={filters.option_type}
                      onValueChange={(value) => handleFilterChange('option_type', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="All Types" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All</SelectItem>
                        <SelectItem value="call">Calls</SelectItem>
                        <SelectItem value="put">Puts</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Expiration</label>
                    <Select
                      value={filters.expiration}
                      onValueChange={(value) => handleFilterChange('expiration', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="All Expirations" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All</SelectItem>
                        {selectedOptionChain?.options.calls.map((opt) => (
                          <SelectItem key={opt.expiration_date} value={opt.expiration_date}>
                            {formatDate(opt.expiration_date)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      Strike Min: ${filters.strike_range_min.toFixed(2)}
                    </label>
                    <Input
                      type="number"
                      step="0.01"
                      value={filters.strike_range_min}
                      onChange={(e) => handleFilterChange('strike_range_min', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      Strike Max: ${filters.strike_range_max.toFixed(2)}
                    </label>
                    <Input
                      type="number"
                      step="0.01"
                      value={filters.strike_range_max}
                      onChange={(e) => handleFilterChange('strike_range_max', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      Volume Min: {formatNumber(filters.volume_min)}
                    </label>
                    <Input
                      type="number"
                      value={filters.volume_min}
                      onChange={(e) => handleFilterChange('volume_min', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <Button variant="outline" size="sm" onClick={handleResetFilters}>
                    <X className="h-4 w-4 mr-2" />
                    Reset Filters
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="calls">Calls</TabsTrigger>
              <TabsTrigger value="puts">Puts</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-green-600" />
                      Calls Overview
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center py-6">
                      <p className="text-sm text-muted-foreground mb-2">Total Calls</p>
                      <p className="text-3xl font-bold">{sortedCalls.length}</p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <TrendingDown className="h-5 w-5 text-red-600" />
                      Puts Overview
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center py-6">
                      <p className="text-sm text-muted-foreground mb-2">Total Puts</p>
                      <p className="text-3xl font-bold">{sortedPuts.length}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="calls" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Call Options</CardTitle>
                  <CardDescription>
                    {sortedCalls.length} calls available
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <OptionChainTable
                    options={sortedCalls}
                    symbol={symbol}
                    onSelect={(opt) => setSelectedOptionChain(selectedOptionChain)}
                    getStrikeClass={getStrikeColumnClass}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="puts" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Put Options</CardTitle>
                  <CardDescription>
                    {sortedPuts.length} puts available
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <OptionChainTable
                    options={sortedPuts}
                    symbol={symbol}
                    onSelect={(opt) => setSelectedOptionChain(selectedOptionChain)}
                    getStrikeClass={getStrikeColumnClass}
                  />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  )
}

interface OptionChainTableProps {
  options: OptionType[]
  symbol: string
  onSelect: (column: string) => void
  getStrikeClass: (strike: number) => string
}

function OptionChainTable({ options, symbol, onSelect, getStrikeClass }: OptionChainTableProps) {
  const [search, setSearch] = useState('')

  const formatNumber = (value: number): string => {
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`
    return value.toFixed(0)
  }

  const filteredOptions = options.filter(opt =>
    opt.symbol.toLowerCase().includes(search.toLowerCase()) ||
    opt.name.toLowerCase().includes(search.toLowerCase()) ||
    opt.strike_price.toString().includes(search)
  )

  const formatCurrency = (value: number, decimals = 2) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value)
  }

  return (
    <div className="space-y-3">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by symbol, name, or strike price..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="rounded-md border">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="text-left p-3 text-sm font-semibold">
                <button
                  onClick={() => onSelect('symbol')}
                  className="flex items-center gap-1 hover:text-primary"
                >
                  Symbol
                  <span>▼</span>
                </button>
              </th>
              <th className="text-left p-3 text-sm font-semibold">
                <button
                  onClick={() => onSelect('strike_price')}
                  className="flex items-center gap-1 hover:text-primary"
                >
                  Strike Price
                  <span>▼</span>
                </button>
              </th>
              <th className="text-left p-3 text-sm font-semibold">
                <button
                  onClick={() => onSelect('last_price')}
                  className="flex items-center gap-1 hover:text-primary"
                >
                  Last Price
                  <span>▼</span>
                </button>
              </th>
              <th className="text-right p-3 text-sm font-semibold">
                <button
                  onClick={() => onSelect('bid')}
                  className="flex items-center gap-1 hover:text-primary justify-end"
                >
                  Bid
                  <span>▼</span>
                </button>
              </th>
              <th className="text-right p-3 text-sm font-semibold">
                <button
                  onClick={() => onSelect('ask')}
                  className="flex items-center gap-1 hover:text-primary justify-end"
                >
                  Ask
                  <span>▼</span>
                </button>
              </th>
              <th className="text-right p-3 text-sm font-semibold">
                <button
                  onClick={() => onSelect('change_percent')}
                  className="flex items-center gap-1 hover:text-primary justify-end"
                >
                  Change %
                  <span>▼</span>
                </button>
              </th>
              <th className="text-right p-3 text-sm font-semibold">
                <button
                  onClick={() => onSelect('volume')}
                  className="flex items-center gap-1 hover:text-primary justify-end"
                >
                  Volume
                  <span>▼</span>
                </button>
              </th>
              <th className="text-right p-3 text-sm font-semibold">
                <button
                  onClick={() => onSelect('open_interest')}
                  className="flex items-center gap-1 hover:text-primary justify-end"
                >
                  Open Interest
                  <span>▼</span>
                </button>
              </th>
              <th className="text-center p-3 text-sm font-semibold">
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Trade Option</DialogTitle>
                      <DialogDescription>
                        Trade {options[0]?.symbol || 'Option'}
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium mb-2 block">Quantity</label>
                        <Input type="number" placeholder="100" />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Price</label>
                        <Input type="number" step="0.01" placeholder="0.00" />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Order Type</label>
                        <Select>
                          <SelectTrigger>
                            <SelectValue placeholder="Market" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="market">Market</SelectItem>
                            <SelectItem value="limit">Limit</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">Expiration</label>
                        <Input value={options[0]?.expiration_date} disabled />
                      </div>
                      <div className="flex justify-end gap-2">
                        <Button variant="outline">Cancel</Button>
                        <Button>Submit Order</Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredOptions.map((opt) => (
              <tr key={opt.id} className="border-b hover:bg-muted/30">
                <td className="p-3">
                  <div>
                    <p className="font-semibold">{opt.symbol}</p>
                    <p className="text-xs text-muted-foreground">{opt.name}</p>
                  </div>
                </td>
                <td className={`p-3 ${getStrikeClass(opt.strike_price)}`}>
                  ${opt.strike_price.toFixed(2)}
                </td>
                <td className="p-3 text-right">
                  {formatCurrency(opt.last_price, 2)}
                </td>
                <td className="p-3 text-right font-medium">
                  {formatCurrency(opt.bid, 2)}
                </td>
                <td className="p-3 text-right">
                  {formatCurrency(opt.ask, 2)}
                </td>
                <td className="p-3 text-right">
                  <span className={cn(
                    'px-2 py-1 rounded text-xs font-medium',
                    opt.change >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  )}>
                    {opt.change >= 0 ? '+' : ''}{opt.change_percent.toFixed(2)}%
                  </span>
                </td>
                <td className="p-3 text-right">
                  {formatNumber(opt.volume)}
                </td>
                <td className="p-3 text-right">
                  {formatNumber(opt.open_interest)}
                </td>
                <td className="p-3 text-center">
                  <Button variant="ghost" size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredOptions.length === 0 && (
        <div className="text-center py-12 bg-muted/30 rounded-lg">
          <p className="text-muted-foreground">No options found matching your filters</p>
        </div>
      )}
    </div>
  )
}
