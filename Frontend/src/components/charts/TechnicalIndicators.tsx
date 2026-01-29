'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'
import {
  TrendingUp,
  Activity,
  Zap,
  Plus,
  X,
  ChevronDown,
  ChevronUp,
  Settings2,
} from 'lucide-react'
import { INDICATOR_CATEGORIES, INDICATOR_LABELS } from '@/lib/constants/indicators'
import { DEFAULT_INDICATORS } from '@/lib/types/indicators'
import type { IndicatorConfig, IndicatorType } from '@/lib/types/indicators'
import { cn } from '@/lib/utils'

interface TechnicalIndicatorsProps {
  symbol: string
  selectedIndicators: IndicatorConfig[]
  onIndicatorsChange: (indicators: IndicatorConfig[]) => void
  className?: string
}

export function TechnicalIndicators({
  symbol,
  selectedIndicators,
  onIndicatorsChange,
  className,
}: TechnicalIndicatorsProps) {
  const [activeCategory, setActiveCategory] = useState<keyof typeof INDICATOR_CATEGORIES>('trend')
  const [expandedIndicators, setExpandedIndicators] = useState<Set<string>>(new Set())
  const [configuringIndicator, setConfiguringIndicator] = useState<IndicatorConfig | null>(null)

  const availableIndicators = (Object.entries(INDICATOR_CATEGORIES).find(
    ([key]) => key === activeCategory
  )?.[1].indicators || []) as IndicatorType[]

  const handleToggleIndicator = (indicatorType: IndicatorType) => {
    const existingIndex = selectedIndicators.findIndex((ind) => ind.type === indicatorType)

    if (existingIndex >= 0) {
      // Remove indicator
      const newIndicators = selectedIndicators.filter((ind) => ind.type !== indicatorType)
      onIndicatorsChange(newIndicators)
    } else {
      // Add indicator with default config
      const defaultConfig: IndicatorConfig = DEFAULT_INDICATORS[indicatorType]
      onIndicatorsChange([...selectedIndicators, defaultConfig])
      setConfiguringIndicator(defaultConfig)
    }
  }

  const handleUpdateConfig = (indicator: IndicatorConfig) => {
    const newIndicators = selectedIndicators.map((ind) =>
      ind.type === indicator.type ? indicator : ind
    )
    onIndicatorsChange(newIndicators)
    setConfiguringIndicator(null)
  }

  const handleToggleVisibility = (type: IndicatorType) => {
    const newIndicators = selectedIndicators.map((ind) =>
      ind.type === type ? { ...ind, visible: !ind.visible } : ind
    )
    onIndicatorsChange(newIndicators)
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'trend':
        return <TrendingUp className="h-4 w-4" />
      case 'momentum':
        return <Activity className="h-4 w-4" />
      case 'volatility':
        return <Zap className="h-4 w-4" />
      default:
        return <Settings2 className="h-4 w-4" />
    }
  }

  return (
    <div className={cn('space-y-4', className)}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Technical Indicators
            <Badge variant="secondary">{selectedIndicators.length} active</Badge>
          </CardTitle>
          <CardDescription>
            Add technical indicators to the chart
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeCategory} onValueChange={(v) => setActiveCategory(v as keyof typeof INDICATOR_CATEGORIES)}>
            <TabsList className="grid w-full grid-cols-4">
              {Object.entries(INDICATOR_CATEGORIES).map(([key, { label, indicators }]) => (
                <TabsTrigger key={key} value={key} className="gap-2">
                  {getCategoryIcon(key)}
                  {label}
                </TabsTrigger>
              ))}
            </TabsList>

            {Object.entries(INDICATOR_CATEGORIES).map(([key, { label, indicators }]) => (
              <TabsContent key={key} value={key} className="space-y-2 mt-4">
                {indicators.map((indicatorType) => {
                  const isSelected = selectedIndicators.some((ind) => ind.type === indicatorType)
                  const config = selectedIndicators.find((ind) => ind.type === indicatorType)
                  const isExpanded = expandedIndicators.has(indicatorType)

                  return (
                    <div
                      key={indicatorType}
                      className="border rounded-lg overflow-hidden"
                    >
                      <div
                        className="flex items-center justify-between p-3 hover:bg-muted/50 cursor-pointer"
                        onClick={() => {
                          const newExpanded = new Set(expandedIndicators)
                          if (isExpanded) {
                            newExpanded.delete(indicatorType)
                          } else {
                            newExpanded.add(indicatorType)
                          }
                          setExpandedIndicators(newExpanded)
                        }}
                      >
                        <div className="flex items-center gap-3">
                          <Button
                            variant={isSelected ? 'default' : 'outline'}
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleToggleIndicator(indicatorType)
                            }}
                          >
                            {isSelected ? (
                              <X className="h-3 w-3" />
                            ) : (
                              <Plus className="h-3 w-3" />
                            )}
                          </Button>
                          <span className="font-medium">
                            {INDICATOR_LABELS[indicatorType]}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          {isSelected && config && (
                            <Switch
                              checked={config.visible}
                              onCheckedChange={() => handleToggleVisibility(indicatorType)}
                              onClick={(e) => e.stopPropagation()}
                            />
                          )}
                          {isExpanded ? (
                            <ChevronUp className="h-4 w-4 text-muted-foreground" />
                          ) : (
                            <ChevronDown className="h-4 w-4 text-muted-foreground" />
                          )}
                        </div>
                      </div>

                      {isExpanded && isSelected && config && (
                        <div className="border-t p-4 space-y-4 bg-muted/30">
                          <div className="grid gap-4 md:grid-cols-2">
                            <div className="space-y-2">
                              <Label>Period</Label>
                              <Input
                                type="number"
                                value={config.params.period || 20}
                                onChange={(e) =>
                                  handleUpdateConfig({
                                    ...config,
                                    params: {
                                      ...config.params,
                                      period: parseFloat(e.target.value),
                                    },
                                  })
                                }
                                className="font-mono"
                              />
                            </div>

                            {config.type === 'bollinger' && (
                              <>
                                <div className="space-y-2">
                                  <Label>Standard Deviations</Label>
                                  <Input
                                    type="number"
                                    step="0.1"
                                    value={config.params.stdDev || 2}
                                    onChange={(e) =>
                                      handleUpdateConfig({
                                        ...config,
                                        params: {
                                          ...config.params,
                                          stdDev: parseFloat(e.target.value),
                                        },
                                      })
                                    }
                                    className="font-mono"
                                  />
                                </div>
                              </>
                            )}

                            {config.type === 'macd' && (
                              <>
                                <div className="space-y-2">
                                  <Label>Fast Period</Label>
                                  <Input
                                    type="number"
                                    value={config.params.fastPeriod || 12}
                                    onChange={(e) =>
                                      handleUpdateConfig({
                                        ...config,
                                        params: {
                                          ...config.params,
                                          fastPeriod: parseFloat(e.target.value),
                                        },
                                      })
                                    }
                                    className="font-mono"
                                  />
                                </div>
                                <div className="space-y-2">
                                  <Label>Slow Period</Label>
                                  <Input
                                    type="number"
                                    value={config.params.slowPeriod || 26}
                                    onChange={(e) =>
                                      handleUpdateConfig({
                                        ...config,
                                        params: {
                                          ...config.params,
                                          slowPeriod: parseFloat(e.target.value),
                                        },
                                      })
                                    }
                                    className="font-mono"
                                  />
                                </div>
                                <div className="space-y-2">
                                  <Label>Signal Period</Label>
                                  <Input
                                    type="number"
                                    value={config.params.signalPeriod || 9}
                                    onChange={(e) =>
                                      handleUpdateConfig({
                                        ...config,
                                        params: {
                                          ...config.params,
                                          signalPeriod: parseFloat(e.target.value),
                                        },
                                      })
                                    }
                                    className="font-mono"
                                  />
                                </div>
                              </>
                            )}

                            {config.type === 'stochastic' && (
                              <>
                                <div className="space-y-2">
                                  <Label>%K Period</Label>
                                  <Input
                                    type="number"
                                    value={config.params.kPeriod || 14}
                                    onChange={(e) =>
                                      handleUpdateConfig({
                                        ...config,
                                        params: {
                                          ...config.params,
                                          kPeriod: parseFloat(e.target.value),
                                        },
                                      })
                                    }
                                    className="font-mono"
                                  />
                                </div>
                                <div className="space-y-2">
                                  <Label>%D Period</Label>
                                  <Input
                                    type="number"
                                    value={config.params.dPeriod || 3}
                                    onChange={(e) =>
                                      handleUpdateConfig({
                                        ...config,
                                        params: {
                                          ...config.params,
                                          dPeriod: parseFloat(e.target.value),
                                        },
                                      })
                                    }
                                    className="font-mono"
                                  />
                                </div>
                              </>
                            )}
                          </div>

                          <div className="space-y-2">
                            <Label>Color</Label>
                            <div className="flex gap-2">
                              {['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6'].map((color) => (
                                <button
                                  key={color}
                                  className={cn(
                                    'w-8 h-8 rounded-md border-2 transition-all',
                                    config.color === color
                                      ? 'border-foreground scale-110'
                                      : 'border-transparent hover:scale-105'
                                  )}
                                  style={{ backgroundColor: color }}
                                  onClick={() =>
                                    handleUpdateConfig({ ...config, color })
                                  }
                                />
                              ))}
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <Switch
                              checked={config.secondary_yaxis || false}
                              onCheckedChange={(checked) =>
                                handleUpdateConfig({
                                  ...config,
                                  secondary_yaxis: checked,
                                })
                              }
                            />
                            <Label className="text-sm">Secondary Y-Axis</Label>
                          </div>

                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleToggleIndicator(indicatorType)}
                          >
                            Remove Indicator
                          </Button>
                        </div>
                      )}
                    </div>
                  )
                })}
              </TabsContent>
            ))}
          </Tabs>

          {selectedIndicators.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No indicators selected</p>
              <p className="text-sm">Add indicators from the categories above</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
