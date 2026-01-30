'use client'

import { useState, useMemo } from 'react'
import {
  AlertTriangle,
  TrendingDown,
  TrendingUp,
  Activity,
  Shield,
  Target,
  BarChart3,
  Settings,
  Bell,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Info,
  CheckCircle,
  XCircle,
  PieChart,
  Layers,
  Zap,
  Globe,
  TrendingUpIcon,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts'

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

export interface RiskMetrics {
  var_95: number
  var_99: number
  cvar_95: number
  beta: number
  sharpe_ratio: number
  sortino_ratio: number
  max_drawdown: number
  current_drawdown: number
  volatility: number
  correlation_sp500: number
  risk_score: number
  leverage: number
  gross_exposure: number
  net_exposure: number
  long_exposure: number
  short_exposure: number
  diversification_score: number
  concentration_risk: number
  liquidity_score: number
  avg_position_size: number
  largest_position_weight: number
}

export interface StressScenario {
  id: string
  name: string
  description: string
  change: number
  impact: number
  selected?: boolean
}

export interface RiskAlert {
  id: string
  type: 'warning' | 'critical' | 'info'
  title: string
  message: string
  timestamp: string
  acknowledged: boolean
}

export interface RiskLimits {
  max_var_95: number
  max_drawdown: number
  max_leverage: number
  max_position_size: number
  max_sector_concentration: number
}

export interface HoldingRisk {
  symbol: string
  name: string
  weight: number
  contribution: number
  beta: number
  correlation: number
}

export interface SectorExposure {
  sector: string
  weight: number
  risk_contribution: number
}

export interface RiskHistoryPoint {
  date: string
  volatility: number
  sharpeRatio: number
  var95: number
  beta: number
}

export interface RiskDashboardProps {
  metrics?: RiskMetrics
  scenarios?: StressScenario[]
  alerts?: RiskAlert[]
  limits?: RiskLimits
  holdings?: HoldingRisk[]
  sectors?: SectorExposure[]
  history?: RiskHistoryPoint[]
  loading?: boolean
  onRefresh?: () => void
  onScenarioSelect?: (scenario: StressScenario) => void
  onAlertAcknowledge?: (alertId: string) => void
  onPeriodChange?: (period: string) => void
  className?: string
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B6B']

function getRiskLevel(value: number, thresholds: { low: number; medium: number; high: number }): RiskLevel {
  if (value <= thresholds.low) return 'low'
  if (value <= thresholds.medium) return 'medium'
  if (value <= thresholds.high) return 'high'
  return 'critical'
}

function getRiskColor(level: RiskLevel): string {
  switch (level) {
    case 'low': return 'text-green-600 bg-green-100'
    case 'medium': return 'text-yellow-600 bg-yellow-100'
    case 'high': return 'text-orange-600 bg-orange-100'
    case 'critical': return 'text-red-600 bg-red-100'
  }
}

function RiskMetricCard({
  title,
  value,
  subValue,
  icon: Icon,
  level,
  description,
  trend,
}: {
  title: string
  value: string | number
  subValue?: string
  icon: React.ElementType
  level?: RiskLevel
  description?: string
  trend?: 'up' | 'down' | 'neutral'
}) {
  return (
    <Card className={cn(
      'border-l-4',
      level === 'critical' && 'border-l-red-500',
      level === 'high' && 'border-l-orange-500',
      level === 'medium' && 'border-l-yellow-500',
      level === 'low' && 'border-l-green-500',
      !level && 'border-l-foreground/20'
    )}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <Icon className="h-4 w-4" />
          {title}
          {description && (
            <Tooltip delayDuration={200}>
              <TooltipTrigger asChild>
                <Info className="h-3 w-3 cursor-help" />
              </TooltipTrigger>
              <TooltipContent className="bg-background border-2 border-foreground shadow-[4px_4px_0px_0px_var(--foreground)] rounded-none max-w-xs">
                <p>{description}</p>
              </TooltipContent>
            </Tooltip>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline justify-between">
          <p className="text-2xl font-black">{value}</p>
          {trend && (
            <div className={cn(
              'flex items-center gap-1',
              trend === 'up' && 'text-green-600',
              trend === 'down' && 'text-red-600',
              trend === 'neutral' && 'text-muted-foreground'
            )}>
              {trend === 'up' && <TrendingUp className="h-4 w-4" />}
              {trend === 'down' && <TrendingDown className="h-4 w-4" />}
            </div>
          )}
        </div>
        {subValue && (
          <p className="text-xs text-muted-foreground mt-1">{subValue}</p>
        )}
        {level && (
          <Badge className={cn('mt-2 text-[10px] font-black uppercase', getRiskColor(level))}>
            {level}
          </Badge>
        )}
      </CardContent>
    </Card>
  )
}

function StressTestingPanel({
  scenarios,
  onSelect,
}: {
  scenarios?: StressScenario[]
  onSelect?: (scenario: StressScenario) => void
}) {
  const [isExpanded, setIsExpanded] = useState(true)

  if (!scenarios || scenarios.length === 0) {
    return (
      <Card className="border-2 border-foreground">
        <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
          <CardTitle className="text-lg font-black uppercase italic flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Stress_Testing
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          <div className="text-center py-8">
            <Activity className="h-12 w-12 mx-auto text-muted-foreground/50 mb-2" />
            <p className="font-black uppercase text-muted-foreground">No Scenarios Available</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-2 border-foreground">
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
        <CardContent className="p-4">
          <div className="space-y-3">
            {scenarios.map((scenario) => (
              <div
                key={scenario.id}
                className={cn(
                  'p-3 border-2 border-foreground/20 cursor-pointer transition-all hover:border-foreground hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[4px_4px_0px_0px_var(--foreground)]',
                  scenario.selected && 'border-foreground bg-primary/5'
                )}
                onClick={() => onSelect?.(scenario)}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-black uppercase text-sm">{scenario.name}</span>
                  <span className={cn(
                    'font-mono font-bold text-sm',
                    scenario.change >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    {scenario.change >= 0 ? '+' : ''}{scenario.change}%
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mb-2">{scenario.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono uppercase text-muted-foreground">Projected Impact</span>
                  <span className={cn(
                    'font-black text-sm',
                    scenario.impact >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    {scenario.impact >= 0 ? '+' : ''}{formatCurrency(scenario.impact)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      )}
    </Card>
  )
}

function RiskAlertsPanel({
  alerts,
  onAcknowledge,
}: {
  alerts?: RiskAlert[]
  onAcknowledge?: (alertId: string) => void
}) {
  const unacknowledged = alerts?.filter(a => !a.acknowledged) || []
  const acknowledged = alerts?.filter(a => a.acknowledged) || []

  return (
    <Card className="border-2 border-foreground">
      <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
        <CardTitle className="text-lg font-black uppercase italic flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Risk_Alerts
          {unacknowledged.length > 0 && (
            <Badge className="bg-red-500 text-white text-[10px] font-black">{unacknowledged.length}</Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="space-y-3 max-h-[300px] overflow-y-auto">
          {alerts && alerts.length > 0 ? (
            [...unacknowledged, ...acknowledged].map((alert) => (
              <div
                key={alert.id}
                className={cn(
                  'p-3 border-2 border-foreground/20',
                  alert.type === 'critical' && 'border-red-500 bg-red-50',
                  alert.type === 'warning' && 'border-yellow-500 bg-yellow-50',
                  alert.type === 'info' && 'border-blue-500 bg-blue-50',
                  alert.acknowledged && 'opacity-50'
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {alert.type === 'critical' && <XCircle className="h-4 w-4 text-red-600 shrink-0" />}
                    {alert.type === 'warning' && <AlertTriangle className="h-4 w-4 text-yellow-600 shrink-0" />}
                    {alert.type === 'info' && <Info className="h-4 w-4 text-blue-600 shrink-0" />}
                    <div>
                      <p className="font-black uppercase text-xs">{alert.title}</p>
                      <p className="text-xs text-muted-foreground mt-1">{alert.message}</p>
                    </div>
                  </div>
                  {!alert.acknowledged && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-6 text-[10px] font-black uppercase border-foreground"
                      onClick={() => onAcknowledge?.(alert.id)}
                    >
                      Dismiss
                    </Button>
                  )}
                </div>
                <p className="text-[10px] font-mono text-muted-foreground mt-2">
                  {new Date(alert.timestamp).toLocaleString()}
                </p>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 mx-auto text-green-500/50 mb-2" />
              <p className="font-black uppercase text-muted-foreground">No Active Alerts</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function ExposureGauge({
  label,
  value,
  max,
  unit = '%',
}: {
  label: string
  value: number
  max: number
  unit?: string
}) {
  const percentage = Math.min((value / max) * 100, 100)
  const level = percentage > 80 ? 'critical' : percentage > 60 ? 'high' : percentage > 40 ? 'medium' : 'low'

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase">{label}</span>
        <span className="text-xs font-mono">{value.toFixed(1)}{unit}</span>
      </div>
      <Progress
        value={percentage}
        className={cn(
          'h-2',
          level === 'critical' && '[&>div]:bg-red-500',
          level === 'high' && '[&>div]:bg-orange-500',
          level === 'medium' && '[&>div]:bg-yellow-500',
          level === 'low' && '[&>div]:bg-green-500'
        )}
      />
    </div>
  )
}

function SummaryCard({
  title,
  value,
  change,
  icon: Icon,
  trend,
  description,
}: {
  title: string
  value: string | number
  change?: number
  icon: React.ElementType
  trend?: 'up' | 'down'
  description?: string
}) {
  const isPositive = change && change >= 0

  return (
    <Card className="border-2 border-foreground">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <Icon className="h-4 w-4" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline justify-between">
          <p className="text-2xl font-black">{value}</p>
          {change !== undefined && (
            <div className={cn(
              'flex items-center gap-1 text-sm font-bold',
              isPositive ? 'text-green-600' : 'text-red-600'
            )}>
              {isPositive ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
              {formatPercent(Math.abs(change))}
            </div>
          )}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  )
}

function RiskHistoryChart({ data }: { data: RiskHistoryPoint[] }) {
  if (!data || data.length === 0) {
    return (
      <Card className="border-2 border-foreground h-[350px]">
        <CardContent className="flex items-center justify-center h-full">
          <p className="text-muted-foreground">No historical data available</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-2 border-foreground">
      <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
        <CardTitle className="text-sm font-black uppercase">Risk Metrics History</CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" className="opacity-20" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
              stroke="currentColor"
            />
            <YAxis yAxisId="left" tick={{ fontSize: 12 }} stroke="currentColor" />
            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} stroke="currentColor" />
            <RechartsTooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--background))',
                border: '2px solid hsl(var(--foreground))',
                borderRadius: '0px',
              }}
              labelFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="volatility"
              stroke="#ef4444"
              name="Volatility %"
              strokeWidth={2}
              dot={{ r: 2 }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="sharpeRatio"
              stroke="#22c55e"
              name="Sharpe Ratio"
              strokeWidth={2}
              dot={{ r: 2 }}
            />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="var95"
              stroke="#f97316"
              name="VaR 95%"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

function ConcentrationPanel({ holdings }: { holdings?: HoldingRisk[] }) {
  const sortedHoldings = useMemo(() => {
    if (!holdings) return []
    return [...holdings].sort((a, b) => b.weight - a.weight).slice(0, 10)
  }, [holdings])

  if (!holdings || holdings.length === 0) {
    return (
      <Card className="border-2 border-foreground">
        <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
          <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
            <Layers className="h-4 w-4" />
            Concentration Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          <div className="text-center py-8">
            <Layers className="h-12 w-12 mx-auto text-muted-foreground/50 mb-2" />
            <p className="font-black uppercase text-muted-foreground">No holdings data</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const top5Weight = sortedHoldings.slice(0, 5).reduce((sum, h) => sum + h.weight, 0)
  const herfindahlIndex = holdings.reduce((sum, h) => sum + Math.pow(h.weight / 100, 2), 0) * 10000

  return (
    <Card className="border-2 border-foreground">
      <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
        <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
          <Layers className="h-4 w-4" />
          Concentration Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 border border-foreground/20">
            <p className="text-xs text-muted-foreground uppercase">Top 5 Weight</p>
            <p className="text-xl font-black">{top5Weight.toFixed(1)}%</p>
          </div>
          <div className="p-3 border border-foreground/20">
            <p className="text-xs text-muted-foreground uppercase">HHI Index</p>
            <p className="text-xl font-black">{herfindahlIndex.toFixed(0)}</p>
            <p className="text-[10px] text-muted-foreground">&lt;1500 = diversified</p>
          </div>
        </div>
        <div className="space-y-2 max-h-[200px] overflow-y-auto">
          {sortedHoldings.map((holding, idx) => (
            <div key={holding.symbol} className="flex items-center justify-between p-2 border border-foreground/10">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-[10px] font-black">{idx + 1}</Badge>
                <div>
                  <p className="text-xs font-bold uppercase">{holding.symbol}</p>
                  <p className="text-[10px] text-muted-foreground truncate max-w-[100px]">{holding.name}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs font-bold">{holding.weight.toFixed(2)}%</p>
                <p className={cn(
                  'text-[10px]',
                  holding.contribution > 0 ? 'text-green-600' : 'text-red-600'
                )}>
                  {holding.contribution >= 0 ? '+' : ''}{holding.contribution.toFixed(2)}%
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function SectorExposureChart({ sectors }: { sectors?: SectorExposure[] }) {
  const chartData = useMemo(() => {
    if (!sectors) return []
    return sectors.map(s => ({
      name: s.sector,
      value: s.weight,
      risk: s.risk_contribution,
    }))
  }, [sectors])

  if (!sectors || sectors.length === 0) {
    return (
      <Card className="border-2 border-foreground">
        <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
          <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
            <PieChart className="h-4 w-4" />
            Sector Exposure
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          <div className="text-center py-8">
            <PieChart className="h-12 w-12 mx-auto text-muted-foreground/50 mb-2" />
            <p className="font-black uppercase text-muted-foreground">No sector data</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-2 border-foreground">
      <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
        <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
          <PieChart className="h-4 w-4" />
          Sector Exposure
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-2 gap-4">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--background))',
                  border: '2px solid hsl(var(--foreground))',
                  borderRadius: '0px',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 max-h-[200px] overflow-y-auto">
            {chartData.map((sector, idx) => (
              <div key={sector.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3"
                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                  />
                  <span className="font-medium uppercase">{sector.name}</span>
                </div>
                <span className="font-mono">{sector.value.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function RecommendationsPanel({ metrics, limits }: { metrics?: RiskMetrics; limits?: RiskLimits }) {
  const recommendations = useMemo(() => {
    const recs: { type: 'warning' | 'success' | 'info'; title: string; message: string }[] = []

    if (metrics) {
      if (metrics.largest_position_weight > 15) {
        recs.push({
          type: 'warning',
          title: 'High Concentration Risk',
          message: `${metrics.largest_position_weight.toFixed(1)}% in single position. Consider diversifying.`,
        })
      }
      if (metrics.diversification_score < 50) {
        recs.push({
          type: 'warning',
          title: 'Low Diversification',
          message: 'Portfolio lacks diversification across assets or sectors.',
        })
      }
      if (metrics.liquidity_score < 50) {
        recs.push({
          type: 'warning',
          title: 'Liquidity Concern',
          message: 'Some positions may be difficult to exit quickly.',
        })
      }
      if (metrics.leverage > 1.5) {
        recs.push({
          type: 'warning',
          title: 'High Leverage',
          message: `Leverage at ${metrics.leverage.toFixed(2)}x increases both gains and losses.`,
        })
      }
      if (metrics.sharpe_ratio > 1) {
        recs.push({
          type: 'success',
          title: 'Good Risk-Adjusted Returns',
          message: `Sharpe ratio of ${metrics.sharpe_ratio.toFixed(2)} indicates good risk management.`,
        })
      }
      if (metrics.volatility < 15) {
        recs.push({
          type: 'success',
          title: 'Low Volatility',
          message: 'Portfolio shows stable returns with controlled volatility.',
        })
      }
      if (limits && metrics.var_95 > limits.max_var_95 * 0.8) {
        recs.push({
          type: 'warning',
          title: 'VaR Approaching Limit',
          message: 'Current VaR is within 20% of your set limit.',
        })
      }
    }

    if (recs.length === 0) {
      recs.push({
        type: 'success',
        title: 'Portfolio Looks Good',
        message: 'No major risk concerns detected. Continue monitoring.',
      })
    }

    return recs
  }, [metrics, limits])

  return (
    <Card className="border-2 border-foreground">
      <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
        <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
          <Zap className="h-4 w-4" />
          Recommendations
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-3 max-h-[300px] overflow-y-auto">
        {recommendations.map((rec, idx) => (
          <div
            key={idx}
            className={cn(
              'p-3 border-2 border-foreground/20',
              rec.type === 'warning' && 'border-yellow-500 bg-yellow-50',
              rec.type === 'success' && 'border-green-500 bg-green-50',
              rec.type === 'info' && 'border-blue-500 bg-blue-50'
            )}
          >
            <div className="flex items-center gap-2">
              {rec.type === 'warning' && <AlertTriangle className="h-4 w-4 text-yellow-600" />}
              {rec.type === 'success' && <CheckCircle className="h-4 w-4 text-green-600" />}
              {rec.type === 'info' && <Info className="h-4 w-4 text-blue-600" />}
              <p className="font-black uppercase text-xs">{rec.title}</p>
            </div>
            <p className="text-xs text-muted-foreground mt-1">{rec.message}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

function DiversificationGauge({
  label,
  value,
  max = 100,
}: {
  label: string
  value: number
  max?: number
}) {
  const percentage = Math.min((value / max) * 100, 100)
  const level = percentage > 70 ? 'low' : percentage > 50 ? 'medium' : percentage > 30 ? 'high' : 'critical'

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase">{label}</span>
        <span className="text-xs font-mono">{value.toFixed(0)}/{max}</span>
      </div>
      <Progress
        value={percentage}
        className={cn(
          'h-3',
          level === 'critical' && '[&>div]:bg-red-500',
          level === 'high' && '[&>div]:bg-orange-500',
          level === 'medium' && '[&>div]:bg-yellow-500',
          level === 'low' && '[&>div]:bg-green-500'
        )}
      />
    </div>
  )
}

export function RiskDashboard({
  metrics,
  scenarios,
  alerts,
  limits,
  holdings,
  sectors,
  history,
  loading = false,
  onRefresh,
  onScenarioSelect,
  onAlertAcknowledge,
  onPeriodChange,
  className,
}: RiskDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview')

  const riskScoreLevel = useMemo(() => {
    if (!metrics) return 'low'
    return getRiskLevel(metrics.risk_score, { low: 30, medium: 50, high: 70 })
  }, [metrics])

  if (loading) {
    return (
      <div className={cn('space-y-6', className)}>
        <Card className="border-2 border-foreground">
          <CardHeader className="border-b-2 border-foreground bg-muted/30">
            <Skeleton className="h-6 w-48" />
          </CardHeader>
          <CardContent className="p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[...Array(8)].map((_, i) => (
                <Skeleton key={i} className="h-28 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className={cn('space-y-6', className)}>
      <Card className="border-2 border-foreground">
        <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-black uppercase italic flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Risk_Dashboard
            </CardTitle>
            <div className="flex items-center gap-2">
              <Select defaultValue="30d" onValueChange={(v) => onPeriodChange?.(v)}>
                <SelectTrigger className="w-28 h-8 border-foreground/20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">7 Days</SelectItem>
                  <SelectItem value="30d">30 Days</SelectItem>
                  <SelectItem value="90d">90 Days</SelectItem>
                  <SelectItem value="180d">180 Days</SelectItem>
                  <SelectItem value="1y">1 Year</SelectItem>
                  <SelectItem value="ytd">YTD</SelectItem>
                </SelectContent>
              </Select>
              <Select defaultValue="95" onValueChange={(v) => {}}>
                <SelectTrigger className="w-24 h-8 border-foreground/20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="95">VaR 95%</SelectItem>
                  <SelectItem value="99">VaR 99%</SelectItem>
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="sm"
                onClick={onRefresh}
                className="h-8 border-foreground/20"
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-4">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="border-2 border-foreground bg-background">
              <TabsTrigger
                value="overview"
                className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs px-4"
              >
                Overview
              </TabsTrigger>
              <TabsTrigger
                value="var"
                className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs px-4"
              >
                VaR & Stress
              </TabsTrigger>
              <TabsTrigger
                value="diversification"
                className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs px-4"
              >
                Diversification
              </TabsTrigger>
              <TabsTrigger
                value="exposure"
                className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs px-4"
              >
                Exposure
              </TabsTrigger>
              <TabsTrigger
                value="alerts"
                className="data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs px-4"
              >
                Alerts
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <SummaryCard
                  title="Portfolio Risk Score"
                  value={metrics?.risk_score.toFixed(0) || 'N/A'}
                  change={-5}
                  icon={Activity}
                  description="Overall risk assessment"
                />
                <SummaryCard
                  title="Value at Risk (95%)"
                  value={formatCurrency(metrics?.var_95 || 0)}
                  icon={TrendingDown}
                  description="1-day VaR at 95% confidence"
                />
                <SummaryCard
                  title="Volatility"
                  value={formatPercent(metrics?.volatility || 0)}
                  change={-2}
                  icon={Activity}
                  description="30-day annualized volatility"
                />
                <SummaryCard
                  title="Sharpe Ratio"
                  value={metrics?.sharpe_ratio?.toFixed(2) || 'N/A'}
                  change={8}
                  icon={Target}
                  description="Risk-adjusted return"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2">
                  <RiskHistoryChart data={history || []} />
                </div>
                <RecommendationsPanel metrics={metrics} limits={limits} />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ConcentrationPanel holdings={holdings} />
                <SectorExposureChart sectors={sectors} />
              </div>

              <Card className="border-2 border-foreground">
                <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
                  <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
                    <Globe className="h-4 w-4" />
                    Diversification & Risk Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 border border-foreground/20 space-y-4">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Diversification Score</p>
                      <p className="text-3xl font-black">{metrics?.diversification_score?.toFixed(0) || 'N/A'}</p>
                      <Progress
                        value={metrics?.diversification_score || 0}
                        className="h-2 [&>div]:bg-green-500"
                      />
                      <p className="text-[10px] text-muted-foreground">Higher = more diversified</p>
                    </div>
                    <div className="p-4 border border-foreground/20 space-y-4">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Concentration Risk</p>
                      <p className="text-3xl font-black">{metrics?.concentration_risk?.toFixed(0) || 'N/A'}</p>
                      <Progress
                        value={metrics?.concentration_risk || 0}
                        className="h-2 [&>div]:bg-red-500"
                      />
                      <p className="text-[10px] text-muted-foreground">Lower = less concentrated</p>
                    </div>
                    <div className="p-4 border border-foreground/20 space-y-4">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Liquidity Score</p>
                      <p className="text-3xl font-black">{metrics?.liquidity_score?.toFixed(0) || 'N/A'}</p>
                      <Progress
                        value={metrics?.liquidity_score || 0}
                        className="h-2 [&>div]:bg-blue-500"
                      />
                      <p className="text-[10px] text-muted-foreground">Higher = more liquid</p>
                    </div>
                    <div className="p-4 border border-foreground/20 space-y-4">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Largest Position</p>
                      <p className="text-3xl font-black">{metrics?.largest_position_weight?.toFixed(1) || 'N/A'}%</p>
                      <Progress
                        value={metrics?.largest_position_weight || 0}
                        className={cn(
                          'h-2',
                          (metrics?.largest_position_weight || 0) > 15 ? '[&>div]:bg-red-500' : '[&>div]:bg-green-500'
                        )}
                      />
                      <p className="text-[10px] text-muted-foreground">&lt;15% recommended</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <RiskMetricCard
                  title="Beta vs S&P 500"
                  value={metrics?.beta?.toFixed(2) || 'N/A'}
                  subValue={metrics?.beta && metrics.beta > 1 ? 'More volatile' : 'Less volatile'}
                  icon={BarChart3}
                  level={metrics?.beta && metrics.beta > 1.5 ? 'high' : metrics?.beta && metrics.beta > 1.2 ? 'medium' : 'low'}
                  description="Portfolio sensitivity to market movements"
                />
                <RiskMetricCard
                  title="Max Drawdown"
                  value={formatPercent(metrics?.max_drawdown || 0)}
                  subValue="Historical maximum"
                  icon={TrendingDown}
                  level={getRiskLevel((metrics?.max_drawdown || 0) * -1, { low: 5, medium: 15, high: 30 })}
                  description="Largest peak-to-trough decline"
                />
                <RiskMetricCard
                  title="Sortino Ratio"
                  value={metrics?.sortino_ratio?.toFixed(2) || 'N/A'}
                  subValue="Downside risk-adjusted"
                  icon={Target}
                />
                <RiskMetricCard
                  title="Leverage"
                  value={`${(metrics?.leverage || 1).toFixed(2)}x`}
                  subValue="Effective leverage"
                  icon={Shield}
                  level={metrics?.leverage && metrics.leverage > 2 ? 'critical' : metrics?.leverage && metrics.leverage > 1.5 ? 'high' : 'low'}
                />
              </div>
            </TabsContent>

            <TabsContent value="var" className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <Card className="border-2 border-foreground">
                    <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
                      <CardTitle className="text-sm font-black uppercase">Value at Risk</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 space-y-4">
                      <div className="flex items-center justify-between p-3 border border-foreground/20">
                        <span className="text-xs font-bold uppercase">VaR 95%</span>
                        <span className="font-black text-red-600">{formatCurrency(metrics?.var_95 || 0)}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 border border-foreground/20">
                        <span className="text-xs font-bold uppercase">VaR 99%</span>
                        <span className="font-black text-red-600">{formatCurrency(metrics?.var_99 || 0)}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 border border-foreground/20">
                        <span className="text-xs font-bold uppercase">CVaR (Expected Shortfall)</span>
                        <span className="font-black text-red-600">{formatCurrency(metrics?.cvar_95 || 0)}</span>
                      </div>
                    </CardContent>
                  </Card>
                  <StressTestingPanel scenarios={scenarios} onSelect={onScenarioSelect} />
                </div>
                <RiskAlertsPanel alerts={alerts} onAcknowledge={onAlertAcknowledge} />
              </div>
            </TabsContent>

            <TabsContent value="diversification" className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ConcentrationPanel holdings={holdings} />
                <SectorExposureChart sectors={sectors} />
              </div>

              <Card className="border-2 border-foreground">
                <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
                  <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
                    <Layers className="h-4 w-4" />
                    Diversification Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 border border-foreground/20 space-y-3">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Diversification Score</p>
                      <p className="text-3xl font-black">{metrics?.diversification_score?.toFixed(0) || 'N/A'}</p>
                      <Progress value={metrics?.diversification_score || 0} className="h-2 [&>div]:bg-green-500" />
                      <p className="text-[10px] text-muted-foreground">Higher = more diversified</p>
                    </div>
                    <div className="p-4 border border-foreground/20 space-y-3">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Concentration Risk</p>
                      <p className="text-3xl font-black">{metrics?.concentration_risk?.toFixed(0) || 'N/A'}</p>
                      <Progress value={metrics?.concentration_risk || 0} className="h-2 [&>div]:bg-red-500" />
                      <p className="text-[10px] text-muted-foreground">Lower = less concentrated</p>
                    </div>
                    <div className="p-4 border border-foreground/20 space-y-3">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Liquidity Score</p>
                      <p className="text-3xl font-black">{metrics?.liquidity_score?.toFixed(0) || 'N/A'}</p>
                      <Progress value={metrics?.liquidity_score || 0} className="h-2 [&>div]:bg-blue-500" />
                      <p className="text-[10px] text-muted-foreground">Higher = more liquid</p>
                    </div>
                    <div className="p-4 border border-foreground/20 space-y-3">
                      <p className="text-xs font-bold uppercase text-muted-foreground">Avg Position Size</p>
                      <p className="text-3xl font-black">{metrics?.avg_position_size?.toFixed(1) || 'N/A'}%</p>
                      <Progress value={metrics?.avg_position_size || 0} className="h-2 [&>div]:bg-purple-500" />
                      <p className="text-[10px] text-muted-foreground">&lt;10% recommended</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <RecommendationsPanel metrics={metrics} limits={limits} />
                <RiskHistoryChart data={history || []} />
              </div>
            </TabsContent>

            <TabsContent value="exposure" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="border-2 border-foreground">
                  <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
                    <CardTitle className="text-sm font-black uppercase">Long/Short Exposure</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4 space-y-4">
                    <ExposureGauge
                      label="Long Exposure"
                      value={metrics?.long_exposure || 0}
                      max={metrics?.gross_exposure || 100}
                      unit="%"
                    />
                    <ExposureGauge
                      label="Short Exposure"
                      value={metrics?.short_exposure || 0}
                      max={metrics?.gross_exposure || 100}
                      unit="%"
                    />
                    <ExposureGauge
                      label="Net Exposure"
                      value={Math.abs((metrics?.net_exposure || 0))}
                      max={200}
                      unit="%"
                    />
                    <ExposureGauge
                      label="Gross Exposure"
                      value={metrics?.gross_exposure || 0}
                      max={200}
                      unit="%"
                    />
                  </CardContent>
                </Card>
                <Card className="border-2 border-foreground">
                  <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
                    <CardTitle className="text-sm font-black uppercase">Risk Limits</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4 space-y-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold uppercase">VaR Limit</span>
                        <span className="font-mono">{formatCurrency(limits?.max_var_95 || 0)}</span>
                      </div>
                      <Progress
                        value={((metrics?.var_95 || 0) / (limits?.max_var_95 || 1)) * 100}
                        className="h-2"
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold uppercase">Max Drawdown Limit</span>
                        <span className="font-mono">{formatPercent(limits?.max_drawdown || 0)}</span>
                      </div>
                      <Progress
                        value={((metrics?.max_drawdown || 0) / -(limits?.max_drawdown || 1)) * 100}
                        className="h-2"
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold uppercase">Max Leverage</span>
                        <span className="font-mono">{(limits?.max_leverage || 2).toFixed(1)}x</span>
                      </div>
                      <Progress
                        value={((metrics?.leverage || 1) / (limits?.max_leverage || 2)) * 100}
                        className="h-2"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="alerts">
              <RiskAlertsPanel alerts={alerts} onAcknowledge={onAlertAcknowledge} />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

export function RiskDashboardSkeleton() {
  return (
    <Card className="border-2 border-foreground">
      <CardHeader className="border-b-2 border-foreground bg-muted/30">
        <Skeleton className="h-6 w-48" />
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-28 w-full" />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
