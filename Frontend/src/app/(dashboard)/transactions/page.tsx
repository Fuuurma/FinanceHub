'use client'

import { useEffect, useState } from 'react'
import { transactionsApi, Transaction } from '@/lib/api/transactions'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Plus, Download, Filter, ArrowUpRight, ArrowDownRight, DollarSign, Calendar, Trash2 } from 'lucide-react'

interface TransactionsPageProps {
  portfolioId: string
  portfolioName: string
}

export default function TransactionsPage({ portfolioId, portfolioName }: TransactionsPageProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [typeFilter, setTypeFilter] = useState('all')
  const [showFilters, setShowFilters] = useState(false)

  const [newTransaction, setNewTransaction] = useState({
    transaction_type: 'buy' as 'buy' | 'sell' | 'dividend',
    asset_id: '',
    quantity: '',
    price_per_share: '',
    fees: '0',
    date: new Date().toISOString().split('T')[0],
    notes: '',
  })

  useEffect(() => {
    fetchTransactions()
  }, [portfolioId, typeFilter])

  const fetchTransactions = async () => {
    setLoading(true)
    setError('')
    try {
      const params: any = {}
      if (typeFilter !== 'all') {
        params.transaction_type = typeFilter
      }
      const data = await transactionsApi.list(portfolioId, params)
      setTransactions(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch transactions')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTransaction = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await transactionsApi.create(portfolioId, {
        ...newTransaction,
        quantity: newTransaction.quantity || undefined,
        fees: newTransaction.fees || undefined,
      })
      setShowCreateDialog(false)
      setNewTransaction({
        transaction_type: 'buy',
        asset_id: '',
        quantity: '',
        price_per_share: '',
        fees: '0',
        date: new Date().toISOString().split('T')[0],
        notes: '',
      })
      fetchTransactions()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create transaction')
    }
  }

  const handleDeleteTransaction = async (transactionId: string) => {
    if (!confirm('Are you sure you want to delete this transaction?')) return
    try {
      await transactionsApi.delete(portfolioId, transactionId)
      fetchTransactions()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete transaction')
    }
  }

  const handleExport = () => {
    const data = JSON.stringify(transactions, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transactions-${portfolioName}-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const totalBuys = transactions
    .filter((t) => t.transaction_type === 'buy')
    .reduce((sum, t) => sum + parseFloat(t.total_amount), 0)

  const totalSells = transactions
    .filter((t) => t.transaction_type === 'sell')
    .reduce((sum, t) => sum + parseFloat(t.total_amount), 0)

  const totalDividends = transactions
    .filter((t) => t.transaction_type === 'dividend')
    .reduce((sum, t) => sum + parseFloat(t.total_amount), 0)

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'buy':
        return <Badge className="bg-green-100 text-green-800">Buy</Badge>
      case 'sell':
        return <Badge className="bg-red-100 text-red-800">Sell</Badge>
      case 'dividend':
        return <Badge className="bg-blue-100 text-blue-800">Dividend</Badge>
      default:
        return <Badge variant="outline">{type}</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{portfolioName}</h1>
          <p className="text-muted-foreground">Transaction History</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Record Transaction
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Record Transaction</DialogTitle>
                <DialogDescription>Add a new transaction to your portfolio</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreateTransaction} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="type">Transaction Type</Label>
                  <Select
                    value={newTransaction.transaction_type}
                    onValueChange={(v: 'buy' | 'sell' | 'dividend') =>
                      setNewTransaction({ ...newTransaction, transaction_type: v })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="buy">Buy</SelectItem>
                      <SelectItem value="sell">Sell</SelectItem>
                      <SelectItem value="dividend">Dividend</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="assetId">Asset ID</Label>
                  <Input
                    id="assetId"
                    value={newTransaction.asset_id}
                    onChange={(e) =>
                      setNewTransaction({ ...newTransaction, asset_id: e.target.value })
                    }
                    placeholder="Enter asset UUID"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="quantity">Quantity</Label>
                    <Input
                      id="quantity"
                      type="number"
                      step="any"
                      value={newTransaction.quantity}
                      onChange={(e) =>
                        setNewTransaction({ ...newTransaction, quantity: e.target.value })
                      }
                      placeholder="0.00"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="price">Price per Share</Label>
                    <Input
                      id="price"
                      type="number"
                      step="any"
                      value={newTransaction.price_per_share}
                      onChange={(e) =>
                        setNewTransaction({ ...newTransaction, price_per_share: e.target.value })
                      }
                      placeholder="0.00"
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="fees">Fees</Label>
                    <Input
                      id="fees"
                      type="number"
                      step="any"
                      value={newTransaction.fees}
                      onChange={(e) =>
                        setNewTransaction({ ...newTransaction, fees: e.target.value })
                      }
                      placeholder="0.00"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="date">Date</Label>
                    <Input
                      id="date"
                      type="date"
                      value={newTransaction.date}
                      onChange={(e) =>
                        setNewTransaction({ ...newTransaction, date: e.target.value })
                      }
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="notes">Notes</Label>
                  <Input
                    id="notes"
                    value={newTransaction.notes}
                    onChange={(e) =>
                      setNewTransaction({ ...newTransaction, notes: e.target.value })
                    }
                    placeholder="Optional notes"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Record</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
          <p>{error}</p>
        </div>
      )}

      {showFilters && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex gap-4">
              <div className="space-y-2">
                <Label>Type Filter</Label>
                <Select value={typeFilter} onValueChange={setTypeFilter}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="buy">Buy</SelectItem>
                    <SelectItem value="sell">Sell</SelectItem>
                    <SelectItem value="dividend">Dividend</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader>
            <CardDescription>Total Buys</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">${totalBuys.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Total Sells</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-600">${totalSells.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Dividends</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-blue-600">${totalDividends.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Total Transactions</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{transactions.length}</p>
          </CardContent>
        </Card>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-16 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : transactions.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Calendar className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-4">No transactions found</p>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Record Your First Transaction
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {transactions.map((transaction) => (
            <Card key={transaction.id}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getTypeBadge(transaction.transaction_type)}
                      <span className="font-semibold">{transaction.asset.ticker}</span>
                      <span className="text-sm text-muted-foreground">
                        {transaction.asset.name}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Date</p>
                        <p className="font-medium">
                          {new Date(transaction.date).toLocaleDateString()}
                        </p>
                      </div>
                      {transaction.quantity && (
                        <div>
                          <p className="text-sm text-muted-foreground">Quantity</p>
                          <p className="font-medium">
                            {parseFloat(transaction.quantity).toLocaleString()}
                          </p>
                        </div>
                      )}
                      <div>
                        <p className="text-sm text-muted-foreground">Price</p>
                        <p className="font-medium">
                          ${parseFloat(transaction.price_per_share).toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Total</p>
                        <p className="font-semibold">
                          ${parseFloat(transaction.total_amount).toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Fees</p>
                        <p className="font-medium">
                          ${parseFloat(transaction.fees).toFixed(2)}
                        </p>
                      </div>
                    </div>
                    {transaction.notes && (
                      <p className="text-sm text-muted-foreground mt-2">
                        Note: {transaction.notes}
                      </p>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteTransaction(transaction.id)}
                  >
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
