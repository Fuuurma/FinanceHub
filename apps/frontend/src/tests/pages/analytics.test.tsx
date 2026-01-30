import { describe, it, expect, beforeEach } from '@jest/globals'
import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import AnalyticsPage from '@/app/(dashboard)/analytics/page'
import { portfolioAnalyticsApi } from '@/lib/api/portfolio-analytics'

jest.mock('@/lib/api/portfolio-analytics', () => ({
  portfolioAnalyticsApi: {
    getAnalytics: jest.fn(),
  },
}))

describe('AnalyticsPage', () => {
  const mockGetAnalytics = portfolioAnalyticsApi.getAnalytics as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders page title and description', () => {
    render(<AnalyticsPage />)
    expect(screen.getByText('Portfolio Analytics')).toBeInTheDocument()
    expect(screen.getByText('Detailed portfolio performance analysis')).toBeInTheDocument()
  })

  it('renders period selector', () => {
    render(<AnalyticsPage />)
    expect(screen.getByText('1 Day')).toBeInTheDocument()
    expect(screen.getByText('7 Days')).toBeInTheDocument()
    expect(screen.getByText('30 Days')).toBeInTheDocument()
    expect(screen.getByText('90 Days')).toBeInTheDocument()
    expect(screen.getByText('1 Year')).toBeInTheDocument()
  })

  it('calls API on mount', async () => {
    const mockResponse = {
      total_return: 15.5,
      total_value: 125000,
      total_value_change: 5000,
      total_value_change_percent: 4.2,
      performance_by_asset: [
        { asset_type: 'Stocks', value: 80000, return: 12.5 },
        { asset_type: 'Crypto', value: 35000, return: 25.8 },
        { asset_type: 'Bonds', value: 10000, return: 3.2 },
      ],
      risk_metrics: {
        volatility: 18.5,
        beta: 1.15,
        sharpe_ratio: 1.45,
      },
      period_start: '2026-01-01T00:00:00Z',
      period_end: '2026-01-28T00:00:00Z',
      total_transactions: 42,
    }
    mockGetAnalytics.mockResolvedValue(mockResponse as any)

    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(mockGetAnalytics).toHaveBeenCalledWith('7d')
    })
  })

  it('changes period when clicked', async () => {
    mockGetAnalytics.mockResolvedValue({} as any)
    render(<AnalyticsPage />)
    
    const oneDayButton = screen.getByText('1 Day')
    oneDayButton.click()

    await waitFor(() => {
      expect(mockGetAnalytics).toHaveBeenCalledWith('1d')
    })
  })

  it('displays loading skeletons while fetching', () => {
    mockGetAnalytics.mockImplementation(() => new Promise(() => {}))
    render(<AnalyticsPage />)
    
    expect(screen.getAllByTestId(/skeleton/i).length).toBeGreaterThan(0)
  })

  it('displays analytics data when loaded', async () => {
    const mockResponse = {
      total_return: 15.5,
      total_value: 125000,
      total_value_change: 5000,
      total_value_change_percent: 4.2,
      performance_by_asset: [
        { asset_type: 'Stocks', value: 80000, return: 12.5 },
      ],
      risk_metrics: {
        volatility: 18.5,
        beta: 1.15,
        sharpe_ratio: 1.45,
      },
      period_start: '2026-01-01T00:00:00Z',
      period_end: '2026-01-28T00:00:00Z',
      total_transactions: 42,
    }
    mockGetAnalytics.mockResolvedValue(mockResponse as any)

    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('+15.50%')).toBeInTheDocument()
      expect(screen.getByText(/125000/)).toBeInTheDocument()
      expect(screen.getByText(/18.50%/)).toBeInTheDocument()
      expect(screen.getByText(/1.15/)).toBeInTheDocument()
      expect(screen.getByText(/1.45/)).toBeInTheDocument()
    })
  })

  it('exports analytics to JSON', async () => {
    const mockResponse = {
      total_return: 15.5,
      total_value: 125000,
      total_value_change: 5000,
      total_value_change_percent: 4.2,
      performance_by_asset: [],
      risk_metrics: { volatility: 0, beta: 0, sharpe_ratio: 0 },
      period_start: '2026-01-01T00:00:00Z',
      period_end: '2026-01-28T00:00:00Z',
      total_transactions: 0,
    }
    mockGetAnalytics.mockResolvedValue(mockResponse as any)

    const createElementSpy = jest.spyOn(document, 'createElement')
    
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Export')).toBeInTheDocument()
    })
    
    const exportButton = screen.getByText('Export')
    exportButton.click()
    
    expect(createElementSpy).toHaveBeenCalledWith('a')
    createElementSpy.mockRestore()
  })
})
