'use client';

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export interface IVSkewDataPoint {
  strike: number;
  callIV: number | null;
  putIV: number | null;
  midIV: number | null;
}

interface IVSkewChartProps {
  data: IVSkewDataPoint[];
  spotPrice: number;
  symbol: string;
  expiry: string;
  className?: string;
}

const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || payload.length === 0) return null;

  const data = payload[0]?.payload;
  return (
    <div className="bg-popover border shadow-lg rounded-lg p-3">
      <p className="font-semibold mb-2">Strike: ${label.toFixed(2)}</p>
      {data.callIV !== null && (
        <p className="text-green-600 text-sm">
          Call IV: {formatPercent(data.callIV)}
        </p>
      )}
      {data.putIV !== null && (
        <p className="text-red-600 text-sm">
          Put IV: {formatPercent(data.putIV)}
        </p>
      )}
      {data.midIV !== null && (
        <p className="text-blue-600 text-sm">
          Mid IV: {formatPercent(data.midIV)}
        </p>
      )}
      {data.callIV !== null && data.putIV !== null && (
        <p className="text-muted-foreground text-sm mt-1">
          Skew: {formatPercent(data.callIV - data.putIV)}
        </p>
      )}
    </div>
  );
};

export function IVSkewChart({ data, spotPrice, symbol, expiry, className }: IVSkewChartProps) {
  const processedData = useMemo(() => {
    return data
      .filter(d => d.callIV !== null || d.putIV !== null)
      .sort((a, b) => a.strike - b.strike);
  }, [data]);

  const chartData = useMemo(() => {
    return processedData.map(d => ({
      ...d,
      callIV: d.callIV !== null ? d.callIV * 100 : undefined,
      putIV: d.putIV !== null ? d.putIV * 100 : undefined,
      midIV: d.midIV !== null ? d.midIV * 100 : undefined,
    }));
  }, [processedData]);

  const minIV = useMemo(() => {
    const values = processedData
      .filter(d => d.callIV !== null || d.putIV !== null)
      .flatMap(d => [d.callIV, d.putIV].filter(Boolean) as number[]);
    return Math.min(...values) * 100 - 5;
  }, [processedData]);

  const maxIV = useMemo(() => {
    const values = processedData
      .filter(d => d.callIV !== null || d.putIV !== null)
      .flatMap(d => [d.callIV, d.putIV].filter(Boolean) as number[]);
    return Math.max(...values) * 100 + 5;
  }, [processedData]);

  const callLineColor = '#22c55e';
  const putLineColor = '#ef4444';
  const midLineColor = '#3b82f6';

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Implied Volatility Skew</CardTitle>
            <CardDescription>
              {symbol} - {expiry} Expiration
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-green-600 border-green-600">
              Calls
            </Badge>
            <Badge variant="outline" className="text-red-600 border-red-600">
              Puts
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="callGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={callLineColor} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={callLineColor} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="putGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={putLineColor} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={putLineColor} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="strike"
                tickFormatter={(value) => `$${value.toFixed(0)}`}
                className="text-xs"
                tick={{ fill: 'muted-foreground' }}
              />
              <YAxis
                domain={[minIV, maxIV]}
                tickFormatter={(value) => `${value.toFixed(0)}%`}
                className="text-xs"
                tick={{ fill: 'muted-foreground' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <ReferenceLine
                x={spotPrice}
                stroke="#eab308"
                strokeDasharray="5 5"
                label={{
                  value: 'Spot',
                  position: 'top',
                  fill: '#eab308',
                  fontSize: 12,
                }}
              />
              {chartData.some(d => d.callIV !== undefined) && (
                <Area
                  type="monotone"
                  dataKey="callIV"
                  name="Call IV"
                  stroke={callLineColor}
                  strokeWidth={2}
                  fill="url(#callGradient)"
                  dot={false}
                  connectNulls
                />
              )}
              {chartData.some(d => d.putIV !== undefined) && (
                <Area
                  type="monotone"
                  dataKey="putIV"
                  name="Put IV"
                  stroke={putLineColor}
                  strokeWidth={2}
                  fill="url(#putGradient)"
                  dot={false}
                  connectNulls
                />
              )}
              {chartData.some(d => d.midIV !== undefined) && (
                <Line
                  type="monotone"
                  dataKey="midIV"
                  name="Mid IV"
                  stroke={midLineColor}
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  connectNulls
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 grid grid-cols-3 gap-4 text-center">
          <div className="p-3 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">Min IV</p>
            <p className="text-lg font-semibold">
              {formatPercent(Math.min(...processedData.flatMap(d => [d.callIV, d.putIV].filter(Boolean) as number[])))}
            </p>
          </div>
          <div className="p-3 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">Max IV</p>
            <p className="text-lg font-semibold">
              {formatPercent(Math.max(...processedData.flatMap(d => [d.callIV, d.putIV].filter(Boolean) as number[])))}
            </p>
          </div>
          <div className="p-3 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">Skew (25Δ)</p>
            <p className="text-lg font-semibold text-muted-foreground">
              —
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
