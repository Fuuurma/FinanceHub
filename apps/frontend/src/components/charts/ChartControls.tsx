'use client'

import { useState, useEffect, KeyboardEvent } from 'react'
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
  Search,
  Plus,
  X,
  Star,
  Clock,
  Settings,
} from 'lucide-react'
import type { ChartType, Timeframe } from './TradingViewChart'
import { IndicatorConfig } from '@/lib/utils/technical-indicators'

interface ChartControlsProps {
  symbol: string
  currentTimeframe: Timeframe
  currentType: ChartType
  showVolume?: boolean
  showIndicators?: string[]
  indicatorConfig?: IndicatorConfig
  availableIndicators?: string[]
  activeIndicators?: string[]
  onSymbolChange?: (symbol: string) => void
  onTimeframeChange?: (tf: Timeframe) => void
  onTypeChange?: (type: ChartType) => void
  onVolumeToggle?: (show: boolean) => void
  onIndicatorToggle?: (indicator: string, show: boolean) => void
  onIndicatorConfigChange?: (config: IndicatorConfig) => void
  onOpenIndicatorSettings?: () => void
}

const TIMEFRAMES: { value: Timeframe; label: string; hotkey: string }[] = [
  { value: '1m', label: '1m', hotkey: '1' },
  { value: '5m', label: '5m', hotkey: '2' },
  { value: '15m', label: '15m', hotkey: '3' },
  { value: '1h', label: '1H', hotkey: '4' },
  { value: '4h', label: '4H', hotkey: '5' },
  { value: '1d', label: '1D', hotkey: '6' },
  { value: '1w', label: '1W', hotkey: '7' },
  { value: '1M', label: '1M', hotkey: '8' },
]

const CHART_TYPES: { value: ChartType; label: string; icon: React.ReactNode; hotkey: string }[] = [
  { value: 'candlestick', label: 'Candlestick', icon: <CandlestickChart className="h-4 w-4" />, hotkey: 'c' },
  { value: 'line', label: 'Line', icon: <LineChart className="h-4 w-4" />, hotkey: 'l' },
  { value: 'area', label: 'Area', icon: <TrendingUp className="h-4 w-4" />, hotkey: 'a' },
  { value: 'bar', label: 'Bar', icon: <GripHorizontal className="h-4 w-4" />, hotkey: 'b' },
]

const AVAILABLE_INDICATORS = [
  { id: 'sma20', label: 'SMA 20', category: 'Moving Averages' },
  { id: 'sma50', label: 'SMA 50', category: 'Moving Averages' },
  { id: 'sma200', label: 'SMA 200', category: 'Moving Averages' },
  { id: 'ema12', label: 'EMA 12', category: 'Moving Averages' },
  { id: 'ema26', label: 'EMA 26', category: 'Moving Averages' },
  { id: 'rsi', label: 'RSI 14', category: 'Oscillators' },
  { id: 'macd', label: 'MACD', category: 'Oscillators' },
  { id: 'bollinger', label: 'Bollinger Bands', category: 'Volatility' },
]

const POPULAR_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'BTC', 'ETH']

const RECENT_SYMBOLS_KEY = 'financehub_recent_symbols'

