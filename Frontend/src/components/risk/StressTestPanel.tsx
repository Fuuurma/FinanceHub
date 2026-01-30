'use client'

import { useState, useMemo, useCallback } from 'react'
import {
  Activity,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Plus,
  X,
  RefreshCw,
  Zap,
  History,
  Globe,
} from 'lucide-react'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { Progress } from '@/components/ui/progress'

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

export interface StressScenario {
  id: string
  name: string
  description: string
  marketChange: number
  sectorChanges?: Record<string, number>
  impact: number
  impactPercent: number
  selected?: boolean
  custom?: boolean
}

export interface StressTestResult {
  scenarioId: string
  portfolioValue: number
  portfolioChange: number
  portfolioChangePercent: number
  varBreach: boolean
  maxDrawdown: number
  leveragedPositions: Array<{
    symbol: string
    newValue: number
    change: number
  }>
}

interface StressTestPanelProps {
  scenarios?: StressScenario[]
  results?: StressTestResult[]
  currentPortfolioValue?: number
  onRunTest?: (scenario: StressScenario) => void
  onCreateScenario?: (scenario: Omit<StressScenario, 'id' | 'impact' | 'impactPercent'>) => void
  onDeleteScenario?: (id: string) => void
  onSelectScenario?: (id: string) => void
  className?: string
}

interface PresetScenarioData {
  name: string
  description: string
  marketChange: number
  sectorChanges?: Record<string, number>
}

const PRESET_SCENARIOS: PresetScenarioData[] = [
  {
    name: '2008 Financial Crisis',
    description: 'S&P 500 drops 50%, financial sector collapses',
    marketChange: -50,
    sectorChanges: { Financials: -65, 'Real Estate': -45, 'Consumer Discretionary': -35 },
  },
  {
    name: 'COVID-19 Crash',
    description: 'Rapid 30% decline with high volatility',
    marketChange: -30,
    sectorChanges: { 'Consumer Discretionary': -40, Energy: -50, Healthcare: -15 },
  },
  {
    name: 'Rate Shock',
    description: 'Fed hikes rates by 200bps, tech selloff',
    marketChange: -20,
    sectorChanges: { Technology: -30, 'Consumer Discretionary': -25, Utilities: -10 },
  },
  {
    name: 'Tech Bubble Burst',
    description: 'NASDAQ crashes 40%, growth stocks decimated',
    marketChange: -40,
    sectorChanges: { Technology: -50, 'Communication Services': -35 },
  },
  {
    name: 'Oil Shock',
    description: 'Oil prices double, energy volatility spikes',
    marketChange: -15,
    sectorChanges: { Energy: +30, 'Consumer Discretionary': -20, Transportation: -25 },
  },
  {
    name: 'Recession',
    description: 'Mild recession, 20% market decline',
    marketChange: -20,
    sectorChanges: { 'Consumer Discretionary': -30, 'Consumer Staples': -10, Healthcare: -5 },
  },
  {
    name: 'Bull Run',
    description: 'Strong recovery, 30% upside',
    marketChange: +30,
    sectorChanges: { Technology: +40, 'Consumer Discretionary': +35 },
  },
  {
    name: 'Volatility Spike',
    description: 'VIX spikes to 50, flat market with noise',
    marketChange: -5,
    sectorChanges: {},
  },
]

function getRiskLevel(value: number): RiskLevel {
  if (value >= -10) return 'low'
  if (value >= -25) return 'medium'
  if (value >= -40) return 'high'
  return 'critical'
}

function getImpactColor(change: number): string {
  if (change >= -5) return 'text-green-600 bg-green-100'
  if (change >= -15) return 'text-yellow-600 bg-yellow-100'
  if (change >= -30) return 'text-orange-600 bg-orange-100'
  return 'text-red-600 bg-red-100'
}

