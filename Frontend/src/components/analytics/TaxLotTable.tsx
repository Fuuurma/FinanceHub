"use client"

import * as React from "react"
import { ChevronDownIcon, ChevronUpIcon } from "lucide-react"

import { cn, formatCurrency, formatPercent, formatDate } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export type TaxLotStatus = "held" | "partial" | "realized" | "harvested"

export interface TaxLot {
  id: string
  symbol: string
  purchaseDate: string
  shares: number
  costBasis: number
  costPerShare?: number
  currentValue: number
  currentPrice?: number
  status: TaxLotStatus
  term?: 'short' | 'long'
  unrealizedGain?: number
  unrealizedGainPercent?: number
  washSale?: boolean
  realizedGain?: number
  realizedDate?: string
}

export interface TaxLotSummary {
  totalLots: number
  totalShares: number
  totalCostBasis: number
  totalCurrentValue: number
  unrealizedGain: number
  unrealizedGainPercent: number
  shortTermLots: number
  longTermLots: number
  heldLots: number
  partialLots: number
  realizedLots: number
  harvestedLots: number
}

export interface TaxLotTableProps {
  lots?: TaxLot[]
  summary?: TaxLotSummary
  isLoading?: boolean
  onLotClick?: (lot: TaxLot) => void
}

const STATUS_CONFIG = {
  held: { label: "Held", variant: "default" as const },
  partial: { label: "Partial", variant: "secondary" as const },
  realized: { label: "Realized", variant: "outline" as const },
  harvested: { label: "Harvested", variant: "destructive" as const },
}

const HOLDING_PERIOD_THRESHOLD_DAYS = 365

function calculateHoldingPeriod(purchaseDate: string): { isLongTerm: boolean; days: number } {
  const purchase = new Date(purchaseDate)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - purchase.getTime())
  const days = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return { isLongTerm: days > HOLDING_PERIOD_THRESHOLD_DAYS, days }
}

function calculateGainLoss(costBasis: number, currentValue: number): { amount: number; percent: number } {
  const amount = currentValue - costBasis
  const percent = costBasis > 0 ? (amount / costBasis) * 100 : 0
  return { amount, percent }
}

export function generateMockTaxLots(): TaxLot[] {
  const symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "V", "JNJ"]
  const statuses: TaxLotStatus[] = ["held", "partial", "realized", "harvested"]
  const lots: TaxLot[] = []

  for (let i = 0; i < 20; i++) {
    const symbol = symbols[Math.floor(Math.random() * symbols.length)]
    const shares = Math.floor(Math.random() * 100) + 10
    const purchaseDate = new Date(Date.now() - Math.random() * 730 * 24 * 60 * 60 * 1000)
    const costPerShare = Math.random() * 200 + 50
    const currentValuePerShare = costPerShare * (1 + (Math.random() - 0.4) * 0.5)
    const costBasis = shares * costPerShare
    const currentValue = shares * currentValuePerShare
    const status = statuses[Math.floor(Math.random() * statuses.length)]

    const realizedGain = status === "realized" || status === "harvested"
      ? (Math.random() - 0.3) * costBasis
      : undefined

    const realizedDate = status === "realized" || status === "harvested"
      ? new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString()
      : undefined

    lots.push({
      id: `lot-${i + 1}`,
      symbol,
      purchaseDate: purchaseDate.toISOString(),
      shares,
      costBasis,
      currentValue,
      status,
      realizedGain,
      realizedDate,
    })
  }

  return lots
}

