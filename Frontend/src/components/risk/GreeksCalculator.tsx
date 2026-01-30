'use client'

import { useMemo, useState } from 'react'
import { Calculator, TrendingUp, Clock, Activity, Percent } from 'lucide-react'
import { cn, formatCurrency } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

export type OptionType = 'call' | 'put'

export interface GreeksInput {
  spotPrice: number
  strikePrice: number
  timeToExpiration: number
  volatility: number
  riskFreeRate: number
  optionType: OptionType
}

export interface GreeksResult {
  delta: number
  gamma: number
  theta: number
  vega: number
  rho: number
  d1: number
  d2: number
  optionPrice: number
}

interface GreeksCalculatorProps {
  initialData?: Partial<GreeksInput>
  className?: string
}

const STANDARD_NORMAL = {
  cdf(x: number): number {
    const a1 = 0.254829592
    const a2 = -0.284496736
    const a3 = 1.421413741
    const a4 = -1.453152027
    const a5 = 1.061405429
    const p = 0.3275911

    const sign = x < 0 ? -1 : 1
    const absX = Math.abs(x) / Math.sqrt(2)

    const t = 1.0 / (1.0 + p * absX)
    const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-absX * absX)

    return 0.5 * (1.0 + sign * y)
  },
  pdf(x: number): number {
    return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI)
  }
}

export function calculateGreeks(input: GreeksInput): GreeksResult {
  const { spotPrice, strikePrice, timeToExpiration, volatility, riskFreeRate, optionType } = input

  if (spotPrice <= 0 || strikePrice <= 0 || timeToExpiration <= 0 || volatility <= 0) {
    return { delta: 0, gamma: 0, theta: 0, vega: 0, rho: 0, d1: 0, d2: 0, optionPrice: 0 }
  }

  const sqrtT = Math.sqrt(timeToExpiration)
  const d1 = (Math.log(spotPrice / strikePrice) + (riskFreeRate + 0.5 * volatility * volatility) * timeToExpiration) / (volatility * sqrtT)
  const d2 = d1 - volatility * sqrtT

  let delta: number
  let theta: number
  let rho: number

  if (optionType === 'call') {
    delta = STANDARD_NORMAL.cdf(d1)
    theta = -(spotPrice * STANDARD_NORMAL.pdf(d1) * volatility) / (2 * sqrtT) - riskFreeRate * strikePrice * Math.exp(-riskFreeRate * timeToExpiration) * STANDARD_NORMAL.cdf(d2)
    rho = strikePrice * timeToExpiration * Math.exp(-riskFreeRate * timeToExpiration) * STANDARD_NORMAL.cdf(d2)
  } else {
    delta = -STANDARD_NORMAL.cdf(-d1)
    theta = -(spotPrice * STANDARD_NORMAL.pdf(d1) * volatility) / (2 * sqrtT) + riskFreeRate * strikePrice * Math.exp(-riskFreeRate * timeToExpiration) * STANDARD_NORMAL.cdf(-d2)
    rho = -strikePrice * timeToExpiration * Math.exp(-riskFreeRate * timeToExpiration) * STANDARD_NORMAL.cdf(-d2)
  }

  const gamma = STANDARD_NORMAL.pdf(d1) / (spotPrice * volatility * sqrtT)
  const vega = spotPrice * sqrtT * STANDARD_NORMAL.pdf(d1)

  let optionPrice: number
  if (optionType === 'call') {
    optionPrice = spotPrice * STANDARD_NORMAL.cdf(d1) - strikePrice * Math.exp(-riskFreeRate * timeToExpiration) * STANDARD_NORMAL.cdf(d2)
  } else {
    optionPrice = strikePrice * Math.exp(-riskFreeRate * timeToExpiration) * STANDARD_NORMAL.cdf(-d2) - spotPrice * STANDARD_NORMAL.cdf(-d1)
  }

  return {
    delta: Math.max(-1, Math.min(1, delta)),
    gamma: Math.max(0, gamma),
    theta,
    vega: Math.max(0, vega),
    rho,
    d1,
    d2,
    optionPrice: Math.max(0, optionPrice)
  }
}

