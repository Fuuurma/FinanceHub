'use client';

import { useEffect } from 'react';
import { useMarketStore } from '@/stores/marketStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function MarketOverviewPage() {
  const { marketData, isLoading, error, fetchMarketData, setTimeRange } = useMarketStore();
  const timeRanges = ['1D', '1W', '1M', '3M', '1Y', 'ALL'];

  useEffect(() => {
    fetchMarketData('stock');
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Market Overview</h1>
          <p className="text-muted-foreground">Comprehensive market data and analysis</p>
        </div>
        <div className="flex gap-2">
          <Input placeholder="Search assets..." className="w-64" />
        </div>
      </div>

      <div className="flex gap-2">
        {timeRanges.map((range) => (
          <Button key={range} variant="outline" size="sm" onClick={() => setTimeRange(range)}>
            {range}
          </Button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Market Indices</CardTitle>
          <CardDescription>Major market indices performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {isLoading ? (
              [...Array(6)].map((_, i) => <Skeleton key={i} className="h-24" />)
            ) : (
              [
                { name: 'S&P 500', value: 4875.43, change: 1.23 },
                { name: 'NASDAQ', value: 15234.56, change: 2.45 },
                { name: 'DOW JONES', value: 38234.12, change: 0.89 },
                { name: 'FTSE 100', value: 7567.89, change: -0.34 },
                { name: 'DAX', value: 16789.23, change: 1.56 },
                { name: 'Nikkei 225', value: 34567.89, change: 0.12 },
              ].map((index) => (
                <div key={index.name} className="p-4 border rounded-lg">
                  <div className="font-semibold">{index.name}</div>
                  <div className="text-2xl font-bold">{index.value.toFixed(2)}</div>
                  <div className={`text-sm ${index.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {index.change >= 0 ? '+' : ''}{index.change.toFixed(2)}%
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Market Sectors</CardTitle>
          <CardDescription>Performance by sector</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[
              { name: 'Technology', change: 2.34, volume: 'High' },
              { name: 'Healthcare', change: 1.23, volume: 'Medium' },
              { name: 'Financials', change: -0.45, volume: 'High' },
              { name: 'Energy', change: 3.45, volume: 'Low' },
              { name: 'Consumer', change: 1.56, volume: 'Medium' },
              { name: 'Industrial', change: 0.89, volume: 'High' },
            ].map((sector) => (
              <div key={sector.name} className="p-4 border rounded-lg">
                <div className="flex justify-between items-center">
                  <div className="font-semibold">{sector.name}</div>
                  <div className={`text-sm ${sector.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {sector.change >= 0 ? '+' : ''}{sector.change.toFixed(2)}%
                  </div>
                </div>
                <div className="text-sm text-muted-foreground mt-2">Volume: {sector.volume}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Market News</CardTitle>
          <CardDescription>Latest market news and updates</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { title: 'Fed signals potential rate cut in Q2', time: '2 hours ago', sentiment: 'Bullish' },
              { title: 'Tech stocks surge on AI optimism', time: '4 hours ago', sentiment: 'Bullish' },
              { title: 'Oil prices stabilize amid supply concerns', time: '6 hours ago', sentiment: 'Neutral' },
            ].map((news) => (
              <div key={news.title} className="p-4 border rounded-lg">
                <div className="font-semibold">{news.title}</div>
                <div className="flex justify-between mt-2 text-sm text-muted-foreground">
                  <span>{news.time}</span>
                  <span className="font-medium">{news.sentiment}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
