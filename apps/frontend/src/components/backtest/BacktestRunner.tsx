'use client';

import React, { useState } from 'react';
import { Play, Clock, TrendingUp, TrendingDown, DollarSign, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface BacktestResult {
  total_return_pct: number;
  annual_return_pct: number;
  max_drawdown_pct: number;
  sharpe_ratio: number;
  win_rate: number;
  total_trades: number;
  profit_factor: number;
}

interface BacktestRunnerProps {
  className?: string;
}

const STRATEGIES = [
  { id: 'sma_crossover', name: 'SMA Crossover', description: 'Fast/Slow SMA signals' },
  { id: 'rsi', name: 'RSI Mean Reversion', description: 'Buy oversold, sell overbought' },
];

export function BacktestRunner({ className }: BacktestRunnerProps) {
  const [symbol, setSymbol] = useState('AAPL');
  const [strategy, setStrategy] = useState('sma_crossover');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [capital, setCapital] = useState('100000');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);

  const runBacktest = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/backtest/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy_type: strategy,
          symbol,
          start_date: startDate,
          end_date: endDate,
          initial_capital: parseFloat(capital),
        }),
      });
      const data = await response.json();
      if (data.metrics) {
        setResult(data.metrics);
      }
    } catch (error) {
      console.error('Backtest failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getReturnColor = (value: number) => {
    if (value > 0) return 'text-green-500';
    if (value < 0) return 'text-red-500';
    return 'text-muted-foreground';
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Strategy Backtester
        </CardTitle>
        <CardDescription>Test trading strategies on historical data</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Symbol</Label>
              <Input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} placeholder="AAPL" />
            </div>
            <div>
              <Label>Strategy</Label>
              <Select value={strategy} onValueChange={setStrategy}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {STRATEGIES.map((s) => (
                    <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label>Start Date</Label>
              <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            </div>
            <div>
              <Label>End Date</Label>
              <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </div>
            <div>
              <Label>Capital ($)</Label>
              <Input type="number" value={capital} onChange={(e) => setCapital(e.target.value)} />
            </div>
          </div>

          <Button onClick={runBacktest} disabled={loading} className="w-full">
            {loading ? (
              <><Progress value={undefined} className="mr-2 h-2 w-4 animate-pulse" /> Running...</>
            ) : (
              <><Play className="mr-2 h-4 w-4" /> Run Backtest</>
            )}
          </Button>

          {result && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4 p-4 bg-muted rounded-lg">
              <div className="text-center">
                <p className={`text-2xl font-bold ${getReturnColor(result.total_return_pct)}`}>
                  {result.total_return_pct >= 0 ? '+' : ''}{result.total_return_pct.toFixed(2)}%
                </p>
                <p className="text-xs text-muted-foreground">Total Return</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{result.sharpe_ratio.toFixed(2)}</p>
                <p className="text-xs text-muted-foreground">Sharpe Ratio</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{result.win_rate.toFixed(1)}%</p>
                <p className="text-xs text-muted-foreground">Win Rate</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-500">-{result.max_drawdown_pct.toFixed(2)}%</p>
                <p className="text-xs text-muted-foreground">Max Drawdown</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{result.total_trades}</p>
                <p className="text-xs text-muted-foreground">Total Trades</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{result.profit_factor.toFixed(2)}</p>
                <p className="text-xs text-muted-foreground">Profit Factor</p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
