import { create } from 'zustand';
import { MarketData, AssetType } from '../lib/types/market';
import { apiClient } from '../lib/api/client';

interface MarketState {
  marketData: MarketData[];
  selectedAsset: MarketData | null;
  isLoading: boolean;
  error: string | null;
  selectedAssetType: AssetType;
  timeRange: string;

  setMarketData: (data: MarketData[]) => void;
  setSelectedAsset: (asset: MarketData | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedAssetType: (type: AssetType) => void;
  setTimeRange: (range: string) => void;

  fetchMarketData: (type: AssetType) => Promise<void>;
  fetchAssetDetails: (symbol: string) => Promise<void>;
  refreshData: () => Promise<void>;
}

export const useMarketStore = create<MarketState>((set, get) => ({
  marketData: [],
  selectedAsset: null,
  isLoading: false,
  error: null,
  selectedAssetType: AssetType.Stock,
  timeRange: '1D',

  setMarketData: (data) => set({ marketData: data }),
  setSelectedAsset: (asset) => set({ selectedAsset: asset }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setSelectedAssetType: (type) => set({ selectedAssetType: type }),
  setTimeRange: (range) => set({ timeRange: range }),

  fetchMarketData: async (type) => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiClient.get<MarketData[]>(`/api/market/${type.toLowerCase()}`);
      set({ marketData: data, selectedAssetType: type });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch market data' });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchAssetDetails: async (symbol) => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiClient.get<MarketData>(`/api/market/asset/${symbol}`);
      set({ selectedAsset: data });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch asset details' });
    } finally {
      set({ isLoading: false });
    }
  },

  refreshData: async () => {
    const { selectedAssetType, timeRange } = get();
    await get().fetchMarketData(selectedAssetType);
  },
}));
