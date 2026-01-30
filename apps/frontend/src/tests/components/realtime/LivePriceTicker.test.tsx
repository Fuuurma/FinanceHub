import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import LivePriceTicker from '@/components/realtime/LivePriceTicker'
import { useRealtimeStore } from '@/stores/realtimeStore'

jest.mock('@/stores/realtimeStore', () => ({
  useRealtimeStore: jest.fn(),
}))

describe('LivePriceTicker', () => {
  const mockUseRealtimeStore = useRealtimeStore as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRealtimeStore.mockReset()
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders empty state when no prices', () => {
    mockUseRealtimeStore.mockReturnValue({
      prices: {},
    })

    render(<LivePriceTicker />)

    expect(screen.getByText('No price data available')).toBeInTheDocument()
  })

  it('renders prices', () => {
    mockUseRealtimeStore.mockReturnValue({
      prices: {
        'BTCUSDT': { price: 50000, change: 2.5, symbol: 'BTCUSDT' },
        'ETHUSDT': { price: 3000, change: -1.2, symbol: 'ETHUSDT' },
        'AAPL': { price: 150, change: 0.5, symbol: 'AAPL' },
      },
    })

    render(<LivePriceTicker />)

    expect(screen.getByText('BTCUSDT')).toBeInTheDocument()
    expect(screen.getByText('50000')).toBeInTheDocument()
    expect(screen.getByText('ETHUSDT')).toBeInTheDocument()
    expect(screen.getByText('3000')).toBeInTheDocument()
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('150')).toBeInTheDocument()
  })

  it('limits displayed symbols to max', () => {
    mockUseRealtimeStore.mockReturnValue({
      prices: {
        'BTCUSDT': { price: 50000, change: 2.5, symbol: 'BTCUSDT' },
        'ETHUSDT': { price: 3000, change: -1.2, symbol: 'ETHUSDT' },
        'AAPL': { price: 150, change: 0.5, symbol: 'AAPL' },
        'GOOGL': { price: 2800, change: 1.8, symbol: 'GOOGL' },
        'TSLA': { price: 900, change: -0.5, symbol: 'TSLA' },
        'MSFT': { price: 380, change: 1.1, symbol: 'MSFT' },
        'AMZN': { price: 175, change: -0.8, symbol: 'AMZN' },
        'META': { price: 350, change: 2.2, symbol: 'META' },
        'NVDA': { price: 480, change: 3.5, symbol: 'NVDA' },
        'NFLX': { price: 420, change: 0.3, symbol: 'NFLX' },
        'AMD': { price: 140, change: -0.2, symbol: 'AMD' },
      },
    })

    render(<LivePriceTicker />)

    const tickerSymbols = screen.getAllByTestId('ticker-item')
    expect(tickerSymbols.length).toBe(10)
  })

  it('pauses on hover', () => {
    mockUseRealtimeStore.mockReturnValue({
      prices: {
        'BTCUSDT': { price: 50000, change: 2.5, symbol: 'BTCUSDT' },
      },
    })

    const { container } = render(<LivePriceTicker />)
    
    const ticker = container.querySelector('[data-testid="price-ticker"]')
    expect(ticker).toHaveClass('hover:pause')
  })
})
