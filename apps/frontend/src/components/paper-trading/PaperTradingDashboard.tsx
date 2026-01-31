'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { PaperTradeForm } from './PaperTradeForm'
import { PaperPortfolioSummary } from './PaperPortfolioSummary'
import { PaperTradeHistory } from './PaperTradeHistory'
import {
  TrendingUp, TrendingDown, RefreshCw, AlertTriangle, Info,
  DollarSign, Trophy, Target, Zap
} from 'lucide-react'

interface PaperTradingDashboardProps {
  className?: string
}

export function PaperTradingDashboard({ className }: PaperTradingDashboardProps) {
  const [resetting, setResetting] = React.useState(false)

  const handleReset = async () => {
    if (!confirm('Are you sure you want to reset your paper trading account? All trades will be deleted.')) {
      return
    }

    setResetting(true)
    try {
      const response = await fetch('/api/paper-trading/reset', { method: 'POST' })
      if (response.ok) {
        window.location.reload()
      }
    } catch (error) {
      console.error('Reset failed:', error)
    } finally {
      setResetting(false)
    }
  }

  return (
    <div className={cn('space-y-6', className)}>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black uppercase tracking-tight">
            Paper Trading
          </h1>
          <p className="text-muted-foreground font-mono text-sm mt-1">
            Practice trading with virtual money ($100,000 starting balance)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="font-mono text-sm border-2">
            <Zap className="h-3 w-3 mr-1" />
            Virtual Trading
          </Badge>
          <Button
            variant="outline"
            onClick={handleReset}
            disabled={resetting}
            className="rounded-none border-2 font-bold uppercase"
          >
            <RefreshCw className={cn('h-4 w-4 mr-2', resetting && 'animate-spin')} />
            Reset Account
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <PaperTradeForm />

          <Card className="rounded-none border-2 border-foreground">
            <CardHeader className="border-b-2 border-foreground">
              <CardTitle className="font-black uppercase flex items-center gap-2 text-sm">
                <Info className="h-4 w-4" />
                How It Works
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-3 text-sm">
              <div className="flex items-start gap-2">
                <div className="h-6 w-6 bg-green-100 flex items-center justify-center border border-green-500 rounded-none text-xs font-black text-green-600">
                  1
                </div>
                <p className="font-mono text-xs">
                  Enter a symbol (e.g., AAPL, GOOGL) and quantity
                </p>
              </div>
              <div className="flex items-start gap-2">
                <div className="h-6 w-6 bg-green-100 flex items-center justify-center border border-green-500 rounded-none text-xs font-black text-green-600">
                  2
                </div>
                <p className="font-mono text-xs">
                  Click BUY or SELL to execute your virtual trade
                </p>
              </div>
              <div className="flex items-start gap-2">
                <div className="h-6 w-6 bg-green-100 flex items-center justify-center border border-green-500 rounded-none text-xs font-black text-green-600">
                  3
                </div>
                <p className="font-mono text-xs">
                  Track your portfolio and performance over time
                </p>
              </div>
              <div className="flex items-start gap-2">
                <div className="h-6 w-6 bg-yellow-100 flex items-center justify-center border border-yellow-500 rounded-none text-xs font-black text-yellow-600">
                  !
                </div>
                <p className="font-mono text-xs text-yellow-700">
                  No real money involved - this is practice only
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="rounded-none border-2 border-yellow-500/50 bg-yellow-50">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-yellow-600 shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-black uppercase text-sm text-yellow-800 mb-1">
                    Risk Warning
                  </h3>
                  <p className="font-mono text-xs text-yellow-700">
                    Paper trading results do not guarantee real trading success.
                    Actual market conditions may differ significantly.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <PaperPortfolioSummary />
          <PaperTradeHistory />
        </div>
      </div>
    </div>
  )
}
