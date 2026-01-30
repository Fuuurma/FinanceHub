'use client'

import { useState, useMemo, useCallback } from 'react'
import { Calculator, RefreshCw } from 'lucide-react'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

export type OptionType = 'call' | 'put'

export interface OptionGreeks {
  delta: number
  gamma: number
  theta: number
  vega: number
  rho: number
  vanna: number
  charm: number
  speed: number
  zomma: number
  color: number
  vor: number
  dvegaDtime: number
}

export interface GreeksInput {
  spotPrice: number
  strikePrice: number
  timeToExpiry: number
  volatility: number
  riskFreeRate: number
  dividendYield: number
  optionType: OptionType
}

export interface GreeksResult extends OptionGreeks {
  blackScholesPrice: number
  intrinsicValue: number
  timeValue: number
  breakeven: number
  probabilityITM: number
}

const DAYS_PER_YEAR = 365

function normalCDF(x: number): number {
  const a1 = 0.254829592, a2 = -0.284496736, a3 = 1.421413741
  const a4 = -1.453152027, a5 = 1.061405429, p = 0.3275911
  const sign = x < 0 ? -1 : 1
  x = Math.abs(x) / Math.sqrt(2)
  const t = 1.0 / (1.0 + p * x)
  const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x)
  return 0.5 * (1.0 + sign * y)
}

function normalPDF(x: number): number {
  return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI)
}

function calculateBlackScholes(spot: number, strike: number, time: number, vol: number, rate: number, dividend: number, optionType: OptionType): { price: number; d1: number; d2: number } {
  const sqrtTime = Math.sqrt(time), volSqrtTime = vol * sqrtTime
  const d1 = (Math.log(spot / strike) + (rate - dividend + 0.5 * vol * vol) * time) / volSqrtTime
  const d2 = d1 - volSqrtTime
  let price: number
  if (optionType === 'call') {
    price = spot * Math.exp(-dividend * time) * normalCDF(d1) - strike * Math.exp(-rate * time) * normalCDF(d2)
  } else {
    price = strike * Math.exp(-rate * time) * normalCDF(-d2) - spot * Math.exp(-dividend * time) * normalCDF(-d1)
  }
  return { price, d1, d2 }
}

export function calculateGreeks(spot: number, strike: number, time: number, vol: number, rate: number, dividend: number, optionType: OptionType): GreeksResult {
  const { price: blackScholesPrice, d1, d2 } = calculateBlackScholes(spot, strike, time, vol, rate, dividend, optionType)
  const sqrtTime = Math.sqrt(time), volSqrtTime = vol * sqrtTime, nd1 = normalCDF(d1), nd2 = normalCDF(d2), n_d1 = normalPDF(d1)
  const expDiv = Math.exp(-dividend * time), expRate = Math.exp(-rate * time)
  const intrinsicValue = optionType === 'call' ? Math.max(0, spot * expDiv - strike * expRate) : Math.max(0, strike * expRate - spot * expDiv)
  const timeValue = Math.max(0, blackScholesPrice - intrinsicValue)
  let delta: number = optionType === 'call' ? expDiv * nd1 : expDiv * (nd1 - 1)
  const gamma = (expDiv * n_d1) / (spot * volSqrtTime)
  let theta: number = optionType === 'call'
    ? (-(spot * vol * expDiv * n_d1) / (2 * sqrtTime) - rate * strike * expRate * nd2 + dividend * spot * expDiv * nd1) / DAYS_PER_YEAR
    : (-(spot * vol * expDiv * n_d1) / (2 * sqrtTime) + rate * strike * expRate * normalCDF(-d2) - dividend * spot * expDiv * normalCDF(-d1)) / DAYS_PER_YEAR
  const vega = (spot * expDiv * n_d1 * sqrtTime) / 100
  let rho: number = optionType === 'call' ? (strike * time * expRate * nd2) / 100 : (-strike * time * expRate * normalCDF(-d2)) / 100
  const vanna = (expDiv * n_d1 * (d1 * d2 - 1)) / 100
  const charm = expDiv * (n_d1 * (rate - dividend) / volSqrtTime + (optionType === 'call' ? -nd1 : nd1 - 1))
  const speed = gamma * (1 - delta / spot)
  const zomma = gamma * (d1 * d2 - 1)
  const color = gamma * (1 - d1 / volSqrtTime)
  const vor = -n_d1 * d1 / vol
  const dvegaDtime = -(spot * expDiv * n_d1) / (2 * sqrtTime)
  const breakeven = optionType === 'call' ? strike * Math.exp(-rate * time) - blackScholesPrice * Math.exp(dividend * time) : strike * Math.exp(-rate * time) + blackScholesPrice * Math.exp(dividend * time)
  const probabilityITM = optionType === 'call' ? normalCDF(d2) : normalCDF(-d2)
  return { delta, gamma, theta, vega, rho, vanna, charm, speed, zomma, color, vor, dvegaDtime, blackScholesPrice, intrinsicValue, timeValue, breakeven, probabilityITM }
}

