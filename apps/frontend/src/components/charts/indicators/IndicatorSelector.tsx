'use client';

import React, { useState } from 'react';
import { Settings, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

export type IndicatorType = 
  | 'sma' | 'ema' | 'wma' | 'rsi' | 'macd' | 'bollinger_bands'
  | 'atr' | 'obv' | 'stochastic' | 'williams_r' | 'cci' | 'momentum' | 'roc';

interface Indicator {
  id: string;
  type: IndicatorType;
  period: number;
  color?: string;
  visible: boolean;
}

interface IndicatorConfig {
  type: IndicatorType;
  name: string;
  category: string;
  defaultPeriod: number;
  params: { name: string; type: 'number'; default: number; min: number; max: number }[];
}

const INDICATOR_CONFIGS: IndicatorConfig[] = [
  { type: 'sma', name: 'SMA', category: 'Trend', defaultPeriod: 20, params: [] },
  { type: 'ema', name: 'EMA', category: 'Trend', defaultPeriod: 20, params: [] },
  { type: 'wma', name: 'WMA', category: 'Trend', defaultPeriod: 20, params: [] },
  { type: 'rsi', name: 'RSI', category: 'Momentum', defaultPeriod: 14, params: [{ name: 'period', type: 'number', default: 14, min: 2, max: 50 }] },
  { type: 'macd', name: 'MACD', category: 'Momentum', defaultPeriod: 12, params: [] },
  { type: 'bollinger_bands', name: 'Bollinger Bands', category: 'Volatility', defaultPeriod: 20, params: [{ name: 'std_dev', type: 'number', default: 2, min: 1, max: 3 }] },
  { type: 'atr', name: 'ATR', category: 'Volatility', defaultPeriod: 14, params: [] },
  { type: 'obv', name: 'OBV', category: 'Volume', defaultPeriod: 14, params: [] },
  { type: 'stochastic', name: 'Stochastic', category: 'Momentum', defaultPeriod: 14, params: [] },
  { type: 'williams_r', name: 'Williams %R', category: 'Momentum', defaultPeriod: 14, params: [] },
  { type: 'cci', name: 'CCI', category: 'Momentum', defaultPeriod: 20, params: [] },
  { type: 'momentum', name: 'Momentum', category: 'Momentum', defaultPeriod: 10, params: [] },
  { type: 'roc', name: 'ROC', category: 'Momentum', defaultPeriod: 10, params: [] },
];

const CATEGORY_COLORS: Record<string, string> = {
  'Trend': 'bg-blue-500',
  'Momentum': 'bg-green-500',
  'Volatility': 'bg-orange-500',
  'Volume': 'bg-purple-500',
};

interface IndicatorSelectorProps {
  indicators: Indicator[];
  onAdd: (indicator: Indicator) => void;
  onRemove: (id: string) => void;
  onUpdate: (id: string, updates: Partial<Indicator>) => void;
  className?: string;
}

export function IndicatorSelector({
  indicators,
  onAdd,
  onRemove,
  onUpdate,
  className,
}: IndicatorSelectorProps) {
  const [showDialog, setShowDialog] = useState(false);
  const [selectedType, setSelectedType] = useState<IndicatorType | null>(null);
  const [customPeriod, setCustomPeriod] = useState(14);

  const handleAdd = () => {
    if (!selectedType) return;
    const config = INDICATOR_CONFIGS.find(c => c.type === selectedType);
    const newIndicator: Indicator = {
      id: `${selectedType}-${Date.now()}`,
      type: selectedType,
      period: customPeriod || config?.defaultPeriod || 14,
      visible: true,
    };
    onAdd(newIndicator);
    setShowDialog(false);
    setSelectedType(null);
    setCustomPeriod(14);
  };

  const getIndicatorName = (type: IndicatorType) => {
    return INDICATOR_CONFIGS.find(c => c.type === type)?.name || type;
  };

  const getIndicatorCategory = (type: IndicatorType) => {
    return INDICATOR_CONFIGS.find(c => c.type === type)?.category || 'Other';
  };

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">Technical Indicators</CardTitle>
          <Button size="sm" variant="outline" onClick={() => setShowDialog(true)}>
            <Plus className="h-4 w-4 mr-1" />
            Add
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {indicators.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            No indicators added. Click Add to add one.
          </p>
        ) : (
          <div className="space-y-2">
            {indicators.map((indicator) => (
              <div
                key={indicator.id}
                className="flex items-center justify-between p-2 rounded-lg bg-muted/50"
              >
                <div className="flex items-center gap-2">
                  <Badge className={`${CATEGORY_COLORS[getIndicatorCategory(indicator.type)]} text-xs`}>
                    {getIndicatorName(indicator.type)}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    P: {indicator.period}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    onClick={() => onUpdate(indicator.id, { visible: !indicator.visible })}
                  >
                    <Settings className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-destructive"
                    onClick={() => onRemove(indicator.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Technical Indicator</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div>
              <Label>Indicator Type</Label>
              <Select
                value={selectedType || ''}
                onValueChange={(v) => {
                  setSelectedType(v as IndicatorType);
                  const config = INDICATOR_CONFIGS.find(c => c.type === v);
                  setCustomPeriod(config?.defaultPeriod || 14);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select indicator" />
                </SelectTrigger>
                <SelectContent>
                  {['Trend', 'Momentum', 'Volatility', 'Volume'].map((cat) => (
                    <div key={cat}>
                      <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                        {cat}
                      </div>
                      {INDICATOR_CONFIGS.filter(c => c.category === cat).map((config) => (
                        <SelectItem key={config.type} value={config.type}>
                          {config.name}
                        </SelectItem>
                      ))}
                    </div>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Period</Label>
              <Input
                type="number"
                value={customPeriod}
                onChange={(e) => setCustomPeriod(parseInt(e.target.value) || 14)}
                min={1}
                max={200}
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleAdd} disabled={!selectedType}>
                Add Indicator
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
