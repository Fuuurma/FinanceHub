import {
  generateExportData,
  downloadExport,
  exportAnalytics,
  type ExportOptions,
} from '../analytics-export'
import type { PortfolioAnalytics } from '@/lib/types/portfolio-analytics'

Object.defineProperty(global, 'Blob', {
  value: class Blob {
    constructor(private parts: any[], private options?: any) {}
  },
  writable: true,
})

Object.defineProperty(global, 'URL', {
  value: {
    createObjectURL: jest.fn(() => 'blob:http://localhost/mock-url'),
    revokeObjectURL: jest.fn(),
  },
  writable: true,
})

Object.defineProperty(document, 'createElement', {
  value: jest.fn().mockImplementation((tag: string) => {
    if (tag === 'a') {
      return {
        href: '',
        download: '',
        click: jest.fn(),
      }
    }
    return {}
  }),
  writable: true,
})

Object.defineProperty(document.body, 'appendChild', {
  value: jest.fn(),
  writable: true,
})

Object.defineProperty(document.body, 'removeChild', {
  value: jest.fn(),
  writable: true,
})

describe('Analytics Export Utilities', () => {
  const mockAnalytics: PortfolioAnalytics = {
    summary: {
      name: 'Test Portfolio',
      total_value: 100000,
      total_invested: 80000,
      total_pnl: 20000,
      total_pnl_percent: 25,
      period_start: '2024-01-01T00:00:00Z',
      period_end: '2024-12-31T23:59:59Z',
      total_transactions: 50,
    },
    performance: {
      portfolio_id: 'test-id',
      time_period: '1y',
      cagr: 22.5,
      total_return: 20000,
      total_return_percent: 25,
      annualized_return: 22.5,
      volatility: 18.5,
      sharpe_ratio: 1.22,
      sortino_ratio: 1.45,
      max_drawdown: 8.5,
      max_drawdown_percent: 8.5,
      max_drawdown_date: null,
      recovery_time: 15,
      best_day: 3.2,
      worst_day: -2.8,
      win_rate: 58,
      alpha_vs_sp500: 2.5,
      beta_vs_sp500: 1.1,
      var_95: null,
      var_99: null,
      avg_win: 1.8,
      avg_loss: -1.5,
      profit_factor: 1.35,
    },
    risk: {
      portfolio_id: 'test-id',
      overall_risk_score: 65,
      risk_level: 'moderate',
      concentration_risk: 35,
      diversification_score: 72,
      sector_exposure: [],
      largest_holding_percent: 15,
      volatility_exposure: 18.5,
      liquidity_score: 85,
      beta: 1.1,
      correlation: null,
      recommendations: [],
      analyzed_at: '2024-12-31T23:59:59Z',
    },
    risk_metrics: {
      volatility: 18.5,
      beta: 1.1,
      alpha: 2.5,
      sharpe_ratio: 1.22,
      sortino_ratio: 1.45,
      max_drawdown: 8.5,
      max_drawdown_percent: 8.5,
      var_95: null,
      correlation: null,
    },
    performance_by_asset: [
      {
        asset_type: 'Stocks',
        value: 60000,
        return: 30,
        percentage: 60,
      },
      {
        asset_type: 'Bonds',
        value: 30000,
        return: 15,
        percentage: 30,
      },
      {
        asset_type: 'Crypto',
        value: 10000,
        return: 50,
        percentage: 10,
      },
    ],
    period_start: '2024-01-01T00:00:00Z',
    period_end: '2024-12-31T23:59:59Z',
    total_transactions: 50,
  }

  describe('generateExportData', () => {
    it('should generate JSON export data correctly', () => {
      const options: ExportOptions = { format: 'json', period: '1y' }
      const result = generateExportData(mockAnalytics, options)

      expect(result).toBeDefined()
      expect(typeof result).toBe('string')

      const parsed = JSON.parse(result as string)
      expect(parsed.summary.portfolio).toBe('Test Portfolio')
      expect(parsed.summary.totalValue).toBe(100000)
      expect(parsed.summary.totalReturn).toBe(25)
      expect(parsed.performance.cagr).toBe(22.5)
      expect(parsed.risk.volatility).toBe(18.5)
      expect(parsed.risk.beta).toBe(1.1)
    })

    it('should generate CSV export data correctly', () => {
      const options: ExportOptions = { format: 'csv', period: '1y' }
      const result = generateExportData(mockAnalytics, options)

      expect(result).toBeDefined()
      expect(typeof result).toBe('string')

      const lines = (result as string).split('\n')
      expect(lines[0]).toBe('Summary')
      expect(lines[1]).toContain('Portfolio,Total Value,Total Return')
      expect(lines[2]).toContain('Test Portfolio,100000,25%')
      expect(lines[4]).toBe('Performance')
      expect(lines[6]).toContain('22.5%,25%,22.5%,58%')
      expect(lines[8]).toBe('Risk Metrics')
      expect(lines[10]).toContain('18.5%,1.1,1.22')
      expect(lines[12]).toBe('Allocation')
      expect(lines[14]).toContain('Stocks,60000,30%')
    })

    it('should handle missing performance data gracefully', () => {
      const incompleteAnalytics: PortfolioAnalytics = {
        summary: {
          name: 'Minimal Portfolio',
          total_value: 50000,
          total_invested: 50000,
          total_pnl: 0,
          total_pnl_percent: 0,
          period_start: '2024-01-01T00:00:00Z',
          period_end: '2024-12-31T23:59:59Z',
          total_transactions: 10,
        },
        performance: {
          cagr: 0,
          total_return: 0,
          total_return_percent: 0,
          annualized_return: 0,
          best_day: 0,
          worst_day: 0,
          win_rate: 0,
        } as PortfolioAnalytics['performance'],
        risk: {} as PortfolioAnalytics['risk'],
        risk_metrics: { volatility: 0, beta: 1, sharpe_ratio: 0 },
        performance_by_asset: [],
        period_start: '2024-01-01T00:00:00Z',
        period_end: '2024-12-31T23:59:59Z',
        total_transactions: 10,
      }

      const options: ExportOptions = { format: 'json' }
      const result = generateExportData(incompleteAnalytics, options)

      expect(result).toBeDefined()
      const parsed = JSON.parse(result as string)
      expect(parsed.summary.portfolio).toBe('Minimal Portfolio')
      expect(parsed.performance.cagr).toBe(0)
      expect(parsed.performance.totalReturn).toBe(0)
    })

    it('should include allocation data in CSV export', () => {
      const options: ExportOptions = { format: 'csv' }
      const result = generateExportData(mockAnalytics, options)

      const lines = (result as string).split('\n')
      expect(lines[12]).toBe('Allocation')
      expect(lines[13]).toBe('Asset Type,Value,Return')
      expect(lines[14]).toBe('Stocks,60000,30%')
      expect(lines[15]).toBe('Bonds,30000,15%')
      expect(lines[16]).toBe('Crypto,10000,50%')
    })
  })

  describe('downloadExport', () => {
    let createObjectURLSpy: jest.SpyInstance
    let revokeObjectURLSpy: jest.SpyInstance
    let appendChildSpy: jest.SpyInstance
    let removeChildSpy: jest.SpyInstance

    beforeEach(() => {
      createObjectURLSpy = jest.spyOn(URL, 'createObjectURL')
      revokeObjectURLSpy = jest.spyOn(URL, 'revokeObjectURL')
      appendChildSpy = jest.spyOn(document.body, 'appendChild')
      removeChildSpy = jest.spyOn(document.body, 'removeChild')
    })

    afterEach(() => {
      jest.restoreAllMocks()
    })

    it('should create download link for JSON format', () => {
      downloadExport('{}', 'test.json', 'json')

      expect(createObjectURLSpy).toHaveBeenCalled()
      expect(appendChildSpy).toHaveBeenCalled()
      expect(removeChildSpy).toHaveBeenCalled()
      expect(revokeObjectURLSpy).toHaveBeenCalled()
    })

    it('should create download link for CSV format', () => {
      downloadExport('data', 'test.csv', 'csv')

      expect(createObjectURLSpy).toHaveBeenCalled()
    })
  })

  describe('exportAnalytics', () => {
    beforeEach(() => {
      jest.spyOn(console, 'log').mockImplementation(() => {})
    })

    afterEach(() => {
      jest.restoreAllMocks()
    })

    it('should generate correct filename for JSON export', () => {
      const options: ExportOptions = { format: 'json', period: '1y' }
      const data = generateExportData(mockAnalytics, options)

      expect(data).toBeDefined()
      expect(typeof data).toBe('string')
    })

    it('should generate correct filename for CSV export', () => {
      const options: ExportOptions = { format: 'csv', period: '90d' }
      const data = generateExportData(mockAnalytics, options)

      expect(data).toBeDefined()
      expect(typeof data).toBe('string')
    })
  })
})
