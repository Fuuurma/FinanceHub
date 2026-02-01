'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { X, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ExpiryDate {
  date: string;
  label: string;
  daysToExpiry: number;
}

interface OptionsFiltersProps {
  expiryDates: ExpiryDate[];
  selectedExpiry: string;
  onExpiryChange: (expiry: string) => void;
  strikeRange: [number, number];
  minStrike: number;
  maxStrike: number;
  onStrikeRangeChange: (range: [number, number]) => void;
  volumeMin: number;
  onVolumeMinChange: (value: number) => void;
  ivRange: [number, number];
  onIVRangeChange: (range: [number, number]) => void;
  sortBy: string;
  onSortByChange: (value: string) => void;
  sortDirection: 'asc' | 'desc';
  onSortDirectionChange: (direction: 'asc' | 'desc') => void;
  filterITM: boolean;
  onFilterITMChange: (value: boolean) => void;
  onReset: () => void;
  onRefresh: () => void;
  isLoading?: boolean;
}

export function OptionsFilters({
  expiryDates,
  selectedExpiry,
  onExpiryChange,
  strikeRange,
  minStrike,
  maxStrike,
  onStrikeRangeChange,
  volumeMin,
  onVolumeMinChange,
  ivRange,
  onIVRangeChange,
  sortBy,
  onSortByChange,
  sortDirection,
  onSortDirectionChange,
  filterITM,
  onFilterITMChange,
  onReset,
  onRefresh,
  isLoading = false,
}: OptionsFiltersProps) {
  const formatCurrency = (value: number) => `$${value.toFixed(0)}`;
  const formatPercent = (value: number) => `${(value * 100).toFixed(0)}%`;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            Filters
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onRefresh}
              disabled={isLoading}
            >
              <RefreshCw className={cn('h-4 w-4 mr-1', isLoading && 'animate-spin')} />
              Refresh
            </Button>
            <Button variant="ghost" size="sm" onClick={onReset}>
              <X className="h-4 w-4 mr-1" />
              Reset
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Expiration Date</label>
            <Select value={selectedExpiry} onValueChange={onExpiryChange}>
              <SelectTrigger>
                <SelectValue placeholder="Select expiry" />
              </SelectTrigger>
              <SelectContent>
                {expiryDates.map(expiry => (
                  <SelectItem key={expiry.date} value={expiry.date}>
                    {expiry.label} ({expiry.daysToExpiry}d)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Sort By</label>
            <div className="flex gap-2">
              <Select value={sortBy} onValueChange={onSortByChange}>
                <SelectTrigger className="flex-1">
                  <SelectValue placeholder="Field" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="strike">Strike</SelectItem>
                  <SelectItem value="bid">Bid</SelectItem>
                  <SelectItem value="ask">Ask</SelectItem>
                  <SelectItem value="iv">IV</SelectItem>
                  <SelectItem value="volume">Volume</SelectItem>
                  <SelectItem value="openInterest">Open Interest</SelectItem>
                  <SelectItem value="delta">Delta</SelectItem>
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="icon"
                onClick={() => onSortDirectionChange(
                  sortDirection === 'asc' ? 'desc' : 'asc'
                )}
              >
                {sortDirection === 'asc' ? '↑' : '↓'}
              </Button>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">
              Min Volume: {volumeMin.toLocaleString()}
            </label>
            <Input
              type="number"
              value={volumeMin}
              onChange={(e) => onVolumeMinChange(parseInt(e.target.value) || 0)}
              min={0}
              step={100}
            />
          </div>

          <div className="flex items-center">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filterITM}
                onChange={(e) => onFilterITMChange(e.target.checked)}
                className="rounded border-gray-300"
              />
              <span className="text-sm font-medium">ITM Options Only</span>
            </label>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Strike Range</span>
            <span className="font-medium">
              {formatCurrency(strikeRange[0])} - {formatCurrency(strikeRange[1])}
            </span>
          </div>
          <Slider
            value={strikeRange}
            onValueChange={(value) => onStrikeRangeChange(value as [number, number])}
            min={minStrike}
            max={maxStrike}
            step={1}
            className="w-full"
          />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">IV Range</span>
            <span className="font-medium">
              {formatPercent(ivRange[0])} - {formatPercent(ivRange[1])}
            </span>
          </div>
          <Slider
            value={ivRange}
            onValueChange={(value) => onIVRangeChange(value as [number, number])}
            min={0}
            max={1}
            step={0.01}
            className="w-full"
          />
        </div>

        <div className="flex flex-wrap gap-2 pt-2">
          <span className="text-xs text-muted-foreground mr-2">Quick Filters:</span>
          {[
            { label: 'ATM ±2%', offset: 0.02 },
            { label: 'ATM ±5%', offset: 0.05 },
            { label: 'Deep ITM', type: 'itm' },
            { label: 'Deep OTM', type: 'otm' },
          ].map(quick => (
            <Button
              key={quick.label}
              variant="outline"
              size="sm"
              className="text-xs"
              onClick={() => {
                if ('offset' in quick) {
                  onStrikeRangeChange([
                    Math.round(minStrike * (1 - quick.offset!)),
                    Math.round(maxStrike * (1 + quick.offset!)),
                  ]);
                } else if (quick.type === 'itm') {
                  onStrikeRangeChange([minStrike, maxStrike]);
                  onFilterITMChange(true);
                }
              }}
            >
              {quick.label}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
