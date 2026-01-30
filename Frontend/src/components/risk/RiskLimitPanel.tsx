"use client"

import { useState } from 'react'
import { AlertTriangle, TrendingUp, TrendingDown, Settings, Bell, CheckCircle, XCircle, Activity } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

export interface RiskLimit {
  id: string
  name: string
  type: 'max_position' | 'max_loss' | 'max_leverage' | 'var_limit' | 'concentration' | 'sector_limit'
  value: number
  currentValue: number
  unit: 'percent' | 'x' | 'currency'
  enabled: boolean
  triggered: boolean
  priority: 'high' | 'medium' | 'low'
}

export interface RiskLimitSummary {
  totalLimits: number
  activeLimits: number
  triggeredLimits: number
  overallRiskScore: number
}

export interface RiskLimitPanelProps {
  limits?: RiskLimit[]
  summary?: RiskLimitSummary
  loading?: boolean
  error?: string
  className?: string
}

const LIMIT_TYPE_LABELS: Record<string, string> = {
  max_position: 'Max Position Size',
  max_loss: 'Max Daily Loss',
  max_leverage: 'Max Leverage',
  var_limit: 'VaR Limit',
  concentration: 'Concentration Limit',
  sector_limit: 'Sector Exposure Limit',
}

const LIMIT_TYPE_ICONS: Record<string, typeof Activity> = {
  max_position: Activity,
  max_loss: TrendingDown,
  max_leverage: TrendingUp,
  var_limit: AlertTriangle,
  concentration: Activity,
  sector_limit: Activity,
}

function LimitCard({ limit, onToggle, onEdit }: { limit: RiskLimit; onToggle: (id: string, enabled: boolean) => void; onEdit: (limit: RiskLimit) => void }) {
  const Icon = LIMIT_TYPE_ICONS[limit.type] || Activity
  const usage = limit.value > 0 ? (limit.currentValue / limit.value) * 100 : 0
  const isOver = limit.currentValue > limit.value

  return (
    <div className={cn('p-4 border rounded-lg transition-colors', limit.triggered ? 'border-red-500 bg-red-50/50 dark:bg-red-950/20' : 'hover:bg-muted/50')}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={cn('p-2 rounded-lg', limit.triggered ? 'bg-red-100 dark:bg-red-900' : 'bg-muted')}>
            <Icon className={cn('h-4 w-4', limit.triggered ? 'text-red-600' : 'text-muted-foreground')} />
          </div>
          <div>
            <h4 className="font-medium">{limit.name}</h4>
            <p className="text-xs text-muted-foreground">{LIMIT_TYPE_LABELS[limit.type]}</p>
          </div>
        </div>
        <Badge variant={limit.priority === 'high' ? 'destructive' : limit.priority === 'medium' ? 'default' : 'secondary'}>
          {limit.priority}
        </Badge>
      </div>

      <div className="mb-3">
        <div className="flex items-center justify-between text-sm mb-1">
          <span className="text-muted-foreground">Usage</span>
          <span className={cn('font-medium', isOver ? 'text-red-500' : 'text-green-500')}>
            {formatPercent(usage / 100)} / {limit.unit === 'percent' ? formatPercent(limit.value) : limit.unit === 'x' ? `${limit.value.toFixed(1)}x` : formatCurrency(limit.value)}
          </span>
        </div>
        <Progress value={Math.min(usage, 100)} className={cn('h-2', isOver && 'bg-red-200')} />
        <div className="flex justify-between text-xs text-muted-foreground mt-1">
          <span>{formatCurrency(limit.currentValue)}</span>
          <span>{formatCurrency(limit.value)}</span>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <Switch checked={limit.enabled} onCheckedChange={(checked) => onToggle(limit.id, checked)} disabled={limit.triggered} />
        <Button variant="ghost" size="sm" onClick={() => onEdit(limit)}>
          <Settings className="h-4 w-4" />
        </Button>
      </div>

      {limit.triggered && (
        <div className="mt-3 pt-3 border-t border-red-200 dark:border-red-900">
          <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
            <AlertTriangle className="h-4 w-4" />
            <span className="font-medium">Limit triggered!</span>
          </div>
        </div>
      )}
    </div>
  )
}

function RiskScoreGauge({ score }: { score: number }) {
  const getColor = () => {
    if (score >= 70) return 'text-red-500'
    if (score >= 40) return 'text-amber-500'
    return 'text-green-500'
  }

  const getBgColor = () => {
    if (score >= 70) return 'bg-red-500'
    if (score >= 40) return 'bg-amber-500'
    return 'bg-green-500'
  }

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg className="w-full h-full transform -rotate-90">
          <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="none" className="text-muted" />
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            strokeDasharray={`${score * 3.52} 352`}
            className={getColor()}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn('text-3xl font-bold', getColor())}>{score}</span>
        </div>
      </div>
      <p className="text-sm text-muted-foreground mt-2">Risk Score</p>
    </div>
  )
}

export function RiskLimitPanel({
  limits = [],
  summary,
  loading = false,
  error,
  className,
}: RiskLimitPanelProps) {
  const [activeTab, setActiveTab] = useState('limits')
  const [editingLimit, setEditingLimit] = useState<RiskLimit | null>(null)

  const handleToggle = (id: string, enabled: boolean) => {
    console.log(`Toggle limit ${id} to ${enabled}`)
  }

  const handleEdit = (limit: RiskLimit) => {
    setEditingLimit(limit)
  }

  const triggeredLimits = limits.filter(l => l.triggered)
  const activeLimits = limits.filter(l => l.enabled && !l.triggered)

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-48 mt-2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-72 w-full" />
        </CardContent>
      </Card>
    )
  }

  if (error || (!limits.length && !summary)) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Risk Limits
          </CardTitle>
          <CardDescription>Configure and monitor portfolio risk limits</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No risk limits configured'}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Risk Limits
            </CardTitle>
            <CardDescription>Configure and monitor portfolio risk limits</CardDescription>
          </div>
          <Button size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Add Limit
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-muted/30 rounded-lg">
            <div className="text-2xl font-bold">{summary?.totalLimits || limits.length}</div>
            <div className="text-xs text-muted-foreground">Total Limits</div>
          </div>
          <div className="text-center p-4 bg-muted/30 rounded-lg">
            <div className="text-2xl font-bold text-green-500">{summary?.activeLimits || activeLimits.length}</div>
            <div className="text-xs text-muted-foreground">Active</div>
          </div>
          <div className="text-center p-4 bg-muted/30 rounded-lg">
            <div className="text-2xl font-bold text-red-500">{summary?.triggeredLimits || triggeredLimits.length}</div>
            <div className="text-xs text-muted-foreground">Triggered</div>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="limits">All Limits</TabsTrigger>
            <TabsTrigger value="triggered">Triggered ({triggeredLimits.length})</TabsTrigger>
            <TabsTrigger value="score">Risk Score</TabsTrigger>
          </TabsList>

          <TabsContent value="limits" className="mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {limits.map((limit) => (
                <LimitCard key={limit.id} limit={limit} onToggle={handleToggle} onEdit={handleEdit} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="triggered" className="mt-4">
            {triggeredLimits.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {triggeredLimits.map((limit) => (
                  <LimitCard key={limit.id} limit={limit} onToggle={handleToggle} onEdit={handleEdit} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No limits triggered</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="score" className="mt-4">
            <div className="flex items-center justify-center py-8">
              <RiskScoreGauge score={summary?.overallRiskScore || 35} />
            </div>
            <div className="text-center text-sm text-muted-foreground mt-4">
              <p>Lower is better · 0-39 Low · 40-69 Medium · 70+ High</p>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