export function generateMockSummary(taxLots: TaxLot[]): TaxLotSummary {
  const totalCostBasis = taxLots.reduce((sum, lot) => sum + lot.costBasis, 0)
  const totalCurrentValue = taxLots.reduce((sum, lot) => sum + lot.currentValue, 0)
  const unrealizedGain = totalCurrentValue - totalCostBasis
  const unrealizedGainPercent = totalCostBasis > 0 ? (unrealizedGain / totalCostBasis) * 100 : 0

  return {
    totalLots: taxLots.length,
    totalShares: taxLots.reduce((sum, lot) => sum + lot.shares, 0),
    totalCostBasis,
    totalCurrentValue,
    unrealizedGain,
    unrealizedGainPercent,
    shortTermLots: taxLots.filter(
      lot => !calculateHoldingPeriod(lot.purchaseDate).isLongTerm
    ).length,
    longTermLots: taxLots.filter(
      lot => calculateHoldingPeriod(lot.purchaseDate).isLongTerm
    ).length,
    heldLots: taxLots.filter(lot => lot.status === "held").length,
    partialLots: taxLots.filter(lot => lot.status === "partial").length,
    realizedLots: taxLots.filter(lot => lot.status === "realized").length,
    harvestedLots: taxLots.filter(lot => lot.status === "harvested").length,
  }
}
function TaxLotRow({
  lot,
  onClick,
}: {
  lot: TaxLot
  onClick?: (lot: TaxLot) => void
}) {
  const { amount, percent } = calculateGainLoss(lot.costBasis, lot.currentValue)
  const { isLongTerm } = calculateHoldingPeriod(lot.purchaseDate)
  const statusConfig = STATUS_CONFIG[lot.status]

  return (
    <tr
      className={cn(
        "border-b transition-colors hover:bg-muted/50 cursor-pointer",
        onClick && "cursor-pointer"
      )}
      onClick={() => onClick?.(lot)}
    >
      <td className="p-4 font-medium">{lot.symbol}</td>
      <td className="p-4">{formatDate(lot.purchaseDate)}</td>
      <td className="p-4 text-right">{lot.shares.toLocaleString()}</td>
      <td className="p-4 text-right">{formatCurrency(lot.costBasis)}</td>
      <td className="p-4 text-right">{formatCurrency(lot.currentValue)}</td>
      <td
        className={cn(
          "p-4 text-right font-medium",
          amount >= 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
        )}
      >
        <div>{formatCurrency(amount)}</div>
        <div className="text-xs">{formatPercent(percent)}</div>
      </td>
      <td className="p-4">
        <Badge variant={statusConfig.variant}>{statusConfig.label}</Badge>
      </td>
      <td className="p-4">
        <Badge variant={isLongTerm ? "secondary" : "outline"}>
          {isLongTerm ? "Long" : "Short"}
        </Badge>
      </td>
    </tr>
  )
}

function TaxLotTableSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-10 w-40" />
      </div>
      <div className="rounded-md border">
        <div className="border-b bg-muted/50 p-4">
          <div className="grid grid-cols-8 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-4 w-20" />
            ))}
          </div>
        </div>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="border-b p-4">
            <div className="grid grid-cols-8 gap-4">
              {Array.from({ length: 8 }).map((_, j) => (
                <Skeleton key={j} className="h-4 w-full" />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
function SummaryView({ summary }: { summary: TaxLotSummary }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Total Lots</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{summary.totalLots}</div>
          <p className="text-xs text-muted-foreground">
            {summary.heldLots} held, {summary.partialLots} partial, {summary.realizedLots} realized, {summary.harvestedLots} harvested
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Total Value</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(summary.totalCurrentValue)}</div>
          <p className="text-xs text-muted-foreground">
            Cost basis: {formatCurrency(summary.totalCostBasis)}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Unrealized Gain/Loss</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className={cn(
              "text-2xl font-bold",
              summary.unrealizedGain >= 0
                ? "text-green-600 dark:text-green-400"
                : "text-red-600 dark:text-red-400"
            )}
          >
            {formatCurrency(summary.unrealizedGain)}
          </div>
          <p className="text-xs text-muted-foreground">
            {formatPercent(summary.unrealizedGainPercent)}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Holding Period</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {summary.longTermLots}/{summary.shortTermLots}
          </div>
          <p className="text-xs text-muted-foreground">
            Long-term / Short-term lots
          </p>
        </CardContent>
      </Card>

      <Card className="md:col-span-2 lg:col-span-4">
        <CardHeader>
          <CardTitle>Tax Lot Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="flex flex-col items-center justify-center p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">Held</span>
              <span className="text-xl font-bold">{summary.heldLots}</span>
            </div>
            <div className="flex flex-col items-center justify-center p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">Partial</span>
              <span className="text-xl font-bold">{summary.partialLots}</span>
            </div>
            <div className="flex flex-col items-center justify-center p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">Realized</span>
              <span className="text-xl font-bold">{summary.realizedLots}</span>
            </div>
            <div className="flex flex-col items-center justify-center p-4 rounded-lg bg-muted/50">
              <span className="text-sm text-muted-foreground">Harvested</span>
              <span className="text-xl font-bold">{summary.harvestedLots}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

type SortField = "date" | "gain" | "value"
type SortDirection = "asc" | "desc"

export function TaxLotTable({
  lots = generateMockTaxLots(),
  summary = generateMockSummary(lots),
  isLoading = false,
  onLotClick,
}: TaxLotTableProps) {
  const [sortField, setSortField] = React.useState<SortField>("date")
  const [sortDirection, setSortDirection] = React.useState<SortDirection>("desc")
  const [statusFilter, setStatusFilter] = React.useState<TaxLotStatus | "all">("all")

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDirection("desc")
    }
  }

  const filteredLots = React.useMemo(() => {
    let result = [...lots]

    if (statusFilter !== "all") {
      result = result.filter(lot => lot.status === statusFilter)
    }

    result.sort((a, b) => {
      let comparison = 0

      switch (sortField) {
        case "date":
          comparison = new Date(a.purchaseDate).getTime() - new Date(b.purchaseDate).getTime()
          break
        case "gain": {
          const aGain = calculateGainLoss(a.costBasis, a.currentValue)
          const bGain = calculateGainLoss(b.costBasis, b.currentValue)
          comparison = aGain.percent - bGain.percent
          break
        }
        case "value":
          comparison = a.currentValue - b.currentValue
          break
      }

      return sortDirection === "asc" ? comparison : -comparison
    })

    return result
  }, [lots, sortField, sortDirection, statusFilter])

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null
    return sortDirection === "asc" ? (
      <ChevronUpIcon className="ml-1 h-4 w-4" />
    ) : (
      <ChevronDownIcon className="ml-1 h-4 w-4" />
    )
  }

  if (isLoading) {
    return <TaxLotTableSkeleton />
  }

  return (
    <div className="space-y-4">
      <Tabs defaultValue="lots" className="w-full">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <TabsList>
            <TabsTrigger value="lots">Lots View</TabsTrigger>
            <TabsTrigger value="summary">Summary</TabsTrigger>
          </TabsList>

          <div className="flex items-center gap-2">
            <Select
              value={statusFilter}
              onValueChange={(value) => setStatusFilter(value as TaxLotStatus | "all")}
            >
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="held">Held</SelectItem>
                <SelectItem value="partial">Partial</SelectItem>
                <SelectItem value="realized">Realized</SelectItem>
                <SelectItem value="harvested">Harvested</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <TabsContent value="lots" className="mt-4">
          <div className="rounded-md border">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-4 text-left font-medium">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleSort("date")}
                        className="flex items-center"
                      >
                        Date
                        <SortIcon field="date" />
                      </Button>
                    </th>
                    <th className="p-4 text-left font-medium">Symbol</th>
                    <th className="p-4 text-right font-medium">Shares</th>
                    <th className="p-4 text-right font-medium">Cost Basis</th>
                    <th className="p-4 text-right font-medium">Current Value</th>
                    <th className="p-4 text-right font-medium">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleSort("gain")}
                        className="flex items-center justify-end"
                      >
                        Gain/Loss
                        <SortIcon field="gain" />
                      </Button>
                    </th>
                    <th className="p-4 text-left font-medium">Status</th>
                    <th className="p-4 text-left font-medium">Holding</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLots.map((lot) => (
                    <TaxLotRow key={lot.id} lot={lot} onClick={onLotClick} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="summary" className="mt-4">
          <SummaryView summary={summary} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
