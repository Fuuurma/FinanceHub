'use client'

import { useState, useMemo, useCallback } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  TrendingUp,
  TrendingDown,
  Clock,
  ChevronUp,
  ChevronDown,
  RefreshCw,
  Maximize2,
  ZoomIn,
  ZoomOut,
  ArrowLeft,
  X,
  Download,
  FileImage,
  FileText,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export type Timeframe = '1D' | '1W' | '1M' | '3M' | 'YTD' | '1Y' | 'ALL'

export interface MarketSector {
  id: string
  name: string
  change: number
  changePercent: number
  marketCap: number
  volume: number
  symbolCount: number
  children?: MarketSymbol[]
}

export interface MarketSymbol {
  id: string
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  marketCap: number
  volume: number
  sector: string
}

export interface MarketHeatmapData {
  sectors: MarketSector[]
  lastUpdated: string
}

interface MarketHeatmapProps {
  data?: MarketHeatmapData
  loading?: boolean
  timeframe?: Timeframe
  onTimeframeChange?: (timeframe: Timeframe) => void
  onRefresh?: () => void
  className?: string
}

const TIMEFRAMES: Timeframe[] = ['1D', '1W', '1M', '3M', 'YTD', '1Y', 'ALL']

function formatNumber(num: number): string {
  if (num >= 1e12) return `${(num / 1e12).toFixed(2)}T`
  if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`
  if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`
  if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`
  return num.toFixed(2)
}

function formatPercent(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

interface TreemapNodeProps {
  node: MarketSector | MarketSymbol
  level: number
  totalSize: number
  onNavigate: (node: MarketSector | MarketSymbol, level: number) => void
  currentLevel: number
}

function TreemapNode({ node, level, totalSize, onNavigate, currentLevel }: TreemapNodeProps) {
  const isPositive = node.change >= 0
  const intensity = Math.min(Math.abs(node.changePercent) / 5, 1)
  const baseColor = isPositive ? '22' : 'ef'
  const alpha = Math.round(40 + intensity * 60).toString(16)
  const bgColor = `#${baseColor}55${alpha}`

  const size = Math.max((node.marketCap / totalSize) * 100, 5)

  const isDrillable = 'children' in node && node.children && node.children.length > 0
  const isSector = 'children' in node

  const handleClick = () => {
    if (isDrillable) {
      onNavigate(node, level)
    }
  }

  const displaySymbol = 'symbol' in node ? node.symbol : node.name.substring(0, 4).toUpperCase()
  const displayName = 'symbol' in node ? node.name : node.name
  const displayChange = formatPercent(node.changePercent)

  return (
    <Tooltip delayDuration={200}>
      <TooltipTrigger asChild>
        <div
          className={cn(
            'relative flex flex-col items-start justify-between p-3 cursor-pointer transition-all duration-200 hover:z-10 hover:scale-[1.02]',
            isDrillable && 'cursor-pointer hover:ring-2 hover:ring-foreground',
            currentLevel > level && currentLevel === level + 1 && node.id === 'back'
          )}
          style={{
            backgroundColor: node.id === 'back' ? 'transparent' : bgColor,
            border: node.id === 'back' ? '2px dashed hsl(var(--foreground) / 0.3)' : '1px solid hsl(var(--foreground) / 0.1)',
            flexGrow: size,
            minHeight: node.id === 'back' ? '40px' : '60px',
          }}
          onClick={handleClick}
        >
          {node.id === 'back' ? (
            <div className="flex items-center gap-2 text-muted-foreground">
              <ArrowLeft className="h-4 w-4" />
              <span className="text-sm font-bold uppercase">Back</span>
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between w-full gap-1">
                <span className="font-black text-sm uppercase truncate max-w-[80%]">
                  {displaySymbol}
                </span>
                {isPositive ? (
                  <TrendingUp className="h-3 w-3 text-green-500 shrink-0" />
                ) : (
                  <TrendingDown className="h-3 w-3 text-red-500 shrink-0" />
                )}
              </div>
              <div className="flex items-center justify-between w-full gap-1">
                <span className={cn(
                  'text-xs font-mono font-bold',
                  isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                )}>
                  {displayChange}
                </span>
                <span className="text-[10px] text-muted-foreground font-mono truncate">
                  {formatNumber(node.marketCap)}
                </span>
              </div>
              {'children' in node && (
                <div className="absolute bottom-1 right-1">
                  <ChevronDown className="h-3 w-3 text-muted-foreground opacity-50" />
                </div>
              )}
            </>
          )}
        </div>
      </TooltipTrigger>
      <TooltipContent
        side="top"
        align="start"
        className="bg-background border-2 border-foreground p-4 shadow-[4px_4px_0px_0px_var(--foreground)] rounded-none max-w-xs"
      >
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-black uppercase">{displaySymbol}</span>
            <span className={cn(
              'font-mono font-bold px-2 py-0.5 text-xs',
              isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            )}>
              {displayChange}
            </span>
          </div>
          <p className="text-sm text-muted-foreground font-medium">{displayName}</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-muted-foreground">Market Cap:</span>
              <span className="font-mono font-bold ml-2">${formatNumber(node.marketCap)}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Volume:</span>
              <span className="font-mono font-bold ml-2">{formatNumber(node.volume)}</span>
            </div>
            {'children' in node && (
              <>
                <div>
                  <span className="text-muted-foreground">Symbols:</span>
                  <span className="font-mono font-bold ml-2">{node.symbolCount}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Change:</span>
                  <span className={cn(
                    'font-mono font-bold ml-2',
                    isPositive ? 'text-green-600' : 'text-red-600'
                  )}>
                    {isPositive ? '+' : ''}{node.change.toFixed(2)}
                  </span>
                </div>
              </>
            )}
          </div>
          {isDrillable && (
            <p className="text-[10px] text-muted-foreground uppercase font-bold">Click to drill down</p>
          )}
        </div>
      </TooltipContent>
    </Tooltip>
  )
}

