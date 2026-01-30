'use client';

import { useEffect, useState } from 'react';
import { useMarketStore } from '@/stores/marketStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/ui/page-header';
import { StatsGrid } from '@/components/ui/stats-grid';
import { PageTabs, TabContent } from '@/components/ui/page-tabs';
import { Search, RefreshCw, TrendingUp, TrendingDown, BarChart3, Star, Activity } from 'lucide-react';

export default function MarketStocksPage() {
  const { marketData, isLoading, error, fetchMarketData, setSelectedAsset } = useMarketStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchMarketData('stock');
      setLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, [fetchMarketData]);

  const handleRefresh = () => {
    setLoading(true);
    fetchMarketData('stock');
    setTimeout(() => setLoading(false), 500);
  };

  const handleAssetClick = (symbol: string) => {
    setSelectedAsset(marketData.find(a => a.symbol === symbol) || null);
  };

  const filteredData = marketData.filter(stock =>
    stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
    stock.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const stats = [
    { title: 'Total Stocks', value: '8,234', change: 23, changeLabel: 'this week', icon: BarChart3 },
    { title: 'Market Cap', value: '$45.2T', change: 2.1, changeLabel: 'today', icon: Activity },
    { title: '24h Volume', value: '$89.4B', change: 8.3, changeLabel: 'vs yesterday', icon: RefreshCw },
    { title: 'Gainers', value: '2,341', change: 12.5, changeLabel: 'today', icon: TrendingUp },
  ];

  const tabs = [
    { value: 'all', label: 'All Stocks', icon: BarChart3 },
    { value: 'gainers', label: 'Top Gainers', icon: TrendingUp },
    { value: 'losers', label: 'Top Losers', icon: TrendingDown },
    { value: 'active', label: 'Most Active', icon: Activity },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Stock Market"
        description="Browse and analyze stocks"
        loading={loading}
        onRefresh={handleRefresh}
        actions={
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search stocks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        }
      />

      {error && (
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : (
        <StatsGrid stats={stats} />
      )}

      <PageTabs tabs={tabs} defaultValue="all" tabsClassName="grid w-full grid-cols-4">
        <TabContent value="all" className="space-y-6">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {[...Array(12)].map((_, i) => <Skeleton key={i} className="h-36" />)}
            </div>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Stock Listings</CardTitle>
                <CardDescription>Browse all available stocks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {filteredData.map((stock) => (
                    <div
                      key={stock.symbol}
                      onClick={() => handleAssetClick(stock.symbol)}
                      className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="outline">{stock.symbol}</Badge>
                        <div className={`text-sm font-medium ${stock.change_percent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                        </div>
                      </div>
                      <div className="font-semibold mb-1 truncate">{stock.name}</div>
                      <div className="text-2xl font-bold">${stock.price.toFixed(2)}</div>
                      <div className="text-sm text-muted-foreground mt-2">
                        Vol: {stock.volume?.toLocaleString() || 'N/A'}
                      </div>
                    </div>
                  ))}
                </div>
                {filteredData.length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">
                    <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No stocks found matching "{searchQuery}"</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabContent>

        <TabContent value="gainers" className="space-y-6">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-36" />)}
            </div>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Top Gainers</CardTitle>
                <CardDescription>Stocks with the highest daily gains</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {filteredData
                    .filter(s => s.change_percent > 0)
                    .sort((a, b) => b.change_percent - a.change_percent)
                    .slice(0, 12)
                    .map((stock) => (
                      <div
                        key={stock.symbol}
                        onClick={() => handleAssetClick(stock.symbol)}
                        className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer border-green-100 bg-green-50/50"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <Badge variant="outline" className="border-green-200">{stock.symbol}</Badge>
                          <div className="text-sm font-medium text-green-600 flex items-center">
                            <TrendingUp className="h-3 w-3 mr-1" />
                            +{stock.change_percent.toFixed(2)}%
                          </div>
                        </div>
                        <div className="font-semibold mb-1 truncate">{stock.name}</div>
                        <div className="text-2xl font-bold">${stock.price.toFixed(2)}</div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabContent>

        <TabContent value="losers" className="space-y-6">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-36" />)}
            </div>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Top Losers</CardTitle>
                <CardDescription>Stocks with the highest daily losses</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {filteredData
                    .filter(s => s.change_percent < 0)
                    .sort((a, b) => a.change_percent - b.change_percent)
                    .slice(0, 12)
                    .map((stock) => (
                      <div
                        key={stock.symbol}
                        onClick={() => handleAssetClick(stock.symbol)}
                        className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer border-red-100 bg-red-50/50"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <Badge variant="outline" className="border-red-200">{stock.symbol}</Badge>
                          <div className="text-sm font-medium text-red-600 flex items-center">
                            <TrendingDown className="h-3 w-3 mr-1" />
                            {stock.change_percent.toFixed(2)}%
                          </div>
                        </div>
                        <div className="font-semibold mb-1 truncate">{stock.name}</div>
                        <div className="text-2xl font-bold">${stock.price.toFixed(2)}</div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabContent>

        <TabContent value="active" className="space-y-6">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-36" />)}
            </div>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Most Active</CardTitle>
                <CardDescription>Stocks with the highest trading volume</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {filteredData
                    .sort((a, b) => (b.volume || 0) - (a.volume || 0))
                    .slice(0, 12)
                    .map((stock) => (
                      <div
                        key={stock.symbol}
                        onClick={() => handleAssetClick(stock.symbol)}
                        className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <Badge variant="outline">{stock.symbol}</Badge>
                          <div className={`text-sm font-medium ${stock.change_percent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                          </div>
                        </div>
                        <div className="font-semibold mb-1 truncate">{stock.name}</div>
                        <div className="text-2xl font-bold">${stock.price.toFixed(2)}</div>
                        <div className="text-sm text-muted-foreground mt-2 flex items-center gap-1">
                          <Activity className="h-3 w-3" />
                          Vol: {stock.volume ? (stock.volume / 1000000).toFixed(1) + 'M' : 'N/A'}
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabContent>
      </PageTabs>
    </div>
  );
}
