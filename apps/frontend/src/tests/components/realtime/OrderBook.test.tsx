import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import OrderBook from '@/components/realtime/OrderBook'
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

describe('OrderBook', () => {
  const mockUseRealtimeStore = useRealtimeStore as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders depth chart tab by default', () => {
    mockUseRealtimeStore.mockReturnValue({
      orderBooks: {
        'AAPL': {
          bids: [
            { price: 149.5, size: 100 },
            { price: 149.4, size: 200 },
          ],
          asks: [
            { price: 149.6, size: 150 },
            { price: 149.7, size: 180 },
          ],
        },
      },
    })

    render(<OrderBook symbol="AAPL" />)

    expect(screen.getByText('Depth Chart')).toBeInTheDocument()
  })

  it('renders bid/ask ladder tab', () => {
    mockUseRealtimeStore.mockReturnValue({
      orderBooks: {
        'AAPL': {
          bids: [
            { price: 149.5, size: 100 },
            { price: 149.4, size: 200 },
          ],
          asks: [
            { price: 149.6, size: 150 },
            { price: 149.7, size: 180 },
          ],
        },
      },
    })

    render(<OrderBook symbol="AAPL" />)

    const bidAskTab = screen.getByText('Bid/Ask Ladder')
    bidAskTab.click()

    expect(bidAskTab).toHaveClass('data-[state=active]')
  })

  it('displays bids and asks', () => {
    mockUseRealtimeStore.mockReturnValue({
      orderBooks: {
        'AAPL': {
          bids: [
            { price: 149.5, size: 100 },
            { price: 149.4, size: 200 },
          ],
          asks: [
            { price: 149.6, size: 150 },
            { price: 149.7, size: 180 },
          ],
        },
      },
    })

    render(<OrderBook symbol="AAPL" />)

    expect(screen.getByText('149.5')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('149.6')).toBeInTheDocument()
    expect(screen.getByText('150')).toBeInTheDocument()
  })

  it('shows depth selector', () => {
    mockUseRealtimeStore.mockReturnValue({
      orderBooks: {},
    })

    render(<OrderBook symbol="AAPL" />)

    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('20')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
  })

  it('subscribes to orderbook on mount', () => {
    const mockSubscribe = jest.fn()
    mockUseRealtimeStore.mockReturnValue({
      orderBooks: {},
      subscribe: mockSubscribe,
    })

    render(<OrderBook symbol="AAPL" />)

    expect(mockSubscribe).toHaveBeenCalledWith(['AAPL'], ['orderbook'])
  })
})
