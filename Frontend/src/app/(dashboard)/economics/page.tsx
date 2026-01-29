'use client'

import { useEffect, useState } from 'react'
import { useEconomicStore } from '@/stores/economicStore'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { IndicatorCard } from '@/components/economic/IndicatorCard'
import { YieldCurveChart } from '@/components/economic/YieldCurveChart'
import {
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Settings,
  Download,
  Brain,
  ChevronDown,
  DollarSign,
  Activity,
  Building,
  ShoppingCart,
  Factory,
  Briefcase,
  BarChart3,
  LineChart,
  Sparkles,
  Eye,
  EyeOff,
  LayoutGrid,
  List,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { MacroDashboardData, YieldCurvePoint } from '@/lib/types'

type ViewMode = 'grid' | 'list'
type TimeRange = '1m' | '3m' | '6m' | '1y' | '5y'

const ECONOMIC_CATEGORIES = [
  { id: 'gdp', name: 'GDP & Growth', icon: TrendingUp, color: 'text-blue-600' },
  { id: 'inflation', name: 'Inflation', icon: Activity, color: 'text-red-600' },
  { id: 'employment', name: 'Employment', icon: Briefcase, color: 'text-green-600' },
  { id: 'interest_rates', name: 'Interest Rates', icon: LineChart, color: 'text-purple-600' },
  { id: 'housing', name: 'Housing', icon: Building, color: 'text-orange-600' },
  { id: 'consumer', name: 'Consumer', icon: ShoppingCart, color: 'text-pink-600' },
  { id: 'industrial', name: 'Industrial', icon: Factory, color: 'text-cyan-600' },
] as const

export default function EconomicsPage() {
  const {
    macroData,
    loading,
    error,
    lastFetched,
    config,
    fetchMacroData,
    refreshData,
    toggleCategory,
    setCategoryVisible,
  } = useEconomicStore()

  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [timeRange, setTimeRange] = useState<TimeRange>('1y')
  const [showAIAnalysis, setShowAIAnalysis] = useState(false)
  const [showCustomize, setShowCustomize] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  useEffect(() => {
    fetchMacroData()
  }, [])

  const handleRefresh = async () => {
    await refreshData()
  }

  const handleExport = () => {
    if (!macroData) return

    const data = JSON.stringify(macroData, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `economic-data-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getYieldCurveData = (): YieldCurvePoint[] => {
    if (!macroData?.treasury_yields) return []

    return Object.entries(macroData.treasury_yields).map(([maturity, data]) => ({
      maturity,
      name: data.name,
      rate: data.rate || 0,
      date: data.date || '',
    }))
  }

  const getGDPValue = () => {
    const obs = macroData?.gdp?.observations
    if (!obs || obs.length === 0) return null
    const latest = obs[obs.length - 1]
    return {
      value: parseFloat(latest.value).toFixed(2),
      unit: 'Billion $',
      date: latest.date,
    }
  }

  const getCPIValue = () => {
    const obs = macroData?.cpi?.observations
    if (!obs || obs.length === 0) return null
    const latest = obs[obs.length - 1]
    return {
      value: parseFloat(latest.value).toFixed(2),
      unit: 'Index',
      date: latest.date,
    }
  }

  const getUnemploymentValue = () => {
    const obs = macroData?.unemployment?.observations
    if (!obs || obs.length === 0) return null
    const latest = obs[obs.length - 1]
    return {
      value: parseFloat(latest.value).toFixed(1),
      unit: '%',
      date: latest.date,
    }
  }

  const getFedFundsRate = () => {
    const obs = macroData?.fed_funds_rate?.observations
    if (!obs || obs.length === 0) return null
    const latest = obs[obs.length - 1]
    return {
      value: parseFloat(latest.value).toFixed(2),
      unit: '%',
      date: latest.date,
    }
  }

  const visibleCategories = ECONOMIC_CATEGORIES.filter((cat) =>
    config.visibleCategories.includes(cat.id)
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Economic Dashboard</h1>
          <p className="text-muted-foreground">
            Real-time economic indicators and macro trends from FRED
          </p>
          {lastFetched && (
            <p className="text-xs text-muted-foreground mt-1">
              Last updated: {new Date(lastFetched).toLocaleString()}
            </p>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex items-center border rounded-md">
            <Button
              variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <LayoutGrid className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>

          {/* Time Range Selector */}
          <Select value={timeRange} onValueChange={(v) => setTimeRange(v as TimeRange)}>
            <SelectTrigger className="w-[100px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1m">1 Month</SelectItem>
              <SelectItem value="3m">3 Months</SelectItem>
              <SelectItem value="6m">6 Months</SelectItem>
              <SelectItem value="1y">1 Year</SelectItem>
              <SelectItem value="5y">5 Years</SelectItem>
            </SelectContent>
          </Select>

          {/* Customize Button */}
          <Dialog open={showCustomize} onOpenChange={setShowCustomize}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Customize
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Customize Dashboard</DialogTitle>
                <DialogDescription>
                  Select which economic categories to display
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-3">
                {ECONOMIC_CATEGORIES.map((category) => {
                  const Icon = category.icon
                  return (
                    <div
                      key={category.id}
                      className="flex items-center justify-between p-2 rounded-md hover:bg-muted"
                    >
                      <div className="flex items-center gap-2">
                        <Icon className={cn('h-4 w-4', category.color)} />
                        <span className="text-sm font-medium">{category.name}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleCategory(category.id)}
                      >
                        {config.visibleCategories.includes(category.id) ? (
                          <Eye className="h-4 w-4" />
                        ) : (
                          <EyeOff className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  )
                })}
              </div>
            </DialogContent>
          </Dialog>

          {/* AI Analysis */}
          <Dialog open={showAIAnalysis} onOpenChange={setShowAIAnalysis}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Brain className="h-4 w-4 mr-2" />
                AI Analysis
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  AI Economic Analysis
                </DialogTitle>
                <DialogDescription>
                  AI-powered insights and economic trend analysis
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="text-center p-8 border-2 border-dashed rounded-lg">
                  <Brain className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-lg font-semibold mb-2">AI Analysis Coming Soon</p>
                  <p className="text-sm text-muted-foreground">
                    Advanced AI-powered economic insights and trend analysis will be available here.
                  </p>
                </div>

                <Separator />

                <div className="space-y-2">
                  <p className="text-sm font-semibold">Upcoming Features:</p>
                  <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                    <li>• Economic trend prediction and forecasting</li>
                    <li>• Correlation analysis between indicators</li>
                    <li>• Anomaly detection in economic data</li>
                    <li>• Natural language queries about economic indicators</li>
                    <li>• Automated economic report generation</li>
                    <li>• Sentiment analysis from economic news</li>
                  </ul>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          {/* Export Button */}
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>

          {/* Refresh Button */}
          <Button variant="default" size="sm" onClick={handleRefresh} disabled={loading}>
            <RefreshCw className={cn('h-4 w-4 mr-2', loading && 'animate-spin')} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <Card className="border-red-600">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <Activity className="h-5 w-5" />
              <p className="font-semibold">Error loading economic data</p>
            </div>
            <p className="text-sm text-muted-foreground mt-1">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Loading Skeleton */}
      {loading && !macroData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-[140px] rounded-lg" />
          ))}
        </div>
      )}

      {/* Yield Curve Section - Always Visible */}
      {!loading && macroData && (
        <YieldCurveChart
          data={getYieldCurveData()}
          showSpreads={true}
          className="col-span-full"
        />
      )}

      {/* Main Dashboard Content */}
      {!loading && macroData && (
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="detailed">Detailed</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Key Indicators Grid */}
            <div
              className={cn(
                'grid gap-4',
                viewMode === 'grid'
                  ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
                  : 'grid-cols-1'
              )}
            >
              {/* GDP Card */}
              {config.visibleCategories.includes('gdp') && getGDPValue() && (
                <IndicatorCard
                  title="GDP"
                  value={getGDPValue()!.value}
                  unit={getGDPValue()!.unit}
                  date={getGDPValue()!.date}
                  icon={<TrendingUp className="h-4 w-4 text-blue-600" />}
                  description="Gross Domestic Product"
                  change={2.1}
                  changeType="positive"
                />
              )}

              {/* Inflation Card */}
              {config.visibleCategories.includes('inflation') && getCPIValue() && (
                <IndicatorCard
                  title="CPI"
                  value={getCPIValue()!.value}
                  unit={getCPIValue()!.unit}
                  date={getCPIValue()!.date}
                  icon={<Activity className="h-4 w-4 text-red-600" />}
                  description="Consumer Price Index"
                  change={3.2}
                  changeType="negative"
                />
              )}

              {/* Unemployment Card */}
              {config.visibleCategories.includes('employment') && getUnemploymentValue() && (
                <IndicatorCard
                  title="Unemployment"
                  value={getUnemploymentValue()!.value}
                  unit={getUnemploymentValue()!.unit}
                  date={getUnemploymentValue()!.date}
                  icon={<Briefcase className="h-4 w-4 text-green-600" />}
                  description="Unemployment Rate"
                  change={-0.2}
                  changeType="positive"
                />
              )}

              {/* Fed Funds Rate Card */}
              {config.visibleCategories.includes('interest_rates') && getFedFundsRate() && (
                <IndicatorCard
                  title="Fed Funds Rate"
                  value={getFedFundsRate()!.value}
                  unit={getFedFundsRate()!.unit}
                  date={getFedFundsRate()!.date}
                  icon={<LineChart className="h-4 w-4 text-purple-600" />}
                  description="Federal Funds Rate"
                  change={0.25}
                  changeType="positive"
                />
              )}
            </div>

            {/* Housing & Consumer Section */}
            <div className="grid gap-4 md:grid-cols-2">
              {/* Housing Data */}
              {config.visibleCategories.includes('housing') && macroData.housing && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Building className="h-5 w-5 text-orange-600" />
                      Housing Market
                    </CardTitle>
                    <CardDescription>Housing starts and building permits</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {macroData.housing.housing_starts && (
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-muted-foreground">Housing Starts</p>
                          <p className="text-2xl font-bold">
                            {macroData.housing.housing_starts.value?.toLocaleString()}
                          </p>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {macroData.housing.housing_starts.units}
                        </Badge>
                      </div>
                    )}
                    <Separator />
                    {macroData.housing.building_permits && (
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-muted-foreground">Building Permits</p>
                          <p className="text-2xl font-bold">
                            {macroData.housing.building_permits.value?.toLocaleString()}
                          </p>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {macroData.housing.building_permits.units}
                        </Badge>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Mortgage Rates */}
              {config.visibleCategories.includes('interest_rates') && macroData.mortgage_rates && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <DollarSign className="h-5 w-5 text-green-600" />
                      Mortgage Rates
                    </CardTitle>
                    <CardDescription>Current mortgage interest rates</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {macroData.mortgage_rates['30y'] && (
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-muted-foreground">30-Year Fixed</p>
                          <p className="text-2xl font-bold">
                            {macroData.mortgage_rates['30y'].rate}%
                          </p>
                        </div>
                        <TrendingUp className="h-5 w-5 text-red-600" />
                      </div>
                    )}
                    <Separator />
                    {macroData.mortgage_rates['15y'] && (
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-muted-foreground">15-Year Fixed</p>
                          <p className="text-2xl font-bold">
                            {macroData.mortgage_rates['15y'].rate}%
                          </p>
                        </div>
                        <TrendingDown className="h-5 w-5 text-green-600" />
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Detailed Tab */}
          <TabsContent value="detailed" className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {visibleCategories.map((category) => {
                const Icon = category.icon
                return (
                  <Card key={category.id} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Icon className={cn('h-5 w-5', category.color)} />
                        {category.name}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Detailed {category.name.toLowerCase()} data and analysis
                      </p>
                      <Button variant="outline" size="sm" className="mt-4 w-full">
                        View Details
                      </Button>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>

          {/* Trends Tab */}
          <TabsContent value="trends" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Economic Trends</CardTitle>
                <CardDescription>
                  Historical trends and patterns for key economic indicators
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12 text-muted-foreground">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Trend charts will be displayed here</p>
                  <p className="text-sm">Select an indicator to view its historical trend</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analysis Tab */}
          <TabsContent value="analysis" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Economic Analysis</CardTitle>
                <CardDescription>
                  In-depth analysis and correlation between indicators
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12 text-muted-foreground">
                  <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Advanced analysis tools coming soon</p>
                  <p className="text-sm">Correlation analysis, forecasting, and more</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
