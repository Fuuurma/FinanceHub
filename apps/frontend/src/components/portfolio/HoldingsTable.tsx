'use client'

import { DataTable, Column } from '@/components/ui/data-table'
import { ExportDropdown } from '@/components/ui/export-dropdown'
import type { PortfolioHolding } from '@/lib/types'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

interface HoldingsTableProps {
  holdings: PortfolioHolding[]
  loading: boolean
}

export default function HoldingsTable({ holdings, loading }: HoldingsTableProps) {
  const columns: Column<PortfolioHolding>[] = [
    {
      key: 'symbol',
      label: 'Symbol',
      sortable: true,
      searchable: true,
      render: (_, item) => <span className="font-medium">{item.symbol}</span>,
    },
    {
      key: 'name',
      label: 'Name',
      searchable: true,
      render: (_, item) => (
        <span className="text-muted-foreground max-w-[200px] truncate block">
          {item.name}
        </span>
      ),
    },
    {
      key: 'quantity',
      label: 'Quantity',
      sortable: true,
      render: (_, item) => item.quantity.toLocaleString(),
      className: 'text-right',
    },
    {
      key: 'current_value',
      label: 'Value',
      sortable: true,
      render: (_, item) => <span className="font-medium">{formatCurrency(item.current_value)}</span>,
      className: 'text-right',
    },
    {
      key: 'average_cost',
      label: 'Avg Cost',
      render: (_, item) => formatCurrency(item.average_cost),
      className: 'text-right text-muted-foreground',
    },
    {
      key: 'unrealized_pnl',
      label: 'P&L',
      sortable: true,
      render: (_, item) => (
        <span className={cn(item.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600')}>
          {formatCurrency(item.unrealized_pnl)}
        </span>
      ),
      className: 'text-right font-medium',
    },
    {
      key: 'unrealized_pnl_percent',
      label: 'Return',
      sortable: true,
      render: (_, item) => (
        <span className={cn(item.unrealized_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600')}>
          {formatPercent(item.unrealized_pnl_percent)}
        </span>
      ),
      className: 'text-right font-medium',
    },
    {
      key: 'day_change_percent',
      label: 'Day',
      sortable: true,
      render: (_, item) => (
        <span className={cn(item.day_change_percent >= 0 ? 'text-green-600' : 'text-red-600')}>
          {formatPercent(item.day_change_percent)}
        </span>
      ),
      className: 'text-right font-medium',
    },
    {
      key: 'weight',
      label: 'Weight',
      sortable: true,
      render: (_, item) => `${(item.weight * 100).toFixed(1)}%`,
      className: 'text-right text-muted-foreground',
    },
  ]

  const exportData = holdings.map((h) => ({
    Symbol: h.symbol,
    Name: h.name,
    Quantity: h.quantity,
    'Current Value': formatCurrency(h.current_value),
    'Average Cost': formatCurrency(h.average_cost),
    'Unrealized P&L': formatCurrency(h.unrealized_pnl),
    'Return %': formatPercent(h.unrealized_pnl_percent),
    'Day Change %': formatPercent(h.day_change_percent),
    'Weight %': `${(h.weight * 100).toFixed(1)}%`,
  }))

  return (
    <div className="space-y-4">
      <DataTable
        title={`Holdings (${holdings.length})`}
        data={holdings}
        columns={columns}
        loading={loading}
        searchable={true}
        searchKeys={['symbol', 'name']}
        searchPlaceholder="Search by symbol or name..."
        pageSize={10}
        showColumnToggle={true}
        emptyMessage={holdings.length === 0 ? 'No holdings in this portfolio' : 'No holdings match your search'}
      />
      {holdings.length > 0 && (
        <div className="flex justify-end">
          <ExportDropdown data={exportData} options={{ filename: 'holdings' }} />
        </div>
      )}
    </div>
  )
}
