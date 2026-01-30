import type { PortfolioAnalytics, AnalyticsPeriod } from '@/lib/types/portfolio-analytics'

export interface ExportOptions {
  format: 'json' | 'csv'
  includeCharts?: boolean
  period?: AnalyticsPeriod
}

export function generateExportData(analytics: PortfolioAnalytics, options: ExportOptions) {
  const { format } = options

  const summary = analytics.summary || { name: 'Unknown Portfolio', total_value: analytics.total_value, total_invested: 0, total_pnl: 0, total_pnl_percent: 0 }
  const performance = analytics.performance || { cagr: 0, total_return: 0, total_return_percent: 0, annualized_return: 0, best_day: 0, worst_day: 0, win_rate: 0 }
  const risk = analytics.risk_metrics || { volatility: 0, beta: 1, sharpe_ratio: 0 }

  const data = {
    summary: {
      portfolio: summary.name,
      totalValue: summary.total_value,
      totalReturn: performance.total_return_percent,
      periodStart: analytics.period_start,
      periodEnd: analytics.period_end,
    },
    performance: {
      cagr: performance.cagr,
      totalReturn: performance.total_return_percent,
      annualizedReturn: performance.annualized_return,
      bestDay: performance.best_day,
      worstDay: performance.worst_day,
      winRate: performance.win_rate,
    },
    risk: {
      volatility: risk.volatility,
      beta: risk.beta,
      sharpeRatio: risk.sharpe_ratio,
    },
    allocation: analytics.performance_by_asset,
    exportedAt: new Date().toISOString(),
    period: options.period || '1y',
  }

  if (format === 'json') {
    return JSON.stringify(data, null, 2)
  }

  if (format === 'csv') {
    const lines: string[] = []

    lines.push('Summary')
    lines.push('Portfolio,Total Value,Total Return,Period Start,Period End')
    lines.push(
      `${data.summary.portfolio},${data.summary.totalValue},${data.summary.totalReturn}%,${data.summary.periodStart},${data.summary.periodEnd}`
    )

    lines.push('')
    lines.push('Performance')
    lines.push('CAGR,Total Return,Annualized Return,Win Rate')
    lines.push(
      `${data.performance.cagr}%,${data.performance.totalReturn}%,${data.performance.annualizedReturn}%,${data.performance.winRate}%`
    )

    lines.push('')
    lines.push('Risk Metrics')
    lines.push('Volatility,Beta,Sharpe Ratio')
    lines.push(
      `${data.risk.volatility}%,${data.risk.beta},${data.risk.sharpeRatio}`
    )

    lines.push('')
    lines.push('Allocation')
    lines.push('Asset Type,Value,Return')
    analytics.performance_by_asset.forEach((asset) => {
      lines.push(`${asset.asset_type},${asset.value},${asset.return}%`)
    })

    return lines.join('\n')
  }

  return null
}

export function downloadExport(data: string, filename: string, format: 'json' | 'csv') {
  const mimeType = format === 'json' ? 'application/json' : 'text/csv'
  const blob = new Blob([data], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function exportAnalytics(analytics: PortfolioAnalytics, options: ExportOptions) {
  const data = generateExportData(analytics, options)
  if (!data) return

  const timestamp = new Date().toISOString().split('T')[0]
  const filename = `portfolio-analytics-${options.period || '1y'}-${timestamp}.${options.format}`

  downloadExport(data, filename, options.format)
}
