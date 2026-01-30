import { renderHook, act } from '@testing-library/react'
import { useAnalyticsStore } from '@/stores/analyticsStore'
import { AnalyticsPeriod, BenchmarkType } from '@/lib/types/portfolio-analytics'

describe('Analytics Store', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should have initial state', () => {
    const { result } = renderHook(() => useAnalyticsStore())
    
    expect(result.current.selectedPeriod).toBe('1y')
    expect(result.current.selectedBenchmark).toBe('sp500')
    expect(result.current.data).toBeNull()
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('should set selected period', () => {
    const { result } = renderHook(() => useAnalyticsStore())
    
    act(() => {
      result.current.setSelectedPeriod('30d')
    })
    
    expect(result.current.selectedPeriod).toBe('30d')
  })

  it('should set selected benchmark', () => {
    const { result } = renderHook(() => useAnalyticsStore())
    
    act(() => {
      result.current.setSelectedBenchmark('nasdaq')
    })
    
    expect(result.current.selectedBenchmark).toBe('nasdaq')
  })

  it('should clear analytics data', () => {
    const { result } = renderHook(() => useAnalyticsStore())
    
    act(() => {
      result.current.clearAnalytics()
    })
    
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeNull()
    expect(result.current.lastUpdated).toBeNull()
  })

  it('should persist selected period to localStorage', () => {
    const { result } = renderHook(() => useAnalyticsStore())
    
    act(() => {
      result.current.setSelectedPeriod('90d')
    })
    
    const stored = localStorage.getItem('analytics-storage')
    expect(stored).toBeTruthy()
    
    const parsed = JSON.parse(stored || '{}')
    expect(parsed.state.selectedPeriod).toBe('90d')
  })

  it('should persist selected benchmark to localStorage', () => {
    const { result } = renderHook(() => useAnalyticsStore())
    
    act(() => {
      result.current.setSelectedBenchmark('dow')
    })
    
    const stored = localStorage.getItem('analytics-storage')
    const parsed = JSON.parse(stored || '{}')
    expect(parsed.state.selectedBenchmark).toBe('dow')
  })
})
