import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { useApi } from '@/hooks/useApi';

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
      <Card>
        <CardHeader>
          <CardTitle>Options Pricing Calculator</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <Label>Stock Price ($)</Label>
              <Input
                type="number"
                value={params.S}
                onChange={(e) => setParams({ ...params, S: parseFloat(e.target.value) })}
              />
            </div>
            <div>
              <Label>Strike Price ($)</Label>
              <Input
                type="number"
                value={params.K}
                onChange={(e) => setParams({ ...params, K: parseFloat(e.target.value) })}
              />
            </div>
            <div>
              <Label>Time to Expiry (Years)</Label>
              <Input
                type="number"
                step="0.01"
                value={params.T}
                onChange={(e) => setParams({ ...params, T: parseFloat(e.target.value) })}
              />
            </div>
            <div>
              <Label>Risk-Free Rate (%)</Label>
              <Input
                type="number"
                step="0.01"
                value={params.r * 100}
                onChange={(e) => setParams({ ...params, r: parseFloat(e.target.value) / 100 })}
              />
            </div>
            <div>
              <Label>Volatility (%)</Label>
              <Input
                type="number"
                step="0.01"
                value={params.sigma * 100}
                onChange={(e) => setParams({ ...params, sigma: parseFloat(e.target.value) / 100 })}
              />
            </div>
            <div>
              <Label>Option Type</Label>
              <Select
                value={params.option_type}
                onValueChange={(value) => setParams({ ...params, option_type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="call">Call</SelectItem>
                  <SelectItem value="put">Put</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="p-4 bg-muted rounded-lg">
                <div className="text-sm text-muted-foreground">Option Price</div>
                <div className="text-2xl font-bold">${result.price.toFixed(2)}</div>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <div className="text-sm text-muted-foreground">Delta</div>
                <div className="text-2xl font-bold">{result.delta.toFixed(4)}</div>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <div className="text-sm text-muted-foreground">Gamma</div>
                <div className="text-2xl font-bold">{result.gamma.toFixed(4)}</div>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <div className="text-sm text-muted-foreground">Theta</div>
                <div className="text-2xl font-bold">{result.theta.toFixed(4)}</div>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <div className="text-sm text-muted-foreground">Vega</div>
                <div className="text-2xl font-bold">{result.vega.toFixed(4)}</div>
              </div>
              <div className="p-4 bg-muted rounded-lg">
                <div className="text-sm text-muted-foreground">Rho</div>
                <div className="text-2xl font-bold">{result.rho.toFixed(4)}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
