'use client'

import { useState, useMemo, useCallback, useEffect, useRef } from 'react'
import { createChart, IChartApi, ColorType, CrosshairMode, LineData, Time } from 'lightweight-charts'
import { useTheme } from 'next-themes'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { cn, formatCurrency } from '@/lib/utils'
import { Download, TrendingUp, TrendingDown, Info, DollarSign, Activity } from 'lucide-react'

export type OptionType = 'call' | 'put'

export interface OptionLeg {
  type: OptionType
  strike: number
  quantity: number
  premium: number
  expiration?: string
}

export interface PayoffScenario {
  underlyingPrice: number
  payoff: number
  profit: number
  breakEven?: boolean
}

export interface OptionsPayoffChartProps {
  symbol: string
  currentPrice: number
  legs?: OptionLeg[]
  strategies?: Array<{ name: string; legs: OptionLeg[] }>
  loading?: boolean
  className?: string
}

type StrategyType = 'custom' | 'long-call' | 'long-put' | 'covered-call' | 'protective-put' | 'straddle' | 'strangle' | 'bull-call-spread' | 'bear-put-spread' | 'iron-condor'

function generatePayoffData(legs: OptionLeg[], priceRange: number): PayoffScenario[] {
  const currentPrice = legs.reduce((sum, leg) => sum + leg.strike, 0) / legs.length || 100
  const minPrice = currentPrice * (1 - priceRange)
  const maxPrice = currentPrice * (1 + priceRange)
  const step = (maxPrice - minPrice) / 100

  const data: PayoffScenario[] = []

  for (let price = minPrice; price <= maxPrice; price += step) {
    let payoff = 0
    let cost = 0

    legs.forEach(leg => {
      const intrinsic = leg.type === 'call'
        ? Math.max(0, price - leg.strike)
        : Math.max(0, leg.strike - price)
      payoff += intrinsic * leg.quantity * 100
      cost += leg.premium * leg.quantity * 100
    })

    data.push({
      underlyingPrice: price,
      payoff: payoff - cost,
      profit: payoff - cost,
      breakEven: Math.abs(payoff - cost) < 1,
    })
  }

  return data
}

function generateStrategyLegs(strategy: StrategyType, currentPrice: number): OptionLeg[] {
  const strikeDistance = currentPrice * 0.05

  switch (strategy) {
    case 'long-call':
      return [{ type: 'call', strike: currentPrice, quantity: 1, premium: currentPrice * 0.05 }]
    case 'long-put':
      return [{ type: 'put', strike: currentPrice, quantity: 1, premium: currentPrice * 0.05 }]
    case 'covered-call':
      return [
        { type: 'call', strike: currentPrice * 1.05, quantity: 1, premium: currentPrice * 0.03 },
      ]
    case 'protective-put':
      return [
        { type: 'put', strike: currentPrice * 0.95, quantity: 1, premium: currentPrice * 0.03 },
      ]
    case 'straddle':
      return [
        { type: 'call', strike: currentPrice, quantity: 1, premium: currentPrice * 0.05 },
        { type: 'put', strike: currentPrice, quantity: 1, premium: currentPrice * 0.05 },
      ]
    case 'strangle':
      return [
        { type: 'call', strike: currentPrice * 1.05, quantity: 1, premium: currentPrice * 0.03 },
        { type: 'put', strike: currentPrice * 0.95, quantity: 1, premium: currentPrice * 0.03 },
      ]
    case 'bull-call-spread':
      return [
        { type: 'call', strike: currentPrice, quantity: 1, premium: currentPrice * 0.06 },
        { type: 'call', strike: currentPrice * 1.05, quantity: 1, premium: currentPrice * 0.03 },
      ]
    case 'bear-put-spread':
      return [
        { type: 'put', strike: currentPrice, quantity: 1, premium: currentPrice * 0.06 },
        { type: 'put', strike: currentPrice * 0.95, quantity: 1, premium: currentPrice * 0.03 },
      ]
    case 'iron-condor':
      return [
        { type: 'put', strike: currentPrice * 0.90, quantity: 1, premium: currentPrice * 0.02 },
        { type: 'put', strike: currentPrice * 0.95, quantity: 1, premium: currentPrice * 0.03 },
        { type: 'call', strike: currentPrice * 1.05, quantity: 1, premium: currentPrice * 0.03 },
        { type: 'call', strike: currentPrice * 1.10, quantity: 1, premium: currentPrice * 0.02 },
      ]
    default:
      return []
  }
}

