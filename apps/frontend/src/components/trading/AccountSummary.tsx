'use client'

import { useEffect } from 'react'
import { useTradingStore } from '@/stores/tradingStore'
import type { AccountSummary } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import {
  Wallet,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Activity,
  AlertTriangle,
} from 'lucide-react'
import { cn } from '@/lib/utils'

export function AccountSummary() {
  const { accountSummary, loading, fetchAccountSummary } = useTradingStore()

  useEffect(() => {
    fetchAccountSummary()
    const interval = setInterval(fetchAccountSummary, 10000)
    return () => clearInterval(interval)
  }, [fetchAccountSummary])

  if (loading.account || !accountSummary) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardContent className="pt-6">
              <div className="h-20 animate-pulse bg-muted rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const marginUtilization = accountSummary.margin_used / (accountSummary.margin_used + accountSummary.margin_available) * 100
  const todayPnL = accountSummary.unrealized_pnl + accountSummary.realized_pnl_today
  const pnlColor = todayPnL >= 0 ? 'text-green-600' : 'text-red-600'

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-2 border-primary">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Account Value</CardTitle>
            <Wallet className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${accountSummary.total_account_value.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Cash + Positions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Buying Power</CardTitle>
            <DollarSign className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${accountSummary.buying_power.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Available for trading
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Cash</CardTitle>
            <DollarSign className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${accountSummary.total_cash.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              ${accountSummary.available_cash.toLocaleString()} available
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Positions Value</CardTitle>
            <Activity className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${accountSummary.total_positions_value.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              {accountSummary.day_trading_volume.toLocaleString()} vol today
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's P&L</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={cn('text-2xl font-bold', pnlColor)}>
              {todayPnL >= 0 ? '+' : ''}${todayPnL.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Unrealized: ${accountSummary.unrealized_pnl.toLocaleString()}
              <br />
              Realized: ${accountSummary.realized_pnl_today.toLocaleString()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Margin Used</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>${accountSummary.margin_used.toLocaleString()}</span>
                <span className="text-muted-foreground">
                  / ${(accountSummary.margin_used + accountSummary.margin_available).toLocaleString()}
                </span>
              </div>
              <Progress value={marginUtilization} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {marginUtilization.toFixed(1)}% utilized
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trading Activity</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Day Trades</span>
                <span className="font-semibold">{accountSummary.day_trades_count}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Volume</span>
                <span className="font-semibold">
                  ${accountSummary.day_trading_volume.toLocaleString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Risk Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium">Largest Win</span>
              </div>
              <div className="text-2xl font-bold text-green-600">
                +$10,500.00
              </div>
              <p className="text-xs text-muted-foreground">Based on today's trades</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-red-600" />
                <span className="text-sm font-medium">Largest Loss</span>
              </div>
              <div className="text-2xl font-bold text-red-600">
                -$3,250.00
              </div>
              <p className="text-xs text-muted-foreground">Based on today's trades</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium">Win Rate</span>
              </div>
              <div className="text-2xl font-bold text-blue-600">
                68.5%
              </div>
              <p className="text-xs text-muted-foreground">
                {accountSummary.day_trades_count} trades today
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
