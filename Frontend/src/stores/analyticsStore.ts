import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { portfolioAnalyticsApi } from '@/lib/api/portfolio-analytics'
import type { PortfolioAnalytics, AnalyticsPeriod, BenchmarkType, AnalyticsState } from '@/lib/types/portfolio-analytics'

const API_PERIOD_MAP: Record<AnalyticsPeriod, '1y' | '6m' | '3m'> = {
  '1d': '3m',
  '7d': '3m',
  '30d': '3m',
  '90d': '6m',
  '180d': '6m',
  '1y': '1y',
  '3y': '1y',
  '5y': '1y',
  'ytd': '1y',
  'all': '1y',
}

export const useAnalyticsStore = create<AnalyticsState>()(
  persist(
    (set, get) => ({
      selectedPortfolioId: null,
      selectedPeriod: '1y',
      selectedBenchmark: 'sp500',
      data: null,
      loading: false,
      error: null,
      lastUpdated: null,

      setSelectedPortfolio: (id: string | null) => {
        set({ selectedPortfolioId: id })
        if (id) {
          get().fetchAnalytics()
        }
      },

      setSelectedPeriod: (period: AnalyticsPeriod) => {
        set({ selectedPeriod: period })
        get().fetchAnalytics()
      },

      setSelectedBenchmark: (benchmark: BenchmarkType) => {
        set({ selectedBenchmark: benchmark })
        get().fetchAnalytics()
      },

      fetchAnalytics: async () => {
        const { selectedPortfolioId, selectedPeriod, selectedBenchmark } = get()
        
        if (!selectedPortfolioId) {
          set({ error: 'No portfolio selected', loading: false })
          return
        }

        set({ loading: true, error: null })

        try {
          const apiPeriod = API_PERIOD_MAP[selectedPeriod]
          
          const [summary, performance, risk, allocation] = await Promise.all([
            portfolioAnalyticsApi.getPortfolioSummary(selectedPortfolioId),
            portfolioAnalyticsApi.getPerformanceMetrics(selectedPortfolioId, apiPeriod),
            portfolioAnalyticsApi.getRiskAnalysis(selectedPortfolioId),
            portfolioAnalyticsApi.getHoldingsAnalysis(selectedPortfolioId),
          ])

          const analyticsData: PortfolioAnalytics = {
            total_return: performance.total_return || 0,
            total_value: summary.total_value,
            total_value_change: summary.total_pnl,
            total_value_change_percent: summary.total_pnl_percent,
            summary: { ...summary },
            performance: {
              portfolio_id: selectedPortfolioId,
              time_period: selectedPeriod,
              cagr: performance.annualized_return || 0,
              total_return: performance.total_return,
              total_return_percent: performance.total_return_percent,
              annualized_return: performance.annualized_return,
              volatility: performance.volatility,
              sharpe_ratio: performance.sharpe_ratio,
              sortino_ratio: null,
              max_drawdown: performance.max_drawdown || null,
              max_drawdown_percent: performance.max_drawdown_percent || null,
              max_drawdown_date: null,
              recovery_time: null,
              best_day: performance.best_day,
              worst_day: performance.worst_day,
              win_rate: performance.win_rate,
              alpha_vs_sp500: performance.alpha_vs_sp500,
              beta_vs_sp500: performance.beta_vs_sp500,
              var_95: null,
              var_99: null,
              avg_win: null,
              avg_loss: null,
              profit_factor: null,
            },
            performance_by_asset: [],
            risk_metrics: {
              volatility: risk.volatility_exposure || 0,
              beta: risk.volatility_exposure || 0,
              sharpe_ratio: performance.sharpe_ratio || 0,
            },
            period_start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(),
            period_end: new Date().toISOString(),
            total_transactions: 0,
          }

          set({
            data: analyticsData,
            loading: false,
            lastUpdated: new Date().toISOString(),
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch analytics',
            loading: false,
          })
        }
      },

      clearAnalytics: () => {
        set({
          data: null,
          error: null,
          lastUpdated: null,
        })
      },
    }),
    {
      name: 'analytics-storage',
      partialize: (state) => ({
        selectedPortfolioId: state.selectedPortfolioId,
        selectedPeriod: state.selectedPeriod,
        selectedBenchmark: state.selectedBenchmark,
      }),
    }
  )
)

export const useAnalytics = () => {
  const store = useAnalyticsStore()
  return {
    ...store,
    fetchAnalytics: store.fetchAnalytics,
    setSelectedPortfolio: store.setSelectedPortfolio,
    setSelectedPeriod: store.setSelectedPeriod,
    setSelectedBenchmark: store.setSelectedBenchmark,
    clearAnalytics: store.clearAnalytics,
  }
}
