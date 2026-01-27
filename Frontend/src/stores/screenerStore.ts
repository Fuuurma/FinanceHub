import { create } from 'zustand';
import { AssetType } from '../types/market';
import { ScreenerCriteria, ScreenerResult } from '../types/screener';
import { apiClient } from '../utils/api';

interface ScreenerState {
  criteria: ScreenerCriteria;
  results: ScreenerResult[];
  isLoading: boolean;
  error: string | null;

  setCriteria: (criteria: Partial<ScreenerCriteria>) => void;
  resetCriteria: () => void;
  setResults: (results: ScreenerResult[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  runScreener: () => Promise<void>;
  loadPreset: (preset: string) => void;
  savePreset: (name: string) => Promise<void>;
}

const defaultCriteria: ScreenerCriteria = {
  assetTypes: [AssetType.Stock],
  exchanges: [],
  sectors: [],
  marketCap: { min: 0, max: Infinity },
  price: { min: 0, max: Infinity },
  volume: { min: 0, max: Infinity },
  peRatio: { min: 0, max: Infinity },
  dividendYield: { min: 0, max: Infinity },
  beta: { min: 0, max: Infinity },
  epsGrowth: { min: 0, max: Infinity },
  revenueGrowth: { min: 0, max: Infinity },
  profitMargin: { min: 0, max: Infinity },
  roe: { min: 0, max: Infinity },
  debtToEquity: { min: 0, max: Infinity },
  currentRatio: { min: 0, max: Infinity },
  quickRatio: { min: 0, max: Infinity },
  freeCashFlow: { min: 0, max: Infinity },
  operatingMargin: { min: 0, max: Infinity },
  priceToBook: { min: 0, max: Infinity },
  priceToSales: { min: 0, max: Infinity },
  evToEbitda: { min: 0, max: Infinity },
  pegRatio: { min: 0, max: Infinity },
};

export const useScreenerStore = create<ScreenerState>((set, get) => ({
  criteria: defaultCriteria,
  results: [],
  isLoading: false,
  error: null,

  setCriteria: (newCriteria) => {
    set((state) => ({
      criteria: { ...state.criteria, ...newCriteria },
    }));
  },

  resetCriteria: () => {
    set({ criteria: defaultCriteria });
  },

  setResults: (results) => set({ results }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),

  runScreener: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiClient.post<ScreenerResult[]>('/api/screener/run', get().criteria);
      set({ results: data });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to run screener' });
    } finally {
      set({ isLoading: false });
    }
  },

  loadPreset: async (preset) => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiClient.get<ScreenerCriteria>(`/api/screener/presets/${preset}`);
      set({ criteria: data });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to load preset' });
    } finally {
      set({ isLoading: false });
    }
  },

  savePreset: async (name) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post('/api/screener/presets', { name, criteria: get().criteria });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to save preset' });
    } finally {
      set({ isLoading: false });
    }
  },
}));
