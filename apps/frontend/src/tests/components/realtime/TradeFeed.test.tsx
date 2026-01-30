import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import TradeFeed from '@/components/realtime/TradeFeed'
import { useRealtimeStore } from '@/stores/realtimeStore'

jest.mock('@/stores/realtimeStore', () => ({
  useRealtimeStore: jest.fn(),
}))

jest.mock('@/lib/api/websocket', () => ({
  getWebSocketClient: () => ({
    subscribe: jest.fn(),
    unsubscribe: jest.fn(),
  }),
}))

describe('TradeFeed', () => {
  const mockUseRealtimeStore = useRealtimeStore as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders empty state when no trades', () => {
    mockUseRealtimeStore.mockReturnValue({
      trades: {},
    })

    render(<TradeFeed symbol="AAPL" />)

    expect(screen.getByText('No trades yet')).toBeInTheDocument()
  })

  it('renders trades', () => {
    const mockTrades = [
      {
        id: '1',
        timestamp: '2026-01-28T12:00:00Z',
        price: 150.25,
        size: 100,
        side: 'buy',
        symbol: 'AAPL',
      },
      {
        id: '2',
        timestamp: '2026-01-28T12:00:01Z',
        price: 150.50,
        size: 50,
        side: 'sell',
        symbol: 'AAPL',
      },
      {
        id: '3',
        timestamp: '2026-01-28T12:00:02Z',
        price: 150.75,
        size: 150,
        side: 'buy',
        symbol: 'AAPL',
      },
    ]
    mockUseRealtimeStore.mockReturnValue({
      trades: {
        'AAPL': mockTrades,
      },
    })

    render(<TradeFeed symbol="AAPL" />)

    expect(screen.getByText('150.25')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('150.50')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
  })

  it('displays trade time', () => {
    const mockTrades = [
      {
        id: '1',
        timestamp: '2026-01-28T12:00:00Z',
        price: 150.25,
        size: 100,
        side: 'buy',
        symbol: 'AAPL',
      },
    ]
    mockUseRealtimeStore.mockReturnValue({
      trades: {
        'AAPL': mockTrades,
      },
    })

    render(<TradeFeed symbol="AAPL" />)

    expect(screen.getByText(/12:00:00/)).toBeInTheDocument()
  })

  it('filters trades by side', () => {
    const mockTrades = [
      {
        id: '1',
        timestamp: '2026-01-28T12:00:00Z',
        price: 150.25,
        size: 100,
        side: 'buy',
        symbol: 'AAPL',
      },
      {
        id: '2',
        timestamp: '2026-01-28T12:00:01Z',
        price: 150.50,
        size: 50,
        side: 'sell',
        symbol: 'AAPL',
      },
    ]
    mockUseRealtimeStore.mockReturnValue({
      trades: {
        'AAPL': mockTrades,
      },
    })

    render(<TradeFeed symbol="AAPL" />)

    const allFilter = screen.getByText('All')
    const buysFilter = screen.getByText('Buys')
    const sellsFilter = screen.getByText('Sells')

    buysFilter.click()

    expect(screen.getByText('150.25')).toBeInTheDocument()
    expect(screen.queryByText('150.50')).not.toBeInTheDocument()
  })

  it('limits trades to configured limit', () => {
    const mockTrades = Array.from({ length: 25 }, (_, i) => ({
      id: String(i),
      timestamp: `2026-01-28T12:00:${String(i).padStart(2, '0')}Z`,
      price: 150 + i * 0.25,
      size: 100 + i * 10,
      side: i % 2 === 0 ? 'buy' : 'sell',
      symbol: 'AAPL',
    }))
    mockUseRealtimeStore.mockReturnValue({
      trades: {
        'AAPL': mockTrades,
      },
    })

    render(<TradeFeed symbol="AAPL" limit={20} />)

    expect(screen.getAllByTestId('trade-item')).toHaveLength(20)
  })

  it('subscribes to trades on mount', () => {
    const mockSubscribe = jest.fn()
    mockUseRealtimeStore.mockReturnValue({
      trades: {},
      subscribe: mockSubscribe,
    })

    render(<TradeFeed symbol="AAPL" />)

    expect(mockSubscribe).toHaveBeenCalledWith(['AAPL'], ['trade'])
  })
})
