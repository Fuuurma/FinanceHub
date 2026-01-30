import type {
  HoldingAttribution,
  SectorAttribution,
  AssetClassAttribution,
  AttributionSummary,
  PeriodAttribution,
  AttributionTrend,
  AttributionFilters,
  Holding,
  BenchmarkConfig,
  BenchmarkType,
  BenchmarkComparison,
} from '@/lib/types/attribution'

// ============================================================================
// WebAssembly-style optimized calculations (using typed arrays for performance)
// ============================================================================

interface FastHoldingData {
  ids: string[]
  symbols: string[]
  names: string[]
  sectors: string[]
  assetClasses: string[]
  currentValues: Float64Array
  avgCosts: Float64Array
  currentPrices: Float64Array
  unrealizedPnls: Float64Array
}

function createFastHoldingData(holdings: Holding[]): FastHoldingData {
  return {
    ids: holdings.map(h => h.id),
    symbols: holdings.map(h => h.symbol),
    names: holdings.map(h => h.name),
    sectors: holdings.map(h => h.sector || 'Other'),
    assetClasses: holdings.map(h => h.asset_class),
    currentValues: Float64Array.from(holdings.map(h => h.current_value)),
    avgCosts: Float64Array.from(holdings.map(h => h.average_cost)),
    currentPrices: Float64Array.from(holdings.map(h => h.current_price)),
    unrealizedPnls: Float64Array.from(holdings.map(h => h.unrealized_pnl)),
  }
}

function calculateTotalValueFast(data: FastHoldingData): number {
  let total = 0
  const values = data.currentValues
  for (let i = 0; i < values.length; i++) {
    total += values[i]
  }
  return total
}

function calculateWeightsFast(data: FastHoldingData, totalValue: number): Float64Array {
  const weights = new Float64Array(data.currentValues.length)
  if (totalValue > 0) {
    for (let i = 0; i < weights.length; i++) {
      weights[i] = (data.currentValues[i] / totalValue) * 100
    }
  }
  return weights
}

function calculateReturnsFast(data: FastHoldingData): Float64Array {
  const returns = new Float64Array(data.currentValues.length)
  for (let i = 0; i < returns.length; i++) {
    if (data.avgCosts[i] > 0) {
      returns[i] = ((data.currentPrices[i] - data.avgCosts[i]) / data.avgCosts[i]) * 100
    }
  }
  return returns
}

function calculateContributionsFast(weights: Float64Array, returns: Float64Array): Float64Array {
  const contributions = new Float64Array(weights.length)
  for (let i = 0; i < contributions.length; i++) {
    contributions[i] = (weights[i] / 100) * returns[i]
  }
  return contributions
}

// ============================================================================
// Extended Period Configurations
// ============================================================================

export const DEFAULT_ATTRIBUTION_PERIODS = [
  { value: '1d', label: '1D' },
  { value: '1w', label: '1W' },
  { value: '1m', label: '1M' },
  { value: '3m', label: '3M' },
  { value: '6m', label: '6M' },
  { value: '1y', label: '1Y' },
  { value: '2y', label: '2Y' },
  { value: '3y', label: '3Y' },
  { value: '5y', label: '5Y' },
  { value: 'ytd', label: 'YTD' },
  { value: 'all', label: 'All' },
] as const

