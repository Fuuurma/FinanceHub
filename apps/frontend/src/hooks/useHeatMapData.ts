import { useState, useEffect, useCallback } from 'react';
import { HeatMapNode, HeatMapViewType } from '@/components/charts/heatmap/types';

interface UseHeatMapDataResult {
  data: HeatMapNode[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

const MOCK_HEATMAP_DATA: HeatMapNode[] = [
  {
    id: 'technology',
    name: 'Technology',
    value: 15000000000,
    change: 2.5,
    changeAmount: 375000000,
    type: 'sector',
    children: [
      { id: 'AAPL', name: 'Apple', symbol: 'AAPL', value: 3000000000, change: 1.8, changeAmount: 54000000, type: 'stock' },
      { id: 'MSFT', name: 'Microsoft', symbol: 'MSFT', value: 2800000000, change: 2.1, changeAmount: 58800000, type: 'stock' },
      { id: 'NVDA', name: 'NVIDIA', symbol: 'NVDA', value: 2000000000, change: 4.5, changeAmount: 90000000, type: 'stock' },
      { id: 'AVGO', name: 'Broadcom', symbol: 'AVGO', value: 1200000000, change: 3.2, changeAmount: 38400000, type: 'stock' },
      { id: 'ORCL', name: 'Oracle', symbol: 'ORCL', value: 800000000, change: 1.5, changeAmount: 12000000, type: 'stock' },
    ]
  },
  {
    id: 'healthcare',
    name: 'Healthcare',
    value: 8000000000,
    change: 1.2,
    changeAmount: 96000000,
    type: 'sector',
    children: [
      { id: 'UNH', name: 'UnitedHealth', symbol: 'UNH', value: 1500000000, change: 0.8, changeAmount: 12000000, type: 'stock' },
      { id: 'JNJ', name: 'Johnson & Johnson', symbol: 'JNJ', value: 1200000000, change: -0.5, changeAmount: -6000000, type: 'stock' },
      { id: 'LLY', name: 'Eli Lilly', symbol: 'LLY', value: 1000000000, change: 2.8, changeAmount: 28000000, type: 'stock' },
      { id: 'PFE', name: 'Pfizer', symbol: 'PFE', value: 600000000, change: -1.2, changeAmount: -7200000, type: 'stock' },
    ]
  },
  {
    id: 'financials',
    name: 'Financials',
    value: 6500000000,
    change: -0.8,
    changeAmount: -52000000,
    type: 'sector',
    children: [
      { id: 'BRK.B', name: 'Berkshire B', symbol: 'BRK.B', value: 1800000000, change: -0.3, changeAmount: -5400000, type: 'stock' },
      { id: 'JPM', name: 'JPMorgan', symbol: 'JPM', value: 1200000000, change: -1.1, changeAmount: -13200000, type: 'stock' },
      { id: 'V', name: 'Visa', symbol: 'V', value: 1000000000, change: 0.5, changeAmount: 5000000, type: 'stock' },
    ]
  },
  {
    id: 'consumer-discretionary',
    name: 'Consumer Disc.',
    value: 5000000000,
    change: 1.5,
    changeAmount: 75000000,
    type: 'sector',
    children: [
      { id: 'AMZN', name: 'Amazon', symbol: 'AMZN', value: 2000000000, change: 2.0, changeAmount: 40000000, type: 'stock' },
      { id: 'TSLA', name: 'Tesla', symbol: 'TSLA', value: 1500000000, change: 3.5, changeAmount: 52500000, type: 'stock' },
      { id: 'HD', name: 'Home Depot', symbol: 'HD', value: 800000000, change: 0.8, changeAmount: 6400000, type: 'stock' },
    ]
  },
  {
    id: 'energy',
    name: 'Energy',
    value: 3500000000,
    change: 3.8,
    changeAmount: 133000000,
    type: 'sector',
    children: [
      { id: 'XOM', name: 'Exxon', symbol: 'XOM', value: 1000000000, change: 2.9, changeAmount: 29000000, type: 'stock' },
      { id: 'CVX', name: 'Chevron', symbol: 'CVX', value: 800000000, change: 2.5, changeAmount: 20000000, type: 'stock' },
      { id: 'COP', name: 'ConocoPhillips', symbol: 'COP', value: 500000000, change: 4.1, changeAmount: 20500000, type: 'stock' },
    ]
  },
  {
    id: 'utilities',
    name: 'Utilities',
    value: 1500000000,
    change: -1.2,
    changeAmount: -18000000,
    type: 'sector',
    children: [
      { id: 'NEE', name: 'NextEra', symbol: 'NEE', value: 400000000, change: -0.9, changeAmount: -3600000, type: 'stock' },
      { id: 'SO', name: 'Southern Co', symbol: 'SO', value: 300000000, change: -1.1, changeAmount: -3300000, type: 'stock' },
    ]
  },
  {
    id: 'materials',
    name: 'Materials',
    value: 1200000000,
    change: 1.1,
    changeAmount: 13200000,
    type: 'sector',
    children: [
      { id: 'LIN', name: 'Linde', symbol: 'LIN', value: 400000000, change: 1.5, changeAmount: 6000000, type: 'stock' },
      { id: 'APD', name: 'Air Products', symbol: 'APD', value: 250000000, change: 0.8, changeAmount: 2000000, type: 'stock' },
    ]
  },
  {
    id: 'real-estate',
    name: 'Real Estate',
    value: 800000000,
    change: -0.5,
    changeAmount: -4000000,
    type: 'sector',
    children: [
      { id: 'PLD', name: 'Prologis', symbol: 'PLD', value: 200000000, change: -0.3, changeAmount: -600000, type: 'stock' },
    ]
  },
];

const generateMockPortfolioData = (): HeatMapNode[] => [
  { id: 'AAPL', name: 'Apple', symbol: 'AAPL', value: 25000, change: 1.8, changeAmount: 450, type: 'stock' },
  { id: 'MSFT', name: 'Microsoft', symbol: 'MSFT', value: 22000, change: 2.1, changeAmount: 462, type: 'stock' },
  { id: 'GOOGL', name: 'Alphabet', symbol: 'GOOGL', value: 18000, change: -0.5, changeAmount: -90, type: 'stock' },
  { id: 'NVDA', name: 'NVIDIA', symbol: 'NVDA', value: 15000, change: 4.5, changeAmount: 675, type: 'stock' },
  { id: 'AMZN', name: 'Amazon', symbol: 'AMZN', value: 12000, change: 2.0, changeAmount: 240, type: 'stock' },
  { id: 'META', name: 'Meta', symbol: 'META', value: 10000, change: 3.2, changeAmount: 320, type: 'stock' },
  { id: 'TSLA', name: 'Tesla', symbol: 'TSLA', value: 8000, change: -1.5, changeAmount: -120, type: 'stock' },
  { id: 'BRK.B', name: 'Berkshire', symbol: 'BRK.B', value: 6000, change: 0.3, changeAmount: 18, type: 'stock' },
];

const generateMockWatchlistData = (): HeatMapNode[] => [
  { id: 'AAPL', name: 'Apple', symbol: 'AAPL', value: 180, change: 1.8, changeAmount: 3.24, type: 'stock' },
  { id: 'GOOGL', name: 'Alphabet', symbol: 'GOOGL', value: 140, change: -0.5, changeAmount: -0.7, type: 'stock' },
  { id: 'MSFT', name: 'Microsoft', symbol: 'MSFT', value: 380, change: 2.1, changeAmount: 7.98, type: 'stock' },
  { id: 'AMZN', name: 'Amazon', symbol: 'AMZN', value: 175, change: 2.0, changeAmount: 3.5, type: 'stock' },
  { id: 'NVDA', name: 'NVIDIA', symbol: 'NVDA', value: 550, change: 4.5, changeAmount: 24.75, type: 'stock' },
  { id: 'TSLA', name: 'Tesla', symbol: 'TSLA', value: 250, change: -1.5, changeAmount: -3.75, type: 'stock' },
  { id: 'META', name: 'Meta', symbol: 'META', value: 480, change: 3.2, changeAmount: 15.36, type: 'stock' },
];

export const useHeatMapData = (view: HeatMapViewType): UseHeatMapDataResult => {
  const [data, setData] = useState<HeatMapNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      await new Promise(resolve => setTimeout(resolve, 500));

      let mockData: HeatMapNode[];
      switch (view) {
        case 'sp500':
          mockData = MOCK_HEATMAP_DATA;
          break;
        case 'portfolio':
          mockData = generateMockPortfolioData();
          break;
        case 'watchlist':
          mockData = generateMockWatchlistData();
          break;
        case 'nasdaq':
        case 'dow':
          mockData = MOCK_HEATMAP_DATA.slice(0, 4);
          break;
        default:
          mockData = MOCK_HEATMAP_DATA;
      }

      setData(mockData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch heat map data');
    } finally {
      setLoading(false);
    }
  }, [view]);

  useEffect(() => {
    fetchData();

    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return { data, loading, error, refresh: fetchData };
};
