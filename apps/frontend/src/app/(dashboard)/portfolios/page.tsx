'use client'

import { useEffect, useState } from 'react'
import { usePortfolioStore } from '@/stores/portfolioStore'
import { portfoliosApi } from '@/lib/api/portfolio'
import type { Portfolio, PortfolioHolding, PortfolioTransaction } from '@/lib/types'
import ShareDialog from '@/components/portfolio/ShareDialog'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Switch } from '@/components/ui/switch'
import {
  ArrowUpRight,
  ArrowDownRight,
  Wallet,
  TrendingUp,
  TrendingDown,
  Plus,
  RefreshCw,
  Filter,
  Download,
  PieChart,
  BarChart3,
  History,
  DollarSign,
  Settings,
} from 'lucide-react'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'
import PortfolioOverview from '@/components/portfolio/PortfolioOverview'
import HoldingsTable from '@/components/portfolio/HoldingsTable'
import PortfolioPerformance from '@/components/portfolio/PortfolioPerformance'
import TransactionsList from '@/components/portfolio/TransactionsList'
import { PortfolioSwitcher } from '@/components/portfolio/PortfolioSwitcher'

export default function PortfoliosPage() {
  const {
    portfolios,
    selectedPortfolioId,
    holdings,
    transactions,
    history,
    metrics,
    loading,
    error,
    fetchPortfolios,
    selectPortfolio,
    fetchHoldings,
    fetchTransactions,
    fetchHistory,
  } = usePortfolioStore()

  const [activeTab, setActiveTab] = useState('overview')
  const [period, setPeriod] = useState<'1m' | '3m' | '6m' | '1y' | 'all'>('1m')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [newPortfolioName, setNewPortfolioName] = useState('')
  const [portfolioVisibility, setPortfolioVisibility] = useState<Record<string, boolean>>({})

  const selectedPortfolio = portfolios.find((p) => p.id === selectedPortfolioId)

  useEffect(() => {
    fetchPortfolios()
  }, [fetchPortfolios])

  useEffect(() => {
    if (selectedPortfolioId) {
      const portfolio = portfolios.find(p => p.id === selectedPortfolioId)
      if (portfolio) {
        setPortfolioVisibility(prev => ({
          ...prev,
          [selectedPortfolioId]: portfolio.is_public
        }))
      }
    }
  }, [selectedPortfolioId, portfolios])

  const handleCreatePortfolio = async () => {
    if (!newPortfolioName.trim()) return
    try {
      await portfoliosApi.createPortfolio({ name: newPortfolioName })
      setNewPortfolioName('')
      setShowCreateDialog(false)
      fetchPortfolios()
    } catch (error) {
      console.error('Failed to create portfolio:', error)
    }
  }

  const totalValue = selectedPortfolio?.total_value || 0
  const dayPnl = selectedPortfolio?.day_pnl || 0
  const totalPnl = selectedPortfolio?.total_pnl || 0

  if (loading && portfolios.length === 0) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
        <Skeleton className="h-96" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Portfolios</h1>
          <p className="text-muted-foreground">Manage your investment portfolios</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => fetchPortfolios()} disabled={loading}>
            <RefreshCw className={cn('w-4 h-4 mr-2', loading && 'animate-spin')} />
            Refresh
          </Button>
          {selectedPortfolioId && selectedPortfolio && (
            <ShareDialog
              portfolioId={selectedPortfolioId}
              portfolioName={selectedPortfolio.name}
              isPublic={portfolioVisibility[selectedPortfolioId] || false}
              onVisibilityChange={async (isPublic) => {
                setPortfolioVisibility(prev => ({ ...prev, [selectedPortfolioId]: isPublic }))
                await portfoliosApi.updatePortfolio(selectedPortfolioId, { is_public: isPublic })
                fetchPortfolios()
              }}
            />
          )}
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                New Portfolio
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Portfolio</DialogTitle>
                <DialogDescription>
                  Create a new portfolio to track your investments
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Portfolio Name</Label>
                  <Input
                    id="name"
                    value={newPortfolioName}
                    onChange={(e) => setNewPortfolioName(e.target.value)}
                    placeholder="My Portfolio"
                  />
                </div>
                <Button onClick={handleCreatePortfolio} className="w-full">
                  Create Portfolio
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Portfolio Switcher */}
      {portfolios.length > 0 && (
        <PortfolioSwitcher />
      )}

      {/* No Portfolio State */}
      {portfolios.length === 0 && !loading && (
        <Card>
          <CardContent className="pt-6 text-center">
            <Wallet className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Portfolios Yet</h3>
            <p className="text-muted-foreground mb-4">
              Create your first portfolio to start tracking your investments
            </p>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Portfolio
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Portfolio Selected */}
      {selectedPortfolio && (
        <>
          {/* KPI Cards */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Total Value</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(totalValue)}</div>
                <div className="flex items-center text-sm">
                  {dayPnl >= 0 ? (
                    <ArrowUpRight className="w-4 h-4 text-green-500 mr-1" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 text-red-500 mr-1" />
                  )}
                  <span className={cn(dayPnl >= 0 ? 'text-green-500' : 'text-red-500')}>
                    {formatCurrency(Math.abs(dayPnl))} ({formatPercent(selectedPortfolio.day_pnl_percent)})
                  </span>
                  <span className="text-muted-foreground ml-1">today</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Total Gain/Loss</CardTitle>
                {totalPnl >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(totalPnl)}</div>
                <div className="flex items-center text-sm">
                  <span className={cn(totalPnl >= 0 ? 'text-green-500' : 'text-red-500')}>
                    {formatPercent(selectedPortfolio.total_pnl_percent)}
                  </span>
                  <span className="text-muted-foreground ml-1">all time</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Holdings</CardTitle>
                <PieChart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{holdings.length}</div>
                <p className="text-sm text-muted-foreground">assets in portfolio</p>
              </CardContent>
            </Card>
          </div>

          {/* Period Selector */}
          <div className="flex gap-2">
            {(['1m', '3m', '6m', '1y', 'all'] as const).map((p) => (
              <Button
                key={p}
                variant={period === p ? 'default' : 'outline'}
                size="sm"
                onClick={() => setPeriod(p)}
              >
                {p === '1m' ? '1M' : p === '3m' ? '3M' : p === '6m' ? '6M' : p === '1y' ? '1Y' : 'All'}
              </Button>
            ))}
          </div>

          {/* Main Content Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="overview">
                <PieChart className="w-4 h-4 mr-2" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="holdings">
                <BarChart3 className="w-4 h-4 mr-2" />
                Holdings
              </TabsTrigger>
              <TabsTrigger value="performance">
                <TrendingUp className="w-4 h-4 mr-2" />
                Performance
              </TabsTrigger>
              <TabsTrigger value="transactions">
                <History className="w-4 h-4 mr-2" />
                Transactions
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-4">
              <PortfolioOverview
                portfolio={selectedPortfolio}
                holdings={holdings}
                history={history}
                metrics={metrics}
              />
            </TabsContent>

            <TabsContent value="holdings" className="mt-4">
              <HoldingsTable holdings={holdings} loading={loading} />
            </TabsContent>

            <TabsContent value="performance" className="mt-4">
              <PortfolioPerformance
                history={history}
                metrics={metrics}
                period={period}
                onPeriodChange={setPeriod}
              />
            </TabsContent>

            <TabsContent value="transactions" className="mt-4">
              <TransactionsList transactions={transactions} loading={loading} />
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  )
}
