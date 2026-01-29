import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { ChartDrawing, TechnicalIndicatorValue, ChartDrawingManager } from '@/lib/api/charts'
import { IndicatorConfig } from '@/lib/types/indicators'

interface ChartsState {
  drawings: Record<string, ChartDrawing[]>
  indicatorValues: Record<string, Record<string, TechnicalIndicatorValue[]>>
  layouts: ChartDrawingManager[]
  activeLayout: string | null
  isLoading: boolean
  error: string | null

  setDrawings: (symbol: string, drawings: ChartDrawing[]) => void
  addDrawing: (symbol: string, drawing: ChartDrawing) => void
  updateDrawing: (symbol: string, drawingId: string, updates: Partial<ChartDrawing>) => void
  removeDrawing: (symbol: string, drawingId: string) => void
  clearDrawings: (symbol: string) => void

  setIndicatorValues: (symbol: string, indicatorType: string, values: TechnicalIndicatorValue[]) => void
  clearIndicatorValues: (symbol: string) => void

  setLayouts: (layouts: ChartDrawingManager[]) => void
  addLayout: (layout: ChartDrawingManager) => void
  updateLayout: (layoutId: string, updates: Partial<ChartDrawingManager>) => void
  removeLayout: (layoutId: string) => void
  setActiveLayout: (layoutId: string | null) => void

  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useChartsStore = create<ChartsState>()(
  persist(
    (set) => ({
      drawings: {},
      indicatorValues: {},
      layouts: [],
      activeLayout: null,
      isLoading: false,
      error: null,

      setDrawings: (symbol, drawings) =>
        set((state) => ({
          drawings: {
            ...state.drawings,
            [symbol]: drawings,
          },
        })),

      addDrawing: (symbol, drawing) =>
        set((state) => ({
          drawings: {
            ...state.drawings,
            [symbol]: [...(state.drawings[symbol] || []), drawing],
          },
        })),

      updateDrawing: (symbol, drawingId, updates) =>
        set((state) => ({
          drawings: {
            ...state.drawings,
            [symbol]: (state.drawings[symbol] || []).map((d) =>
              d.id === drawingId ? { ...d, ...updates } : d
            ),
          },
        })),

      removeDrawing: (symbol, drawingId) =>
        set((state) => ({
          drawings: {
            ...state.drawings,
            [symbol]: (state.drawings[symbol] || []).filter((d) => d.id !== drawingId),
          },
        })),

      clearDrawings: (symbol) =>
        set((state) => ({
          drawings: {
            ...state.drawings,
            [symbol]: [],
          },
        })),

      setIndicatorValues: (symbol, indicatorType, values) =>
        set((state) => ({
          indicatorValues: {
            ...state.indicatorValues,
            [symbol]: {
              ...(state.indicatorValues[symbol] || {}),
              [indicatorType]: values,
            },
          },
        })),

      clearIndicatorValues: (symbol) =>
        set((state) => ({
          indicatorValues: {
            ...state.indicatorValues,
            [symbol]: {},
          },
        })),

      setLayouts: (layouts) => set({ layouts }),

      addLayout: (layout) =>
        set((state) => ({
          layouts: [...state.layouts, layout],
        })),

      updateLayout: (layoutId, updates) =>
        set((state) => ({
          layouts: state.layouts.map((l) =>
            l.id === layoutId ? { ...l, ...updates } : l
          ),
        })),

      removeLayout: (layoutId) =>
        set((state) => ({
          layouts: state.layouts.filter((l) => l.id !== layoutId),
        })),

      setActiveLayout: (layoutId) => set({ activeLayout: layoutId }),

      setLoading: (loading) => set({ isLoading: loading }),

      setError: (error) => set({ error }),

      clearError: () => set({ error: null }),
    }),
    {
      name: 'charts-storage',
      partialize: (state) => ({
        activeLayout: state.activeLayout,
        layouts: state.layouts,
      }),
    }
  )
)