function GreeksCard({ greeks, label }: { greeks: GreeksResult; label: string }) {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">{label}</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Price</span>
          <span className="font-semibold">{formatCurrency(greeks.blackScholesPrice)}</span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <TooltipProvider><Tooltip><TooltipTrigger asChild><span className="text-xs text-muted-foreground cursor-help border-b border-dotted">Delta</span></TooltipTrigger><TooltipContent className="max-w-xs"><p>Rate of change of option price w.r.t underlying</p></TooltipContent></Tooltip></TooltipProvider>
            <div className={cn('text-lg font-bold', greeks.delta > 0 ? 'text-green-600' : 'text-red-600')}>{greeks.delta.toFixed(4)}</div>
          </div>
          <div className="space-y-1">
            <TooltipProvider><Tooltip><TooltipTrigger asChild><span className="text-xs text-muted-foreground cursor-help border-b border-dotted">Gamma</span></TooltipTrigger><TooltipContent className="max-w-xs"><p>Rate of change of Delta w.r.t underlying</p></TooltipContent></Tooltip></TooltipProvider>
            <div className="text-lg font-bold">{greeks.gamma.toFixed(4)}</div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <TooltipProvider><Tooltip><TooltipTrigger asChild><span className="text-xs text-muted-foreground cursor-help border-b border-dotted">Theta</span></TooltipTrigger><TooltipContent className="max-w-xs"><p>Time decay per day</p></TooltipContent></Tooltip></TooltipProvider>
            <div className="text-lg font-bold text-red-600">{greeks.theta.toFixed(4)}</div>
          </div>
          <div className="space-y-1">
            <TooltipProvider><Tooltip><TooltipTrigger asChild><span className="text-xs text-muted-foreground cursor-help border-b border-dotted">Vega</span></TooltipTrigger><TooltipContent className="max-w-xs"><p>Volatility sensitivity (1%)</p></TooltipContent></Tooltip></TooltipProvider>
            <div className="text-lg font-bold text-green-600">{greeks.vega.toFixed(4)}</div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1"><span className="text-xs text-muted-foreground">Intrinsic</span><div className="text-sm font-semibold">{formatCurrency(greeks.intrinsicValue)}</div></div>
          <div className="space-y-1"><span className="text-xs text-muted-foreground">Time Value</span><div className="text-sm font-semibold">{formatCurrency(greeks.timeValue)}</div></div>
        </div>
        <div className="flex items-center justify-between pt-2 border-t">
          <span className="text-xs text-muted-foreground">Prob. ITM</span>
          <Badge variant={greeks.probabilityITM > 0.5 ? 'default' : 'secondary'}>{formatPercent(greeks.probabilityITM)}</Badge>
        </div>
      </CardContent>
    </Card>
  )
}

