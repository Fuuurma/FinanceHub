import type { Holding, Transaction, AssetAllocationItem } from '@/lib/types/holdings'

export interface HoldingsExportData {
  holdings: Holding[]
  transactions: Transaction[]
  allocation: AssetAllocationItem[]
  exportedAt: string
  totalValue: number
  totalPnL: number
}

export function exportHoldingsToJSON(data: HoldingsExportData): string {
  return JSON.stringify(data, null, 2)
}

export function exportHoldingsToCSV(holdings: Holding[]): string {
  const lines: string[] = []

  lines.push('Symbol,Name,Asset Class,Quantity,Average Cost,Current Price,Current Value,Unrealized P&L,Unrealized P&L %,Day Change,Day Change %,Weight,Sector,Exchange')

  holdings.forEach((h) => {
    lines.push(
      `${h.symbol},"${h.name}",${h.asset_class},${h.quantity},${h.average_cost},${h.current_price},${h.current_value},${h.unrealized_pnl},${h.unrealized_pnl_percent},${h.day_change},${h.day_change_percent},${h.weight},"${h.sector || ''}","${h.exchange || ''}"`
    )
  })

  return lines.join('\n')
}

export function exportTransactionsToCSV(transactions: Transaction[]): string {
  const lines: string[] = []

  lines.push('Date,Type,Symbol,Quantity,Price,Total,Fees')

  transactions.forEach((t) => {
    lines.push(
      `${new Date(t.date).toLocaleDateString()},${t.type},${t.symbol},${t.quantity},${t.price},${t.total},${t.fees}`
    )
  })

  return lines.join('\n')
}

export function exportAllocationToCSV(allocation: AssetAllocationItem[]): string {
  const lines: string[] = []

  lines.push('Asset Class,Value,Percentage,Holdings Count')

  allocation.forEach((a) => {
    lines.push(`${a.asset_class},${a.value},${a.percentage},${a.holdings_count}`)
  })

  return lines.join('\n')
}

export function generateExportFilename(
  type: 'holdings' | 'transactions' | 'allocation' | 'full',
  format: 'json' | 'csv' = 'csv'
): string {
  const date = new Date().toISOString().split('T')[0]
  return `portfolio-${type}-${date}.${format}`
}

export function downloadExport(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function exportHoldings(
  holdings: Holding[],
  format: 'json' | 'csv' = 'csv'
): void {
  const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0)
  const totalPnL = holdings.reduce((sum, h) => sum + h.unrealized_pnl, 0)

  if (format === 'json') {
    const data: HoldingsExportData = {
      holdings,
      transactions: [],
      allocation: [],
      exportedAt: new Date().toISOString(),
      totalValue,
      totalPnL,
    }
    const content = exportHoldingsToJSON(data)
    const filename = generateExportFilename('holdings', 'json')
    downloadExport(content, filename, 'application/json')
  } else {
    const content = exportHoldingsToCSV(holdings)
    const filename = generateExportFilename('holdings', 'csv')
    downloadExport(content, filename, 'text/csv')
  }
}

export function exportTransactions(
  transactions: Transaction[],
  format: 'json' | 'csv' = 'csv'
): void {
  if (format === 'json') {
    const data = {
      transactions,
      exportedAt: new Date().toISOString(),
    }
    const content = JSON.stringify(data, null, 2)
    const filename = generateExportFilename('transactions', 'json')
    downloadExport(content, filename, 'application/json')
  } else {
    const content = exportTransactionsToCSV(transactions)
    const filename = generateExportFilename('transactions', 'csv')
    downloadExport(content, filename, 'text/csv')
  }
}

export function exportAllocation(
  allocation: AssetAllocationItem[],
  format: 'json' | 'csv' = 'csv'
): void {
  if (format === 'json') {
    const data = {
      allocation,
      exportedAt: new Date().toISOString(),
    }
    const content = JSON.stringify(data, null, 2)
    const filename = generateExportFilename('allocation', 'json')
    downloadExport(content, filename, 'application/json')
  } else {
    const content = exportAllocationToCSV(allocation)
    const filename = generateExportFilename('allocation', 'csv')
    downloadExport(content, filename, 'text/csv')
  }
}

export function exportFullPortfolio(
  holdings: Holding[],
  transactions: Transaction[],
  allocation: AssetAllocationItem[],
  format: 'json' | 'csv' = 'csv'
): void {
  if (format === 'json') {
    const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0)
    const totalPnL = holdings.reduce((sum, h) => sum + h.unrealized_pnl, 0)

    const data: HoldingsExportData = {
      holdings,
      transactions,
      allocation,
      exportedAt: new Date().toISOString(),
      totalValue,
      totalPnL,
    }
    const content = exportHoldingsToJSON(data)
    const filename = generateExportFilename('full', 'json')
    downloadExport(content, filename, 'application/json')
  } else {
    console.warn('Full portfolio export only supports JSON format')
  }
}
