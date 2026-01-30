'use client'

import { useState, useEffect } from 'react'
import { ChevronDown, Building2, Briefcase, TrendingUp } from 'lucide-react'
import { portfoliosApi } from '@/lib/api/portfolio'
import type { Portfolio } from '@/lib/types/portfolio'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'

interface PortfolioSelectorProps {
  selectedPortfolioId: string | null
  onSelectPortfolio: (portfolioId: string | null) => void
}

export function PortfolioSelector({
  selectedPortfolioId,
  onSelectPortfolio,
}: PortfolioSelectorProps) {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPortfolios = async () => {
      try {
        setLoading(true)
        const data = await portfoliosApi.list()
        setPortfolios(data.portfolios)
        if (data.portfolios.length > 0 && !selectedPortfolioId) {
          const defaultPortfolio = data.portfolios.find(p => p.is_default) || data.portfolios[0]
          onSelectPortfolio(defaultPortfolio.id)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load portfolios')
      } finally {
        setLoading(false)
      }
    }

    fetchPortfolios()
  }, [onSelectPortfolio, selectedPortfolioId])

  const selectedPortfolio = portfolios.find(p => p.id === selectedPortfolioId)

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        <Skeleton className="h-10 w-48" />
      </div>
    )
  }

  if (error) {
    return (
      <Button variant="outline" disabled>
        <Building2 className="mr-2 h-4 w-4" />
        Error loading portfolios
      </Button>
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="min-w-[200px] justify-between">
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            <span>{selectedPortfolio?.name || 'Select Portfolio'}</span>
          </div>
          <ChevronDown className="ml-2 h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-72">
        <div className="px-2 py-1.5">
          <span className="text-xs font-medium text-muted-foreground">
            {portfolios.length} Portfolio{portfolios.length !== 1 ? 's' : ''}
          </span>
        </div>
        <DropdownMenuSeparator />
        {portfolios.map((portfolio) => (
          <DropdownMenuItem
            key={portfolio.id}
            onClick={() => onSelectPortfolio(portfolio.id)}
            className="flex flex-col items-start gap-1 p-3"
          >
            <div className="flex w-full items-center justify-between">
              <div className="flex items-center gap-2">
                {portfolio.is_default ? (
                  <Briefcase className="h-4 w-4 text-primary" />
                ) : (
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                )}
                <span className="font-medium">{portfolio.name}</span>
                {portfolio.is_default && (
                  <Badge variant="secondary" className="text-xs">
                    Default
                  </Badge>
                )}
              </div>
            </div>
            <div className="flex w-full items-center justify-between text-xs text-muted-foreground">
              <span>{formatCurrency(portfolio.total_value)}</span>
              <span className={portfolio.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                {portfolio.total_pnl >= 0 ? '+' : ''}
                {portfolio.total_pnl_percent.toFixed(2)}%
              </span>
            </div>
          </DropdownMenuItem>
        ))}
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={() => onSelectPortfolio(null)}
          className="flex items-center gap-2 text-muted-foreground"
        >
          <TrendingUp className="h-4 w-4" />
          <span>Aggregate View (All Portfolios)</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