function TreemapLayout({
  items,
  onNavigate,
  level,
  currentLevel,
}: {
  items: (MarketSector | MarketSymbol)[]
  onNavigate: (node: MarketSector | MarketSymbol, level: number) => void
  level: number
  currentLevel: number
}) {
  const totalSize = useMemo(() =>
    items.reduce((sum, item) => sum + item.marketCap, 0),
    [items]
  )

  const sectors = items.filter((item): item is MarketSector => 'children' in item)
  const symbols = items.filter((item): item is MarketSymbol => !('children' in item))

  if (currentLevel > level) {
    const backNode: MarketSector = {
      id: 'back',
      name: 'Back',
      change: 0,
      changePercent: 0,
      marketCap: 0,
      volume: 0,
      symbolCount: 0,
    }
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-1">
        <TreemapNode
          node={backNode}
          level={level}
          totalSize={totalSize}
          onNavigate={onNavigate}
          currentLevel={currentLevel}
        />
        {symbols.slice(0, 17).map((symbol) => (
          <TreemapNode
            key={symbol.id}
            node={symbol}
            level={level}
            totalSize={totalSize}
            onNavigate={onNavigate}
            currentLevel={currentLevel}
          />
        ))}
      </div>
    )
  }

  if (sectors.length > 0) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-1">
        {sectors.map((sector) => (
          <TreemapNode
            key={sector.id}
            node={sector}
            level={level}
            totalSize={totalSize}
            onNavigate={onNavigate}
            currentLevel={currentLevel}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-1">
      {symbols.slice(0, 24).map((symbol) => (
        <TreemapNode
          key={symbol.id}
          node={symbol}
          level={level}
          totalSize={totalSize}
          onNavigate={onNavigate}
          currentLevel={currentLevel}
        />
      ))}
    </div>
  )
}

export function MarketHeatmap({
  data,
  loading = false,
  timeframe = '1D',
  onTimeframeChange,
  onRefresh,
  className,
}: MarketHeatmapProps) {
  const [currentLevel, setCurrentLevel] = useState(0)
  const [selectedSector, setSelectedSector] = useState<MarketSector | null>(null)
  const [isExporting, setIsExporting] = useState(false)

  const handleNavigate = useCallback((node: MarketSector | MarketSymbol, level: number) => {
    if ('children' in node && node.children && node.children.length > 0) {
      setSelectedSector(node as MarketSector)
      setCurrentLevel(level + 1)
    }
  }, [])

  const handleBack = useCallback(() => {
    setCurrentLevel(0)
    setSelectedSector(null)
  }, [])

  const handleExportPNG = useCallback(async () => {
    setIsExporting(true)
    try {
      const element = document.querySelector('.border-2.border-foreground.overflow-hidden') as HTMLElement
      if (element && typeof window !== 'undefined') {
        const html2canvasModule = await import('html2canvas')
        const html2canvas = html2canvasModule.default
        const canvas = await html2canvas(element, {
          scale: 2,
          backgroundColor: null,
          logging: false,
        })
        
        const link = document.createElement('a')
        link.download = `market-heatmap-${timeframe}-${new Date().toISOString().slice(0, 10)}.png`
        link.href = canvas.toDataURL('image/png')
        link.click()
      }
    } catch (err) {
      console.error('Failed to export PNG:', err)
    } finally {
      setIsExporting(false)
    }
  }, [timeframe])

  const handleExportCSV = useCallback(() => {
    if (!data) return
    
    const flattenData = (items: (MarketSector | MarketSymbol)[], level = 0): Record<string, any>[] => {
      return items.flatMap(item => {
        const base: Record<string, any> = {
          name: item.name,
          change: item.change,
          changePercent: item.changePercent,
          marketCap: item.marketCap,
          volume: item.volume,
          type: 'children' in item ? 'sector' : 'symbol',
          level,
        }
        if ('children' in item && item.children) {
          return [base, ...flattenData(item.children, level + 1)]
        }
        return [base]
      })
    }
    
    const csv = [
      ['Name', 'Type', 'Change', 'Change %', 'Market Cap', 'Volume', 'Level'].join(','),
      ...flattenData(currentLevel === 0 ? data.sectors : (selectedSector?.children || [])).map(row =>
        [row.name, row.type, row.change, row.changePercent, row.marketCap, row.volume, row.level].join(',')
      )
    ].join('\n')
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.download = `market-heatmap-${timeframe}-${new Date().toISOString().slice(0, 10)}.csv`
    link.href = url
    link.click()
    URL.revokeObjectURL(url)
  }, [data, timeframe, currentLevel, selectedSector])

  const displayData = useMemo(() => {
    if (!data) return null
    if (currentLevel === 0) {
      return data.sectors
    }
    return selectedSector?.children || []
  }, [data, currentLevel, selectedSector])

  const allPositive = displayData?.every(item => item.change >= 0)
  const allNegative = displayData?.every(item => item.change < 0)

  if (loading) {
    return (
      <Card className={cn('border-2 border-foreground', className)}>
        <CardHeader className="border-b-2 border-foreground bg-muted/30">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-32" />
            </div>
            <div className="flex gap-2">
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-8 w-16" />
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-4">
          <div className="grid grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('border-2 border-foreground overflow-hidden', className)}>
      <CardHeader className="border-b-2 border-foreground bg-muted/30 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {currentLevel > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBack}
                className="h-8 px-2 border border-foreground/20 hover:bg-foreground hover:text-background"
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            )}
            <div>
              <CardTitle className="text-lg font-black uppercase italic flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Market_Heatmap
              </CardTitle>
              <p className="text-xs font-mono text-muted-foreground">
                {currentLevel > 0 ? selectedSector?.name : 'S&P 500 Sectors'}
              </p>
            </div>
          </div>

            <div className="flex items-center gap-2">
              <div className="flex items-center border border-foreground/20">
                {TIMEFRAMES.map((tf) => (
                  <Button
                    key={tf}
                    variant={timeframe === tf ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => onTimeframeChange?.(tf)}
                    className={cn(
                      'h-8 px-3 text-xs font-black uppercase rounded-none border-r border-foreground/20 last:border-r-0',
                      timeframe === tf && 'bg-foreground text-background'
                    )}
                  >
                    {tf}
                  </Button>
                ))}
              </div>

              <Button
                variant="ghost"
                size="icon"
                onClick={onRefresh}
                className="h-8 w-8 border border-foreground/20"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 border border-foreground/20"
                    disabled={isExporting}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={handleExportPNG} disabled={isExporting}>
                    <FileImage className="h-4 w-4 mr-2" />
                    Export as PNG
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleExportCSV} disabled={!data}>
                    <FileText className="h-4 w-4 mr-2" />
                    Export as CSV
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
        </div>
      </CardHeader>

      <CardContent className="p-4 bg-muted/5">
        <TooltipProvider>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="font-black uppercase text-muted-foreground">Legend:</span>
                  <div className="flex items-center gap-1">
                    <div className="w-4 h-4 bg-green-500/50 border border-foreground/20" />
                    <span className="font-mono uppercase">Gainers</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-4 h-4 bg-red-500/50 border border-foreground/20" />
                    <span className="font-mono uppercase">Losers</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] uppercase text-muted-foreground">
                  Size = Market Cap
                </span>
              </div>
            </div>

            {displayData && displayData.length > 0 ? (
              <TreemapLayout
                items={displayData}
                onNavigate={handleNavigate}
                level={0}
                currentLevel={currentLevel}
              />
            ) : (
              <div className="h-[400px] flex items-center justify-center bg-muted/30 border-2 border-dashed border-foreground/20">
                <div className="text-center">
                  <TrendingUp className="h-12 w-12 mx-auto text-muted-foreground/50 mb-2" />
                  <p className="font-black uppercase text-muted-foreground">No Data Available</p>
                  <p className="text-xs font-mono text-muted-foreground">Select a timeframe to view market data</p>
                </div>
              </div>
            )}
          </div>
        </TooltipProvider>
      </CardContent>
    </Card>
  )
}

export function MarketHeatmapSkeleton() {
  return (
    <Card className="border-2 border-foreground">
      <CardHeader className="border-b-2 border-foreground bg-muted/30">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-32" />
          </div>
          <div className="flex gap-2">
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-8 w-16" />
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