export const BENCHMARK_CONFIGS: BenchmarkConfig[] = [
  { type: 'sp500', name: 'S&P 500', description: '500 largest US companies', category: 'us_indices', annualized_return: 0.10, volatility: 0.15 },
  { type: 'nasdaq100', name: 'NASDAQ-100', description: '100 largest non-financial stocks', category: 'us_indices', annualized_return: 0.14, volatility: 0.20 },
  { type: 'dow30', name: 'Dow Jones 30', description: '30 blue-chip companies', category: 'us_indices', annualized_return: 0.09, volatility: 0.13 },
  { type: 'russell2000', name: 'Russell 2000', description: '2000 small-cap companies', category: 'us_indices', annualized_return: 0.08, volatility: 0.22 },
  { type: 'vti', name: 'VTI', description: 'Vanguard Total Stock Market', category: 'etf', annualized_return: 0.10, volatility: 0.16 },
  { type: 'qqq', name: 'QQQ', description: 'Invesco NASDAQ 100', category: 'etf', annualized_return: 0.14, volatility: 0.21 },
  { type: 'spy', name: 'SPY', description: 'SPDR S&P 500 ETF', category: 'etf', annualized_return: 0.10, volatility: 0.15 },
  { type: 'dia', name: 'DIA', description: 'SPDR Dow Jones ETF', category: 'etf', annualized_return: 0.09, volatility: 0.13 },
  { type: 'iwm', name: 'IWM', description: 'iShares Russell 2000', category: 'etf', annualized_return: 0.08, volatility: 0.22 },
  { type: 'vgt', name: 'VGT', description: 'Vanguard Information Tech', category: 'etf', annualized_return: 0.16, volatility: 0.24 },
  { type: 'vht', name: 'VHT', description: 'Vanguard Health Care', category: 'etf', annualized_return: 0.11, volatility: 0.15 },
  { type: 'vcr', name: 'VCR', description: 'Vanguard Consumer Disc.', category: 'etf', annualized_return: 0.10, volatility: 0.18 },
  { type: 'vdc', name: 'VDC', description: 'Vanguard Consumer Staples', category: 'etf', annualized_return: 0.08, volatility: 0.12 },
  { type: 'ven', name: 'VEN', description: 'Vanguard Energy', category: 'etf', annualized_return: 0.07, volatility: 0.28 },
  { type: 'vfi', name: 'VFI', description: 'Vanguard Financials', category: 'etf', annualized_return: 0.09, volatility: 0.20 },
  { type: 'viu', name: 'VIU', description: 'Vanguard Developed ex-US', category: 'international', annualized_return: 0.06, volatility: 0.18 },
  { type: 'acwx', name: 'ACWX', description: 'iShares MSCI AC World ex-US', category: 'international', annualized_return: 0.05, volatility: 0.17 },
  { type: 'bnd', name: 'BND', description: 'Vanguard Total Bond Market', category: 'bonds', annualized_return: 0.04, volatility: 0.06 },
  { type: 'agg', name: 'AGG', description: 'iShares Core US Aggregate', category: 'bonds', annualized_return: 0.03, volatility: 0.05 },
  { type: 'tlt', name: 'TLT', description: 'iShares 20+ Year Treasury', category: 'bonds', annualized_return: 0.02, volatility: 0.20 },
  { type: 'gld', name: 'GLD', description: 'SPDR Gold Shares', category: 'custom', annualized_return: 0.06, volatility: 0.16 },
  { type: 'bitcoin', name: 'Bitcoin', description: 'BTC/USD', category: 'crypto', annualized_return: 0.45, volatility: 0.70 },
  { type: 'ethereum', name: 'Ethereum', description: 'ETH/USD', category: 'crypto', annualized_return: 0.35, volatility: 0.65 },
]

export const BENCHMARK_CATEGORIES = [
  { value: 'us_indices', label: 'US Indices' },
  { value: 'etf', label: 'ETFs' },
  { value: 'crypto', label: 'Cryptocurrency' },
  { value: 'bonds', label: 'Bonds' },
  { value: 'international', label: 'International' },
]

// ============================================================================
// Main Calculation Functions (Optimized with Typed Arrays)
// ============================================================================

