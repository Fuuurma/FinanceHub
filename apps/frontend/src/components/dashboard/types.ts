export type WidgetType = 'chart' | 'watchlist' | 'portfolio' | 'news' | 'screener' | 'metrics' | 'positions' | 'performance';

export type WidgetSize = 'small' | 'medium' | 'large' | 'full';

export interface WidgetPosition {
  x: number;
  y: number;
}

export interface WidgetConfig {
  id: string;
  type: WidgetType;
  title: string;
  size: WidgetSize;
  position: WidgetPosition;
  config: Record<string, unknown>;
  visible: boolean;
}

export interface DashboardLayout {
  id: string;
  name: string;
  widgets: WidgetConfig[];
  isDefault: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface DashboardState {
  widgets: WidgetConfig[];
  activeDashboard: string;
  dashboards: string[];
  isEditMode: boolean;
}
