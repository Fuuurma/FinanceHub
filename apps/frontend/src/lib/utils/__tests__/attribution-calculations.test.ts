import {
  calculateHoldingAttribution,
  calculateSectorAttribution,
  calculateAssetClassAttribution,
  calculateAttributionSummary,
  filterAttribution,
  sortAttribution,
  calculateBrinsonFachlerAttribution,
  formatAttributionValue,
} from '@/lib/utils/attribution-calculations'
import type { Holding, HoldingAttribution, SectorAttribution, AssetClassAttribution, AttributionSummary } from '@/lib/types/attribution'

describe('Attribution Calculations', () => {
  const mockHoldings: Holding[] = [
    {
      id: '1',
      symbol: 'AAPL',
      name: 'Apple Inc.',
      asset_class: 'stocks',
      quantity: 100,
      average_cost: 150,
      current_price: 178.50,
      current_value: 17850,
      unrealized_pnl: 2850,
      unrealized_pnl_percent: 19,
      sector: 'Technology',
    },
    {
      id: '2',
      symbol: 'MSFT',
      name: 'Microsoft Corp.',
      asset_class: 'stocks',
      quantity: 50,
      average_cost: 300,
      current_price: 378,
      current_value: 18900,
      unrealized_pnl: 3900,
      unrealized_pnl_percent: 26,
      sector: 'Technology',
    },
    {
      id: '3',
      symbol: 'JPM',
      name: 'JPMorgan Chase',
      asset_class: 'stocks',
      quantity: 80,
      average_cost: 140,
      current_price: 172,
      current_value: 13760,
      unrealized_pnl: 2560,
      unrealized_pnl_percent: 22.86,
      sector: 'Finance',
    },
    {
      id: '4',
      symbol: 'XOM',
      name: 'Exxon Mobil',
      asset_class: 'stocks',
      quantity: 60,
      average_cost: 100,
      current_price: 92,
      current_value: 5520,
      unrealized_pnl: -480,
      unrealized_pnl_percent: -8,
      sector: 'Energy',
    },
  ]

  describe('calculateHoldingAttribution', () => {
    it('should calculate holding attribution correctly', () => {
      const result = calculateHoldingAttribution(mockHoldings)

      expect(result).toHaveLength(4)

      const aapl = result.find(h => h.symbol === 'AAPL')
      expect(aapl).toBeDefined()
      expect(aapl!.weight).toBeCloseTo(31.85, 1)
      expect(aapl!.return).toBeCloseTo(19, 0)
      expect(aapl!.contribution).toBeCloseTo(6.05, 0)
      expect(aapl!.value_change).toBe(2850)
    })

    it('should handle empty holdings', () => {
      const result = calculateHoldingAttribution([])
      expect(result).toEqual([])
    })

    it('should calculate correct weights as percentages', () => {
      const result = calculateHoldingAttribution(mockHoldings)
      const weights = result.map(h => h.weight)
      const totalWeight = weights.reduce((sum, w) => sum + w, 0)

      expect(totalWeight).toBeCloseTo(100, 2)
    })
  })

  describe('calculateSectorAttribution', () => {
    it('should aggregate holdings by sector', () => {
      const result = calculateSectorAttribution(mockHoldings)

      expect(result).toHaveLength(3) // Technology, Finance, Energy

      const tech = result.find(s => s.sector === 'Technology')
      expect(tech).toBeDefined()
      expect(tech!.weight).toBeCloseTo(65.59, 2)
      expect(tech!.return).toBeGreaterThan(0)
      expect(tech!.contribution).toBeCloseTo(14.81, 1)
    })

    it('should handle holdings without sector', () => {
      const holdingsWithUndefinedSector: Holding[] = [
        {
          id: '1',
          symbol: 'BTC',
          asset_class: 'crypto',
          quantity: 1,
          average_cost: 30000,
          current_price: 45000,
          current_value: 45000,
          unrealized_pnl: 15000,
          unrealized_pnl_percent: 50,
        },
      ]
      const result = calculateSectorAttribution(holdingsWithUndefinedSector)

      expect(result).toHaveLength(1)
      const uncategorized = result.find(s => s.sector === 'Other')
      expect(uncategorized).toBeDefined()
    })

    it('should calculate negative contribution correctly', () => {
      const result = calculateSectorAttribution(mockHoldings)

      const energy = result.find(s => s.sector === 'Energy')
      expect(energy).toBeDefined()
      expect(energy!.contribution).toBeLessThan(0)
    })
  })

  describe('calculateAssetClassAttribution', () => {
    it('should group holdings by asset class', () => {
      const result = calculateAssetClassAttribution(mockHoldings)

      expect(result).toHaveLength(1) // All stocks
      expect(result[0].asset_class).toBe('stocks')
      expect(result[0].weight).toBeCloseTo(100, 2)
    })

    it('should handle multiple asset classes', () => {
      const mixedHoldings: Holding[] = [
        ...mockHoldings,
        {
          id: '5',
          symbol: 'BTC',
          asset_class: 'crypto',
          quantity: 0.5,
          average_cost: 40000,
          current_price: 60000,
          current_value: 30000,
          unrealized_pnl: 10000,
          unrealized_pnl_percent: 50,
        },
      ]
      const result = calculateAssetClassAttribution(mixedHoldings)

      expect(result).toHaveLength(2)
      expect(result.find(r => r.asset_class === 'stocks')).toBeDefined()
      expect(result.find(r => r.asset_class === 'crypto')).toBeDefined()
    })
  })

  describe('calculateAttributionSummary', () => {
    it('should return top and bottom contributors', () => {
      const result = calculateAttributionSummary(mockHoldings)

      expect(result.top_contributor).toBeDefined()
      expect(result.bottom_contributor).toBeDefined()
      expect(result.best_sector).toBeDefined()
      expect(result.worst_sector).toBeDefined()
      expect(result.positive_holdings).toBeGreaterThan(0)
    })

    it('should identify best and worst performers correctly', () => {
      const result = calculateAttributionSummary(mockHoldings)

      expect(result.best_sector?.sector).toBeDefined()
      expect(result.worst_sector?.sector).toBeDefined()
      expect(result.total_contribution).toBeGreaterThan(0)
    })
  })

  describe('filterAttribution', () => {
    it('should filter by asset class', () => {
      const result = filterAttribution(mockHoldings, { asset_class: ['stocks'] })
      expect(result).toHaveLength(4)
    })

    it('should filter by sector', () => {
      const result = filterAttribution(mockHoldings, { sector: ['Technology'] })
      expect(result).toHaveLength(2)
      expect(result.every(h => h.sector === 'Technology')).toBe(true)
    })
  })

  describe('sortAttribution', () => {
    it('should sort by contribution descending', () => {
      const result = sortAttribution(mockHoldings, 'contribution', 'desc')
      const contributions = result.map(h => h.contribution)

      for (let i = 1; i < contributions.length; i++) {
        expect(contributions[i - 1]).toBeGreaterThanOrEqual(contributions[i])
      }
    })

    it('should sort by return ascending', () => {
      const result = sortAttribution(mockHoldings, 'return', 'asc')
      const returns = result.map(h => h.return)

      for (let i = 1; i < returns.length; i++) {
        expect(returns[i - 1]).toBeLessThanOrEqual(returns[i])
      }
    })
  })

  describe('calculateBrinsonFachlerAttribution', () => {
    it('should calculate allocation and selection effects', () => {
      const portfolioWeight = 30
      const benchmarkWeight = 25
      const portfolioReturn = 15
      const benchmarkReturn = 10

      const result = calculateBrinsonFachlerAttribution(
        portfolioWeight,
        benchmarkWeight,
        portfolioReturn,
        benchmarkReturn
      )

      expect(result.allocation).toBeDefined()
      expect(result.selection).toBeDefined()
      expect(result.interaction).toBeDefined()
      expect(result.total).toBeCloseTo(
        result.allocation + result.selection + result.interaction,
        2
      )
    })
  })

  describe('formatAttributionValue', () => {
    it('should format positive values with + prefix', () => {
      expect(formatAttributionValue(5.5)).toBe('+5.50%')
    })

    it('should format negative values with - prefix', () => {
      expect(formatAttributionValue(-3.2)).toBe('-3.20%')
    })

    it('should format zero values', () => {
      expect(formatAttributionValue(0)).toBe('+0.00%')
    })
  })
})