export function GreeksCalculator({ className }: { className?: string }) {
  const [inputs, setInputs] = useState<GreeksInput>({ spotPrice: 100, strikePrice: 100, timeToExpiry: 30, volatility: 20, riskFreeRate: 5, dividendYield: 0, optionType: 'call' })
  const greeks = useMemo(() => calculateGreeks(inputs.spotPrice, inputs.strikePrice, inputs.timeToExpiry / DAYS_PER_YEAR, inputs.volatility / 100, inputs.riskFreeRate / 100, inputs.dividendYield / 100, inputs.optionType), [inputs])
  const updateInput = useCallback((key: keyof GreeksInput, value: number | string) => setInputs(prev => ({ ...prev, [key]: value })), [])
  const resetToDefault = useCallback(() => setInputs({ spotPrice: 100, strikePrice: 100, timeToExpiry: 30, volatility: 20, riskFreeRate: 5, dividendYield: 0, optionType: 'call' }), [])
  return (
    <Card className={cn('', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div><CardTitle className="flex items-center gap-2"><Calculator className="h-5 w-5" />Greeks Calculator</CardTitle><CardDescription>Black-Scholes option pricing and Greeks analysis</CardDescription></div>
          <Button variant="outline" size="sm" onClick={resetToDefault}><RefreshCw className="h-4 w-4 mr-2" />Reset</Button>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="inputs" className="w-full">
          <TabsList className="grid w-full grid-cols-2"><TabsTrigger value="inputs">Inputs</TabsTrigger><TabsTrigger value="greeks">Greeks</TabsTrigger></TabsList>
          <TabsContent value="inputs" className="space-y-6 mt-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2"><Label>Option Type</Label><Select value={inputs.optionType} onValueChange={(v) => updateInput('optionType', v as OptionType)}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent><SelectItem value="call">Call</SelectItem><SelectItem value="put">Put</SelectItem></SelectContent></Select></div>
              <div className="space-y-2"><Label>Spot Price ($)</Label><Input type="number" value={inputs.spotPrice} onChange={(e) => updateInput('spotPrice', parseFloat(e.target.value) || 0)} min={0} step={0.01} /></div>
            </div>
            <div className="space-y-2"><div className="flex items-center justify-between"><Label>Strike Price ($)</Label><span className="text-sm font-medium">{formatCurrency(inputs.strikePrice)}</span></div><Slider value={[inputs.strikePrice]} onValueChange={([v]) => updateInput('strikePrice', v)} min={1} max={inputs.spotPrice * 3} step={1} /></div>
            <div className="space-y-2"><div className="flex items-center justify-between"><Label>Days to Expiry</Label><span className="text-sm font-medium">{inputs.timeToExpiry} days</span></div><Slider value={[inputs.timeToExpiry]} onValueChange={([v]) => updateInput('timeToExpiry', v)} min={1} max={365} step={1} /></div>
            <div className="space-y-2"><div className="flex items-center justify-between"><Label>Volatility (%)</Label><span className="text-sm font-medium">{inputs.volatility}%</span></div><Slider value={[inputs.volatility]} onValueChange={([v]) => updateInput('volatility', v)} min={1} max={200} step={0.5} /></div>
            <div className="space-y-2"><div className="flex items-center justify-between"><Label>Risk-Free Rate (%)</Label><span className="text-sm font-medium">{inputs.riskFreeRate}%</span></div><Slider value={[inputs.riskFreeRate]} onValueChange={([v]) => updateInput('riskFreeRate', v)} min={0} max={20} step={0.1} /></div>
            <div className="space-y-2"><div className="flex items-center justify-between"><Label>Dividend Yield (%)</Label><span className="text-sm font-medium">{inputs.dividendYield}%</span></div><Slider value={[inputs.dividendYield]} onValueChange={([v]) => updateInput('dividendYield', v)} min={0} max={20} step={0.1} /></div>
          </TabsContent>
          <TabsContent value="greeks" className="mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <GreeksCard greeks={greeks} label="Option Greeks" />
              <Card className="overflow-hidden"><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Advanced Greeks</CardTitle></CardHeader><CardContent className="space-y-2">
                <div className="grid grid-cols-2 gap-2 text-sm"><div className="flex justify-between"><span className="text-muted-foreground">Rho:</span><span className="font-medium">{greeks.rho.toFixed(4)}</span></div><div className="flex justify-between"><span className="text-muted-foreground">Vanna:</span><span className="font-medium">{greeks.vanna.toFixed(4)}</span></div><div className="flex justify-between"><span className="text-muted-foreground">Charm:</span><span className="font-medium">{greeks.charm.toFixed(4)}</span></div><div className="flex justify-between"><span className="text-muted-foreground">Speed:</span><span className="font-medium">{greeks.speed.toFixed(4)}</span></div><div className="flex justify-between"><span className="text-muted-foreground">Zomma:</span><span className="font-medium">{greeks.zomma.toFixed(4)}</span></div><div className="flex justify-between"><span className="text-muted-foreground">Color:</span><span className="font-medium">{greeks.color.toFixed(4)}</span></div></div>
                <div className="pt-2 border-t"><div className="flex justify-between text-sm"><span className="text-muted-foreground">Breakeven:</span><span className="font-medium">{formatCurrency(greeks.breakeven)}</span></div></div>
              </CardContent></Card>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
