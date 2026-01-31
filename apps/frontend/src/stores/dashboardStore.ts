import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { WidgetConfig } from '@/components/dashboard/types';

interface DashboardStoreState {
  widgets: WidgetConfig[];
  activeDashboard: string;
  dashboards: string[];
  isEditMode: boolean;
  isLoading: boolean;

  loadWidgets: () => Promise<void>;
  addWidget: (widget: WidgetConfig) => void;
  updateWidget: (id: string, updates: Partial<WidgetConfig>) => void;
  deleteWidget: (id: string) => void;
  reorderWidgets: (widgets: WidgetConfig[]) => void;
  setWidgets: (widgets: WidgetConfig[]) => void;

  createDashboard: (name: string) => void;
  switchDashboard: (name: string) => void;
  deleteDashboard: (name: string) => void;

  setEditMode: (isEdit: boolean) => void;
  saveLayout: () => Promise<void>;
  resetLayout: () => void;
}

const DEFAULT_WIDGETS: WidgetConfig[] = [
  {
    id: 'widget-1',
    type: 'portfolio',
    title: 'Portfolio',
    size: 'large',
    position: { x: 0, y: 0 },
    config: {},
    visible: true,
  },
  {
    id: 'widget-2',
    type: 'watchlist',
    title: 'Watchlist',
    size: 'medium',
    position: { x: 1, y: 0 },
    config: {},
    visible: true,
  },
  {
    id: 'widget-3',
    type: 'chart',
    title: 'Market Chart',
    size: 'large',
    position: { x: 0, y: 1 },
    config: {},
    visible: true,
  },
  {
    id: 'widget-4',
    type: 'news',
    title: 'News',
    size: 'medium',
    position: { x: 2, y: 1 },
    config: {},
    visible: true,
  },
];

export const useDashboardStore = create<DashboardStoreState>()(
  persist(
    (set, get) => ({
      widgets: [],
      activeDashboard: 'Default',
      dashboards: ['Default'],
      isEditMode: false,
      isLoading: false,

      loadWidgets: async () => {
        set({ isLoading: true });
        try {
          const response = await fetch('/api/dashboard/widgets/');
          if (response.ok) {
            const data = await response.json();
            set({ widgets: data.widgets || [] });
          }
        } catch (error) {
          console.error('Failed to load widgets:', error);
        } finally {
          set({ isLoading: false });
        }
      },

      addWidget: (widget) => {
        set((state) => ({
          widgets: [...state.widgets, widget],
        }));
      },

      updateWidget: (id, updates) => {
        set((state) => ({
          widgets: state.widgets.map((w) =>
            w.id === id ? { ...w, ...updates } : w
          ),
        }));
      },

      deleteWidget: (id) => {
        set((state) => ({
          widgets: state.widgets.filter((w) => w.id !== id),
        }));
      },

      reorderWidgets: (widgets) => {
        set({ widgets });
      },

      setWidgets: (widgets) => {
        set({ widgets });
      },

      createDashboard: (name) => {
        const { dashboards } = get();
        if (!dashboards.includes(name)) {
          set({
            dashboards: [...dashboards, name],
            activeDashboard: name,
            widgets: [],
          });
        }
      },

      switchDashboard: (name) => {
        const { dashboards } = get();
        if (dashboards.includes(name)) {
          set({ activeDashboard: name, widgets: [] });
          get().loadWidgets();
        }
      },

      deleteDashboard: (name) => {
        const { dashboards, activeDashboard } = get();
        if (dashboards.length > 1 && dashboards.includes(name)) {
          const newDashboards = dashboards.filter((d) => d !== name);
          set({
            dashboards: newDashboards,
            activeDashboard:
              activeDashboard === name ? newDashboards[0] : activeDashboard,
            widgets: activeDashboard === name ? [] : get().widgets,
          });
        }
      },

      setEditMode: (isEdit) => {
        set({ isEditMode: isEdit });
      },

      saveLayout: async () => {
        const { widgets, activeDashboard } = get();
        try {
          const response = await fetch('/api/dashboard/save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              dashboard: activeDashboard,
              widgets,
            }),
          });
          if (!response.ok) {
            throw new Error('Failed to save');
          }
        } catch (error) {
          console.error('Failed to save layout:', error);
          throw error;
        }
      },

      resetLayout: () => {
        set({ widgets: DEFAULT_WIDGETS });
      },
    }),
    {
      name: 'dashboard-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        activeDashboard: state.activeDashboard,
        dashboards: state.dashboards,
      }),
    }
  )
);