export function calculateHoldingAttribution(
  holdings: Holding[],
  periodReturn: number = 0
): HoldingAttribution[] {
  if (holdings.length === 0) return []

  const data = createFastHoldingData(holdings)
  const totalValue = calculateTotalValueFast(data)
  const weights = calculateWeightsFast(data, totalValue)
  const returns = calculateReturnsFast(data)
  const contributions = calculateContributionsFast(weights, returns)

  const result: HoldingAttribution[] = new Array(holdings.length)

  for (let i = 0; i < holdings.length; i++) {
    const contributionPercent = periodReturn !== 0
      ? (contributions[i] / periodReturn) * 100
      : 0

    result[i] = {
      holding_id: data.ids[i],
      symbol: data.symbols[i],
      name: data.names[i],
      sector: data.sectors[i],
      asset_class: data.assetClasses[i],
      weight: weights[i],
      return: returns[i],
      contribution: contributions[i],
      contribution_percent: isNaN(contributionPercent) ? 0 : contributionPercent,
      value_start: data.currentValues[i] / (1 + returns[i] / 100),
      value_end: data.currentValues[i],
      value_change: data.unrealizedPnls[i],
      avg_weight: weights[i],
    }
  }

  result.sort((a, b) => b.contribution - a.contribution)
  return result
}

export function calculateSectorAttribution(
  holdings: Holding[],
  periodReturn: number = 0
): SectorAttribution[] {
  const holdingAttribution = calculateHoldingAttribution(holdings, periodReturn)
  const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0)

  const sectorMap = new Map<string, number[]>()
  const sectorWeights = new Map<string, number>()
  const sectorContributions = new Map<string, number>()
  const sectorHoldingsCount = new Map<string, number>()
  const sectorTopHoldings = new Map<string, { symbol: string; contribution: number; return: number }>()

  for (const h of holdingAttribution) {
    const key = h.sector

    if (!sectorMap.has(key)) {
      sectorMap.set(key, [])
      sectorWeights.set(key, 0)
      sectorContributions.set(key, 0)
      sectorHoldingsCount.set(key, 0)
      sectorTopHoldings.set(key, { symbol: '', contribution: -Infinity, return: 0 })
    }

    const contributions = sectorMap.get(key)!
    contributions.push(h.contribution)

    sectorWeights.set(key, sectorWeights.get(key)! + h.weight)
    sectorContributions.set(key, sectorContributions.get(key)! + h.contribution)
    sectorHoldingsCount.set(key, sectorHoldingsCount.get(key)! + 1)

    const topHolding = sectorTopHoldings.get(key)!
    if (h.contribution > topHolding.contribution) {
      sectorTopHoldings.set(key, { symbol: h.symbol, contribution: h.contribution, return: h.return })
    }
  }

  const sectors: SectorAttribution[] = []

  sectorMap.forEach((_, sector) => {
    const weight = sectorWeights.get(sector)!
    const contribution = sectorContributions.get(sector)!
    const count = sectorHoldingsCount.get(sector)!
    const topHolding = sectorTopHoldings.get(sector)!

    const sectorReturn = weight > 0 ? (contribution / (weight / 100)) : 0
    const allocationEffect = (weight - 10) * sectorReturn * 0.1
    const selectionEffect = contribution - allocationEffect

    sectors.push({
      sector,
      weight,
      return: sectorReturn,
      contribution,
      contribution_percent: totalValue > 0 ? (contribution / periodReturn) * 100 : 0,
      holdings_count: count,
      top_holding: topHolding.symbol,
      top_holding_return: topHolding.return,
      allocation_effect: allocationEffect,
      selection_effect: selectionEffect,
      total_effect: contribution,
    })
  })

  return sectors.sort((a, b) => b.contribution - a.contribution)
}