function GreekCard({ name, value }: { name: keyof GreeksResult; value: number }) {
  const labels: Record<string, { label: string; description: string; icon: typeof TrendingUp }> = {
    delta: { label: 'Delta (Δ)', description: 'Price sensitivity - change in option price per $1 change in underlying', icon: TrendingUp },
    gamma: { label: 'Gamma (Γ)', description: 'Delta sensitivity - rate of change of delta', icon: Activity },
    theta: { label: 'Theta (Θ)', description: 'Time decay - daily value loss from time passing', icon: Clock },
    vega: { label: 'Vega (ν)', description: 'Volatility sensitivity - change per 1% volatility change', icon: Percent },
    rho: { label: 'Rho (ρ)', description: 'Interest rate sensitivity - change per 1% rate change', icon: Percent }
  }

  const { label, description, icon: Icon } = labels[name] || { label: name, description: '', icon: Calculator }

  const getColor = (val: number, greek: string): string => {
    if (greek === 'theta') return val < 0 ? 'text-red-600' : 'text-green-600'
    if (greek === 'delta') {
      if (val > 0.5) return 'text-green-600'
      if (val < -0.5) return 'text-red-600'
      return 'text-yellow-600'
    }
    return ''
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-help">
            <div className="flex items-center gap-2 mb-2">
              <Icon className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium text-muted-foreground">{label}</span>
            </div>
            <p className={cn('text-2xl font-bold', getColor(value, name))}>
              {value.toFixed(4)}
            </p>
            {name === 'delta' && (
              <p className="text-xs text-muted-foreground mt-1">
                {value >= 0 ? `${(value * 100).toFixed(0)}%` : `${(Math.abs(value) * 100).toFixed(0)}%`} delta
              </p>
            )}
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p className="text-sm">{description}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

export function GreeksCalculator({ initialData, className }: GreeksCalculatorProps) {
  const [spotPrice, setSpotPrice] = useState(initialData?.spotPrice || 100)
  const [strikePrice, setStrikePrice] = useState(initialData?.strikePrice || 100)
  const [timeToExpiration, setTimeToExpiration] = useState(initialData?.timeToExpiration || 0.25)
  const [volatility, setVolatility] = useState(initialData?.volatility || 0.2)
  const [riskFreeRate, setRiskFreeRate] = useState(initialData?.riskFreeRate || 0.05)
  const [optionType, setOptionType] = useState<OptionType>(initialData?.optionType || 'call')

  const greeks = useMemo(() => {
    return calculateGreeks({ spotPrice, strikePrice, timeToExpiration, volatility, riskFreeRate, optionType })
  }, [spotPrice, strikePrice, timeToExpiration, volatility, riskFreeRate, optionType])

  const daysToExpiration = useMemo(() => Math.round(timeToExpiration * 365), [timeToExpiration])

  const intrinsicValue = useMemo(() => {
    if (optionType === 'call') return Math.max(0, spotPrice - strikePrice)
    return Math.max(0, strikePrice - spotPrice)
  }, [spotPrice, strikePrice, optionType])

  const extrinsicValue = useMemo(() => Math.max(0, greeks.optionPrice - intrinsicValue), [greeks.optionPrice, intrinsicValue])

  const moneyness = useMemo(() => spotPrice / strikePrice, [spotPrice, strikePrice])

  const getMoneynessLabel = (): { label: string; variant: 'default' | 'destructive' | 'secondary' | 'outline' } => {
    if (moneyness > 1.05) return { label: 'ITM', variant: 'default' }
    if (moneyness < 0.95) return { label: 'OTM', variant: 'destructive' }
    return { label: 'ATM', variant: 'secondary' }
  }

  const moneynessStatus = getMoneynessLabel()

  return (
    <Card className={cn('', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Options Greeks Calculator
            </CardTitle>
            <CardDescription>Black-Scholes model calculations</CardDescription>
          </div>
          <Badge variant={moneynessStatus.variant}>
            {moneynessStatus.label} ({moneyness.toFixed(2)}x)
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="inputs" className="space-y-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="inputs">Inputs</TabsTrigger>
            <TabsTrigger value="results">Results</TabsTrigger>
          </TabsList>

          <TabsContent value="inputs" className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="spotPrice">Spot Price ($)</Label>
                <Input id="spotPrice" type="number" value={spotPrice} onChange={(e) => setSpotPrice(parseFloat(e.target.value) || 0)} min={0} step={0.01} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="strikePrice">Strike Price ($)</Label>
                <Input id="strikePrice" type="number" value={strikePrice} onChange={(e) => setStrikePrice(parseFloat(e.target.value) || 0)} min={0} step={0.01} />
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Time to Expiration</Label>
                  <span className="text-sm text-muted-foreground">{daysToExpiration} days</span>
                </div>
                <Slider value={[timeToExpiration]} onValueChange={([value]) => setTimeToExpiration(value)} min={0.01} max={2} step={0.01} />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>1 day</span><span>2 years</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Volatility (σ)</Label>
                  <span className="text-sm text-muted-foreground">{(volatility * 100).toFixed(1)}%</span>
                </div>
                <Slider value={[volatility]} onValueChange={([value]) => setVolatility(value)} min={0.01} max={2} step={0.01} />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Risk-Free Rate</Label>
                  <span className="text-sm text-muted-foreground">{(riskFreeRate * 100).toFixed(2)}%</span>
                </div>
                <Slider value={[riskFreeRate]} onValueChange={([value]) => setRiskFreeRate(value)} min={0} max={0.2} step={0.001} />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Option Type</Label>
              <Select value={optionType} onValueChange={(v) => setOptionType(v as OptionType)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="call">Call Option</SelectItem>
                  <SelectItem value="put">Put Option</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <GreekCard name="delta" value={greeks.delta} />
              <GreekCard name="gamma" value={greeks.gamma} />
              <GreekCard name="theta" value={greeks.theta} />
              <GreekCard name="vega" value={greeks.vega} />
              <GreekCard name="rho" value={greeks.rho} />
            </div>

            <div className="p-6 rounded-lg bg-primary/5 border border-primary/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Theoretical Option Price</p>
                  <p className="text-xs text-muted-foreground mt-1">d1: {greeks.d1.toFixed(4)} | d2: {greeks.d2.toFixed(4)}</p>
                </div>
                <p className="text-3xl font-bold">{formatCurrency(greeks.optionPrice)}</p>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
                <div className="text-center">
                  <p className="text-xs text-muted-foreground">Intrinsic Value</p>
                  <p className="text-sm font-semibold">{formatCurrency(intrinsicValue)}</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-muted-foreground">Extrinsic Value</p>
                  <p className="text-sm font-semibold">{formatCurrency(extrinsicValue)}</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-muted-foreground">Break-Even</p>
                  <p className="text-sm font-semibold">{formatCurrency(optionType === 'call' ? strikePrice + greeks.optionPrice : strikePrice - greeks.optionPrice)}</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="p-3 rounded-lg bg-muted">
                <p className="text-muted-foreground">If Stock Goes Up $1</p>
                <p className="font-semibold text-green-600">{formatCurrency(greeks.delta)}</p>
              </div>
              <div className="p-3 rounded-lg bg-muted">
                <p className="text-muted-foreground">If 1 Day Passes</p>
                <p className={cn('font-semibold', greeks.theta < 0 ? 'text-red-600' : 'text-green-600')}>{formatCurrency(greeks.theta)}</p>
              </div>
              <div className="p-3 rounded-lg bg-muted">
                <p className="text-muted-foreground">If Volatility +1%</p>
                <p className="font-semibold text-green-600">{formatCurrency(greeks.vega * 0.01)}</p>
              </div>
              <div className="p-3 rounded-lg bg-muted">
                <p className="text-muted-foreground">If Rates +1%</p>
                <p className={cn('font-semibold', greeks.rho > 0 ? 'text-green-600' : 'text-red-600')}>{formatCurrency(greeks.rho * 0.01)}</p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default GreeksCalculator
