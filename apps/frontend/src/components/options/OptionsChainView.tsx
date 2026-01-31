import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useApi } from '@/hooks/useApi';

interface OptionChainItem {
  strike: number;
  price: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
  intrinsic: number;
  moneyness: number;
}

interface OptionsChainViewProps {
  symbol: string;
  currentPrice: number;
}

export function OptionsChainView({ symbol, currentPrice }: OptionsChainViewProps) {
  const [params, setParams] = useState({
    S: currentPrice,
    T: 0.25,
    r: 0.05,
    sigma: 0.3,
    option_type: 'call' as 'call' | 'put',
  });
  const [chain, setChain] = useState<OptionChainItem[]>([]);
  const [loading, setLoading] = useState(false);
  const api = useApi();

  const strikes = React.useMemo(() => {
    const base = params.S;
    return Array.from({ length: 21 }, (_, i) => base * (0.85 + i * 0.015));
  }, [params.S]);

  const fetchChain = async () => {
    setLoading(true);
    try {
      const response = await api.post('/options/chain', {
        ...params,
        strikes: strikes,
      });
      setChain(response.chain || []);
    } catch (error) {
      console.error('Error fetching option chain:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchChain();
  }, [params]);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>{symbol} Options Chain</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <div>
              <label className="text-sm">Time to Expiry</label>
              <Select
                value={String(params.T)}
                onValueChange={(v) => setParams({ ...params, T: parseFloat(v) })}
              >
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0.02">1 Week</SelectItem>
                  <SelectItem value="0.06">2 Weeks</SelectItem>
                  <SelectItem value="0.12">1 Month</SelectItem>
                  <SelectItem value="0.25">3 Months</SelectItem>
                  <SelectItem value="0.5">6 Months</SelectItem>
                  <SelectItem value="1">1 Year</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm">Volatility</label>
              <Select
                value={String(params.sigma)}
                onValueChange={(v) => setParams({ ...params, sigma: parseFloat(v) })}
              >
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0.15">15%</SelectItem>
                  <SelectItem value="0.2">20%</SelectItem>
                  <SelectItem value="0.25">25%</SelectItem>
                  <SelectItem value="0.3">30%</SelectItem>
                  <SelectItem value="0.4">40%</SelectItem>
                  <SelectItem value="0.5">50%</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm">Type</label>
              <Select
                value={params.option_type}
                onValueChange={(v) => setParams({ ...params, option_type: v as 'call' | 'put' })}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="call">Call</SelectItem>
                  <SelectItem value="put">Put</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Strike</th>
                  <th className="text-right p-2">Price</th>
                  <th className="text-right p-2">Delta</th>
                  <th className="text-right p-2">Gamma</th>
                  <th className="text-right p-2">Theta</th>
                  <th className="text-right p-2">Vega</th>
                  <th className="text-right p-2">Intrinsic</th>
                </tr>
              </thead>
              <tbody>
                {chain.map((item) => (
                  <tr key={item.strike} className="border-b hover:bg-muted/50">
                    <td className="p-2">${item.strike.toFixed(2)}</td>
                    <td className="p-2 text-right font-medium">${item.price.toFixed(2)}</td>
                    <td className="p-2 text-right">{item.delta.toFixed(3)}</td>
                    <td className="p-2 text-right">{item.gamma.toFixed(4)}</td>
                    <td className="p-2 text-right">{item.theta.toFixed(3)}</td>
                    <td className="p-2 text-right">{item.vega.toFixed(3)}</td>
                    <td className="p-2 text-right text-muted-foreground">${item.intrinsic.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
