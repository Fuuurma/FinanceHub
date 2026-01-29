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

      setSelectedPortfolio: (id: string) => {
        set({ selectedPortfolioId: id })
        get().fetchAnalytics()
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
            summary: {
              ...summary,
              period_start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(),
              period_end: new Date().toISOString(),
              total_transactions: 0,
            },
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
              max_drawdown: performance.max_drawdown || 0,
              max_drawdown_percent: performance.max_drawdown_percent || 0,
              max_drawdown_date: null,
              recovery_time: null,
              best_day: performance.best_day,
              worst_day: performance.worst_day,
              win_rate: performance.win_rate,
              alpha_vs_sp500: performance.alpha_vs_sp500,
              beta_vs_sp500: performance.beta_vs_sp500,
              var_95: null,
              var_99: null,
              avg_win: performance.avg_win || null,
              avg_loss: performance.avg_loss || null,
              profit_factor: performance.profit_factor || null,
            },
            risk: {
              portfolio_id: selectedPortfolioId,
              overall_risk_score: risk.overall_risk_score,
              risk_level: risk.risk_level,
              concentration_risk: risk.concentration_risk,
              diversification_score: risk.diversification_score,
              sector_exposure: risk.sector_exposure,
              largest_holding_percent: risk.largest_holding_percent,
              volatility_exposure: risk.volatility_exposure,
              liquidity_score: risk.liquidity_score,
              beta: risk.volatility_exposure,
              correlation: null,
              recommendations: risk.recommendations,
              analyzed_at: risk.analyzed_at,
            },
            performance_by_asset: [],
            risk_metrics: {
              volatility: risk.volatility_exposure || 0,
              beta: risk.volatility_exposure || 0,
              alpha: performance.alpha_vs_sp500 || 0,
              sharpe_ratio: performance.sharpe_ratio || 0,
              sortino_ratio: null,
              max_drawdown: performance.max_drawdown || 0,
              max_drawdown_percent: performance.max_drawdown_percent || 0,
              var_95: null,
              correlation: null,
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
