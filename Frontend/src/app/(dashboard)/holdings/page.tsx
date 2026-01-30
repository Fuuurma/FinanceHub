'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { useHoldings } from '@/stores/holdingsStore'
import {
  HoldingsDataTable,
  HoldingsToolbar,
  EditHoldingDialog,
  TransactionHistory,
} from '@/components/holdings'
import {
  HoldingsPnLChart,
  HoldingsAllocationChart,
  TopHoldingsChart,
} from '@/components/charts'
import { AddTransactionDialog } from '@/components/holdings/AddTransactionDialog'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { TrendingUp, TrendingDown, Wallet, PieChart, BarChart3, History, Plus } from 'lucide-react'
import type { Holding, Transaction, HoldingsFilter, TransactionFilter } from '@/lib/types/holdings'
import { exportHoldingsToCSV, exportHoldingsToJSON, exportTransactionsToCSV, exportTransactionsToJSON } from '@/lib/utils/export'
import { cn, formatCurrency } from '@/lib/utils'

export default function HoldingsPage() {
  const params = useParams()
  const portfolioId = (params.id as string) || 'default'

  const {
    holdings,
    transactions,
    portfolioSummary,
    pnlHistory,
    allocation,
    holdingsLoading,
    transactionsLoading,
    summaryLoading,
    pnlLoading,
    holdingsError,
    transactionsError,
    fetchHoldings,
    fetchTransactions,
    fetchSummary,
    fetchPnL,
    fetchAllocation,
    addHolding,
    updateHolding,
    removeHolding,
    addTransaction,
    removeTransaction,
    setHoldingsFilters,
    setTransactionsFilters,
  } = useHoldings()

  const [holdingsFilters, setLocalHoldingsFilters] = useState<HoldingsFilter>({})
  const [transactionsFilters, setLocalTransactionsFilters] = useState<TransactionFilter>({})
  const [editHolding, setEditHolding] = useState<Holding | null>(null)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [addTransactionOpen, setAddTransactionOpen] = useState(false)

  useEffect(() => {
    fetchHoldings(portfolioId, holdingsFilters)
    fetchTransactions(portfolioId, transactionsFilters)
    fetchSummary(portfolioId)
    fetchPnL(portfolioId, '1y')
    fetchAllocation(portfolioId)
  }, [portfolioId])

  const handleSearch = (search: string) => {
    const newFilters = { ...holdingsFilters, search }
    setLocalHoldingsFilters(newFilters)
    fetchHoldings(portfolioId, newFilters)
  }

  const handleFilterChange = (filters: Partial<HoldingsFilter>) => {
    const newFilters = { ...holdingsFilters, ...filters }
    setLocalHoldingsFilters(newFilters)
    fetchHoldings(portfolioId, newFilters)
  }

  const handleRefresh = () => {
    fetchHoldings(portfolioId, holdingsFilters)
    fetchTransactions(portfolioId, transactionsFilters)
    fetchSummary(portfolioId)
    fetchPnL(portfolioId, '1y')
    fetchAllocation(portfolioId)
  }

  const handleEditHolding = (holding: Holding) => {
    setEditHolding(holding)
    setEditDialogOpen(true)
  }

  const handleUpdateHolding = async (data: any) => {
    if (!editHolding) return
    await updateHolding(portfolioId, editHolding.id, data)
    setEditDialogOpen(false)
    setEditHolding(null)
  }

  const handleDeleteHolding = async (holding: Holding) => {
    if (!confirm(`Are you sure you want to remove ${holding.symbol} from your portfolio?`)) {
      return
    }
    await removeHolding(portfolioId, holding.id)
  }

  const handleAddTransaction = async (data: any) => {
    await addTransaction(portfolioId, data)
    setAddTransactionOpen(false)
  }

  const handleViewTransaction = (transaction: Transaction) => {
    console.log('View transaction:', transaction)
  }

  const handleDeleteTransaction = async (transaction: Transaction) => {
    if (!confirm(`Are you sure you want to delete this ${transaction.type} transaction?`)) {
      return
    }
    await removeTransaction(portfolioId, transaction.id)
  }

  const handleTransactionFilterChange = (filters: Partial<TransactionFilter>) => {
    const newFilters = { ...transactionsFilters, ...filters }
    setLocalTransactionsFilters(newFilters)
    fetchTransactions(portfolioId, newFilters)
  }

  const handleExportHoldingsCSV = () => {
    exportHoldingsToCSV(holdings)
  }

  const handleExportHoldingsJSON = () => {
    exportHoldingsToJSON(holdings)
  }

  const handleExportTransactionsCSV = () => {
    exportTransactionsToCSV(transactions)
  }

  const handleExportTransactionsJSON = () => {
    exportTransactionsToJSON(transactions)
  }

  const totalValue = portfolioSummary?.total_value || 0
  const totalPnl = portfolioSummary?.total_pnl || 0
  const dayChange = portfolioSummary?.day_change || 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Portfolio Holdings</h1>
          <p className="text-muted-foreground">
            {portfolioSummary?.name || 'My Portfolio'} - Manage your investments
          </p>
        </div>
        <Button onClick={() => setAddTransactionOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Transaction
        </Button>
      </div>

      {holdingsError && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
          <p>{holdingsError}</p>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-base">Total Value</CardDescription>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className="h-9 w-32" />
            ) : (
              <p className="text-3xl font-bold">{formatCurrency(totalValue)}</p>
            )}
            {dayChange !== 0 && (
              <p className={cn(
                'text-sm mt-1 flex items-center',
                dayChange >= 0 ? 'text-green-600' : 'text-red-600'
              )}>
                {dayChange >= 0 ? (
                  <TrendingUp className="w-3 h-3 mr-1" />
                ) : (
                  <TrendingDown className="w-3 h-3 mr-1" />
                )}
                {dayChange >= 0 ? '+' : ''}{formatCurrency(dayChange)}
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-base">Total P&L</CardDescription>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className="h-9 w-32" />
            ) : (
              <p className={cn(
                'text-3xl font-bold',
                totalPnl >= 0 ? 'text-green-600' : 'text-red-600'
              )}>
                {totalPnl >= 0 ? '+' : ''}{formatCurrency(totalPnl)}
              </p>
            )}
            {portfolioSummary && (
              <p className={cn(
                'text-sm mt-1',
                portfolioSummary.total_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'
              )}>
                {portfolioSummary.total_pnl_percent >= 0 ? '+' : ''}{portfolioSummary.total_pnl_percent.toFixed(2)}%
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-base">Holdings</CardDescription>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <p className="text-3xl font-bold">{portfolioSummary?.holdings_count || holdings.length}</p>
            )}
            <p className="text-sm text-muted-foreground mt-1">
              Across {(portfolioSummary?.asset_allocation?.length || 0)} asset classes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-base">Day Change</CardDescription>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className="h-9 w-32" />
            ) : (
              <p className={cn(
                'text-3xl font-bold',
                dayChange >= 0 ? 'text-green-600' : 'text-red-600'
              )}>
                {dayChange >= 0 ? '+' : ''}{formatCurrency(dayChange)}
              </p>
            )}
            {portfolioSummary && (
              <p className={cn(
                'text-sm mt-1',
                portfolioSummary.day_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
              )}>
                {portfolioSummary.day_change_percent >= 0 ? '+' : ''}{portfolioSummary.day_change_percent.toFixed(2)}%
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="holdings" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="holdings">
            <Wallet className="w-4 h-4 mr-2" />
            Holdings
          </TabsTrigger>
          <TabsTrigger value="charts">
            <PieChart className="w-4 h-4 mr-2" />
            Charts
          </TabsTrigger>
          <TabsTrigger value="transactions">
            <History className="w-4 h-4 mr-2" />
            Transactions
          </TabsTrigger>
          <TabsTrigger value="overview">
            <BarChart3 className="w-4 h-4 mr-2" />
            Overview
          </TabsTrigger>
        </TabsList>

        <TabsContent value="holdings" className="space-y-4">
          <HoldingsToolbar
            onSearch={handleSearch}
            onFilterChange={handleFilterChange}
            onRefresh={handleRefresh}
            onExport={handleExportHoldingsCSV}
            loading={holdingsLoading}
            filters={holdingsFilters}
          />
          <HoldingsDataTable
            holdings={holdings}
            loading={holdingsLoading}
            onEdit={handleEditHolding}
            onDelete={handleDeleteHolding}
          />
        </TabsContent>

        <TabsContent value="charts" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>P&L History</CardTitle>
                <CardDescription>Portfolio value and profit over time</CardDescription>
              </CardHeader>
              <CardContent>
                <HoldingsPnLChart data={pnlHistory} loading={pnlLoading} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Asset Allocation</CardTitle>
                <CardDescription>Distribution by asset class</CardDescription>
              </CardHeader>
              <CardContent>
                <HoldingsAllocationChart data={allocation} loading={summaryLoading} />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Top Holdings</CardTitle>
              <CardDescription>Your largest positions by value</CardDescription>
            </CardHeader>
            <CardContent>
              <TopHoldingsChart holdings={holdings} loading={holdingsLoading} topN={10} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="transactions" className="space-y-4">
          <TransactionHistory
            transactions={transactions}
            loading={transactionsLoading}
            onView={handleViewTransaction}
            onDelete={handleDeleteTransaction}
            onFilterChange={handleTransactionFilterChange}
            filters={transactionsFilters}
            pagination={{
              page: 1,
              pageSize: 20,
              total: transactions.length,
              onPageChange: (page) => console.log('Page:', page),
            }}
          />
        </TabsContent>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Asset Allocation</CardTitle>
                <CardDescription>Distribution by asset class</CardDescription>
              </CardHeader>
              <CardContent>
                <HoldingsAllocationChart data={allocation} loading={summaryLoading} type="pie" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Holdings</CardTitle>
                <CardDescription>Your largest positions</CardDescription>
              </CardHeader>
              <CardContent>
                <TopHoldingsChart holdings={holdings} loading={holdingsLoading} topN={10} />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Performance History</CardTitle>
              <CardDescription>Portfolio value and P&L over time</CardDescription>
            </CardHeader>
            <CardContent>
              <HoldingsPnLChart data={pnlHistory} loading={pnlLoading} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <EditHoldingDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        holding={editHolding}
        onSubmit={handleUpdateHolding}
      />

      <AddTransactionDialog
        open={addTransactionOpen}
        onOpenChange={setAddTransactionOpen}
        onSubmit={handleAddTransaction}
        existingHoldings={holdings.map((h) => ({
          symbol: h.symbol,
          name: h.name,
          quantity: h.quantity,
          average_cost: h.average_cost,
        }))}
      />
    </div>
  )
}
