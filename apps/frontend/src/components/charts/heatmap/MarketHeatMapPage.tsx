'use client';

import React, { useState, useCallback } from 'react';
import { MarketHeatMap } from './MarketHeatMap';
import { useHeatMapData } from '@/hooks/useHeatMapData';
import { HeatMapViewType } from './types';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { RefreshCw, ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRouter } from 'next/navigation';

const VIEW_OPTIONS: { id: HeatMapViewType; label: string; icon: string }[] = [
  { id: 'sp500', label: 'S&P 500', icon: '📊' },
  { id: 'nasdaq', label: 'NASDAQ', icon: '📈' },
  { id: 'dow', label: 'DOW', icon: '📉' },
  { id: 'portfolio', label: 'My Portfolio', icon: '💼' },
  { id: 'watchlist', label: 'Watchlist', icon: '⭐' },
];

export function MarketHeatMapPage() {
  const [view, setView] = useState<HeatMapViewType>('sp500');
  const { data, loading, error, refresh } = useHeatMapData(view);
  const router = useRouter();

  const handleNodeClick = useCallback((node: any) => {
    if (node.type === 'stock' && node.symbol) {
      router.push(`/assets/${node.symbol}`);
    }
  }, [router]);

  const handleRefresh = useCallback(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="container mx-auto p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Market Heat Map</h1>
            <p className="text-muted-foreground text-sm">
              Visual overview of market performance
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={handleRefresh} disabled={loading}>
          <RefreshCw className={cn('h-4 w-4 mr-2', loading && 'animate-spin')} />
          Refresh
        </Button>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-2">
            {VIEW_OPTIONS.map((option) => (
              <Button
                key={option.id}
                variant={view === option.id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setView(option.id)}
                className="gap-2"
              >
                <span>{option.icon}</span>
                <span>{option.label}</span>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {loading && (
        <div className="space-y-4">
          <Skeleton className="h-[600px] w-full rounded-lg" />
        </div>
      )}

      {error && (
        <Card className="border-destructive">
          <CardContent className="p-6 text-center text-destructive">
            <p className="font-medium">Failed to load heat map data</p>
            <p className="text-sm mt-1">{error}</p>
            <Button variant="outline" className="mt-4" onClick={handleRefresh}>
              Try Again
            </Button>
          </CardContent>
        </Card>
      )}

      {!loading && !error && (
        <MarketHeatMap data={data} onNodeClick={handleNodeClick} />

      )}

      <Card>
        <CardContent className="p-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-4 flex-wrap">
            <span>
              <strong>Legend:</strong>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-4 h-4 rounded bg-green-500"></span>
              Gainers
            </span>
            <span className="flex items-center gap-1">
              <span className="w-4 h-4 rounded bg-red-500"></span>
              Losers
            </span>
            <span>
              Box size = Market cap / Portfolio weight
            </span>
            <span>
              Click sectors to drill down to stocks
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
