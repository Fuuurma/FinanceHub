import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import RealTimeChart from '@/components/realtime/RealTimeChart'
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

describe('RealTimeChart', () => {
  const mockUseRealtimeStore = useRealtimeStore as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders chart component', () => {
    mockUseRealtimeStore.mockReturnValue({
      charts: {},
    })

    render(<RealTimeChart symbol="AAPL" />)

    expect(screen.getByRole('img')).toBeInTheDocument()
  })

  it('renders with default timeframe', () => {
    mockUseRealtimeStore.mockReturnValue({
      charts: {},
    })

    render(<RealTimeChart symbol="AAPL" />)

    expect(screen.getByText('1h')).toBeInTheDocument()
  })

  it('shows all timeframe options', () => {
    mockUseRealtimeStore.mockReturnValue({
      charts: {},
    })

    render(<RealTimeChart symbol="AAPL" />)

    expect(screen.getByText('1m')).toBeInTheDocument()
    expect(screen.getByText('5m')).toBeInTheDocument()
    expect(screen.getByText('15m')).toBeInTheDocument()
    expect(screen.getByText('1h')).toBeInTheDocument()
    expect(screen.getByText('4h')).toBeInTheDocument()
    expect(screen.getByText('1d')).toBeInTheDocument()
    expect(screen.getByText('1w')).toBeInTheDocument()
  })

  it('subscribes to symbol on mount', () => {
    const mockSubscribe = jest.fn()
    mockUseRealtimeStore.mockReturnValue({
      charts: {},
      subscribe: mockSubscribe,
    })

    render(<RealTimeChart symbol="AAPL" />)

    expect(mockSubscribe).toHaveBeenCalledWith(['AAPL'], ['chart'])
  })

  it('changes timeframe when clicked', () => {
    const mockSubscribe = jest.fn()
    mockUseRealtimeStore.mockReturnValue({
      charts: {},
      subscribe: mockSubscribe,
    })

    render(<RealTimeChart symbol="AAPL" />)

    const fiveMinButton = screen.getByText('5m')
    fiveMinButton.click()

    expect(mockSubscribe).toHaveBeenCalledWith(['AAPL'], ['chart'])
  })
})
