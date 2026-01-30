import { create } from 'zustand';
import type { Watchlist } from '@/lib/types/watchlist';
import { apiClient } from '@/lib/api/client';

interface WatchlistState {
  watchlists: Watchlist[];
  currentWatchlist: Watchlist | null;
  isLoading: boolean;
  error: string | null;

  setWatchlists: (watchlists: Watchlist[]) => void;
  setCurrentWatchlist: (watchlist: Watchlist | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  fetchWatchlists: () => Promise<void>;
  createWatchlist: (name: string, symbols: string[]) => Promise<void>;
  updateWatchlist: (id: string, name: string, symbols: string[]) => Promise<void>;
  deleteWatchlist: (id: string) => Promise<void>;
  addAssetToWatchlist: (watchlistId: string, symbol: string) => Promise<void>;
  removeAssetFromWatchlist: (watchlistId: string, symbol: string) => Promise<void>;
}

export const useWatchlistStore = create<WatchlistState>((set, get) => ({
  watchlists: [],
  currentWatchlist: null,
  isLoading: false,
  error: null,

  setWatchlists: (watchlists) => set({ watchlists }),
  setCurrentWatchlist: (watchlist) => set({ currentWatchlist: watchlist }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),

  fetchWatchlists: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiClient.get<Watchlist[]>('/watchlist');
      set({ watchlists: data });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch watchlists' });
    } finally {
      set({ isLoading: false });
    }
  },

  createWatchlist: async (name, symbols) => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiClient.post<Watchlist>('/watchlist', { name, symbols });
      set((state) => ({ watchlists: [...state.watchlists, data] }));
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to create watchlist' });
    } finally {
      set({ isLoading: false });
    }
  },

  updateWatchlist: async (id, name, symbols) => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiClient.put<Watchlist>(`/watchlist/${id}`, { name, symbols });
      set((state) => ({
        watchlists: state.watchlists.map((w) => (w.id === id ? data : w)),
        currentWatchlist: state.currentWatchlist?.id === id ? data : state.currentWatchlist,
      }));
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to update watchlist' });
    } finally {
      set({ isLoading: false });
    }
  },

  deleteWatchlist: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.delete(`/watchlist/${id}`);
      set((state) => ({
        watchlists: state.watchlists.filter((w) => w.id !== id),
        currentWatchlist: state.currentWatchlist?.id === id ? null : state.currentWatchlist,
      }));
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to delete watchlist' });
    } finally {
      set({ isLoading: false });
    }
  },

  addAssetToWatchlist: async (watchlistId, symbol) => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiClient.post<Watchlist>(`/watchlist/${watchlistId}/assets`, { symbol });
      set((state) => ({
        watchlists: state.watchlists.map((w) => (w.id === watchlistId ? data : w)),
        currentWatchlist: state.currentWatchlist?.id === watchlistId ? data : state.currentWatchlist,
      }));
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to add asset to watchlist' });
    } finally {
      set({ isLoading: false });
    }
  },

  removeAssetFromWatchlist: async (watchlistId, symbol) => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiClient.delete<Watchlist>(`/watchlist/${watchlistId}/assets/${symbol}`);
      set((state) => ({
        watchlists: state.watchlists.map((w) => (w.id === watchlistId ? data : w)),
        currentWatchlist: state.currentWatchlist?.id === watchlistId ? data : state.currentWatchlist,
      }));
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to remove asset from watchlist' });
    } finally {
      set({ isLoading: false });
    }
  },
}));