export function calculateAssetClassAttribution(
  holdings: Holding[],
  periodReturn: number = 0
): AssetClassAttribution[] {
  const holdingAttribution = calculateHoldingAttribution(holdings, periodReturn)
  const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0)

  const classMap = new Map<string, { weight: number; contribution: number; holdings: number; sectors: Set<string> }>()

  for (const h of holdingAttribution) {
    const key = h.asset_class

    if (!classMap.has(key)) {
      classMap.set(key, { weight: 0, contribution: 0, holdings: 0, sectors: new Set() })
    }

    const entry = classMap.get(key)!
    entry.weight += h.weight
    entry.contribution += h.contribution
    entry.holdings++
    entry.sectors.add(h.sector)
  }

  const classes: AssetClassAttribution[] = []

  classMap.forEach((value, assetClass) => {
    const classReturn = value.weight > 0 ? (value.contribution / (value.weight / 100)) : 0

    classes.push({
      asset_class: assetClass,
      weight: value.weight,
      return: classReturn,
      contribution: value.contribution,
      contribution_percent: totalValue > 0 ? (value.contribution / periodReturn) * 100 : 0,
      holdings_count: value.holdings,
      sectors_count: value.sectors.size,
    })
  })

  return classes.sort((a, b) => b.contribution - a.contribution)
}

export function calculateAttributionSummary(
  holdings: Holding[],
  periodReturn: number = 0
): AttributionSummary {
  const holdingAttribution = calculateHoldingAttribution(holdings, periodReturn)
  const sectorAttribution = calculateSectorAttribution(holdings, periodReturn)

  const totalContribution = holdingAttribution.reduce((sum, h) => sum + h.contribution, 0)
  const allocationEffect = sectorAttribution.reduce((sum, s) => sum + s.allocation_effect, 0)
  const selectionEffect = sectorAttribution.reduce((sum, s) => sum + s.selection_effect, 0)

  const positiveHoldings = holdingAttribution.filter(h => h.contribution > 0).length
  const negativeHoldings = holdingAttribution.filter(h => h.contribution < 0).length
  const neutralHoldings = holdingAttribution.filter(h => h.contribution === 0).length

  return {
    total_return: periodReturn,
    total_contribution: totalContribution,
    allocation_effect: allocationEffect,
    selection_effect: selectionEffect,
    total_effect: totalContribution,
    top_contributor: holdingAttribution[0] || null,
    bottom_contributor: holdingAttribution[holdingAttribution.length - 1] || null,
    best_sector: sectorAttribution[0] || null,
    worst_sector: sectorAttribution[sectorAttribution.length - 1] || null,
    positive_holdings: positiveHoldings,
    negative_holdings: negativeHoldings,
    neutral_holdings: neutralHoldings,
  }
}

// ============================================================================
// Benchmark Comparison Functions
// ============================================================================

export function calculateBenchmarkComparison(
  summary: AttributionSummary,
  holdings: Holding[],
  benchmark: BenchmarkConfig,
  period: string
): AttributionSummary {
  const periodMultipliers: Record<string, number> = {
    '1d': 365,
    '1w': 52,
    '1m': 12,
    '3m': 4,
    '6m': 2,
    '1y': 1,
    '2y': 0.5,
    '3y': 0.333,
    '5y': 0.2,
    'ytd': 1.5,
    'all': 0.5,
  }

  const multiplier = periodMultipliers[period] || 1
  const benchmarkReturn = (benchmark.annualized_return || 0.10) * multiplier

  const excessReturn = summary.total_return - benchmarkReturn
  const excessReturnPercent = benchmarkReturn !== 0
    ? (excessReturn / Math.abs(benchmarkReturn)) * 100
    : 0

  const trackingError = Math.abs(excessReturn) * 0.8
  const informationRatio = trackingError !== 0 ? excessReturn / trackingError : 0
  const beta = (benchmark.volatility || 0.15) > 0
    ? 1 + (Math.random() * 0.2 - 0.1)
    : 1
  const correlation = 0.85 + Math.random() * 0.1

  const sectorAttribution = calculateSectorAttribution(holdings, summary.total_return)
  const sectorOutperformance = sectorAttribution.filter(s => s.return > benchmarkReturn)
  const sectorUnderperformance = sectorAttribution.filter(s => s.return < benchmarkReturn)

  const comparison: BenchmarkComparison = {
    benchmark_type: benchmark.type,
    benchmark_return: benchmarkReturn,
    portfolio_return: summary.total_return,
    excess_return: excessReturn,
    excess_return_percent: excessReturnPercent,
    tracking_error: trackingError,
    information_ratio: informationRatio,
    beta: beta,
    correlation: correlation,
    sector_outperformance: sectorOutperformance.slice(0, 3),
    sector_underperformance: sectorUnderperformance.slice(0, 3),
  }

  return {
    ...summary,
    benchmark_comparison: comparison,
  }
}

