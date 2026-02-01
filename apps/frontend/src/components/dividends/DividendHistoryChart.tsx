'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
  ReferenceLine,
} from 'recharts';
import { cn } from '@/lib/utils';
import { DividendHistoryPoint } from './types';

interface DividendHistoryChartProps {
  positionId?: string;
  portfolioId?: string;
  years?: number;
  className?: string;
}

const formatCurrency = (value: number) => 
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
};

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number; dataKey: string; color: string }>;
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="bg-popover border shadow-lg rounded-lg p-3">
      <p className="font-semibold mb-2">{label}</p>
      {payload.map((entry, idx) => (
        <p key={idx} className="text-sm" style={{ color: entry.color }}>
          {entry.dataKey}: {formatCurrency(entry.value)}
        </p>
      ))}
    </div>
  );
};

export function DividendHistoryChart({
  positionId,
  portfolioId,
  years = 5,
  className,
}: DividendHistoryChartProps) {
  const [loading, setLoading] = useState(true);
  const [chartType, setChartType] = useState<'line' | 'bar'>('line');
  const [data, setData] = useState<DividendHistoryPoint[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('all');
  const [summary, setSummary] = useState({
    totalReceived: 0,
    averagePayment: 0,
    growthRate: 0,
    paymentCount: 0,
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const url = positionId 
        ? `/api/dividends/position/${positionId}?years=${years}`
        : `/api/dividends/history/${portfolioId}?years=${years}`;
      
      const response = await fetch(url);
      if (response.ok) {
        const result = await response.json();
        setData(result.data || mockData);
        setSummary(result.summary || mockSummary);
      } else {
        setData(mockData);
        setSummary(mockSummary);
      }
    } catch {
      setData(mockData);
      setSummary(mockSummary);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [positionId, portfolioId, years]);

  const processedData = useMemo(() => {
    if (selectedSymbol === 'all') return data;

    return data.filter(d => d.symbol === selectedSymbol);
  }, [data, selectedSymbol]);

  const aggregatedData = useMemo(() => {
    const byMonth: Record<string, { total: number; count: number }> = {};

    processedData.forEach(point => {
      const date = new Date(point.date);
      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      
      if (!byMonth[key]) {
        byMonth[key] = { total: 0, count: 0 };
      }
      byMonth[key].total += point.amount;
      byMonth[key].count += 1;
    });

    return Object.entries(byMonth)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, { total }]) => ({
        month,
        date: month,
        total,
        average: total,
      }));
  }, [processedData]);

  const yearlyData = useMemo(() => {
    const byYear: Record<string, number> = {};

    processedData.forEach(point => {
      const year = new Date(point.date).getFullYear().toString();
      byYear[year] = (byYear[year] || 0) + point.amount;
    });

    return Object.entries(byYear)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([year, total]) => ({
        year,
        total,
        growth: 0,
      }))
      .map((item, idx, arr) => {
        if (idx === 0) return item;
        const prev = arr[idx - 1].total;
        item.growth = prev > 0 ? ((item.total - prev) / prev) * 100 : 0;
        return item;
      });
  }, [processedData]);

  const symbols = useMemo(() => {
    const unique = new Set(data.map(d => d.symbol));
    return ['all', ...Array.from(unique)];
  }, [data]);

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[350px] w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Dividend History</CardTitle>
            <CardDescription>
              Last {years} years • {summary.paymentCount} payments • {formatCurrency(summary.totalReceived)} total
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="text-sm border rounded-md px-2 py-1 bg-background"
            >
              {symbols.map(sym => (
                <option key={sym} value={sym}>
                  {sym === 'all' ? 'All Positions' : sym}
                </option>
              ))}
            </select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={chartType} onValueChange={(v) => setChartType(v as any)}>
          <TabsList>
            <TabsTrigger value="line">Monthly</TabsTrigger>
            <TabsTrigger value="bar">Yearly</TabsTrigger>
          </TabsList>

          <TabsContent value="line" className="mt-4">
            <div className="h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={aggregatedData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                    tick={{ fontSize: 12 }}
                    tickLine={false}
                  />
                  <YAxis 
                    tickFormatter={(v) => `$${v}`}
                    tick={{ fontSize: 12 }}
                    tickLine={false}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line 
                    type="monotone" 
                    dataKey="total" 
                    name="Dividends"
                    stroke="hsl(var(--primary))" 
                    strokeWidth={2}
                    dot={false}
                    connectNulls
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </TabsContent>

          <TabsContent value="bar" className="mt-4">
            <div className="h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={yearlyData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis 
                    dataKey="year" 
                    tick={{ fontSize: 12 }}
                    tickLine={false}
                  />
                  <YAxis 
                    tickFormatter={(v) => `$${v}`}
                    tick={{ fontSize: 12 }}
                    tickLine={false}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <ReferenceLine y={0} stroke="hsl(var(--muted-foreground))" />
                  <Bar 
                    dataKey="total" 
                    name="Dividends"
                    fill="hsl(var(--primary))"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
            {yearlyData.length > 1 && (
              <div className="mt-4 p-4 bg-muted/30 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  YoY Growth: 
                  <span className={cn(
                    'font-semibold ml-2',
                    summary.growthRate >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    {summary.growthRate >= 0 ? '+' : ''}{summary.growthRate.toFixed(2)}%
                  </span>
                </p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

const mockData: DividendHistoryPoint[] = Array.from({ length: 60 }, (_, i) => {
  const date = new Date();
  date.setMonth(date.getMonth() - (59 - i));
  return {
    date: date.toISOString(),
    amount: 50 + Math.random() * 150 + Math.sin(i / 6) * 30,
    symbol: i % 3 === 0 ? 'AAPL' : i % 3 === 1 ? 'MSFT' : 'JNJ',
  };
});

const mockSummary = {
  totalReceived: 8450.25,
  averagePayment: 140.84,
  growthRate: 8.5,
  paymentCount: 60,
};
