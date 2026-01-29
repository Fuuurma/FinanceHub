'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { cn, formatCurrency, formatDate } from '@/lib/utils'
import type { PortfolioTransaction } from '@/lib/types'
import { ArrowUpDown, Search, Filter, Download } from 'lucide-react'

interface TransactionsListProps {
  transactions: PortfolioTransaction[]
  loading: boolean
}

type FilterType = 'all' | 'buy' | 'sell' | 'dividend' | 'deposit' | 'withdrawal'

export default function TransactionsList({ transactions, loading }: TransactionsListProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<FilterType>('all')

  const filteredTransactions = transactions
    .filter((t) => {
      if (filterType !== 'all' && t.type !== filterType) return false
      if (searchTerm) {
        const search = searchTerm.toLowerCase()
        return (
          t.symbol?.toLowerCase().includes(search) ||
          t.type.toLowerCase().includes(search)
        )
      }
      return true
    })
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())

  const getTransactionIcon = (type: PortfolioTransaction['type']) => {
    switch (type) {
      case 'buy':
        return <ArrowUpDown className="w-4 h-4 text-green-500 rotate-180" />
      case 'sell':
        return <ArrowUpDown className="w-4 h-4 text-red-500" />
      case 'dividend':
        return <span className="text-green-500 font-bold">D</span>
      case 'deposit':
      case 'transfer_in':
        return <span className="text-green-500 font-bold">+</span>
      case 'withdrawal':
      case 'transfer_out':
        return <span className="text-red-500 font-bold">-</span>
      default:
        return null
    }
  }

  const getTransactionBadge = (type: PortfolioTransaction['type']) => {
    const styles: Record<PortfolioTransaction['type'], string> = {
      buy: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
      sell: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100',
      dividend: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100',
      deposit: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
      withdrawal: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100',
      transfer_in: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
      transfer_out: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100',
    }
    return styles[type] || 'bg-muted'
  }

  const handleExport = () => {
    const headers = ['Date', 'Type', 'Symbol', 'Quantity', 'Price', 'Amount', 'Fees']
    const rows = filteredTransactions.map((t) => [
      t.date,
      t.type,
      t.symbol || '-',
      t.quantity?.toString() || '-',
      t.price?.toString() || '-',
      t.amount.toString(),
      t.fees.toString(),
    ])
    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transactions-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-16" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Transactions</CardTitle>
            <CardDescription>Recent portfolio activity</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search transactions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
          <Select
            value={filterType}
            onValueChange={(v) => setFilterType(v as FilterType)}
          >
            <SelectTrigger className="w-40">
              <Filter className="w-4 h-4 mr-2" />
              <SelectValue placeholder="Filter" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="buy">Buy</SelectItem>
              <SelectItem value="sell">Sell</SelectItem>
              <SelectItem value="dividend">Dividend</SelectItem>
              <SelectItem value="deposit">Deposit</SelectItem>
              <SelectItem value="withdrawal">Withdrawal</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Transactions List */}
        <div className="space-y-3">
          {filteredTransactions.map((transaction) => (
            <div
              key={transaction.id}
              className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                  {getTransactionIcon(transaction.type)}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className={cn('px-2 py-0.5 rounded text-xs font-medium', getTransactionBadge(transaction.type))}>
                      {transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)}
                    </span>
                    {transaction.symbol && (
                      <span className="font-medium">{transaction.symbol}</span>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(transaction.date)}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-medium">
                  {transaction.type === 'buy' || transaction.type === 'sell' ? formatCurrency(transaction.amount) : ''}
                  {transaction.type === 'dividend' && `+${formatCurrency(transaction.amount)}`}
                  {transaction.type === 'deposit' && `+${formatCurrency(transaction.amount)}`}
                  {transaction.type === 'withdrawal' && `-${formatCurrency(transaction.amount)}`}
                </p>
                {transaction.quantity && transaction.price && (
                  <p className="text-sm text-muted-foreground">
                    {transaction.quantity} @ {formatCurrency(transaction.price)}
                  </p>
                )}
                {transaction.fees > 0 && (
                  <p className="text-xs text-muted-foreground">Fees: {formatCurrency(transaction.fees)}</p>
                )}
              </div>
            </div>
          ))}
        </div>

        {filteredTransactions.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            {transactions.length === 0 ? 'No transactions yet' : 'No transactions match your filters'}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
