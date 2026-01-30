'use client'

import { useState, useMemo, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  TrendingUp,
  TrendingDown,
  Download,
  Copy,
  FileJson,
  FileSpreadsheet,
  BarChart3,
  LineChart,
  Table,
  RefreshCw,
  Trophy,
  AlertCircle,
  CheckCircle,
  Target,
  Clock,
  Zap,
  Calendar,
  DollarSign,
  Percent,
  Activity,
  TrendingUpIcon,
} from 'lucide-react'
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts'
import { useEffect, useRef } from 'react'
import type { BacktestResult, StrategyComparisonResult, BacktestResultEnhanced, Trade, MonthlyReturn, RiskMetricsDetail } from '@/lib/types/analytics'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

interface BacktestResultsProps {
  result?: BacktestResultEnhanced | null
  comparison?: StrategyComparisonResult | null
  loading?: boolean
  className?: string
}

const MOCK_BACKTEST_RESULT: BacktestResultEnhanced = {
  success: true,
  data: {
    strategy_name: 'Equal Weight S&P 500',
    total_return: 0.156,
    annualized_return: 0.124,
    sharpe_ratio: 0.85,
    max_drawdown: -0.12,
    win_rate: 0.58,
    equity_curve: [100000, 102500, 101000, 104000, 103500, 106000, 108500, 107000, 110000, 112500, 115000, 113000, 116000],
    interpretation: 'Strategy showed positive returns with moderate volatility. Sharpe ratio indicates reasonable risk-adjusted performance.',
    trades: [
      { id: '1', symbol: 'AAPL', entry_date: '2023-01-15', exit_date: '2023-03-20', entry_price: 135.50, exit_price: 155.30, quantity: 100, pnl: 1980, pnl_percent: 14.61, side: 'long', status: 'closed' },
      { id: '2', symbol: 'MSFT', entry_date: '2023-02-01', exit_date: '2023-04-15', entry_price: 240.00, exit_price: 285.40, quantity: 50, pnl: 2270, pnl_percent: 18.92, side: 'long', status: 'closed' },
      { id: '3', symbol: 'GOOGL', entry_date: '2023-03-10', exit_date: '2023-05-20', entry_price: 95.20, exit_date: '2023-05-20', entry_price: 95.20, exit_price: 118.50, quantity: 120, pnl: 2796, pnl_percent: 24.47, side: 'long', status: 'closed' },
      { id: '4', symbol: 'NVDA', entry_date: '2023-04-01', exit_date: '2023-06-15', entry_price: 275.00, exit_price: 380.50, quantity: 40, pnl: 4220, pnl_percent: 38.36, side: 'long', status: 'closed' },
      { id: '5', symbol: 'TSLA', entry_date: '2023-05-15', exit_date: '2023-07-01', entry_price: 165.00, exit_price: 210.00, quantity: 60, pnl: 2700, pnl_percent: 27.27, side: 'long', status: 'closed' },
    ],
    monthly_returns: [
      { month: 'Jan', year: 2023, return: 0.025, benchmark_return: 0.018 },
      { month: 'Feb', year: 2023, return: -0.012, benchmark_return: -0.008 },
      { month: 'Mar', year: 2023, return: 0.038, benchmark_return: 0.032 },
      { month: 'Apr', year: 2023, return: 0.052, benchmark_return: 0.045 },
      { month: 'May', year: 2023, return: 0.018, benchmark_return: 0.015 },
      { month: 'Jun', year: 2023, return: -0.022, benchmark_return: -0.018 },
      { month: 'Jul', year: 2023, return: 0.041, benchmark_return: 0.035 },
      { month: 'Aug', year: 2023, return: -0.008, benchmark_return: -0.005 },
      { month: 'Sep', year: 2023, return: 0.029, benchmark_return: 0.022 },
      { month: 'Oct', year: 2023, return: -0.015, benchmark_return: -0.012 },
      { month: 'Nov', year: 2023, return: 0.062, benchmark_return: 0.055 },
      { month: 'Dec', year: 2023, return: 0.024, benchmark_return: 0.020 },
    ],
    risk_metrics: {
      volatility: 0.156,
      beta: 1.05,
      alpha: 0.028,
      sortino_ratio: 1.12,
      calmar_ratio: 1.03,
      var_95: -0.025,
      cvar_95: -0.038,
      recovery_time: 45,
    },
    benchmark_comparison: {
      benchmark_return: 0.125,
      alpha: 0.031,
      beta: 1.05,
      tracking_error: 0.045,
    },
    total_trades: 156,
    profitable_trades: 91,
    losing_trades: 65,
    avg_win: 2845,
    avg_loss: -1520,
    profit_factor: 1.87,
    consecutive_wins: 8,
    consecutive_losses: 4,
  },
  fetched_at: '2024-01-15T10:30:00Z',
}

