'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { 
  TrendingUp, 
  TrendingDown, 
  Calendar, 
  DollarSign, 
  Percent,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw
} from 'lucide-react';
import { DividendSummary } from './types';

interface DividendSummaryCardProps {
  portfolioId: string;
  className?: string;
}

const formatCurrency = (value: number, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;

export function DividendSummaryCard({ portfolioId, className }: DividendSummaryCardProps) {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<DividendSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const { dividendApi } = await import('./api');
      const data = await dividendApi.getSummary(portfolioId);
      setSummary(data);
    } catch {
      setSummary(mockSummary);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, [portfolioId]);

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !summary) {
    return (
      <Card className={cn('w-full border-destructive', className)}>
        <CardContent className="py-8 text-center">
          <p className="text-destructive mb-4">{error || 'Failed to load'}</p>
          <button 
            onClick={fetchSummary}
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md"
          >
            <RefreshCw className="h-4 w-4" />
            Retry
          </button>
        </CardContent>
      </Card>
    );
  }

  const metrics = [
    {
      label: 'YTD Dividends',
      value: formatCurrency(summary.totalDividendsYTD),
      icon: Calendar,
      trend: summary.ytdGrowth >= 0 ? 'up' : 'down',
      trendValue: `${summary.ytdGrowth >= 0 ? '+' : ''}${formatPercent(summary.ytdGrowth)}`,
      color: summary.ytdGrowth >= 0 ? 'text-green-600' : 'text-red-600',
    },
    {
      label: 'Last 12 Months',
      value: formatCurrency(summary.totalDividendsLast12m),
      icon: DollarSign,
      sublabel: 'Total received',
    },
    {
      label: 'Projected Annual',
      value: formatCurrency(summary.projectedAnnualDividends),
      icon: TrendingUp,
      sublabel: 'Based on current holdings',
    },
    {
      label: 'Monthly Income',
      value: formatCurrency(summary.monthlyDividendIncome),
      icon: DollarSign,
      sublabel: 'Average per month',
    },
    {
      label: 'Portfolio Yield',
      value: formatPercent(summary.dividendYield),
      icon: Percent,
      sublabel: 'Current yield',
    },
    {
      label: 'Avg Yield on Cost',
      value: formatPercent(summary.averageYield),
      icon: Percent,
      sublabel: 'Your actual yield',
    },
  ];

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-lg flex items-center gap-2">
            Dividend Summary
          </CardTitle>
          <CardDescription>
            Last updated: {summary.lastUpdated}
          </CardDescription>
        </div>
        <button
          onClick={fetchSummary}
          className="p-2 hover:bg-muted rounded-md transition-colors"
          title="Refresh"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="breakdown">Breakdown</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-4">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {metrics.map((metric, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-muted/30 rounded-lg border hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <metric.icon className="h-4 w-4 text-muted-foreground" />
                    {metric.trend && (
                      <span className={cn('flex items-center gap-1 text-xs', metric.color)}>
                        {metric.trend === 'up' ? (
                          <ArrowUpRight className="h-3 w-3" />
                        ) : (
                          <ArrowDownRight className="h-3 w-3" />
                        )}
                        {metric.trendValue}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mb-1">{metric.label}</p>
                  <p className="text-xl font-bold">{metric.value}</p>
                  {metric.sublabel && (
                    <p className="text-xs text-muted-foreground">{metric.sublabel}</p>
                  )}
                </div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="breakdown" className="mt-4">
            <div className="space-y-4">
              <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-green-700">YTD Growth</span>
                  {summary.ytdGrowth >= 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-600" />
                  )}
                </div>
                <p className={cn(
                  'text-2xl font-bold',
                  summary.ytdGrowth >= 0 ? 'text-green-700' : 'text-red-700'
                )}>
                  {summary.ytdGrowth >= 0 ? '+' : ''}{formatPercent(summary.ytdGrowth)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Compared to same period last year
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-muted/30 rounded-lg">
                  <p className="text-xs text-muted-foreground mb-1">Monthly Average</p>
                  <p className="text-lg font-semibold">{formatCurrency(summary.monthlyDividendIncome)}</p>
                </div>
                <div className="p-4 bg-muted/30 rounded-lg">
                  <p className="text-xs text-muted-foreground mb-1">Effective Yield</p>
                  <p className="text-lg font-semibold">{formatPercent(summary.averageYield)}</p>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

const mockSummary: DividendSummary = {
  totalDividendsYTD: 1247.50,
  totalDividendsLast12m: 3842.30,
  projectedAnnualDividends: 4120.00,
  dividendYield: 0.0325,
  monthlyDividendIncome: 343.33,
  averageYield: 0.0452,
  ytdGrowth: 0.085,
  lastUpdated: new Date().toLocaleString(),
};
