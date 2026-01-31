export interface HeatMapNode {
  id: string;
  name: string;
  value: number;
  change: number;
  changeAmount: number;
  children?: HeatMapNode[];
  type: 'sector' | 'stock' | 'asset';
  symbol?: string;
}

export interface HeatMapView {
  id: string;
  name: string;
  type: 'market' | 'portfolio' | 'watchlist';
  data: HeatMapNode[];
}

export interface HeatMapConfig {
  colorScheme: 'green-red' | 'blue-orange' | 'custom';
  sizeMetric: 'market_cap' | 'allocation' | 'equal';
  showLabels: boolean;
  showValues: boolean;
  groupBy: 'sector' | 'industry' | 'asset_class';
}

export interface HeatMapLayoutNode {
  node: HeatMapNode;
  x: number;
  y: number;
  width: number;
  height: number;
}

export type HeatMapViewType = 'sp500' | 'nasdaq' | 'dow' | 'portfolio' | 'watchlist';
