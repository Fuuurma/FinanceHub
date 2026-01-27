'use client';

import { useEffect } from 'react';
import { useMarketStore } from '@/stores/marketStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { AssetType } from '@/types/market';

export default function MarketStocksPage() {
  const { marketData, isLoading, error, fetchMarketData, setSelectedAsset } = useMarketStore();

  useEffect(() => {
    fetchMarketData(AssetType.Stock);
  }, []);

  const handleAssetClick = (symbol: string) => {
    setSelectedAsset(marketData.find(a => a.symbol === symbol) || null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Stock Market</h1>
          <p className="text-muted-foreground">Browse and analyze stocks</p>
        </div>
        <div className="flex gap-2">
          <Input placeholder="Search stocks..." className="w-64" />
          <Button onClick={() => fetchMarketData(AssetType.Stock)}>Refresh</Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Stocks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8,234</div>
            <p className="text-xs text-muted-foreground">+23 this week</p>
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
            <CardTitle className="text-sm font-medium">Active Traders</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1.2M</div>
            <p className="text-xs text-muted-foreground">+5.7% this week</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Stock Listings</CardTitle>
          <CardDescription>Browse all available stocks</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(12)].map((_, i) => <Skeleton key={i} className="h-32" />)}
            </div>
          ) : error ? (
            <div className="text-red-500">{error}</div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {marketData.map((stock) => (
                <div
                  key={stock.symbol}
                  onClick={() => handleAssetClick(stock.symbol)}
                  className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-2">
                    <Badge variant="outline">{stock.symbol}</Badge>
                    <div className={`text-sm ${stock.changePercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                    </div>
                  </div>
                  <div className="font-semibold mb-1">{stock.name}</div>
                  <div className="text-2xl font-bold">${stock.price.toFixed(2)}</div>
                  <div className="text-sm text-muted-foreground mt-2">
                    Vol: {stock.volume?.toLocaleString() || 'N/A'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
