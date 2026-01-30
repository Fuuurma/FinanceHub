'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { HelpCircle, Settings, Info, TrendingUp, Activity, BarChart2, LineChart } from 'lucide-react'
import { INDICATOR_DESCRIPTIONS, IndicatorConfig } from '@/lib/utils/technical-indicators'

interface IndicatorConfigModalProps {
  showIndicators: string[]
  indicatorConfig: IndicatorConfig
  onShowIndicatorsChange: (indicators: string[]) => void
  onIndicatorConfigChange: (config: IndicatorConfig) => void
  children: React.ReactNode
}

export function IndicatorConfigModal({
  showIndicators,
  indicatorConfig,
  onShowIndicatorsChange,
  onIndicatorConfigChange,
  children,
}: IndicatorConfigModalProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [tempIndicators, setTempIndicators] = useState(showIndicators)
  const [tempConfig, setTempConfig] = useState(indicatorConfig)

  const movingAverageIndicators = [
    { id: 'sma20', ...INDICATOR_DESCRIPTIONS.sma20 },
    { id: 'sma50', ...INDICATOR_DESCRIPTIONS.sma50 },
    { id: 'sma200', ...INDICATOR_DESCRIPTIONS.sma200 },
    { id: 'ema12', ...INDICATOR_DESCRIPTIONS.ema12 },
    { id: 'ema26', ...INDICATOR_DESCRIPTIONS.ema26 },
  ]

  const oscillatorIndicators = [
    { id: 'rsi', ...INDICATOR_DESCRIPTIONS.rsi },
    { id: 'macd', ...INDICATOR_DESCRIPTIONS.macd },
    { id: 'bollinger', ...INDICATOR_DESCRIPTIONS.bollinger },
  ]

  const handleToggleIndicator = (id: string) => {
    setTempIndicators((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    )
  }

  const handleSave = () => {
    onShowIndicatorsChange(tempIndicators)
    onIndicatorConfigChange(tempConfig)
    setIsOpen(false)
  }

  const handleReset = () => {
    setTempIndicators([])
    setTempConfig({
      rsiPeriod: 14,
      rsiOverbought: 70,
      rsiOversold: 30,
      macdFast: 12,
      macdSlow: 26,
      macdSignal: 9,
      bollingerPeriod: 20,
      bollingerStdDev: 2,
    })
  }

  const formatIndicatorValue = (value: number | undefined) => {
    if (value === undefined) return '--'
    return value.toString()
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Technical Indicators Configuration
          </DialogTitle>
          <DialogDescription>
            Customize which technical indicators to display on the chart and their parameters.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="moving-averages" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="moving-averages" className="flex items-center gap-2">
              <LineChart className="h-4 w-4" />
              Moving Averages
            </TabsTrigger>
            <TabsTrigger value="oscillators" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Oscillators
            </TabsTrigger>
            <TabsTrigger value="volatility" className="flex items-center gap-2">
              <BarChart2 className="h-4 w-4" />
              Volatility
            </TabsTrigger>
          </TabsList>

          <TabsContent value="moving-averages" className="space-y-4 mt-4">
            <div className="grid gap-3">
              {movingAverageIndicators.map((indicator) => (
                <Card key={indicator.id} className="cursor-pointer transition-colors hover:bg-muted/50">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Switch
                          checked={tempIndicators.includes(indicator.id)}
                          onCheckedChange={() => handleToggleIndicator(indicator.id)}
                        />
                        <div className="flex items-center gap-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: indicator.color }}
                          />
                          <span className="font-medium">{indicator.name}</span>
                        </div>
                      </div>
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <HelpCircle className="h-4 w-4 text-muted-foreground cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent className="max-w-sm">
                            <p className="font-medium">{indicator.fullName}</p>
                            <p className="text-sm text-muted-foreground mt-1">{indicator.description}</p>
                            <p className="text-sm mt-2">{indicator.interpretation}</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                    {tempIndicators.includes(indicator.id) && (
                      <div className="mt-2 text-sm text-muted-foreground">
                        <p>{indicator.description}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="oscillators" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-purple-500" />
                    <CardTitle className="text-sm">RSI Settings</CardTitle>
                  </div>
                  <Switch
                    checked={tempIndicators.includes('rsi')}
                    onCheckedChange={() => handleToggleIndicator('rsi')}
                  />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {tempIndicators.includes('rsi') && (
                  <>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="rsiPeriod">Period</Label>
                        <Input
                          id="rsiPeriod"
                          type="number"
                          value={tempConfig.rsiPeriod || 14}
                          onChange={(e) =>
                            setTempConfig((prev) => ({
                              ...prev,
                              rsiPeriod: parseInt(e.target.value) || 14,
                            }))
                          }
                          min={2}
                          max={50}
                        />
                        <p className="text-xs text-muted-foreground">
                          Number of periods for RSI calculation
                        </p>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="rsiOverbought">Overbought</Label>
                        <Input
                          id="rsiOverbought"
                          type="number"
                          value={tempConfig.rsiOverbought || 70}
                          onChange={(e) =>
                            setTempConfig((prev) => ({
                              ...prev,
                              rsiOverbought: parseInt(e.target.value) || 70,
                            }))
                          }
                          min={50}
                          max={100}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="rsiOversold">Oversold</Label>
                        <Input
                          id="rsiOversold"
                          type="number"
                          value={tempConfig.rsiOversold || 30}
                          onChange={(e) =>
                            setTempConfig((prev) => ({
                              ...prev,
                              rsiOversold: parseInt(e.target.value) || 30,
                            }))
                          }
                          min={0}
                          max={50}
                        />
                      </div>
                    </div>
                    <div className="p-3 bg-muted rounded-lg">
                      <div className="flex items-start gap-2">
                        <Info className="h-4 w-4 text-muted-foreground mt-0.5" />
                        <div className="text-sm">
                          <p className="font-medium">How RSI works:</p>
                          <p className="text-muted-foreground mt-1">
                            RSI measures the speed and change of price movements on a scale of 0-100.
                            Traditionally, RSI above {tempConfig.rsiOverbought || 70} suggests the asset may be overbought,
                            while RSI below {tempConfig.rsiOversold || 30} suggests it may be oversold.
                          </p>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-blue-500" />
                    <CardTitle className="text-sm">MACD Settings</CardTitle>
                  </div>
                  <Switch
                    checked={tempIndicators.includes('macd')}
                    onCheckedChange={() => handleToggleIndicator('macd')}
                  />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {tempIndicators.includes('macd') && (
                  <>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="macdFast">Fast Period</Label>
                        <Input
                          id="macdFast"
                          type="number"
                          value={tempConfig.macdFast || 12}
                          onChange={(e) =>
                            setTempConfig((prev) => ({
                              ...prev,
                              macdFast: parseInt(e.target.value) || 12,
                            }))
                          }
                          min={2}
                          max={50}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="macdSlow">Slow Period</Label>
                        <Input
                          id="macdSlow"
                          type="number"
                          value={tempConfig.macdSlow || 26}
                          onChange={(e) =>
                            setTempConfig((prev) => ({
                              ...prev,
                              macdSlow: parseInt(e.target.value) || 26,
                            }))
                          }
                          min={2}
                          max={100}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="macdSignal">Signal Period</Label>
                        <Input
                          id="macdSignal"
                          type="number"
                          value={tempConfig.macdSignal || 9}
                          onChange={(e) =>
                            setTempConfig((prev) => ({
                              ...prev,
                              macdSignal: parseInt(e.target.value) || 9,
                            }))
                          }
                          min={1}
                          max={50}
                        />
                      </div>
                    </div>
                    <div className="p-3 bg-muted rounded-lg">
                      <div className="flex items-start gap-2">
                        <Info className="h-4 w-4 text-muted-foreground mt-0.5" />
                        <div className="text-sm">
                          <p className="font-medium">How MACD works:</p>
                          <p className="text-muted-foreground mt-1">
                            MACD shows the relationship between two EMAs. When MACD crosses above the signal line,
                            it may indicate bullish momentum. When it crosses below, it may indicate bearish momentum.
                          </p>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="volatility" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <BarChart2 className="h-4 w-4 text-amber-500" />
                    <CardTitle className="text-sm">Bollinger Bands Settings</CardTitle>
                  </div>
                  <Switch
                    checked={tempIndicators.includes('bollinger')}
                    onCheckedChange={() => handleToggleIndicator('bollinger')}
                  />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {tempIndicators.includes('bollinger') && (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="bollingerPeriod">Period</Label>
                        <Input
                          id="bollingerPeriod"
                          type="number"
                          value={tempConfig.bollingerPeriod || 20}
                          onChange={(e) =>
                            setTempConfig((prev) => ({
                              ...prev,
                              bollingerPeriod: parseInt(e.target.value) || 20,
                            }))
                          }
                          min={2}
                          max={100}
                        />
                        <p className="text-xs text-muted-foreground">
                          Number of periods for SMA calculation
                        </p>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="bollingerStdDev">Standard Deviations</Label>
                        <Input
                          id="bollingerStdDev"
                          type="number"
                          value={tempConfig.bollingerStdDev || 2}
                          onChange={(e) =>
                            setTempConfig((prev) => ({
                              ...prev,
                              bollingerStdDev: parseFloat(e.target.value) || 2,
                            }))
                          }
                          min={0.5}
                          max={5}
                          step={0.5}
                        />
                      </div>
                    </div>
                    <div className="p-3 bg-muted rounded-lg">
                      <div className="flex items-start gap-2">
                        <Info className="h-4 w-4 text-muted-foreground mt-0.5" />
                        <div className="text-sm">
                          <p className="font-medium">How Bollinger Bands work:</p>
                          <p className="text-muted-foreground mt-1">
                            Bollinger Bands consist of a middle band (SMA) with upper and lower bands
                            set at a specified number of standard deviations. When bands widen, it indicates
                            higher volatility; when they narrow, it indicates lower volatility.
                          </p>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {tempIndicators.length} indicator{tempIndicators.length !== 1 ? 's' : ''} active
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={handleReset}>
              Reset
            </Button>
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>Apply Changes</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