const MOCK_COMPARISON: StrategyComparisonResult = {
  success: true,
  data: {
    results: {
      'Equal Weight': { total_return: 0.156, sharpe_ratio: 0.85, max_drawdown: -0.12, win_rate: 0.58 },
      'Momentum': { total_return: 0.198, sharpe_ratio: 0.92, max_drawdown: -0.15, win_rate: 0.62 },
      'Value': { total_return: 0.134, sharpe_ratio: 0.78, max_drawdown: -0.10, win_rate: 0.55 },
      'Quality': { total_return: 0.176, sharpe_ratio: 0.91, max_drawdown: -0.08, win_rate: 0.64 },
    },
    best_by_sharpe: 'Momentum',
    best_by_return: 'Momentum',
    best_by_drawdown: 'Quality',
  },
  fetched_at: '2024-01-15T10:30:00Z',
}

export function BacktestResults({
  result,
  comparison,
  loading = false,
  className,
}: BacktestResultsProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedMetric, setSelectedMetric] = useState<'return' | 'sharpe' | 'drawdown' | 'winrate'>('return')

  const displayResult = result || MOCK_BACKTEST_RESULT
  const displayComparison = comparison || MOCK_COMPARISON

  useEffect(() => {
    if (!chartContainerRef.current || !displayResult) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#6b7280',
      },
      grid: {
        vertLines: { color: '#e5e7eb' },
        horzLines: { color: '#e5e7eb' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 300,
      crosshair: {
        mode: CrosshairMode.Normal,
      },
    })

    const equityCurve = displayResult.data.equity_curve.map((value, index) => ({
      time: index as any,
      value,
    }))

    const chartAny = chart as any
    const lineSeries = chartAny.addLineSeries({
      color: '#3b82f6',
      lineWidth: 2,
    })
    lineSeries.setData(equityCurve)

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }

    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [displayResult])

  const handleCopy = useCallback(() => {
    const text = `Strategy: ${displayResult.data.strategy_name}
Total Return: ${formatPercent(displayResult.data.total_return)}
Annualized Return: ${formatPercent(displayResult.data.annualized_return)}
Sharpe Ratio: ${displayResult.data.sharpe_ratio.toFixed(2)}
Max Drawdown: ${formatPercent(displayResult.data.max_drawdown)}
Win Rate: ${formatPercent(displayResult.data.win_rate)}`
    navigator.clipboard.writeText(text)
  }, [displayResult])

  const exportToCSV = useCallback(() => {
    const headers = ['Metric', 'Value']
    const rows = [
      ['Strategy', displayResult.data.strategy_name],
      ['Total Return', formatPercent(displayResult.data.total_return)],
      ['Annualized Return', formatPercent(displayResult.data.annualized_return)],
      ['Sharpe Ratio', displayResult.data.sharpe_ratio.toFixed(2)],
      ['Max Drawdown', formatPercent(displayResult.data.max_drawdown)],
      ['Win Rate', formatPercent(displayResult.data.win_rate)],
    ]
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
    downloadFile(csv, 'backtest-results.csv', 'text/csv')
  }, [displayResult])

  const exportToJSON = useCallback(() => {
    downloadFile(JSON.stringify(displayResult, null, 2), 'backtest-results.json', 'application/json')
  }, [displayResult])

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const metrics = [
    {
      label: 'Total Return',
      value: formatPercent(displayResult.data.total_return),
      icon: TrendingUp,
      color: displayResult.data.total_return >= 0 ? 'text-green-600' : 'text-red-600',
      bg: displayResult.data.total_return >= 0 ? 'bg-green-100' : 'bg-red-100',
    },
    {
      label: 'Annualized Return',
      value: formatPercent(displayResult.data.annualized_return),
      icon: Zap,
      color: displayResult.data.annualized_return >= 0 ? 'text-green-600' : 'text-red-600',
      bg: displayResult.data.annualized_return >= 0 ? 'bg-green-100' : 'bg-red-100',
    },
    {
      label: 'Sharpe Ratio',
      value: displayResult.data.sharpe_ratio.toFixed(2),
      icon: Target,
      color: displayResult.data.sharpe_ratio >= 1 ? 'text-green-600' : displayResult.data.sharpe_ratio >= 0.5 ? 'text-yellow-600' : 'text-red-600',
      bg: displayResult.data.sharpe_ratio >= 1 ? 'bg-green-100' : displayResult.data.sharpe_ratio >= 0.5 ? 'bg-yellow-100' : 'bg-red-100',
    },
    {
      label: 'Max Drawdown',
      value: formatPercent(displayResult.data.max_drawdown),
      icon: TrendingDown,
      color: 'text-red-600',
      bg: 'bg-red-100',
    },
    {
      label: 'Win Rate',
      value: formatPercent(displayResult.data.win_rate),
      icon: Trophy,
      color: displayResult.data.win_rate >= 0.5 ? 'text-green-600' : 'text-red-600',
      bg: displayResult.data.win_rate >= 0.5 ? 'bg-green-100' : 'bg-red-100',
    },
  ]

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-48 w-full" />
            <div className="grid grid-cols-5 gap-4">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-24" />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Backtest Results
            </CardTitle>
            <CardDescription>
              {displayResult.data.strategy_name}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-1" />
                  Export
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={handleCopy}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy to Clipboard
                </DropdownMenuItem>
                <DropdownMenuItem onClick={exportToCSV}>
                  <FileSpreadsheet className="h-4 w-4 mr-2" />
                  Export as CSV
                </DropdownMenuItem>
                <DropdownMenuItem onClick={exportToJSON}>
                  <FileJson className="h-4 w-4 mr-2" />
                  Export as JSON
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="w-full grid grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="comparison">Strategy Comparison</TabsTrigger>
            <TabsTrigger value="details">Details</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4 mt-4">
            <div className="grid gap-4 md:grid-cols-5">
              {metrics.map((metric) => (
                <Card key={metric.label} className="bg-muted/30">
                  <CardContent className="pt-4">
                    <div className={cn('flex items-center justify-center w-10 h-10 rounded-full mb-2', metric.bg)}>
                      <metric.icon className={cn('h-5 w-5', metric.color)} />
                    </div>
                    <p className="text-2xl font-bold text-center">{metric.value}</p>
                    <p className="text-sm text-muted-foreground text-center">{metric.label}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Equity Curve</CardTitle>
              </CardHeader>
              <CardContent>
                <div ref={chartContainerRef} className="w-full h-[300px]" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Interpretation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{displayResult.data.interpretation}</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="comparison" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Trophy className="h-4 w-4" />
                  Strategy Comparison
                </CardTitle>
                <CardDescription>Compare performance across different strategies</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4 flex gap-2">
                  {(['return', 'sharpe', 'drawdown', 'winrate'] as const).map((metric) => (
                    <Button
                      key={metric}
                      variant={selectedMetric === metric ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSelectedMetric(metric)}
                    >
                      {metric === 'return' && 'Return'}
                      {metric === 'sharpe' && 'Sharpe'}
                      {metric === 'drawdown' && 'Drawdown'}
                      {metric === 'winrate' && 'Win Rate'}
                    </Button>
                  ))}
                </div>
                <div className="space-y-3">
                  {Object.entries(displayComparison.data.results).map(([strategy, stats]) => {
                    const isBest = (selectedMetric === 'return' && strategy === displayComparison.data.best_by_return) ||
                      (selectedMetric === 'sharpe' && strategy === displayComparison.data.best_by_sharpe) ||
                      (selectedMetric === 'drawdown' && strategy === displayComparison.data.best_by_drawdown) ||
                      (selectedMetric === 'winrate' && Object.entries(displayComparison.data.results)
                        .reduce((a, b) => a[1].win_rate > b[1].win_rate ? a : b)[0] === strategy)

                    const getValue = () => {
                      switch (selectedMetric) {
                        case 'return': return formatPercent(stats.total_return)
                        case 'sharpe': return stats.sharpe_ratio.toFixed(2)
                        case 'drawdown': return formatPercent(stats.max_drawdown)
                        case 'winrate': return formatPercent(stats.win_rate)
                      }
                    }

                    return (
                      <div
                        key={strategy}
                        className={cn(
                          'flex items-center justify-between p-3 border rounded-lg',
                          isBest && 'border-green-500 bg-green-50'
                        )}
                      >
                        <div className="flex items-center gap-2">
                          {isBest && <Trophy className="h-4 w-4 text-green-600" />}
                          <span className="font-medium">{strategy}</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-sm text-muted-foreground">
                            Sharpe: {stats.sharpe_ratio.toFixed(2)}
                          </span>
                          <span className={cn(
                            'font-bold',
                            selectedMetric === 'return' && stats.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                          )}>
                            {getValue()}
                          </span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="details" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Detailed Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-3">
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Strategy</span>
                      <span className="font-medium">{displayResult.data.strategy_name}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Total Return</span>
                      <span className={cn('font-medium', displayResult.data.total_return >= 0 ? 'text-green-600' : 'text-red-600')}>
                        {formatPercent(displayResult.data.total_return)}
                      </span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Annualized Return</span>
                      <span className="font-medium">{formatPercent(displayResult.data.annualized_return)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Sharpe Ratio</span>
                      <span className="font-medium">{displayResult.data.sharpe_ratio.toFixed(2)}</span>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Max Drawdown</span>
                      <span className="font-medium text-red-600">{formatPercent(displayResult.data.max_drawdown)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Win Rate</span>
                      <span className="font-medium">{formatPercent(displayResult.data.win_rate)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Data Points</span>
                      <span className="font-medium">{displayResult.data.equity_curve.length}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Last Updated</span>
                      <span className="font-medium">{new Date(displayResult.fetched_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default BacktestResults