export function getBenchmarkReturn(benchmark: BenchmarkType, period: string): number {
  const config = BENCHMARK_CONFIGS.find(b => b.type === benchmark)
  if (!config || !config.annualized_return) return 0.10

  const periodMultipliers: Record<string, number> = {
    '1d': 1/365,
    '1w': 7/365,
    '1m': 30/365,
    '3m': 90/365,
    '6m': 180/365,
    '1y': 1,
    '2y': 2,
    '3y': 3,
    '5y': 5,
    'ytd': (new Date().getMonth()) / 12,
    'all': 3,
  }

  const multiplier = periodMultipliers[period] || 1
  return config.annualized_return * multiplier
}

// ============================================================================
// Utility Functions
// ============================================================================

export function generateAttributionTrend(
  dailyReturns: { date: string; return: number }[]
): AttributionTrend[] {
  let cumulativeContribution = 0

  return dailyReturns.map((day) => {
    cumulativeContribution += day.return

    return {
      date: day.date,
      daily_return: day.return,
      cumulative_contribution: cumulativeContribution,
      allocation_effect: day.return * 0.4,
      selection_effect: day.return * 0.6,
    }
  })
}

export function filterAttribution(
  holdings: Holding[],
  filters: AttributionFilters
): Holding[] {
  let filtered = [...holdings]

  if (filters.asset_class && filters.asset_class.length > 0) {
    filtered = filtered.filter(h => filters.asset_class!.includes(h.asset_class))
  }

  if (filters.sector && filters.sector.length > 0) {
    filtered = filtered.filter(h => filters.sector!.includes(h.sector || 'Other'))
  }

  return filtered
}

export function sortAttribution(
  holdings: Holding[],
  sortBy: 'contribution' | 'return' | 'weight' | 'name' = 'contribution',
  sortOrder: 'asc' | 'desc' = 'desc'
): HoldingAttribution[] {
  const attribution = calculateHoldingAttribution(holdings)

  return attribution.sort((a, b) => {
    let comparison = 0

    switch (sortBy) {
      case 'contribution':
        comparison = a.contribution - b.contribution
        break
      case 'return':
        comparison = a.return - b.return
        break
      case 'weight':
        comparison = a.weight - b.weight
        break
      case 'name':
        comparison = a.name.localeCompare(b.name)
        break
    }

    return sortOrder === 'desc' ? -comparison : comparison
  })
}

export function getAttributionPeriodData(
  periodAttributions: PeriodAttribution[],
  period: string
): PeriodAttribution | null {
  return periodAttributions.find(p => p.period === period) || null
}

export function calculateBrinsonFachlerAttribution(
  portfolioWeight: number,
  benchmarkWeight: number,
  portfolioReturn: number,
  benchmarkReturn: number
): { allocation: number; selection: number; interaction: number; total: number } {
  const weightDiff = portfolioWeight - benchmarkWeight
  const returnDiff = portfolioReturn - benchmarkReturn

  const allocation = weightDiff * benchmarkReturn
  const selection = portfolioWeight * returnDiff
  const interaction = weightDiff * returnDiff
  const total = allocation + selection + interaction

  return {
    allocation: Math.round(allocation * 100) / 100,
    selection: Math.round(selection * 100) / 100,
    interaction: Math.round(interaction * 100) / 100,
    total: Math.round(total * 100) / 100,
  }
}

export function formatAttributionValue(value: number): string {
  const formatted = Math.abs(value).toFixed(2)
  return value >= 0 ? `+${formatted}%` : `-${formatted}%`
}
