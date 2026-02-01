'use client'

import { useState } from 'react'
import { DollarSign, Percent, TrendingDown, Target, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'

interface PositionSizeResult {
  position_shares: number
  position_value: number
  position_percentage: number
  risk_amount: number
  risk_per_share: number
  max_loss: number
  stop_loss_distance: number
  error?: string
}

export interface PositionSizeInput {
  portfolio_value: number
  account_balance: number
  risk_per_trade: number
  entry_price: number
  stop_loss_price: number
  position_type?: 'LONG' | 'SHORT'
}

interface PositionSizeCalculatorProps {
  onCalculate?: (result: PositionSizeResult, input: PositionSizeInput) => void
  className?: string
}

const POSITION_TYPES = ['LONG', 'SHORT'] as const

export function PositionSizeCalculator({ onCalculate, className }: PositionSizeCalculatorProps) {
  const [positionType, setPositionType] = useState<typeof POSITION_TYPES[number]>('LONG')
  const [portfolioValue, setPortfolioValue] = useState<string>('')
  const [accountBalance, setAccountBalance] = useState<string>('')
  const [riskPerTrade, setRiskPerTrade] = useState<string>('1')
  const [entryPrice, setEntryPrice] = useState<string>('')
  const [stopLossPrice, setStopLossPrice] = useState<string>('')
  const [result, setResult] = useState<PositionSizeResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const calculate = async () => {
    const input: PositionSizeInput = {
      portfolio_value: parseFloat(portfolioValue) || 0,
      account_balance: parseFloat(accountBalance) || 0,
      risk_per_trade: (parseFloat(riskPerTrade) || 0) / 100,
      entry_price: parseFloat(entryPrice) || 0,
      stop_loss_price: parseFloat(stopLossPrice) || 0,
      position_type: positionType
    }

    try {
      const response = await fetch('/risk/position-size', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input)
      })

      const data = await response.json()
      if (data.error) {
        setError(data.error)
        setResult(null)
      } else {
        setResult(data)
        setError(null)
        onCalculate?.(data, input)
      }
    } catch (err) {
      setError('Failed to calculate position size')
      setResult(null)
    }
  }

  const estimatedStopLoss = parseFloat(entryPrice) * (1 - (parseFloat(riskPerTrade) || 1) / 100)

  const getRiskColor = (pct: number) => {
    if (pct > 20) return 'text-red-500'
    if (pct > 10) return 'text-yellow-500'
    return 'text-green-500'
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5" />
          Position Size Calculator
        </CardTitle>
        <CardDescription>
          Calculate optimal position size based on your risk parameters
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="portfolio-value">Portfolio Value ($)</Label>
              <Input
                id="portfolio-value"
                type="number"
                placeholder="100000"
                value={portfolioValue}
                onChange={(e) => setPortfolioValue(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="account-balance">Available Balance ($)</Label>
              <Input
                id="account-balance"
                type="number"
                placeholder="50000"
                value={accountBalance}
                onChange={(e) => setAccountBalance(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="entry-price">Entry Price ($)</Label>
              <Input
                id="entry-price"
                type="number"
                placeholder="150.00"
                value={entryPrice}
                onChange={(e) => setEntryPrice(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="stop-loss">Stop Loss ($)</Label>
              <Input
                id="stop-loss"
                type="number"
                placeholder={estimatedStopLoss.toFixed(2)}
                value={stopLossPrice}
                onChange={(e) => setStopLossPrice(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="risk-per-trade">Risk per Trade (%)</Label>
              <Input
                id="risk-per-trade"
                type="number"
                placeholder="1"
                value={riskPerTrade}
                onChange={(e) => setRiskPerTrade(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="position-type">Position Type</Label>
              <Select value={positionType} onValueChange={(v) => setPositionType(v as typeof POSITION_TYPES[number])}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {POSITION_TYPES.map((type) => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="text-sm text-muted-foreground">
            <TrendingDown className="h-4 w-4 inline mr-1" />
            Suggested stop loss: ${estimatedStopLoss.toFixed(2)} ({riskPerTrade || 1}% below entry)
          </div>

          <Button onClick={calculate} className="w-full">
            Calculate Position Size
          </Button>

          {error && (
            <div className="flex items-center gap-2 text-red-500 p-3 bg-red-50 rounded-lg">
              <AlertTriangle className="h-4 w-4" />
              {error}
            </div>
          )}

          {result && !result.error && (
            <div className="grid grid-cols-2 gap-3 p-4 bg-muted rounded-lg">
              <div className="text-center">
                <div className="text-2xl font-bold">{result.position_shares.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground">Shares</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">${result.position_value.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground">Position Value</div>
              </div>
              <div className="text-center">
                <div className={`text-2xl font-bold ${getRiskColor(result.position_percentage)}`}>
                  {result.position_percentage}%
                </div>
                <div className="text-sm text-muted-foreground">of Portfolio</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-500">${result.max_loss.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground">Max Loss</div>
              </div>
              <div className="col-span-2 text-center">
                <div className="text-sm text-muted-foreground">Risk: ${result.risk_amount} ({result.stop_loss_distance}% stop distance)</div>
              </div>
            </div>
          )}

          <div className="text-xs text-muted-foreground">
            <AlertTriangle className="h-3 w-3 inline mr-1" />
            Never risk more than 2% per trade. Professional traders typically risk 1%.
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
