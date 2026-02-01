import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { useApi } from '@/hooks/useApi';
import { Calculator, TrendingUp, TrendingDown, Zap } from 'lucide-react';

interface OptionResult {
  price: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
}

interface OptionsCalculatorProps {
  symbol?: string;
  currentPrice?: number;
}

export function OptionsCalculator({ symbol = 'AAPL', currentPrice = 150 }: OptionsCalculatorProps) {
  const [params, setParams] = useState({
    S: currentPrice,
    K: currentPrice,
    T: 0.25,
    r: 0.05,
    sigma: 0.3,
    option_type: 'call',
  });
  const [result, setResult] = useState<OptionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const api = useApi();

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/options/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error calculating option:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    handleCalculate();
  }, [params]);

  return (
    <div className="space-y-6">
      <Card className="rounded-none border-1">
        <CardHeader className="border-b-1">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            Options Pricing Calculator
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <Label className="text-xs font-bold uppercase mb-2 block">Stock Price ($)</Label>
              <Input
                type="number"
                value={params.S}
                onChange={(e) => setParams({ ...params, S: parseFloat(e.target.value) })}
                className="rounded-none border-1 font-mono"
              />
            </div>
            <div>
              <Label className="text-xs font-bold uppercase mb-2 block">Strike Price ($)</Label>
              <Input
                type="number"
                value={params.K}
                onChange={(e) => setParams({ ...params, K: parseFloat(e.target.value) })}
                className="rounded-none border-1 font-mono"
              />
            </div>
            <div>
              <Label className="text-xs font-bold uppercase mb-2 block">Time to Expiry (Years)</Label>
              <Input
                type="number"
                step="0.01"
                value={params.T}
                onChange={(e) => setParams({ ...params, T: parseFloat(e.target.value) })}
                className="rounded-none border-1 font-mono"
              />
            </div>
            <div>
              <Label className="text-xs font-bold uppercase mb-2 block">Risk-Free Rate (%)</Label>
              <Input
                type="number"
                step="0.01"
                value={params.r * 100}
                onChange={(e) => setParams({ ...params, r: parseFloat(e.target.value) / 100 })}
                className="rounded-none border-1 font-mono"
              />
            </div>
            <div>
              <Label className="text-xs font-bold uppercase mb-2 block">Volatility (%)</Label>
              <Input
                type="number"
                step="0.01"
                value={params.sigma * 100}
                onChange={(e) => setParams({ ...params, sigma: parseFloat(e.target.value) / 100 })}
                className="rounded-none border-1 font-mono"
              />
            </div>
            <div>
              <Label className="text-xs font-bold uppercase mb-2 block">Option Type</Label>
              <Select
                value={params.option_type}
                onValueChange={(value) => setParams({ ...params, option_type: value })}
              >
                <SelectTrigger className="rounded-none border-1 font-mono">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="call" className="font-mono">Call</SelectItem>
                  <SelectItem value="put" className="font-mono">Put</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {result && (
        <Card className="rounded-none border-1">
          <CardHeader className="border-b-1 bg-muted/30">
            <CardTitle className="font-black uppercase flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Results
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="border-1 p-4">
                <div className="text-xs font-bold uppercase text-muted-foreground mb-1">Option Price</div>
                <div className="text-2xl font-black font-mono">${result.price.toFixed(2)}</div>
              </div>
              <div className="border-1 p-4">
                <div className="text-xs font-bold uppercase text-muted-foreground mb-1">Delta</div>
                <div className="text-2xl font-black font-mono flex items-center gap-1">
                  {result.delta >= 0 ? (
                    <TrendingUp className="h-4 w-4 text-success" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-destructive" />
                  )}
                  {result.delta.toFixed(4)}
                </div>
              </div>
              <div className="border-1 p-4">
                <div className="text-xs font-bold uppercase text-muted-foreground mb-1">Gamma</div>
                <div className="text-2xl font-black font-mono">{result.gamma.toFixed(4)}</div>
              </div>
              <div className="border-1 p-4">
                <div className="text-xs font-bold uppercase text-muted-foreground mb-1">Theta</div>
                <div className="text-2xl font-black font-mono">{result.theta.toFixed(4)}</div>
              </div>
              <div className="border-1 p-4">
                <div className="text-xs font-bold uppercase text-muted-foreground mb-1">Vega</div>
                <div className="text-2xl font-black font-mono">{result.vega.toFixed(4)}</div>
              </div>
              <div className="border-1 p-4">
                <div className="text-xs font-bold uppercase text-muted-foreground mb-1">Rho</div>
                <div className="text-2xl font-black font-mono">{result.rho.toFixed(4)}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
