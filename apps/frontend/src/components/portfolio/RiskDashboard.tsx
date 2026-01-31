'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, TrendingDown, Activity, RefreshCw, BarChart3, AlertCircle } from 'lucide-react'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

interface RiskDashboardProps {
  portfolioId: string
}

interface VaRResult {
  var_amount: number
  var_percentage: number
  expected_shortfall: number
  portfolio_value: number
  method: string
  confidence_level: number
  time_horizon: number
  portfolio_volatility: number
}

interface StressTestResult {
  scenario_name: string
  portfolio_loss: number
  portfolio_loss_pct: number
  portfolio_value_before: number
  portfolio_value_after: number
  worst_performing_assets: Array<{ symbol: string; loss: number; loss_amount: number }>
}

const SCENARIOS = [
  { id: '2008_financial_crisis', name: '2008 Financial Crisis', drop: -50 },
  { id: 'covid_crash', name: 'COVID-19 Crash (2020)', drop: -34 },
  { id: 'dot_com_bubble', name: 'Dot-Com Bubble (2000-2002)', drop: -49 },
]

export function RiskDashboard({ portfolioId }: RiskDashboardProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [varResult, setVarResult] = useState<VaRResult | null>(null)
  const [stressTests, setStressTests] = useState<StressTestResult[]>([])
  const [varMethod, setVarMethod] = useState('parametric')
  const [confidenceLevel, setConfidenceLevel] = useState(95)
  const [timeHorizon, setTimeHorizon] = useState(1)

  const fetchVar = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/risk/var/${portfolioId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          method: varMethod,
          confidence_level: confidenceLevel,
          time_horizon: timeHorizon,
        }),
      })
      if (!response.ok) throw new Error('Failed to calculate VaR')
      const data = await response.json()
      setVarResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'VaR calculation failed')
    } finally {
      setLoading(false)
    }
  }, [portfolioId, varMethod, confidenceLevel, timeHorizon])

  const runStressTest = useCallback(async (scenarioId: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/risk/stress-test/${portfolioId}/historical?scenario=${scenarioId}`, {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Stress test failed')
      const data = await response.json()
      setStressTests(prev => [data, ...prev].slice(0, 10))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Stress test failed')
    } finally {
      setLoading(false)
    }
  }, [portfolioId])

  useEffect(() => {
    fetchVar()
  }, [fetchVar])

  const getRiskLevel = (varPct: number) => {
    if (varPct < 1) return { level: 'Low', color: 'text-green-500', bg: 'bg-green-100' }
    if (varPct < 3) return { level: 'Moderate', color: 'text-yellow-500', bg: 'bg-yellow-100' }
    if (varPct < 5) return { level: 'High', color: 'text-orange-500', bg: 'bg-orange-100' }
    return { level: 'Very High', color: 'text-red-500', bg: 'bg-red-100' }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Risk Analysis</h2>
          <p className="text-muted-foreground">Value-at-Risk and stress testing</p>
        </div>
        <Button onClick={fetchVar} disabled={loading} variant="outline">
          <RefreshCw className={cn('w-4 h-4 mr-2', loading && 'animate-spin')} />
          Recalculate
        </Button>
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Value at Risk (VaR)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {varResult ? (
              <div>
                <div className={cn('text-2xl font-bold', getRiskLevel(varResult.var_percentage).color)}>
                  {formatCurrency(varResult.var_amount)}
                </div>
                <p className="text-sm text-muted-foreground">
                  {formatPercent(varResult.var_percentage / 100)} of portfolio
                </p>
                <div className="mt-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100">
                  {getRiskLevel(varResult.var_percentage).level} Risk
                </div>
              </div>
            ) : (
              <div className="h-12 bg-muted animate-pulse rounded" />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingDown className="h-4 w-4" />
              Expected Shortfall (CVaR)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {varResult ? (
              <div>
                <div className="text-2xl font-bold">{formatCurrency(varResult.expected_shortfall)}</div>
                <p className="text-sm text-muted-foreground">
                  Average loss if VaR is breached
                </p>
              </div>
            ) : (
              <div className="h-12 bg-muted animate-pulse rounded" />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Portfolio Volatility
            </CardTitle>
          </CardHeader>
          <CardContent>
            {varResult?.portfolio_volatility ? (
              <div>
                <div className="text-2xl font-bold">{formatPercent(varResult.portfolio_volatility)}</div>
                <p className="text-sm text-muted-foreground">
                  Daily volatility (annualized)
                </p>
              </div>
            ) : (
              <div className="h-12 bg-muted animate-pulse rounded" />
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>VaR Configuration</CardTitle>
          <CardDescription>Adjust calculation parameters</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div>
              <Label>Method</Label>
              <Select value={varMethod} onValueChange={setVarMethod}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="parametric">Parametric</SelectItem>
                  <SelectItem value="historical">Historical</SelectItem>
                  <SelectItem value="monte_carlo">Monte Carlo</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Confidence Level</Label>
              <Select value={String(confidenceLevel)} onValueChange={(v) => setConfidenceLevel(Number(v))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="90">90%</SelectItem>
                  <SelectItem value="95">95%</SelectItem>
                  <SelectItem value="99">99%</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Time Horizon</Label>
              <Select value={String(timeHorizon)} onValueChange={(v) => setTimeHorizon(Number(v))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 Day</SelectItem>
                  <SelectItem value="5">1 Week</SelectItem>
                  <SelectItem value="21">1 Month</SelectItem>
                  <SelectItem value="63">3 Months</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button onClick={fetchVar} disabled={loading} className="w-full">
                Update VaR
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="stress">
        <TabsList>
          <TabsTrigger value="stress">Stress Tests</TabsTrigger>
          <TabsTrigger value="methods">VaR Methods</TabsTrigger>
        </TabsList>

        <TabsContent value="stress" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Historical Stress Tests</CardTitle>
              <CardDescription>See how your portfolio would have performed during historical market crashes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3 mb-6">
                {SCENARIOS.map((scenario) => (
                  <Button
                    key={scenario.id}
                    variant="outline"
                    onClick={() => runStressTest(scenario.id)}
                    disabled={loading}
                  >
                    <BarChart3 className="w-4 h-4 mr-2" />
                    {scenario.name} ({scenario.drop}%)
                  </Button>
                ))}
              </div>

              {stressTests.length > 0 && (
                <div className="space-y-4">
                  {stressTests.map((test, i) => (
                    <div key={i} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold">{test.scenario_name}</h4>
                        <span className={cn('font-bold', test.portfolio_loss_pct > 5 ? 'text-red-500' : 'text-orange-500')}>
                          {formatCurrency(test.portfolio_loss)} ({formatPercent(-test.portfolio_loss_pct / 100)})
                        </span>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Portfolio would drop from {formatCurrency(test.portfolio_value_before)} to {formatCurrency(test.portfolio_value_after)}
                      </div>
                      {test.worst_performing_assets.length > 0 && (
                        <div className="mt-2 flex gap-2 flex-wrap">
                          {test.worst_performing_assets.slice(0, 3).map((asset) => (
                            <span key={asset.symbol} className="text-xs bg-muted px-2 py-1 rounded">
                              {asset.symbol}: {formatPercent(asset.loss)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="methods" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>VaR Calculation Methods</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Parametric (Variance-Covariance)</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    Assumes normal distribution of returns. Fast but may underestimate tail risk.
                  </p>
                  <div className="flex gap-4 text-sm">
                    <span className="text-green-600">✓ Fast calculation</span>
                    <span className="text-green-600">✓ Well understood</span>
                    <span className="text-red-600">✗ Assumes normality</span>
                    <span className="text-red-600">✗ May underestimate extreme losses</span>
                  </div>
                </div>

                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Historical Simulation</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    Uses actual historical returns. Non-parametric approach.
                  </p>
                  <div className="flex gap-4 text-sm">
                    <span className="text-green-600">✓ No distribution assumptions</span>
                    <span className="text-green-600">✓ Captures fat tails</span>
                    <span className="text-red-600">✗ Requires sufficient history</span>
                    <span className="text-red-600">✗ Past may not predict future</span>
                  </div>
                </div>

                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Monte Carlo Simulation</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    Simulates thousands of random scenarios based on historical parameters.
                  </p>
                  <div className="flex gap-4 text-sm">
                    <span className="text-green-600">✓ Flexible</span>
                    <span className="text-green-600">✓ Handles complex portfolios</span>
                    <span className="text-red-600">✗ Computationally intensive</span>
                    <span className="text-red-600">✗ Model risk</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default RiskDashboard
