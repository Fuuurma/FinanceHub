'use client';

import { useEffect } from 'react';
import { useMarketStore } from '@/stores/marketStore';
import { useWatchlistStore } from '@/stores/watchlistStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { AssetType } from '@/types/market';

export default function MarketDashboardPage() {
  const { marketData, selectedAsset, isLoading, error, fetchMarketData, setSelectedAssetType } = useMarketStore();
  const { watchlists, fetchWatchlists } = useWatchlistStore();

  useEffect(() => {
    fetchMarketData(AssetType.Stock);
    fetchWatchlists();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Market Dashboard</h1>
          <p className="text-muted-foreground">Real-time market data and analytics</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => fetchMarketData(AssetType.Stock)}>Stocks</Button>
          <Button variant="outline" onClick={() => fetchMarketData(AssetType.Crypto)}>Crypto</Button>
          <Button variant="outline" onClick={() => fetchMarketData(AssetType.ETF)}>ETFs</Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{marketData.length}</div>
            <p className="text-xs text-muted-foreground">+12.5% from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Market Cap</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$45.2T</div>
            <p className="text-xs text-muted-foreground">+2.1% today</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">24h Volume</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$89.4B</div>
            <p className="text-xs text-muted-foreground">+8.3% from yesterday</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Watchlists</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{watchlists.length}</div>
            <p className="text-xs text-muted-foreground">{watchlists.reduce((acc, w) => acc + w.symbols.length, 0)} symbols tracked</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Movers</CardTitle>
            <CardDescription>Best performing assets today</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-16" />
                ))}
              </div>
            ) : error ? (
              <div className="text-red-500">{error}</div>
            ) : (
              <div className="space-y-4">
                {marketData.slice(0, 5).map((asset) => (
                  <div key={asset.symbol} className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{asset.symbol}</div>
                      <div className="text-sm text-muted-foreground">{asset.name}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">${asset.price.toFixed(2)}</div>
                      <div className="text-sm text-green-500">+{asset.changePercent.toFixed(2)}%</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Market Watchlist</CardTitle>
            <CardDescription>Your tracked assets</CardDescription>
          </CardHeader>
          <CardContent>
            {watchlists.length === 0 ? (
              <p className="text-muted-foreground">No watchlists yet. Create one to track assets.</p>
            ) : (
              <div className="space-y-4">
                {watchlists.slice(0, 3).map((watchlist) => (
                  <div key={watchlist.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <div className="font-semibold">{watchlist.name}</div>
                      <div className="text-sm text-muted-foreground">{watchlist.symbols.length} symbols</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
