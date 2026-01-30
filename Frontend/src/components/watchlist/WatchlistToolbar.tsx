'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Search, Filter, SortAsc, Download, Upload, RefreshCw } from 'lucide-react'

interface WatchlistToolbarProps {
  onSearch?: (query: string) => void
  onSort?: (sortBy: string) => void
  onFilter?: (filterBy: string) => void
  onExport?: () => void
  onImport?: () => void
  onRefresh?: () => void
  className?: string
}

export function WatchlistToolbar({
  onSearch,
  onSort,
  onFilter,
  onExport,
  onImport,
  onRefresh,
  className,
}: WatchlistToolbarProps) {
  return (
    <div className={cn('flex items-center gap-3 flex-wrap', className)}>
      <div className="relative flex-1 min-w-[200px]">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search symbols..."
          className="pl-9"
          onChange={(e) => onSearch?.(e.target.value)}
        />
      </div>

      <Select onValueChange={(v) => onFilter?.(v)}>
        <SelectTrigger className="w-[140px]">
          <Filter className="h-4 w-4 mr-2" />
          <SelectValue placeholder="Filter" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Stocks</SelectItem>
          <SelectItem value="gainers">Gainers Only</SelectItem>
          <SelectItem value="losers">Losers Only</SelectItem>
          <SelectItem value="new">New Additions</SelectItem>
        </SelectContent>
      </Select>

      <Select onValueChange={(v) => onSort?.(v)}>
        <SelectTrigger className="w-[140px]">
          <SortAsc className="h-4 w-4 mr-2" />
          <SelectValue placeholder="Sort" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="name">Name</SelectItem>
          <SelectItem value="price">Price</SelectItem>
          <SelectItem value="change">% Change</SelectItem>
          <SelectItem value="added">Date Added</SelectItem>
        </SelectContent>
      </Select>

      <div className="flex items-center gap-2">
        {onExport && (
          <Button variant="outline" size="sm" onClick={onExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        )}
        {onImport && (
          <Button variant="outline" size="sm" onClick={onImport}>
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
        )}
        {onRefresh && (
          <Button variant="outline" size="sm" onClick={onRefresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  )
}

export default WatchlistToolbar
