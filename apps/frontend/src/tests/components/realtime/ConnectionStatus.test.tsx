import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { render, screen, waitFor, act } from '@testing-library/react'
import '@testing-library/jest-dom'
import ConnectionStatus from '@/components/realtime/ConnectionStatus'
import { useRealtimeStore } from '@/stores/realtimeStore'

jest.mock('@/stores/realtimeStore', () => ({
  useRealtimeStore: jest.fn(),
}))

jest.mock('@/lib/api/websocket', () => ({
  getWebSocketClient: () => ({
    getPingMs: () => 45,
    connect: jest.fn(),
    disconnect: jest.fn(),
  }),
}))

describe('ConnectionStatus', () => {
  const mockUseRealtimeStore = useRealtimeStore as jest.Mock
  const mockGetWebSocketClient = (getWebSocketClient as jest.Mock)

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRealtimeStore.mockReset()
    mockGetWebSocketClient.mockReturnValue({
      getPingMs: () => 45,
      connect: jest.fn(),
      disconnect: jest.fn(),
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders connected status', () => {
    mockUseRealtimeStore.mockReturnValue({
      connectionState: 'connected',
      error: null,
    })

    render(<ConnectionStatus />)

    expect(screen.getByText('Connected')).toBeInTheDocument()
    expect(screen.getByRole('status', { hidden: true })).toHaveClass('bg-green-500')
  })

  it('renders connecting status', () => {
    mockUseRealtimeStore.mockReturnValue({
      connectionState: 'connecting',
      error: null,
    })

    render(<ConnectionStatus />)

    expect(screen.getByText('Connecting...')).toBeInTheDocument()
    expect(screen.getByRole('status', { hidden: true })).toHaveClass('bg-yellow-500')
  })

  it('renders disconnected status', () => {
    mockUseRealtimeStore.mockReturnValue({
      connectionState: 'disconnected',
      error: null,
    })

    render(<ConnectionStatus />)

    expect(screen.getByText('Disconnected')).toBeInTheDocument()
    expect(screen.getByRole('status', { hidden: true })).toHaveClass('bg-red-500')
  })

  it('renders error status', () => {
    mockUseRealtimeStore.mockReturnValue({
      connectionState: 'error',
      error: 'Connection failed',
    })

    render(<ConnectionStatus />)

    expect(screen.getByText('Error')).toBeInTheDocument()
    expect(screen.getByText('Connection failed')).toBeInTheDocument()
    expect(screen.getByRole('status', { hidden: true })).toHaveClass('bg-red-500')
  })

  it('shows reconnect button when disconnected', () => {
    const mockConnect = jest.fn()
    mockUseRealtimeStore.mockReturnValue({
      connectionState: 'disconnected',
      error: null,
      connect: mockConnect,
    })

    render(<ConnectionStatus />)

    const reconnectButton = screen.getByText('Reconnect')
    expect(reconnectButton).toBeInTheDocument()

    act(() => {
      reconnectButton.click()
    })

    expect(mockConnect).toHaveBeenCalled()
  })

  it('shows reconnect button on error', () => {
    const mockConnect = jest.fn()
    mockUseRealtimeStore.mockReturnValue({
      connectionState: 'error',
      error: 'Connection failed',
      connect: mockConnect,
    })

    render(<ConnectionStatus />)

    const reconnectButton = screen.getByText('Reconnect')
    expect(reconnectButton).toBeInTheDocument()

    act(() => {
      reconnectButton.click()
    })

    expect(mockConnect).toHaveBeenCalled()
  })

  it('does not show reconnect button when connected', () => {
    mockUseRealtimeStore.mockReturnValue({
      connectionState: 'connected',
      error: null,
    })

    render(<ConnectionStatus />)

    expect(screen.queryByText('Reconnect')).not.toBeInTheDocument()
  })

  it('displays ping time', () => {
    mockUseRealtimeStore.mockReturnValue({
      connectionState: 'connected',
      error: null,
    })

    render(<ConnectionStatus />)

    expect(screen.getByText(/45ms/)).toBeInTheDocument()
  })
})
