import { describe, it, expect, beforeEach } from '@jest/globals'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import AlertsPage from '@/app/(dashboard)/alerts/page'
import { alertsApi } from '@/lib/api/alerts'

jest.mock('@/lib/api/alerts', () => ({
  alertsApi: {
    list: jest.fn(),
    getStats: jest.fn(),
    create: jest.fn(),
    delete: jest.fn(),
    enable: jest.fn(),
    disable: jest.fn(),
    getHistory: jest.fn(),
    test: jest.fn(),
  },
}))

describe('AlertsPage', () => {
  const mockListAlerts = alertsApi.list as jest.Mock
  const mockGetStats = alertsApi.getStats as jest.Mock
  const mockDeleteAlert = alertsApi.delete as jest.Mock
  const mockToggleAlert = alertsApi.enable as jest.Mock
  const mockGetHistory = alertsApi.getHistory as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders page title and description', () => {
    render(<AlertsPage />)
    expect(screen.getByText('Alerts')).toBeInTheDocument()
    expect(screen.getByText('Manage and monitor price alerts')).toBeInTheDocument()
  })

  it('fetches alerts and stats on mount', async () => {
    const mockAlerts = [
      {
        id: '1',
        name: 'Test Alert',
        alert_type: 'price_above',
        symbol: 'AAPL',
        condition_value: 150,
        condition_operator: '>=',
        status: 'active',
        priority: 5,
        triggered_count: 2,
        delivery_channels: ['email'],
        cooldown_seconds: 300,
        valid_from: '2026-01-01T00:00:00Z',
        valid_until: null,
        created_at: '2026-01-01T00:00:00Z',
        last_triggered_at: '2026-01-27T00:00:00Z',
      },
    ]
    const mockStats = {
      total_alerts: 10,
      active_alerts: 8,
      triggered_today: 3,
      type_distribution: { price_above: 5, price_below: 3, volume_spike: 2 },
    }
    mockListAlerts.mockResolvedValue(mockAlerts)
    mockGetStats.mockResolvedValue(mockStats as any)

    render(<AlertsPage />)
    
    await waitFor(() => {
      expect(mockListAlerts).toHaveBeenCalledWith({ status: 'all' })
      expect(mockGetStats).toHaveBeenCalled()
    })
  })

  it('displays statistics cards', async () => {
    const mockStats = {
      total_alerts: 10,
      active_alerts: 8,
      triggered_today: 3,
      type_distribution: {},
    }
    mockListAlerts.mockResolvedValue([])
    mockGetStats.mockResolvedValue(mockStats as any)

    render(<AlertsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Total Alerts')).toBeInTheDocument()
      expect(screen.getByText('10')).toBeInTheDocument()
      expect(screen.getByText('Active Alerts')).toBeInTheDocument()
      expect(screen.getByText('8')).toBeInTheDocument()
      expect(screen.getByText('Triggered Today')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })

  it('filters alerts by status', async () => {
    mockListAlerts.mockResolvedValue([])
    mockGetStats.mockResolvedValue({} as any)

    render(<AlertsPage />)
    
    await waitFor(() => {
      expect(mockListAlerts).toHaveBeenCalledWith({ status: 'all' })
    })

    const select = screen.getByDisplayValue('All')
    fireEvent.change(select, { target: { value: 'active' } })

    await waitFor(() => {
      expect(mockListAlerts).toHaveBeenCalledWith({ status: 'active' })
    })
  })

  it('searches alerts by name or symbol', async () => {
    mockListAlerts.mockResolvedValue([])
    mockGetStats.mockResolvedValue({} as any)

    render(<AlertsPage />)
    
    const input = screen.getByPlaceholderText('Search alerts by name or symbol...')
    fireEvent.change(input, { target: { value: 'AAPL' } })

    await waitFor(() => {
      expect(mockListAlerts).toHaveBeenCalledWith({ status: 'all' })
    })
  })

  it('shows create alert dialog', () => {
    mockListAlerts.mockResolvedValue([])
    mockGetStats.mockResolvedValue({} as any)

    render(<AlertsPage />)
    
    expect(screen.getByText('Create Alert')).toBeInTheDocument()
  })

  it('creates new alert', async () => {
    mockListAlerts.mockResolvedValue([])
    mockGetStats.mockResolvedValue({} as any)
    mockListAlerts.mockResolvedValue([])
    (alertsApi.create as jest.Mock).mockResolvedValue({ id: '2', message: 'Alert created successfully' })

    render(<AlertsPage />)
    
    const createButton = screen.getByText('Create Alert')
    fireEvent.click(createButton)
    
    await waitFor(() => {
      const nameInput = screen.getByLabelText('Alert Name')
      fireEvent.change(nameInput, { target: { value: 'My Test Alert' } })
      
      const symbolInput = screen.getByLabelText('Symbol')
      fireEvent.change(symbolInput, { target: { value: 'AAPL' } })
      
      const typeSelect = screen.getByLabelText('Alert Type')
      fireEvent.change(typeSelect, { target: { value: 'price_above' } })
      
      const triggerValueInput = screen.getByLabelText('Trigger Value')
      fireEvent.change(triggerValueInput, { target: { value: '150' } })
      
      const form = nameInput.closest('form')
      fireEvent.submit(form!)
    })

    await waitFor(() => {
      expect(alertsApi.create).toHaveBeenCalledWith({
        name: 'My Test Alert',
        symbol: 'AAPL',
        alert_type: 'price_above',
        condition_value: 150,
        condition_operator: '>=',
        delivery_channels: undefined,
        priority: 5,
        cooldown_seconds: 300,
      })
    })
  })

  it('deletes an alert', async () => {
    const mockAlerts = [
      {
        id: '1',
        name: 'Test Alert',
        alert_type: 'price_above',
        symbol: 'AAPL',
        condition_value: 150,
        condition_operator: '>=',
        status: 'active',
        priority: 5,
        triggered_count: 2,
        delivery_channels: ['email'],
        cooldown_seconds: 300,
        valid_from: '2026-01-01T00:00:00Z',
        valid_until: null,
        created_at: '2026-01-01T00:00:00Z',
        last_triggered_at: '2026-01-27T00:00:00Z',
      },
    ]
    mockListAlerts.mockResolvedValue(mockAlerts)
    mockGetStats.mockResolvedValue({} as any)
    mockDeleteAlert.mockResolvedValue({ message: 'Alert deleted successfully' })

    render(<AlertsPage />)
    
    await waitFor(() => {
      const deleteButtons = screen.getAllByText('Delete')
      deleteButtons[0].click()
    })

    await waitFor(() => {
      expect(mockDeleteAlert).toHaveBeenCalledWith('1')
    })
  })

  it('enables an alert', async () => {
    const mockAlerts = [
      {
        id: '1',
        name: 'Test Alert',
        alert_type: 'price_above',
        symbol: 'AAPL',
        condition_value: 150,
        condition_operator: '>=',
        status: 'active',
        priority: 5,
        triggered_count: 2,
        delivery_channels: ['email'],
        cooldown_seconds: 300,
        valid_from: '2026-01-01T00:00:00Z',
        valid_until: null,
        created_at: '2026-01-01T00:00:00Z',
        last_triggered_at: '2026-01-27T00:00:00Z',
      },
    ]
    mockListAlerts.mockResolvedValue(mockAlerts)
    mockGetStats.mockResolvedValue({} as any)
    (alertsApi.disable as jest.Mock).mockResolvedValue(mockAlerts[0])

    render(<AlertsPage />)
    
    await waitFor(() => {
      const disableButtons = screen.getAllByText('Disable')
      disableButtons[0].click()
    })

    await waitFor(() => {
      expect(alertsApi.disable).toHaveBeenCalledWith('1')
    })
  })

  it('shows alert history dialog', async () => {
    const mockAlerts = [
      {
        id: '1',
        name: 'Test Alert',
        alert_type: 'price_above',
        symbol: 'AAPL',
        condition_value: 150,
        condition_operator: '>=',
        status: 'active',
        priority: 5,
        triggered_count: 2,
        delivery_channels: ['email'],
        cooldown_seconds: 300,
        valid_from: '2026-01-01T00:00:00Z',
        valid_until: null,
        created_at: '2026-01-01T00:00:00Z',
        last_triggered_at: '2026-01-27T00:00:00Z',
      },
    ]
    const mockHistory = [
      {
        id: 'h1',
        triggered_at: '2026-01-27T10:00:00Z',
        trigger_value: 152,
        condition_met: true,
        notification_sent: true,
        notification_channels: ['email'],
      },
    ]
    mockListAlerts.mockResolvedValue(mockAlerts)
    mockGetStats.mockResolvedValue({} as any)
    mockGetHistory.mockResolvedValue(mockHistory)

    render(<AlertsPage />)
    
    await waitFor(() => {
      const historyButtons = screen.getAllByText('View History')
      historyButtons[0].click()
    })

    await waitFor(() => {
      expect(mockGetHistory).toHaveBeenCalledWith('1', 20)
    })
  })

  it('tests an alert', async () => {
    const mockAlerts = [
      {
        id: '1',
        name: 'Test Alert',
        alert_type: 'price_above',
        symbol: 'AAPL',
        condition_value: 150,
        condition_operator: '>=',
        status: 'active',
        priority: 5,
        triggered_count: 2,
        delivery_channels: ['email'],
        cooldown_seconds: 300,
        valid_from: '2026-01-01T00:00:00Z',
        valid_until: null,
        created_at: '2026-01-01T00:00:00Z',
        last_triggered_at: '2026-01-27T00:00:00Z',
      },
    ]
    mockListAlerts.mockResolvedValue(mockAlerts)
    mockGetStats.mockResolvedValue({} as any)
    (alertsApi.test as jest.Mock).mockResolvedValue({ success: true, trigger_value: 152 })

    render(<AlertsPage />)
    
    await waitFor(() => {
      const testButtons = screen.getAllByText('Test')
      testButtons[0].click()
    })

    await waitFor(() => {
      expect(alertsApi.test).toHaveBeenCalledWith('1')
    })
  })
})
