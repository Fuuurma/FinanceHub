'use client'

import { useState, useCallback } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Search,
  X,
  History,
  TrendingUp,
  Clock,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useDebounce } from '@/hooks/use-debounce'

interface NewsSearchProps {
  onSearch: (query: string) => void
  onClear?: () => void
  placeholder?: string
  className?: string
}

const RECENT_SEARCHES = ['NVDA earnings', 'Fed rate', 'Bitcoin', 'AI stocks', 'oil prices']

const TRENDING_SEARCHES = [
  { term: 'NVIDIA H200', trend: 'hot' },
  { term: 'Fed meeting', trend: 'rising' },
  { term: 'Bitcoin ETF', trend: 'stable' },
  { term: 'Apple earnings', trend: 'falling' },
]

export function NewsSearch({
  onSearch,
  onClear,
  placeholder = 'Search news, symbols, topics...',
  className,
}: NewsSearchProps) {
  const [query, setQuery] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const [showHistory, setShowHistory] = useState(false)

  const handleSearch = useCallback(() => {
    if (query.trim()) {
      onSearch(query.trim())
      setShowHistory(false)
    }
  }, [query, onSearch])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const handleClear = () => {
    setQuery('')
    onClear?.()
  }

  const handleRecentSearch = (term: string) => {
    setQuery(term)
    onSearch(term)
    setShowHistory(false)
  }

  return (
    <div className={cn('relative', className)}>
      <div className={cn(
        'flex items-center border-2 border-foreground bg-background transition-all',
        isFocused && 'ring-2 ring-foreground'
      )}>
        <Search className="h-4 w-4 ml-3 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setTimeout(() => setShowHistory(false), 200)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="border-0 focus-visible:ring-0 rounded-none"
        />
        {query && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 mr-1"
            onClick={handleClear}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
        <Button
          size="sm"
          onClick={handleSearch}
          className="mr-1 h-8 border-2 border-foreground rounded-none font-black uppercase text-[10px]"
        >
          Search
        </Button>
      </div>

      {isFocused && !query && (
        <div className="absolute top-full left-0 right-0 z-50 mt-1 border-2 border-foreground bg-background">
          {RECENT_SEARCHES.length > 0 && (
            <div className="p-3 border-b border-foreground/20">
              <div className="flex items-center gap-2 text-xs font-bold uppercase text-muted-foreground mb-2">
                <Clock className="h-3 w-3" />
                Recent Searches
              </div>
              <div className="space-y-1">
                {RECENT_SEARCHES.map((term) => (
                  <button
                    key={term}
                    className="w-full text-left px-2 py-1 text-sm hover:bg-muted flex items-center gap-2"
                    onClick={() => handleRecentSearch(term)}
                  >
                    <History className="h-3 w-3 text-muted-foreground" />
                    {term}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="p-3">
            <div className="flex items-center gap-2 text-xs font-bold uppercase text-muted-foreground mb-2">
              <TrendingUp className="h-3 w-3" />
              Trending Now
            </div>
            <div className="flex flex-wrap gap-2">
              {TRENDING_SEARCHES.map((item) => (
                <button
                  key={item.term}
                  className="px-3 py-1 text-xs font-bold border border-foreground hover:bg-muted transition-colors"
                  onClick={() => handleRecentSearch(item.term)}
                >
                  {item.term}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default NewsSearch
