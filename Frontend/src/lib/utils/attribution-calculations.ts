import type {
  HoldingAttribution,
  SectorAttribution,
  AssetClassAttribution,
  AttributionSummary,
  PeriodAttribution,
  AttributionTrend,
  AttributionFilters,
  Holding,
} from '@/lib/types/attribution'

export function calculateHoldingAttribution(
  holdings: Holding[],
  periodReturn: number = 0
): HoldingAttribution[] {
  const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0)

  return holdings
    .map((holding) => {
      const weight = totalValue > 0 ? (holding.current_value / totalValue) * 100 : 0
      const return_pct = holding.average_cost > 0
        ? ((holding.current_price - holding.average_cost) / holding.average_cost) * 100
        : 0
      const contribution = (weight / 100) * return_pct
      const contribution_percent = totalValue > 0
        ? (contribution / periodReturn) * 100
        : 0

      return {
        holding_id: holding.id,
        symbol: holding.symbol,
        name: holding.name,
        sector: holding.sector || 'Other',
        asset_class: holding.asset_class,
        weight,
        return: return_pct,
        contribution,
        contribution_percent: isNaN(contribution_percent) ? 0 : contribution_percent,
        value_start: holding.current_value / (1 + return_pct / 100),
        value_end: holding.current_value,
        value_change: holding.unrealized_pnl,
        avg_weight: weight,
      }
    })
    .sort((a, b) => b.contribution - a.contribution)
}

export function calculateSectorAttribution(
  holdings: Holding[],
  periodReturn: number = 0
): SectorAttribution[] {
  const holdingAttribution = calculateHoldingAttribution(holdings, periodReturn)
  const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0)

  const sectorMap = new Map<string, HoldingAttribution[]>()

  holdingAttribution.forEach((h) => {
    const existing = sectorMap.get(h.sector) || []
    sectorMap.set(h.sector, [...existing, h])
  })

  const sectors: SectorAttribution[] = []

  sectorMap.forEach((sectorHoldings, sector) => {
    const sectorWeight = sectorHoldings.reduce((sum, h) => sum + h.weight, 0)
    const sectorReturn = sectorHoldings.length > 0
      ? sectorHoldings.reduce((sum, h) => sum + h.contribution, 0) / (sectorWeight / 100)
      : 0
    const contribution = sectorHoldings.reduce((sum, h) => sum + h.contribution, 0)
    const topHolding = sectorHoldings.sort((a, b) => b.contribution - a.contribution)[0]

    const allocationEffect = (sectorWeight - 10) * sectorReturn * 0.1
    const selectionEffect = contribution - allocationEffect

    sectors.push({
      sector,
      weight: sectorWeight,
      return: sectorReturn,
      contribution,
      contribution_percent: totalValue > 0 ? (contribution / periodReturn) * 100 : 0,
      holdings_count: sectorHoldings.length,
      top_holding: topHolding?.symbol || '',
      top_holding_return: topHolding?.return || 0,
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

  const classMap = new Map<string, HoldingAttribution[]>()

  holdingAttribution.forEach((h) => {
    const existing = classMap.get(h.asset_class) || []
    classMap.set(h.asset_class, [...existing, h])
  })

  const classes: AssetClassAttribution[] = []

  classMap.forEach((classHoldings, assetClass) => {
    const classWeight = classHoldings.reduce((sum, h) => sum + h.weight, 0)
    const classReturn = classHoldings.length > 0
      ? classHoldings.reduce((sum, h) => sum + h.contribution, 0) / (classWeight / 100)
      : 0
    const contribution = classHoldings.reduce((sum, h) => sum + h.contribution, 0)
    const sectors = new Set(classHoldings.map(h => h.sector)).size

    classes.push({
      asset_class: assetClass,
      weight: classWeight,
      return: classReturn,
      contribution,
      contribution_percent: totalValue > 0 ? (contribution / periodReturn) * 100 : 0,
      holdings_count: classHoldings.length,
      sectors_count: sectors,
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

  if (filters.min_contribution !== undefined) {
    const attribution = calculateHoldingAttribution(filtered)
    filtered = filtered.filter((h, i) => attribution[i].contribution >= filters.min_contribution!)
  }

  if (filters.max_contribution !== undefined) {
    const attribution = calculateHoldingAttribution(filtered)
    filtered = filtered.filter((h, i) => attribution[i].contribution <= filters.max_contribution!)
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
