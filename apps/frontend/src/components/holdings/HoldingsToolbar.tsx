'use client'

import { useState, useCallback } from 'react'
import { Search, Filter, Download, RefreshCw, Plus, SlidersHorizontal } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { AssetClass, HoldingsFilter } from '@/lib/types/holdings'
import { ASSET_CLASS_LABELS } from '@/lib/types/holdings'
import { cn } from '@/lib/utils'
import { useDebouncedCallback } from '@/hooks/use-debounce'

interface HoldingsToolbarProps {
  onSearch: (search: string) => void
  onFilterChange: (filters: Partial<HoldingsFilter>) => void
  onRefresh: () => void
  onAdd?: () => void
  onExport?: () => void
  loading?: boolean
  filters?: HoldingsFilter
}

export function HoldingsToolbar({
  onSearch,
  onFilterChange,
  onRefresh,
  onAdd,
  onExport,
  loading = false,
  filters = {},
}: HoldingsToolbarProps) {
  const [searchInput, setSearchInput] = useState('')

  const debouncedSearch = useDebouncedCallback((value: string) => {
    onSearch(value)
  }, 300)

  const handleSearchChange = (value: string) => {
    setSearchInput(value)
    debouncedSearch(value)
  }

  const handleAssetClassFilter = (value: string) => {
    if (value === 'all') {
      onFilterChange({ asset_class: undefined })
    } else {
      onFilterChange({ asset_class: value as AssetClass })
    }
  }

  const handleSortChange = (value: string) => {
    const [sort_by, sort_order] = value.split('-')
    onFilterChange({
      sort_by: sort_by as any,
      sort_order: sort_order as 'asc' | 'desc',
    })
  }

  const currentAssetClass = Array.isArray(filters.asset_class)
    ? filters.asset_class[0]
    : filters.asset_class

  return (
    <div className="flex items-center justify-between gap-4 flex-wrap">
      <div className="flex items-center gap-2 flex-1">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search holdings..."
            value={searchInput}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>

        <Select
          value={currentAssetClass || 'all'}
          onValueChange={handleAssetClassFilter}
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Asset Class" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Classes</SelectItem>
            {Object.entries(ASSET_CLASS_LABELS).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={`${filters.sort_by || 'current_value'}-${filters.sort_order || 'desc'}`}
          onValueChange={handleSortChange}
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="current_value-desc">Value (High-Low)</SelectItem>
            <SelectItem value="current_value-asc">Value (Low-High)</SelectItem>
            <SelectItem value="unrealized_pnl_percent-desc">P&L % (High-Low)</SelectItem>
            <SelectItem value="unrealized_pnl_percent-asc">P&L % (Low-High)</SelectItem>
            <SelectItem value="day_change_percent-desc">Day Change (High-Low)</SelectItem>
            <SelectItem value="day_change_percent-asc">Day Change (Low-High)</SelectItem>
            <SelectItem value="symbol-asc">Symbol (A-Z)</SelectItem>
            <SelectItem value="weight-desc">Weight (High-Low)</SelectItem>
            <SelectItem value="weight-asc">Weight (Low-High)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          disabled={loading}
        >
          <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} />
        </Button>

        {onExport && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onExport()}>
                Export as CSV
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onExport()}>
                Export as JSON
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        {onAdd && (
          <Button size="sm" onClick={onAdd}>
            <Plus className="h-4 w-4 mr-2" />
            Add Holding
          </Button>
        )}
      </div>
    </div>
  )
}
