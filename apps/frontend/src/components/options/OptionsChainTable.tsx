'use client';

import React, { useState, useMemo, useCallback } from 'react';
import {
  ChevronUp,
  ChevronDown,
  Info,
  Filter,
  Download,
  RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

export interface OptionContract {
  strike: number;
  expiry: string;
  type: 'call' | 'put';
  bid: number;
  ask: number;
  last: number;
  change: number;
  changePercent: number;
  volume: number;
  openInterest: number;
  iv: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
  intrinsicValue: number;
  timeValue: number;
  inTheMoney: boolean;
  symbol: string;
}

export interface OptionsChainData {
  symbol: string;
  spotPrice: number;
  calls: OptionContract[];
  puts: OptionContract[];
  lastUpdated: string;
}

interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

interface OptionsChainTableProps {
  data: OptionsChainData;
  onSelectContract?: (contract: OptionContract) => void;
  selectedStrike?: number | null;
  filter?: 'all' | 'itm' | 'otm';
  onFilterChange?: (filter: 'all' | 'itm' | 'otm') => void;
}

const GREEKS_LABELS: Record<string, string> = {
  delta: 'Delta',
  gamma: 'Gamma',
  theta: 'Theta',
  vega: 'Vega',
  rho: 'Rho',
};

export function OptionsChainTable({
  data,
  onSelectContract,
  selectedStrike,
  filter = 'all',
  onFilterChange,
}: OptionsChainTableProps) {
  const [sortConfig, setSortConfig] = useState<SortConfig>({ field: 'strike', direction: 'asc' });

  const formatCurrency = useCallback((value: number, decimals = 2) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  }, []);

  const formatNumber = useCallback((value: number) => {
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
    return value.toLocaleString();
  }, []);

  const formatPercent = useCallback((value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  }, []);

  const getSortedStrikes = useCallback(() => {
    const allStrikes = [...new Set([
      ...data.calls.map(c => c.strike),
      ...data.puts.map(p => p.strike),
    ])].sort((a, b) => sortConfig.direction === 'asc' ? a - b : b - a);

    return allStrikes;
  }, [data.calls, data.puts, sortConfig.direction]);

  const getContract = useCallback((strike: number, type: 'call' | 'put') => {
    if (type === 'call') {
      return data.calls.find(c => c.strike === strike);
    }
    return data.puts.find(p => p.strike === strike);
  }, [data.calls, data.puts]);

  const getMoneynessClass = useCallback((strike: number, type: 'call' | 'put') => {
    const spot = data.spotPrice;
    const isATM = Math.abs(strike - spot) < spot * 0.02;
    const isITM = type === 'call' ? strike < spot : strike > spot;

    if (isATM) return 'bg-muted/40';
    if (isITM) return type === 'call' ? 'bg-green-500/10' : 'bg-red-500/10';
    return type === 'call' ? 'bg-red-500/5' : 'bg-green-500/5';
  }, [data.spotPrice]);

  const getChangeColor = useCallback((change: number) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return '';
  }, []);

  const handleSort = useCallback((field: string) => {
    setSortConfig(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  }, []);

  const handleRowClick = useCallback((contract: OptionContract) => {
    onSelectContract?.(contract);
  }, [onSelectContract]);

  const handleExport = useCallback(() => {
    const headers = ['Symbol', 'Type', 'Strike', 'Bid', 'Ask', 'Last', 'Change %', 'Volume', 'OI', 'IV', 'Delta', 'Gamma', 'Theta', 'Vega', 'Rho'];
    const rows = [
      headers.join(','),
      ...data.calls.map(c => [
        c.symbol, 'call', c.strike, c.bid, c.ask, c.last,
        c.changePercent.toFixed(2), c.volume, c.openInterest,
        c.iv.toFixed(4), c.delta.toFixed(4), c.gamma.toFixed(4),
        c.theta.toFixed(4), c.vega.toFixed(4), c.rho.toFixed(4),
      ].join(',')),
      ...data.puts.map(p => [
        p.symbol, 'put', p.strike, p.bid, p.ask, p.last,
        p.changePercent.toFixed(2), p.volume, p.openInterest,
        p.iv.toFixed(4), p.delta.toFixed(4), p.gamma.toFixed(4),
        p.theta.toFixed(4), p.vega.toFixed(4), p.rho.toFixed(4),
      ].join(',')),
    ];

    const csv = rows.join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${data.symbol}_options_chain_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [data]);

  const SortIcon = useCallback(({ field }: { field: string }) => {
    if (sortConfig.field !== field) return <span className="opacity-30">↕</span>;
    return sortConfig.direction === 'asc'
      ? <ChevronUp className="h-3 w-3" />
      : <ChevronDown className="h-3 w-3" />;
  }, [sortConfig]);

  const filteredStrikes = useMemo(() => {
    const strikes = getSortedStrikes();
    if (filter === 'all') return strikes;

    return strikes.filter(strike => {
      const call = data.calls.find(c => c.strike === strike);
      const put = data.puts.find(p => p.strike === strike);

      if (filter === 'itm') {
        return (call?.inTheMoney) || (put?.inTheMoney);
      }
      if (filter === 'otm') {
        return (!call?.inTheMoney) || (!put?.inTheMoney);
      }
      return true;
    });
  }, [getSortedStrikes, data.calls, data.puts, filter]);

  return (
    <Card className="w-full overflow-hidden">
      <CardHeader className="pb-3 border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">
            {data.symbol} Options Chain
          </CardTitle>
          <div className="flex items-center gap-2">
            {onFilterChange && (
              <div className="flex gap-1">
                {(['all', 'itm', 'otm'] as const).map(f => (
                  <Button
                    key={f}
                    variant={filter === f ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => onFilterChange(f)}
                    className="text-xs"
                  >
                    {f.toUpperCase()}
                  </Button>
                ))}
              </div>
            )}
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="h-4 w-4 mr-1" />
              Export
            </Button>
          </div>
        </div>
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>Spot: {formatCurrency(data.spotPrice)}</span>
          <span>Last updated: {data.lastUpdated}</span>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-muted/50 border-b">
                <th className="text-left p-2 font-semibold text-xs uppercase tracking-wider text-muted-foreground">
                  Calls
                </th>
                <th
                  className="text-center p-2 font-semibold cursor-pointer hover:bg-muted/70 transition-colors"
                  onClick={() => handleSort('strike')}
                >
                  <div className="flex items-center justify-center gap-1">
                    Strike
                    <SortIcon field="strike" />
                  </div>
                </th>
                <th className="text-right p-2 font-semibold text-xs uppercase tracking-wider text-muted-foreground">
                  Puts
                </th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b bg-muted/30">
                <td colSpan={3} className="p-2">
                  <div className="grid grid-cols-15 gap-1 text-xs text-muted-foreground text-center">
                    <span>Bid</span>
                    <span>Ask</span>
                    <span>Last</span>
                    <span>Δ</span>
                    <span>Γ</span>
                    <span>Θ</span>
                    <span>V</span>
                    <span>R</span>
                    <span>IV</span>
                    <span>Vol</span>
                    <span>OI</span>
                    <span className="col-span-2">Strike</span>
                    <span>OI</span>
                    <span>Vol</span>
                    <span>IV</span>
                    <span>R</span>
                    <span>V</span>
                    <span>Θ</span>
                    <span>Γ</span>
                    <span>Δ</span>
                    <span>Last</span>
                    <span>Ask</span>
                    <span>Bid</span>
                  </div>
                </td>
              </tr>
              {filteredStrikes.map(strike => {
                const call = getContract(strike, 'call');
                const put = getContract(strike, 'put');
                const isSpotRow = Math.abs(strike - data.spotPrice) < data.spotPrice * 0.01;
                const moneynessClass = getMoneynessClass(strike, 'call');

                return (
                  <tr
                    key={strike}
                    className={cn(
                      'border-b hover:bg-muted/50 cursor-pointer transition-colors',
                      selectedStrike === strike && 'bg-primary/5 ring-2 ring-primary',
                      isSpotRow && 'bg-yellow-500/10',
                      moneynessClass
                    )}
                    onClick={() => {
                      if (call) handleRowClick(call);
                      else if (put) handleRowClick(put);
                    }}
                  >
                    <td colSpan={3} className="p-1">
                      <div className="grid grid-cols-15 gap-1 items-center">
                        {call ? (
                          <>
                            <span className="text-right font-medium">{formatCurrency(call.bid)}</span>
                            <span className="text-left">{formatCurrency(call.ask)}</span>
                            <span className={cn('text-right', getChangeColor(call.change))}>
                              {formatCurrency(call.last)}
                            </span>
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <span className={cn('text-right cursor-help', call.delta >= 0 ? 'text-green-600' : 'text-red-600')}>
                                    {call.delta.toFixed(3)}
                                  </span>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Delta: {call.delta.toFixed(4)}</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                            <span className="text-right">{call.gamma.toFixed(4)}</span>
                            <span className="text-right">{call.theta.toFixed(3)}</span>
                            <span className="text-right">{call.vega.toFixed(3)}</span>
                            <span className="text-right">{call.rho.toFixed(3)}</span>
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <span className="text-right cursor-help">{formatPercent(call.iv)}</span>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Implied Volatility: {formatPercent(call.iv)}</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                            <span className="text-right">{formatNumber(call.volume)}</span>
                            <span className="text-right">{formatNumber(call.openInterest)}</span>
                          </>
                        ) : (
                          <div className="col-span-11 text-muted-foreground text-center">—</div>
                        )}

                        <span className={cn(
                          'col-span-2 text-center font-bold text-base',
                          isSpotRow && 'bg-yellow-500/20 text-yellow-700 dark:text-yellow-400 rounded px-2'
                        )}>
                          ${strike.toFixed(2)}
                        </span>

                        {put ? (
                          <>
                            <span className="text-right">{formatNumber(put.openInterest)}</span>
                            <span className="text-right">{formatNumber(put.volume)}</span>
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <span className="text-right cursor-help">{formatPercent(put.iv)}</span>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Implied Volatility: {formatPercent(put.iv)}</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                            <span className="text-right">{put.rho.toFixed(3)}</span>
                            <span className="text-right">{put.vega.toFixed(3)}</span>
                            <span className="text-right">{put.theta.toFixed(3)}</span>
                            <span className="text-right">{put.gamma.toFixed(4)}</span>
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <span className={cn('text-right cursor-help', put.delta >= 0 ? 'text-green-600' : 'text-red-600')}>
                                    {put.delta.toFixed(3)}
                                  </span>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Delta: {put.delta.toFixed(4)}</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                            <span className={cn('text-right', getChangeColor(put.change))}>
                              {formatCurrency(put.last)}
                            </span>
                            <span className="text-left">{formatCurrency(put.ask)}</span>
                            <span className="text-left font-medium">{formatCurrency(put.bid)}</span>
                          </>
                        ) : (
                          <div className="col-span-11 text-muted-foreground text-center">—</div>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {filteredStrikes.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            No options found matching your filters
          </div>
        )}
      </CardContent>
    </Card>
  );
}