export function ChartControls({
  symbol,
  currentTimeframe,
  currentType,
  showVolume = true,
  showIndicators = [],
  indicatorConfig = {},
  availableIndicators = [],
  activeIndicators = [],
  onSymbolChange,
  onTimeframeChange,
  onTypeChange,
  onVolumeToggle,
  onIndicatorToggle,
  onIndicatorConfigChange,
  onOpenIndicatorSettings,
}: ChartControlsProps) {
  const [symbolInput, setSymbolInput] = useState(symbol)
  const [recentSymbols, setRecentSymbols] = useState<string[]>([])
  const [isSearching, setIsSearching] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem(RECENT_SYMBOLS_KEY)
    if (saved) {
      try {
        setRecentSymbols(JSON.parse(saved))
      } catch {
        setRecentSymbols([])
      }
    }
  }, [])

  const handleSymbolSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (symbolInput.trim()) {
      const newSymbol = symbolInput.toUpperCase().trim()
      onSymbolChange?.(newSymbol)
      addToRecent(newSymbol)
      setSymbolInput(newSymbol)
      setIsSearching(false)
    }
  }

  const handleSymbolSelect = (sym: string) => {
    onSymbolChange?.(sym)
    addToRecent(sym)
    setSymbolInput(sym)
    setIsSearching(false)
  }

  const addToRecent = (sym: string) => {
    setRecentSymbols((prev) => {
      const filtered = prev.filter((s) => s !== sym)
      const updated = [sym, ...filtered].slice(0, 10)
      localStorage.setItem(RECENT_SYMBOLS_KEY, JSON.stringify(updated))
      return updated
    })
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      setIsSearching(false)
    }
  }

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return

      if (e.key >= '1' && e.key <= '8') {
        const tf = TIMEFRAMES.find((t) => t.hotkey === e.key)
        if (tf) onTimeframeChange?.(tf.value)
      }

      if (e.key === 'c' || e.key === 'C') onTypeChange?.('candlestick')
      if (e.key === 'l' || e.key === 'L') onTypeChange?.('line')
      if (e.key === 'a' || e.key === 'A') onTypeChange?.('area')
      if (e.key === 'b' || e.key === 'B') onTypeChange?.('bar')
    }

    window.addEventListener('keydown', handleKeyPress as any)
    return () => window.removeEventListener('keydown', handleKeyPress as any)
  }, [onTimeframeChange, onTypeChange])

  const currentTypeInfo = CHART_TYPES.find((t) => t.value === currentType)

  const groupedIndicators = AVAILABLE_INDICATORS.reduce((acc, indicator) => {
    if (!acc[indicator.category]) acc[indicator.category] = []
    acc[indicator.category].push(indicator)
    return acc
  }, {} as Record<string, typeof AVAILABLE_INDICATORS>)

  const hasActiveIndicators = activeIndicators.length > 0

  return (
    <div className="flex flex-wrap items-center gap-2 p-3 border rounded-lg bg-card shadow-sm">
      <div className="relative">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsSearching(!isSearching)}
          className="h-8"
        >
          <Search className="h-4 w-4" />
        </Button>
        {isSearching && (
          <div className="absolute top-full left-0 mt-1 z-50 w-64 bg-popover border rounded-lg shadow-lg p-2">
            <form onSubmit={handleSymbolSubmit} className="flex gap-1 mb-2">
              <Input
                type="text"
                placeholder="Enter symbol..."
                value={symbolInput}
                onChange={(e) => setSymbolInput(e.target.value.toUpperCase())}
                onKeyDown={handleKeyDown}
                className="h-8 text-sm font-mono"
                autoFocus
              />
              <Button type="submit" size="sm" variant="secondary">
                Go
              </Button>
            </form>
            {recentSymbols.length > 0 && (
              <>
                <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1 px-1">
                  <Clock className="h-3 w-3" />
                  Recent
                </div>
                <div className="flex flex-wrap gap-1 mb-2">
                  {recentSymbols.slice(0, 5).map((sym) => (
                    <Button
                      key={sym}
                      variant="outline"
                      size="sm"
                      className="h-6 text-xs font-mono"
                      onClick={() => handleSymbolSelect(sym)}
                    >
                      {sym}
                    </Button>
                  ))}
                </div>
              </>
            )}
            <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1 px-1">
              <Star className="h-3 w-3" />
              Popular
            </div>
            <div className="flex flex-wrap gap-1">
              {POPULAR_SYMBOLS.map((sym) => (
                <Button
                  key={sym}
                  variant={symbol === sym ? 'default' : 'ghost'}
                  size="sm"
                  className="h-6 text-xs font-mono"
                  onClick={() => handleSymbolSelect(sym)}
                >
                  {sym}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSymbolSubmit} className="flex items-center gap-1">
        <Input
          type="text"
          placeholder="Symbol"
          value={symbolInput}
          onChange={(e) => setSymbolInput(e.target.value.toUpperCase())}
          className="w-20 h-8 text-sm font-mono"
        />
        <Button type="submit" size="sm" variant="secondary">
          <Plus className="h-4 w-4" />
        </Button>
      </form>

      <div className="h-6 w-px bg-border" />

      <div className="flex items-center gap-0.5 bg-muted rounded-md p-0.5">
        {TIMEFRAMES.map((tf) => (
          <Button
            key={tf.value}
            variant={currentTimeframe === tf.value ? 'default' : 'ghost'}
            size="sm"
            className="h-7 px-2 text-xs font-medium"
            onClick={() => onTimeframeChange?.(tf.value)}
            title={`Press ${tf.hotkey}`}
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
        <SelectTrigger className="h-8 w-36">
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
                <span className="text-xs text-muted-foreground ml-2">({type.hotkey})</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <div className="h-6 w-px bg-border" />

      <Button
        variant={showVolume ? 'default' : 'outline'}
        size="sm"
        className="h-8 px-3"
        onClick={() => onVolumeToggle?.(!showVolume)}
      >
        <Activity className="h-4 w-4 mr-1" />
        <span className="text-xs">Vol</span>
      </Button>

      <div className="h-6 w-px bg-border" />

      {hasActiveIndicators && (
        <Button
          variant="outline"
          size="sm"
          className="h-8"
          onClick={onOpenIndicatorSettings}
        >
          <Settings className="h-4 w-4 mr-1" />
          <span className="text-xs">Indicators</span>
          <span className="ml-1 px-1.5 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
            {activeIndicators.length}
          </span>
        </Button>
      )}

      {AVAILABLE_INDICATORS.length > 0 && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant={hasActiveIndicators ? 'default' : 'outline'} size="sm" className="h-8">
              <Settings2 className="h-4 w-4 mr-1" />
              <span className="text-xs">Indicators</span>
              {activeIndicators.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
                  {activeIndicators.length}
                </span>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel className="flex items-center justify-between">
              Technical Indicators
              {activeIndicators.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 text-xs"
                  onClick={() => {
                    activeIndicators.forEach((ind) => onIndicatorToggle?.(ind, false))
                  }}
                >
                  Clear all
                </Button>
              )}
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            {Object.entries(groupedIndicators).map(([category, indicators]) => (
              <div key={category}>
                <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
                  {category}
                </div>
                {indicators.map((indicator) => (
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
                <DropdownMenuSeparator />
              </div>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      )}

      <div className="ml-auto flex items-center gap-2">
        <span className="text-sm font-bold font-mono text-foreground">{symbol}</span>
        {recentSymbols.includes(symbol) && (
          <span className="text-xs text-muted-foreground hidden sm:inline">recent</span>
        )}
      </div>
    </div>
  )
}
