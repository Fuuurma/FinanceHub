'use client'

import { useEffect, useCallback, useMemo, useState } from 'react'
import { usePortfolioStore } from '@/stores/portfolioStore'
import type { Portfolio } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  ChevronDown,
  Briefcase,
  ArrowUpRight,
  ArrowDownRight,
  Keyboard,
  Star,
} from 'lucide-react'
import { cn, formatCurrency, formatPercent } from '@/lib/utils'

interface PortfolioSwitcherProps {
  onPortfolioChange?: (portfolio: Portfolio) => void
}

export function PortfolioSwitcher({ onPortfolioChange }: PortfolioSwitcherProps) {
  const {
    portfolios,
    selectedPortfolioId,
    selectPortfolio,
  } = usePortfolioStore()

  const [recentlySwitched, setRecentlySwitched] = useState<string | null>(null)

  const selectedPortfolio = useMemo(
    () => portfolios.find((p) => p.id === selectedPortfolioId),
    [portfolios, selectedPortfolioId]
  )

  const handleSelectPortfolio = useCallback(
    async (portfolioId: string) => {
      const portfolio = portfolios.find((p) => p.id === portfolioId)
      if (portfolio) {
        await selectPortfolio(portfolioId)
        setRecentlySwitched(portfolioId)
        setTimeout(() => setRecentlySwitched(null), 2000)
        onPortfolioChange?.(portfolio)
      }
    },
    [portfolios, selectPortfolio, onPortfolioChange]
  )

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        const num = parseInt(e.key)
        if (!isNaN(num) && num >= 1 && num <= 9) {
          const index = num - 1
          if (portfolios[index]) {
            e.preventDefault()
            handleSelectPortfolio(portfolios[index].id)
          }
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [portfolios, handleSelectPortfolio])

  const formatTotalPnl = (pnl: number, percent: number) => {
    const isPositive = pnl >= 0
    return {
      value: formatCurrency(Math.abs(pnl)),
      percent: formatPercent(Math.abs(percent)),
      isPositive,
    }
  }

  if (portfolios.length === 0) {
    return null
  }

  if (portfolios.length === 1 && selectedPortfolio) {
    return (
      <div className="flex items-center gap-3 p-3 rounded-lg border bg-card">
        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10">
          <Briefcase className="w-5 h-5 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-semibold truncate">{selectedPortfolio.name}</span>
            {selectedPortfolio.is_default && (
              <Badge variant="secondary" className="text-xs">
                <Star className="w-3 h-3 mr-1" />
                Default
              </Badge>
            )}
          </div>
          <div className="text-sm text-muted-foreground">
            {formatCurrency(selectedPortfolio.total_value)}
          </div>
        </div>
        <Keyboard className="w-4 h-4 text-muted-foreground" />
        <kbd className="text-xs text-muted-foreground">Ctrl+1</kbd>
      </div>
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            'w-full justify-between gap-2 h-auto py-3 px-4',
            recentlySwitched && 'ring-2 ring-primary/50'
          )}
        >
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10">
              <Briefcase className="w-4 h-4 text-primary" />
            </div>
            <div className="text-left">
              <div className="font-semibold">{selectedPortfolio?.name || 'Select Portfolio'}</div>
              <div className="text-xs text-muted-foreground">
                {selectedPortfolio && formatCurrency(selectedPortfolio.total_value)}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs hidden sm:inline-flex">
              {portfolios.length} {portfolios.length === 1 ? 'portfolio' : 'portfolios'}
            </Badge>
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          </div>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-80">
        <div className="p-3 border-b">
          <h4 className="font-semibold text-sm">Switch Portfolio</h4>
          <p className="text-xs text-muted-foreground mt-1">
            Press <kbd className="kbd">Ctrl</kbd>+<kbd className="kbd">1-9</kbd> to switch quickly
          </p>
        </div>
        <div className="max-h-80 overflow-y-auto">
          {portfolios.map((portfolio, index) => {
            const pnl = formatTotalPnl(portfolio.total_pnl, portfolio.total_pnl_percent)
            const isSelected = portfolio.id === selectedPortfolioId
            const isDefault = portfolio.is_default

            return (
              <DropdownMenuItem
                key={portfolio.id}
                onClick={() => handleSelectPortfolio(portfolio.id)}
                className={cn(
                  'flex items-start gap-3 p-3 cursor-pointer',
                  isSelected && 'bg-accent'
                )}
              >
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-primary">{index + 1}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium truncate">{portfolio.name}</span>
                    {isDefault && (
                      <Badge variant="outline" className="text-xs px-1 py-0">
                        <Star className="w-3 h-3 mr-1" />
                        Default
                      </Badge>
                    )}
                    {isSelected && (
                      <Badge variant="default" className="text-xs px-1 py-0">
                        Selected
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-sm text-muted-foreground">
                      {formatCurrency(portfolio.total_value)}
                    </span>
                    <span className="text-xs text-muted-foreground">•</span>
                    <span className="text-xs text-muted-foreground">
                      {portfolio.holdings_count} holdings
                    </span>
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    {pnl.isPositive ? (
                      <ArrowUpRight className="w-3 h-3 text-green-500" />
                    ) : (
                      <ArrowDownRight className="w-3 h-3 text-red-500" />
                    )}
                    <span
                      className={cn(
                        'text-xs font-medium',
                        pnl.isPositive ? 'text-green-500' : 'text-red-500'
                      )}
                    >
                      {pnl.value} ({pnl.percent})
                    </span>
                    <span className="text-xs text-muted-foreground">all time</span>
                  </div>
                </div>
              </DropdownMenuItem>
            )
          })}
        </div>
        <DropdownMenuSeparator />
        <div className="p-3 bg-muted/50">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Keyboard shortcuts:</span>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((num) => (
                <kbd key={num} className="kbd">
                  {num}
                </kbd>
              ))}
              {portfolios.length > 5 && (
                <span className="ml-1">+</span>
              )}
            </div>
          </div>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
