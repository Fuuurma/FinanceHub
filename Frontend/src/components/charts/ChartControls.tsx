'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import {
  BarChart3,
  LineChart,
  TrendingUp,
  GripHorizontal,
  CandlestickChart,
  Activity,
  Settings2,
} from 'lucide-react'
import type { ChartType, Timeframe } from './TradingViewChart'

interface ChartControlsProps {
  symbol: string
  currentTimeframe: Timeframe
  currentType: ChartType
  showVolume?: boolean
  availableIndicators?: string[]
  activeIndicators?: string[]
  onSymbolChange?: (symbol: string) => void
  onTimeframeChange?: (tf: Timeframe) => void
  onTypeChange?: (type: ChartType) => void
  onVolumeToggle?: (show: boolean) => void
  onIndicatorToggle?: (indicator: string, show: boolean) => void
}

const TIMEFRAMES: { value: Timeframe; label: string }[] = [
  { value: '1m', label: '1m' },
  { value: '5m', label: '5m' },
  { value: '15m', label: '15m' },
  { value: '1h', label: '1H' },
  { value: '4h', label: '4H' },
  { value: '1d', label: '1D' },
  { value: '1w', label: '1W' },
  { value: '1M', label: '1M' },
]

const CHART_TYPES: { value: ChartType; label: string; icon: React.ReactNode }[] = [
  { value: 'candlestick', label: 'Candlestick', icon: <CandlestickChart className="h-4 w-4" /> },
  { value: 'line', label: 'Line', icon: <LineChart className="h-4 w-4" /> },
  { value: 'area', label: 'Area', icon: <TrendingUp className="h-4 w-4" /> },
  { value: 'bar', label: 'Bar', icon: <GripHorizontal className="h-4 w-4" /> },
]

const AVAILABLE_INDICATORS = [
  { id: 'sma20', label: 'SMA 20' },
  { id: 'sma50', label: 'SMA 50' },
  { id: 'sma200', label: 'SMA 200' },
  { id: 'ema12', label: 'EMA 12' },
  { id: 'ema26', label: 'EMA 26' },
  { id: 'rsi14', label: 'RSI 14' },
  { id: 'macd', label: 'MACD' },
  { id: 'bollinger', label: 'Bollinger Bands' },
]

export function ChartControls({
  symbol,
  currentTimeframe,
  currentType,
  showVolume = true,
  availableIndicators = [],
  activeIndicators = [],
  onSymbolChange,
  onTimeframeChange,
  onTypeChange,
  onVolumeToggle,
  onIndicatorToggle,
}: ChartControlsProps) {
  const [symbolInput, setSymbolInput] = useState(symbol)

  const handleSymbolSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (symbolInput.trim()) {
      onSymbolChange?.(symbolInput.toUpperCase().trim())
    }
  }

  const currentTypeInfo = CHART_TYPES.find((t) => t.value === currentType)

  return (
    <div className="flex flex-wrap items-center gap-2 p-3 border rounded-lg bg-card">
      <form onSubmit={handleSymbolSubmit} className="flex items-center gap-2">
        <Input
          type="text"
          placeholder="Symbol"
          value={symbolInput}
          onChange={(e) => setSymbolInput(e.target.value.toUpperCase())}
          className="w-24 h-8 text-sm font-mono"
        />
        <Button type="submit" size="sm" variant="secondary">
          Go
        </Button>
      </form>

      <div className="h-6 w-px bg-border" />

      <div className="flex items-center gap-1">
        {TIMEFRAMES.map((tf) => (
          <Button
            key={tf.value}
            variant={currentTimeframe === tf.value ? 'default' : 'ghost'}
            size="sm"
            className="h-8 px-2 text-xs"
            onClick={() => onTimeframeChange?.(tf.value)}
          >
            {tf.label}
          </Button>
        ))}
      </div>

      <div className="h-6 w-px bg-border" />

      <Select
        value={currentType}
        onValueChange={(value) => onTypeChange?.(value as ChartType)}
      >
        <SelectTrigger className="h-8 w-32">
          <SelectValue>
            <div className="flex items-center gap-2">
              {currentTypeInfo?.icon}
              <span className="text-xs">{currentTypeInfo?.label}</span>
            </div>
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {CHART_TYPES.map((type) => (
            <SelectItem key={type.value} value={type.value}>
              <div className="flex items-center gap-2">
                {type.icon}
                <span>{type.label}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <div className="h-6 w-px bg-border" />

      <Button
        variant={showVolume ? 'default' : 'ghost'}
        size="sm"
        className="h-8"
        onClick={() => onVolumeToggle?.(!showVolume)}
      >
        <Activity className="h-4 w-4" />
      </Button>

      {AVAILABLE_INDICATORS.length > 0 && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="h-8">
              <Settings2 className="h-4 w-4 mr-1" />
              Indicators
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>Technical Indicators</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {AVAILABLE_INDICATORS.map((indicator) => (
              <DropdownMenuCheckboxItem
                key={indicator.id}
                checked={activeIndicators.includes(indicator.id)}
                onCheckedChange={(checked) =>
                  onIndicatorToggle?.(indicator.id, checked as boolean)
                }
              >
                {indicator.label}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      )}

      <div className="ml-auto flex items-center gap-2 text-sm text-muted-foreground">
        <span className="font-mono font-bold">{symbol}</span>
      </div>
    </div>
  )
}