function OptionsPayoffChartSkeleton() {
  return (
    <div className="w-full rounded-lg border bg-card">
      <div className="p-4 border-b">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-32" />
      </div>
      <Skeleton className="h-80 w-full" />
    </div>
  )
}

export function OptionsPayoffChart({ symbol, currentPrice, legs: propLegs, strategies, loading = false, className }: OptionsPayoffChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const lineRef = useRef<any>(null)
  const [strategy, setStrategy] = useState<StrategyType>('straddle')
  const [legs, setLegs] = useState<OptionLeg[]>(() => propLegs || generateStrategyLegs('straddle', currentPrice))
  const [priceRange, setPriceRange] = useState(0.3)
  const { theme } = useTheme()

  const isDark = theme === 'dark'
  const payoffData = useMemo(() => generatePayoffData(legs, priceRange), [legs, priceRange])

  const stats = useMemo(() => {
    const maxProfit = Math.max(...payoffData.map(d => d.payoff))
    const maxLoss = Math.min(...payoffData.map(d => d.payoff))
    const breakEvens = payoffData.filter(d => d.breakEven).map(d => d.underlyingPrice)
    const maxProfitPrice = payoffData.find(d => d.payoff === maxProfit)?.underlyingPrice
    const maxLossPrice = payoffData.find(d => d.payoff === maxLoss)?.underlyingPrice

    return { maxProfit, maxLoss, breakEvens, maxProfitPrice, maxLossPrice }
  }, [payoffData])

  useEffect(() => {
    if (propLegs) {
      setLegs(propLegs)
    }
  }, [propLegs])

  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: isDark ? '#0a0a0a' : '#ffffff' },
        textColor: isDark ? '#d4d4d4' : '#1a1a1a',
      },
      grid: {
        vertLines: { color: isDark ? '#262626' : '#e5e5e5' },
        horzLines: { color: isDark ? '#262626' : '#e5e5e5' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 350,
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: {
        borderColor: isDark ? '#262626' : '#e5e5e5',
      },
      timeScale: {
        borderColor: isDark ? '#262626' : '#e5e5e5',
      },
    })

    const lineSeries = (chart as any).addLineSeries({
      color: '#3b82f6',
      lineWidth: 2,
    })

    chartRef.current = chart
    lineRef.current = lineSeries

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }

    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [isDark])

  useEffect(() => {
    if (!lineRef.current || !payoffData.length) return

    const lineData: LineData[] = payoffData.map(d => ({
      time: d.underlyingPrice as Time,
      value: d.payoff,
    }))

    lineRef.current.setData(lineData)

    if (chartRef.current) {
      chartRef.current.timeScale().fitContent()
    }
  }, [payoffData])

  const handleStrategyChange = useCallback((newStrategy: string) => {
    setStrategy(newStrategy as StrategyType)
    setLegs(generateStrategyLegs(newStrategy as StrategyType, currentPrice))
  }, [currentPrice])

  const handleExport = useCallback(() => {
    const csvData = payoffData.map(d => ({
      'Underlying Price': d.underlyingPrice.toFixed(2),
      'Payoff': d.payoff.toFixed(2),
      'Break Even': d.breakEven ? 'Yes' : 'No',
    }))
    const csv = ['Underlying Price,Payoff,Break Even', ...csvData.map(row => Object.values(row).join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${symbol}_payoff_chart.csv`
    a.click()
  }, [payoffData, symbol])

  if (loading) return <OptionsPayoffChartSkeleton />

  return (
    <div className={cn('rounded-lg border bg-card', className)}>
      <div className="flex items-center justify-between p-4 border-b">
        <div>
          <h3 className="font-semibold text-lg">Options Payoff Chart</h3>
          <p className="text-sm text-muted-foreground">{symbol} - Profit/Loss analysis at expiration</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={strategy} onValueChange={handleStrategyChange}>
            <SelectTrigger className="w-40" aria-label="Select strategy">
              <SelectValue placeholder="Strategy" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="custom">Custom</SelectItem>
              <SelectItem value="long-call">Long Call</SelectItem>
              <SelectItem value="long-put">Long Put</SelectItem>
              <SelectItem value="covered-call">Covered Call</SelectItem>
              <SelectItem value="protective-put">Protective Put</SelectItem>
              <SelectItem value="straddle">Straddle</SelectItem>
              <SelectItem value="strangle">Strangle</SelectItem>
              <SelectItem value="bull-call-spread">Bull Call Spread</SelectItem>
              <SelectItem value="bear-put-spread">Bear Put Spread</SelectItem>
              <SelectItem value="iron-condor">Iron Condor</SelectItem>
            </SelectContent>
          </Select>
          <Select value={priceRange.toString()} onValueChange={(v) => setPriceRange(parseFloat(v))}>
            <SelectTrigger className="w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="0.15">±15%</SelectItem>
              <SelectItem value="0.20">±20%</SelectItem>
              <SelectItem value="0.30">±30%</SelectItem>
              <SelectItem value="0.50">±50%</SelectItem>
            </SelectContent>
          </Select>
          <Button size="sm" variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-1" />
            Export
          </Button>
        </div>
      </div>

      <div className="p-4 border-b bg-muted/30">
        <div className="grid grid-cols-4 gap-4">
          <div className="p-3 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="text-xs text-green-700 font-medium">Max Profit</span>
            </div>
            <p className="text-xl font-bold text-green-700">
              {stats.maxProfit > 100000 ? 'Unlimited' : formatCurrency(stats.maxProfit)}
            </p>
            {stats.maxProfitPrice && stats.maxProfit < 100000 && (
              <p className="text-xs text-green-600">@ {formatCurrency(stats.maxProfitPrice)}</p>
            )}
          </div>
          <div className="p-3 bg-red-50 rounded-lg border border-red-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <span className="text-xs text-red-700 font-medium">Max Loss</span>
            </div>
            <p className="text-xl font-bold text-red-700">{formatCurrency(Math.abs(stats.maxLoss))}</p>
          </div>
          <div className="p-3 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground font-medium">Break Even</span>
            </div>
            <p className="text-xl font-bold">
              {stats.breakEvens.length > 0 ? stats.breakEvens.map(be => formatCurrency(be)).join(', ') : 'N/A'}
            </p>
          </div>
          <div className="p-3 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs text-muted-foreground font-medium">Legs</span>
            </div>
            <p className="text-xl font-bold">{legs.length}</p>
          </div>
        </div>
      </div>

      <div ref={chartContainerRef} style={{ height: 350 }} />

      <div className="p-4 border-t">
        <h4 className="font-semibold mb-3">Position Legs</h4>
        <div className="space-y-2">
          {legs.map((leg, i) => (
            <div key={i} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-3">
                <Badge className={cn(leg.type === 'call' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700')}>
                  {leg.type.toUpperCase()}
                </Badge>
                <span className="font-medium">Strike: {formatCurrency(leg.strike)}</span>
                <span className="text-muted-foreground">×{leg.quantity}</span>
              </div>
              <span className="text-sm">Premium: {formatCurrency(leg.premium)}</span>
            </div>
          ))}
        </div>
        <div className="flex items-center gap-2 mt-4 text-xs text-muted-foreground">
          <Info className="h-4 w-4" />
          <span>Payoff calculated at expiration. Does not account for time value or implied volatility changes.</span>
        </div>
      </div>
    </div>
  )
}

export default OptionsPayoffChart
