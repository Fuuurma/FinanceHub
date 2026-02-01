'use client';

import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import {
  TrendingUp,
  TrendingDown,
  Clock,
  DollarSign,
  Percent,
  Activity,
  Info,
  BarChart3,
} from 'lucide-react';

interface OptionContract {
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

interface OptionDetailPanelProps {
  contract: OptionContract;
  spotPrice: number;
  onClose?: () => void;
}

const GREEKS_INFO: Record<string, string> = {
  delta: 'Delta measures the option\'s price sensitivity to changes in the underlying asset price.',
  gamma: 'Gamma measures the rate of change of Delta, indicating how stable the Delta is.',
  theta: 'Theta measures time decay - how much value the option loses each day.',
  vega: 'Vega measures sensitivity to changes in implied volatility.',
  rho: 'Rho measures sensitivity to interest rate changes.',
};

const formatCurrency = (value: number, decimals = 2) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;

const formatNumber = (value: number) => {
  if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
  return value.toLocaleString();
};

export function OptionDetailPanel({ contract, spotPrice, onClose }: OptionDetailPanelProps) {
  const isCall = contract.type === 'call';
  const itmText = contract.inTheMoney ? 'ITM' : 'OTM';
  const itmColor = contract.inTheMoney
    ? isCall
      ? 'bg-green-500/10 text-green-700 border-green-500'
      : 'bg-red-500/10 text-red-700 border-red-500'
    : isCall
      ? 'bg-red-500/10 text-red-700 border-red-500'
      : 'bg-green-500/10 text-green-700 border-green-500';

  const breakEven = isCall
    ? contract.strike + contract.bid
    : contract.strike - contract.bid;

  const daysToExpiry = Math.max(
    0,
    Math.ceil((new Date(contract.expiry).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
  );

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Badge variant={isCall ? 'default' : 'destructive'} className="text-sm">
              {isCall ? 'CALL' : 'PUT'}
            </Badge>
            <span className="font-semibold text-lg">{contract.symbol}</span>
            <Badge variant="outline" className={cn('border', itmColor)}>
              {itmText}
            </Badge>
          </div>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              ×
            </Button>
          )}
        </div>
        <CardDescription>
          {contract.strike} Strike • {new Date(contract.expiry).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })} ({daysToExpiry} days)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-3 bg-muted/30 rounded-lg text-center">
            <p className="text-xs text-muted-foreground mb-1">Bid / Ask</p>
            <p className="text-lg font-semibold">
              {formatCurrency(contract.bid)} / {formatCurrency(contract.ask)}
            </p>
            <p className="text-xs text-muted-foreground">
              Spread: {formatCurrency(contract.ask - contract.bid)}
            </p>
          </div>
          <div className="p-3 bg-muted/30 rounded-lg text-center">
            <p className="text-xs text-muted-foreground mb-1">Last</p>
            <p className={cn(
              'text-lg font-semibold',
              contract.change >= 0 ? 'text-green-600' : 'text-red-600'
            )}>
              {formatCurrency(contract.last)}
            </p>
            <p className="text-xs text-muted-foreground">
              {contract.change >= 0 ? '+' : ''}{formatCurrency(contract.change)}
            </p>
          </div>
          <div className="p-3 bg-muted/30 rounded-lg text-center">
            <p className="text-xs text-muted-foreground mb-1">Volume / OI</p>
            <p className="text-lg font-semibold">
              {formatNumber(contract.volume)} / {formatNumber(contract.openInterest)}
            </p>
          </div>
          <div className="p-3 bg-muted/30 rounded-lg text-center">
            <p className="text-xs text-muted-foreground mb-1">Implied Volatility</p>
            <p className="text-lg font-semibold">{formatPercent(contract.iv)}</p>
          </div>
        </div>

        <Separator />

        <div>
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <Activity className="h-4 w-4" />
            The Greeks
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {[
              { key: 'delta', value: contract.delta, icon: TrendingUp },
              { key: 'gamma', value: contract.gamma, icon: BarChart3 },
              { key: 'theta', value: contract.theta, icon: Clock },
              { key: 'vega', value: contract.vega, icon: Activity },
              { key: 'rho', value: contract.rho, icon: DollarSign },
            ].map(({ key, value, icon: Icon }) => (
              <TooltipProvider key={key}>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="p-3 bg-muted/30 rounded-lg cursor-help hover:bg-muted/50 transition-colors">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-muted-foreground">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                        <Info className="h-3 w-3 text-muted-foreground" />
                      </div>
                      <p className={cn(
                        'text-lg font-semibold',
                        key === 'delta' && value >= 0 && isCall && 'text-green-600',
                        key === 'delta' && value < 0 && !isCall && 'text-green-600'
                      )}>
                        {value.toFixed(4)}
                      </p>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p>{GREEKS_INFO[key]}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            ))}
          </div>
        </div>

        <Separator />

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-3 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">Intrinsic Value</p>
            <p className="text-lg font-semibold">
              {formatCurrency(contract.intrinsicValue)}
            </p>
          </div>
          <div className="p-3 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">Time Value</p>
            <p className="text-lg font-semibold">
              {formatCurrency(contract.timeValue)}
            </p>
          </div>
          <div className="p-3 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">Break Even</p>
            <p className="text-lg font-semibold">
              {formatCurrency(breakEven)}
            </p>
          </div>
          <div className="p-3 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">Days to Expiry</p>
            <p className="text-lg font-semibold">{daysToExpiry}</p>
          </div>
        </div>

        <Separator />

        <div className="p-4 bg-muted/20 rounded-lg">
          <h4 className="font-semibold mb-2">Probability Analysis</h4>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-muted-foreground">ITM Probability</p>
              <p className="text-xl font-bold text-green-600">
                {((Math.abs(contract.delta) * 100)).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Break Even Risk</p>
              <p className="text-xl font-semibold">
                {contract.inTheMoney ? 'Low' : 'High'}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Return on Margin</p>
              <p className="text-xl font-semibold">
                {((contract.bid / (spotPrice * 0.1)) * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
