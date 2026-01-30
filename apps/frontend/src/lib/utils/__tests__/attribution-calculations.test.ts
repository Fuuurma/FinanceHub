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
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const result = calculateHoldingAttribution(mockHoldings, totalValue)

      expect(result).toHaveLength(4)

      const aapl = result.find(h => h.symbol === 'AAPL')
      expect(aapl).toBeDefined()
      expect(aapl!.weight).toBeCloseTo(0.2376, 2)
      expect(aapl!.return).toBeCloseTo(19, 0)
      expect(aapl!.contribution).toBeCloseTo(4.51, 1)
      expect(aapl!.valueChange).toBe(2850)
    })

    it('should handle empty holdings', () => {
      const result = calculateHoldingAttribution([], 0)
      expect(result).toEqual([])
    })

    it('should calculate correct weight when totalValue is provided', () => {
      const totalValue = 56030
      const result = calculateHoldingAttribution(mockHoldings, totalValue)
      const weights = result.map(h => h.weight)
      const totalWeight = weights.reduce((sum, w) => sum + w, 0)

      expect(totalWeight).toBeCloseTo(1, 2)
    })
  })

  describe('calculateSectorAttribution', () => {
    it('should aggregate holdings by sector', () => {
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const result = calculateSectorAttribution(mockHoldings, totalValue)

      expect(result).toHaveLength(3) // Technology, Finance, Energy

      const tech = result.find(s => s.sector === 'Technology')
      expect(tech).toBeDefined()
      expect(tech!.weight).toBeCloseTo(0.655, 2)
      expect(tech!.return).toBeCloseTo(22.5, 0) // (19 + 26) / 2
      expect(tech!.contribution).toBeCloseTo(14.72, 1)
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
      const totalValue = 45000
      const result = calculateSectorAttribution(holdingsWithUndefinedSector, totalValue)

      expect(result).toHaveLength(1)
      const uncategorized = result.find(s => s.sector === 'Uncategorized')
      expect(uncategorized).toBeDefined()
    })

    it('should calculate negative contribution correctly', () => {
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const result = calculateSectorAttribution(mockHoldings, totalValue)

      const energy = result.find(s => s.sector === 'Energy')
      expect(energy).toBeDefined()
      expect(energy!.contribution).toBeLessThan(0)
    })
  })

  describe('calculateAssetClassAttribution', () => {
    it('should group holdings by asset class', () => {
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const result = calculateAssetClassAttribution(mockHoldings, totalValue)

      expect(result).toHaveLength(1) // All stocks
      expect(result[0].asset_class).toBe('stocks')
      expect(result[0].weight).toBeCloseTo(1, 2)
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
      const totalValue = mixedHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const result = calculateAssetClassAttribution(mixedHoldings, totalValue)

      expect(result).toHaveLength(2)
      expect(result.find(r => r.asset_class === 'stocks')).toBeDefined()
      expect(result.find(r => r.asset_class === 'crypto')).toBeDefined()
    })
  })

  describe('calculateAttributionSummary', () => {
    it('should return top and bottom contributors', () => {
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const holdings = calculateHoldingAttribution(mockHoldings, totalValue)
      const sectors = calculateSectorAttribution(mockHoldings, totalValue)
      const assetClasses = calculateAssetClassAttribution(mockHoldings, totalValue)

      const result = calculateAttributionSummary(holdings, sectors, assetClasses)

      expect(result.topContributors).toBeDefined()
      expect(result.worstPerformer).toBeDefined()
      expect(result.topContributors).toHaveLength(3)
      expect(result.bestSector).toBeDefined()
      expect(result.worstSector).toBeDefined()
    })

    it('should identify best and worst performers correctly', () => {
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const holdings = calculateHoldingAttribution(mockHoldings, totalValue)
      const sectors = calculateSectorAttribution(mockHoldings, totalValue)
      const assetClasses = calculateAssetClassAttribution(mockHoldings, totalValue)

      const result = calculateAttributionSummary(holdings, sectors, assetClasses)

      // Technology should be best sector (highest return)
      expect(result.bestSector?.sector).toBe('Technology')
      // Energy should be worst sector (negative return)
      expect(result.worstSector?.sector).toBe('Energy')
    })
  })

  describe('filterAttribution', () => {
    it('should filter by asset class', () => {
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const holdings = calculateHoldingAttribution(mockHoldings, totalValue)

      const result = filterAttribution(holdings, { assetClass: 'stocks' })
      expect(result).toHaveLength(4)
    })

    it('should filter by sector', () => {
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const holdings = calculateHoldingAttribution(mockHoldings, totalValue)

      const result = filterAttribution(holdings, { sector: 'Technology' })
      expect(result).toHaveLength(2)
      expect(result.every(h => h.sector === 'Technology')).toBe(true)
    })

    it('should filter by contribution range', () => {
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const holdings = calculateHoldingAttribution(mockHoldings, totalValue)

      const result = filterAttribution(holdings, { minContribution: 3 })
      expect(result.every(h => h.contribution >= 3)).toBe(true)
    })
  })

  describe('sortAttribution', () => {
    it('should sort by contribution descending', () => {
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const holdings = calculateHoldingAttribution(mockHoldings, totalValue)

      const result = sortAttribution(holdings, 'contribution', 'desc')
      const contributions = result.map(h => h.contribution)

      for (let i = 1; i < contributions.length; i++) {
        expect(contributions[i - 1]).toBeGreaterThanOrEqual(contributions[i])
      }
    })

    it('should sort by return ascending', () => {
      const totalValue = mockHoldings.reduce((sum, h) => sum + h.current_value, 0)
      const holdings = calculateHoldingAttribution(mockHoldings, totalValue)

      const result = sortAttribution(holdings, 'return', 'asc')
      const returns = result.map(h => h.return)

      for (let i = 1; i < returns.length; i++) {
        expect(returns[i - 1]).toBeLessThanOrEqual(returns[i])
      }
    })
  })

  describe('calculateBrinsonFachlerAttribution', () => {
    it('should calculate allocation and selection effects', () => {
      const result = calculateBrinsonFachlerAttribution(mockHoldings)

      expect(result).toHaveLength(4)
      result.forEach(item => {
        expect(item.allocationEffect).toBeDefined()
        expect(item.selectionEffect).toBeDefined()
        expect(item.interactionEffect).toBeDefined()
        expect(item.totalEffect).toBeCloseTo(
          item.allocationEffect + item.selectionEffect + item.interactionEffect,
          2
        )
      })
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
      expect(formatAttributionValue(0)).toBe('0.00%')
    })
  })
})