export function StressTestPanel({
  scenarios = [],
  results = [],
  currentPortfolioValue = 100000,
  onRunTest,
  onCreateScenario,
  onDeleteScenario,
  onSelectScenario,
  className,
}: StressTestPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null)
  const [newScenario, setNewScenario] = useState({
    name: '',
    description: '',
    marketChange: -20,
    sectorChanges: '',
  })

  const allScenarios = useMemo(() => {
    const presets = PRESET_SCENARIOS.map((preset, index) => ({
      ...preset,
      id: `preset-${index}`,
      impact: currentPortfolioValue * (preset.marketChange / 100),
      impactPercent: preset.marketChange,
      selected: selectedScenarioId === `preset-${index}`,
      custom: false,
    }))
    const customScenarios = scenarios.map(s => ({ ...s, selected: selectedScenarioId === s.id }))
    return [...customScenarios, ...presets]
  }, [scenarios, currentPortfolioValue, selectedScenarioId])

  const handleRunTest = useCallback((scenario: StressScenario) => {
    setSelectedScenarioId(scenario.id)
    onSelectScenario?.(scenario.id)
    onRunTest?.(scenario)
  }, [onRunTest, onSelectScenario])

  const handleCreateScenario = useCallback(() => {
    if (!newScenario.name || !newScenario.description) return

    const sectorChanges: Record<string, number> = {}
    if (newScenario.sectorChanges) {
      newScenario.sectorChanges.split(',').forEach(s => {
        const [sector, change] = s.split(':')
        if (sector && change) {
          sectorChanges[sector.trim()] = parseFloat(change.trim())
        }
      })
    }

    onCreateScenario?.({
      name: newScenario.name,
      description: newScenario.description,
      marketChange: newScenario.marketChange,
      sectorChanges: Object.keys(sectorChanges).length > 0 ? sectorChanges : undefined,
    })
    setIsCreateDialogOpen(false)
    setNewScenario({ name: '', description: '', marketChange: -20, sectorChanges: '' })
  }, [newScenario, onCreateScenario])

  const getScenarioResult = useCallback((scenarioId: string) => {
    return results.find(r => r.scenarioId === scenarioId)
  }, [results])

  return (
    <Card className={cn('border-2 border-foreground', className)}>
      <CardHeader
        className="border-b-2 border-foreground bg-muted/30 py-3 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-black uppercase italic flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Stress_Testing
          </CardTitle>
          {isExpanded ? (
            <ChevronUp className="h-5 w-5" />
          ) : (
            <ChevronDown className="h-5 w-5" />
          )}
        </div>
        <CardDescription className="text-xs font-mono">
          Simulate portfolio performance under market stress scenarios
        </CardDescription>
      </CardHeader>

      {isExpanded && (
        <CardContent className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                <Globe className="h-3 w-3 mr-1" />
                {allScenarios.filter(s => s.custom).length} Custom
              </Badge>
              <Badge variant="secondary" className="text-xs">
                <Zap className="h-3 w-3 mr-1" />
                {PRESET_SCENARIOS.length} Presets
              </Badge>
            </div>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm" variant="outline" className="text-xs">
                  <Plus className="h-3 w-3 mr-1" />
                  Create
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle className="text-sm font-bold uppercase">Create Custom Scenario</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-xs">Scenario Name</Label>
                    <Input
                      id="name"
                      value={newScenario.name}
                      onChange={e => setNewScenario(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="e.g., China Trade War"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description" className="text-xs">Description</Label>
                    <Input
                      id="description"
                      value={newScenario.description}
                      onChange={e => setNewScenario(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Describe the scenario..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs">Market Change: {newScenario.marketChange}%</Label>
                    <Slider
                      value={[newScenario.marketChange]}
                      onValueChange={([value]) => setNewScenario(prev => ({ ...prev, marketChange: value }))}
                      min={-80}
                      max={80}
                      step={5}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="sectors" className="text-xs">Sector Changes (optional)</Label>
                    <Input
                      id="sectors"
                      value={newScenario.sectorChanges}
                      onChange={e => setNewScenario(prev => ({ ...prev, sectorChanges: e.target.value }))}
                      placeholder="Tech:-30, Energy:+20"
                    />
                    <p className="text-[10px] text-muted-foreground">Format: Sector:Change, Sector:Change</p>
                  </div>
                </div>
                <DialogFooter>
                  <Button size="sm" onClick={handleCreateScenario} disabled={!newScenario.name || !newScenario.description}>
                    Create Scenario
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {allScenarios.map((scenario) => {
              const result = getScenarioResult(scenario.id)
              const riskLevel = getRiskLevel(scenario.impactPercent)

              return (
                <div
                  key={scenario.id}
                  className={cn(
                    'p-3 border-2 border-foreground/20 cursor-pointer transition-all',
                    'hover:border-foreground hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[4px_4px_0px_0px_var(--foreground)]',
                    scenario.selected && 'border-foreground bg-primary/5'
                  )}
                  onClick={() => handleRunTest(scenario)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-black uppercase text-sm">{scenario.name}</span>
                      {scenario.custom && (
                        <Badge variant="secondary" className="text-[10px]">Custom</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {result && (
                        <Badge className={cn('text-[10px]', getImpactColor(result.portfolioChangePercent))}>
                          {result.portfolioChangePercent >= 0 ? '+' : ''}{result.portfolioChangePercent.toFixed(1)}%
                        </Badge>
                      )}
                      <span className={cn(
                        'font-mono font-bold text-sm',
                        scenario.marketChange >= 0 ? 'text-green-600' : 'text-red-600'
                      )}>
                        {scenario.marketChange >= 0 ? '+' : ''}{scenario.marketChange}%
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">{scenario.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <span className="text-[10px] font-mono uppercase text-muted-foreground cursor-help">
                              Projected Impact
                            </span>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p className="text-xs">Estimated portfolio impact under this scenario</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                      {scenario.custom && onDeleteScenario && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-4 w-4 p-0"
                          onClick={(e) => {
                            e.stopPropagation()
                            onDeleteScenario(scenario.id)
                          }}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={cn(
                        'text-[10px] font-black uppercase',
                        riskLevel === 'low' && 'bg-green-100 text-green-700',
                        riskLevel === 'medium' && 'bg-yellow-100 text-yellow-700',
                        riskLevel === 'high' && 'bg-orange-100 text-orange-700',
                        riskLevel === 'critical' && 'bg-red-100 text-red-700'
                      )}>
                        {riskLevel}
                      </Badge>
                      <span className={cn(
                        'font-black text-sm',
                        scenario.impact >= 0 ? 'text-green-600' : 'text-red-600'
                      )}>
                        {scenario.impact >= 0 ? '+' : ''}{formatCurrency(scenario.impact)}
                      </span>
                    </div>
                  </div>

                  {result && (
                    <div className="mt-3 pt-3 border-t border-foreground/20 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">New Portfolio Value</span>
                        <span className="font-semibold">{formatCurrency(result.portfolioValue)}</span>
                      </div>
                      {result.varBreach && (
                        <div className="flex items-center gap-2 text-xs text-red-600">
                          <AlertTriangle className="h-3 w-3" />
                          VaR Breach Detected
                        </div>
                      )}
                      {result.leveragedPositions.length > 0 && (
                        <div className="text-xs">
                          <p className="text-muted-foreground mb-1">Leveraged Positions at Risk:</p>
                          <div className="flex flex-wrap gap-1">
                            {result.leveragedPositions.slice(0, 3).map(pos => (
                              <Badge key={pos.symbol} variant="outline" className="text-[10px]">
                                {pos.symbol}: {pos.change >= 0 ? '+' : ''}{pos.change.toFixed(1)}%
                              </Badge>
                            ))}
                            {result.leveragedPositions.length > 3 && (
                              <Badge variant="outline" className="text-[10px]">
                                +{result.leveragedPositions.length - 3} more
                              </Badge>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {results.length > 0 && (
            <div className="pt-3 border-t border-foreground/20">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <History className="h-3 w-3" />
                  {results.length} scenario{results.length !== 1 ? 's' : ''} simulated
                </span>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 text-xs"
                  onClick={() => onRunTest?.({ id: 'all', name: 'All', description: '', marketChange: 0, impact: 0, impactPercent: 0, selected: false })}
                >
                  <RefreshCw className="h-3 w-3 mr-1" />
                  Re-run All
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  )
}

export default StressTestPanel
