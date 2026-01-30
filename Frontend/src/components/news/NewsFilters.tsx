'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { cn } from '@/lib/utils'
import {
  Filter,
  TrendingUp,
  TrendingDown,
  Clock,
  Calendar,
} from 'lucide-react'

export interface NewsFilters {
  category: string
  sentiment: string
  impact: string
  timeframe: string
  source: string
}

interface NewsFiltersProps {
  filters: NewsFilters
  onFiltersChange: (filters: NewsFilters) => void
  className?: string
}

const CATEGORIES = ['ALL', 'URGENT', 'MACRO', 'CRYPTO', 'TECH', 'COMMODITIES', 'SECURITY', 'EARNINGS', 'ECONOMY', 'GEOPOLITICAL']

const SENTIMENTS = [
  { value: 'all', label: 'All Sentiments' },
  { value: 'bullish', label: 'Bullish' },
  { value: 'bearish', label: 'Bearish' },
  { value: 'positive', label: 'Positive' },
  { value: 'negative', label: 'Negative' },
  { value: 'neutral', label: 'Neutral' },
]

const IMPACTS = [
  { value: 'all', label: 'All Impacts' },
  { value: 'urgent', label: 'Urgent' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
]

const TIMEFRAMES = [
  { value: '1h', label: 'Last Hour' },
  { value: '6h', label: 'Last 6 Hours' },
  { value: '24h', label: 'Last 24 Hours' },
  { value: '7d', label: 'Last 7 Days' },
  { value: '30d', label: 'Last 30 Days' },
]

const SOURCES = [
  { value: 'all', label: 'All Sources' },
  { value: 'REUTERS', label: 'Reuters' },
  { value: 'BLOOMBERG', label: 'Bloomberg' },
  { value: 'CNBC', label: 'CNBC' },
  { value: 'WSJ', label: 'WSJ' },
  { value: 'FED_WIRE', label: 'Fed Wire' },
  { value: 'BLOCK_REPORT', label: 'Block Report' },
  { value: 'EXCHANGE_ALERTS', label: 'Exchange Alerts' },
]

export function NewsFilters({ filters, onFiltersChange, className }: NewsFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const updateFilter = (key: keyof NewsFilters, value: string) => {
    onFiltersChange({ ...filters, [key]: value })
  }

  const resetFilters = () => {
    onFiltersChange({
      category: 'ALL',
      sentiment: 'all',
      impact: 'all',
      timeframe: '24h',
      source: 'all',
    })
  }

  const hasActiveFilters = Object.values(filters).some((v) => v !== 'ALL' && v !== 'all' && v !== '24h')

  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center gap-2 flex-wrap">
        <div className="flex gap-1">
          {CATEGORIES.slice(0, 5).map((category) => (
            <Button
              key={category}
              variant="ghost"
              size="sm"
              onClick={() => updateFilter('category', category)}
              className={cn(
                'text-[10px] font-black uppercase px-3 py-1 border-2 border-foreground transition-all rounded-none',
                filters.category === category
                  ? 'bg-foreground text-background shadow-[2px_2px_0px_0px_var(--primary)]'
                  : 'bg-transparent hover:bg-muted'
              )}
            >
              {category}
            </Button>
          ))}

          <Select
            value={filters.category}
            onValueChange={(value) => updateFilter('category', value)}
          >
            <SelectTrigger className="h-8 w-24 text-[10px] font-black uppercase border-2 border-foreground rounded-none">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {CATEGORIES.map((category) => (
                <SelectItem key={category} value={category}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-[10px] font-black uppercase border-2 border-foreground rounded-none"
        >
          <Filter className="h-4 w-4 mr-1" />
          Filters
          {hasActiveFilters && (
            <span className="ml-1 w-2 h-2 bg-primary rounded-full" />
          )}
        </Button>

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={resetFilters}
            className="text-[10px] font-black uppercase border-2 border-foreground rounded-none"
          >
            Reset
          </Button>
        )}
      </div>

      {isExpanded && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 border-2 border-foreground bg-muted/20">
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              Sentiment
            </label>
            <Select
              value={filters.sentiment}
              onValueChange={(value) => updateFilter('sentiment', value)}
            >
              <SelectTrigger className="border-foreground/20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SENTIMENTS.map((s) => (
                  <SelectItem key={s.value} value={s.value}>
                    {s.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              Impact
            </label>
            <Select
              value={filters.impact}
              onValueChange={(value) => updateFilter('impact', value)}
            >
              <SelectTrigger className="border-foreground/20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {IMPACTS.map((i) => (
                  <SelectItem key={i.value} value={i.value}>
                    {i.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Timeframe
            </label>
            <Select
              value={filters.timeframe}
              onValueChange={(value) => updateFilter('timeframe', value)}
            >
              <SelectTrigger className="border-foreground/20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIMEFRAMES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase flex items-center gap-1">
              <TrendingDown className="h-3 w-3" />
              Source
            </label>
            <Select
              value={filters.source}
              onValueChange={(value) => updateFilter('source', value)}
            >
              <SelectTrigger className="border-foreground/20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SOURCES.map((s) => (
                  <SelectItem key={s.value} value={s.value}>
                    {s.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      )}
    </div>
  )
}

export default NewsFilters
