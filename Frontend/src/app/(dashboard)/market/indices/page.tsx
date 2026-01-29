'use client';

import { useEffect } from 'react';
import { useMarketStore } from '@/stores/marketStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export default function MarketIndicesPage() {
  const { marketData, isLoading, error, fetchMarketData } = useMarketStore();

  useEffect(() => {
    fetchMarketData('index');
  }, []);

  const indices = [
    { symbol: 'SPX', name: 'S&P 500', price: 4875.43, change: 1.23, volume: 2.3 },
    { symbol: 'NDX', name: 'NASDAQ-100', price: 15234.56, change: 2.45, volume: 1.8 },
    { symbol: 'DJI', name: 'DOW JONES', price: 38234.12, change: 0.89, volume: 0.9 },
    { symbol: 'UKX', name: 'FTSE 100', price: 7567.89, change: -0.34, volume: 0.7 },
    { symbol: 'DAX', name: 'DAX 40', price: 16789.23, change: 1.56, volume: 1.2 },
    { symbol: 'NKY', name: 'Nikkei 225', price: 34567.89, change: 0.12, volume: 1.5 },
    { symbol: 'SHANGHAI', name: 'Shanghai Composite', price: 2890.45, change: -0.67, volume: 2.1 },
    { symbol: 'RTS', name: 'MOEX Russia', price: 3421.56, change: 0.45, volume: 0.5 },
    { symbol: 'BSE', name: 'BSE Sensex', price: 71234.56, change: 0.89, volume: 1.1 },
    { symbol: 'TSX', name: 'S&P/TSX', price: 19876.34, change: 0.34, volume: 0.8 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Market Indices</h1>
          <p className="text-muted-foreground">Global market indices and performance</p>
        </div>
        <Button onClick={() => fetchMarketData('index')}>Refresh</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Major Indices</CardTitle>
          <CardDescription>Real-time performance of global market indices</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(10)].map((_, i) => <Skeleton key={i} className="h-24" />)}
            </div>
          ) : error ? (
            <div className="text-red-500">{error}</div>
          ) : (
            <div className="space-y-4">
              {indices.map((index) => (
                <div key={index.symbol} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-4">
                    <Badge variant="outline">{index.symbol}</Badge>
                    <div>
                      <div className="font-semibold">{index.name}</div>
                      <div className="text-sm text-muted-foreground">Volume: {index.volume}B</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{index.price.toFixed(2)}</div>
                    <div className={`text-sm ${index.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {index.change >= 0 ? '+' : ''}{index.change.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Gainers</CardTitle>
            <CardDescription>Best performing indices today</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {indices.filter(i => i.change > 0).sort((a, b) => b.change - a.change).slice(0, 5).map((index) => (
                <div key={index.symbol} className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold">{index.symbol}</div>
                    <div className="text-sm text-muted-foreground">{index.name}</div>
                  </div>
                  <div className="text-green-500 font-semibold">+{index.change.toFixed(2)}%</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Losers</CardTitle>
            <CardDescription>Worst performing indices today</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {indices.filter(i => i.change < 0).sort((a, b) => a.change - b.change).slice(0, 5).map((index) => (
                <div key={index.symbol} className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold">{index.symbol}</div>
                    <div className="text-sm text-muted-foreground">{index.name}</div>
                  </div>
                  <div className="text-red-500 font-semibold">{index.change.toFixed(2)}%</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
