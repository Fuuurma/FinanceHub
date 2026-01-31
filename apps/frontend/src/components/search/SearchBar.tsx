'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Search, X, TrendingUp, Building2, Coins, LineChart, DollarSign } from 'lucide-react'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

interface SearchBarProps {
  onSelect?: (asset: SearchResult) => void
  placeholder?: string
  className?: string
  autoFocus?: boolean
}

interface SearchResult {
  id: number
  symbol: string
  name: string
  asset_type: string
  exchange: string
  current_price: number
  change_pct: number
  market_cap: number | null
}

export function SearchBar({ onSelect, placeholder = 'Search stocks, crypto, ETFs...', className, autoFocus = false }: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [suggestions, setSuggestions] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  const ASSET_TYPE_ICONS: Record<string, React.ReactNode> = {
    stock: <Building2 className="w-4 h-4" />,
    etf: <LineChart className="w-4 h-4" />,
    crypto: <Coins className="w-4 h-4" />,
    forex: <DollarSign className="w-4 h-4" />,
    commodity: <TrendingUp className="w-4 h-4" />,
  }

  const searchAssets = useCallback(async (searchQuery: string, typeFilter?: string | null) => {
    if (!searchQuery || searchQuery.length < 1) {
      setResults([])
      setSuggestions([])
      return
    }

    setLoading(true)
    try {
      const params = new URLSearchParams({ q: searchQuery })
      if (typeFilter) {
        params.append('asset_types', typeFilter)
      }
      params.append('limit', '10')

      const response = await fetch(`/api/search/quick?${params}`)
      if (!response.ok) throw new Error('Search failed')
      const data = await response.json()
      setResults(data.results || [])
      setSuggestions(data.results?.slice(0, 3) || [])
    } catch (error) {
      console.error('Search error:', error)
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    debounceRef.current = setTimeout(() => {
      searchAssets(query, selectedType)
    }, 200)

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [query, selectedType, searchAssets])

  const handleSelect = (asset: SearchResult) => {
    setQuery(asset.symbol)
    setShowResults(false)
    if (onSelect) {
      onSelect(asset)
    }
  }

  const handleClear = () => {
    setQuery('')
    setResults([])
    setShowResults(false)
    inputRef.current?.focus()
  }

  const getChangeColor = (changePct: number) => {
    if (changePct > 0) return 'text-green-500'
    if (changePct < 0) return 'text-red-500'
    return 'text-muted-foreground'
  }

  return (
    <div className={cn('relative', className)}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setShowResults(true)
          }}
          onFocus={() => setShowResults(true)}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className="pl-10 pr-10"
        />
        {query && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0"
            onClick={handleClear}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {showResults && query && (
        <Card className="absolute top-full left-0 right-0 z-50 mt-1 max-h-96 overflow-auto">
          <CardContent className="p-0">
            {loading ? (
              <div className="p-4 text-center text-muted-foreground">
                Searching...
              </div>
            ) : results.length > 0 ? (
              <div className="py-1">
                {results.map((asset, index) => (
                  <div
                    key={`${asset.id}-${index}`}
                    className="flex items-center justify-between px-4 py-3 hover:bg-muted cursor-pointer transition-colors"
                    onClick={() => handleSelect(asset)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted">
                        {ASSET_TYPE_ICONS[asset.asset_type] || <Building2 className="w-4 h-4" />}
                      </div>
                      <div>
                        <div className="font-semibold">{asset.symbol}</div>
                        <div className="text-sm text-muted-foreground truncate max-w-[200px]">
                          {asset.name}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">
                        {formatCurrency(asset.current_price)}
                      </div>
                      <div className={cn('text-sm', getChangeColor(asset.change_pct))}>
                        {formatPercent(asset.change_pct / 100)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center text-muted-foreground">
                No results found for &quot;{query}&quot;
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default SearchBar
