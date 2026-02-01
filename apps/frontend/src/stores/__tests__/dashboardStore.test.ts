import { useDashboardStore } from '../dashboardStore';

describe('DashboardStore', () => {
  beforeEach(() => {
    localStorage.clear();
    useDashboardStore.setState({
      widgets: [],
      activeDashboard: 'Default',
      dashboards: ['Default'],
      isEditMode: false,
      isLoading: false,
    });
  });

  it('has default values', () => {
    const state = useDashboardStore.getState();
    expect(state.widgets).toEqual([]);
    expect(state.activeDashboard).toBe('Default');
    expect(state.dashboards).toEqual(['Default']);
    expect(state.isEditMode).toBe(false);
  });

  it('adds widget', () => {
    const { addWidget } = useDashboardStore.getState();
    const newWidget = {
      id: 'test-1',
      type: 'chart' as const,
      title: 'Test',
      size: 'medium' as const,
      position: { x: 0, y: 0 },
      config: {},
      visible: true,
    };
    addWidget(newWidget);
    const state = useDashboardStore.getState();
    expect(state.widgets).toHaveLength(1);
    expect(state.widgets[0].id).toBe('test-1');
  });

  it('deletes widget', () => {
    const { addWidget, deleteWidget } = useDashboardStore.getState();
    addWidget({
      id: 'widget-1',
      type: 'chart',
      title: 'Test',
      size: 'medium',
      position: { x: 0, y: 0 },
      config: {},
      visible: true,
    });
    deleteWidget('widget-1');
    const state = useDashboardStore.getState();
    expect(state.widgets).toHaveLength(0);
  });

  it('updates widget', () => {
    const { addWidget, updateWidget } = useDashboardStore.getState();
    addWidget({
      id: 'widget-1',
      type: 'chart',
      title: 'Original',
      size: 'medium',
      position: { x: 0, y: 0 },
      config: {},
      visible: true,
    });
    updateWidget('widget-1', { title: 'Updated' });
    const state = useDashboardStore.getState();
    expect(state.widgets[0].title).toBe('Updated');
  });

  it('creates new dashboard', () => {
    const { createDashboard } = useDashboardStore.getState();
    createDashboard('My Dashboard');
    const state = useDashboardStore.getState();
    expect(state.dashboards).toContain('Default');
    expect(state.dashboards).toContain('My Dashboard');
    expect(state.activeDashboard).toBe('My Dashboard');
  });

  it('switches dashboard', () => {
    const { createDashboard, switchDashboard } = useDashboardStore.getState();
    createDashboard('Test Dashboard');
    switchDashboard('Default');
    const state = useDashboardStore.getState();
    expect(state.activeDashboard).toBe('Default');
  });

  it('toggles edit mode', () => {
    const { setEditMode } = useDashboardStore.getState();
    setEditMode(true);
    expect(useDashboardStore.getState().isEditMode).toBe(true);
    setEditMode(false);
    expect(useDashboardStore.getState().isEditMode).toBe(false);
  });

  it('reorders widgets', () => {
    const { addWidget, reorderWidgets } = useDashboardStore.getState();
    addWidget({ id: 'w1', type: 'chart', title: 'W1', size: 'small', position: { x: 0, y: 0 }, config: {}, visible: true });
    addWidget({ id: 'w2', type: 'watchlist', title: 'W2', size: 'small', position: { x: 1, y: 0 }, config: {}, visible: true });
    reorderWidgets([useDashboardStore.getState().widgets[1], useDashboardStore.getState().widgets[0]]);
    const state = useDashboardStore.getState();
    expect(state.widgets[0].id).toBe('w2');
    expect(state.widgets[1].id).toBe('w1');
  });

  it('resets layout to defaults', () => {
    const { addWidget, resetLayout } = useDashboardStore.getState();
    addWidget({ id: 'custom', type: 'chart', title: 'Custom', size: 'small', position: { x: 0, y: 0 }, config: {}, visible: true });
    resetLayout();
    const state = useDashboardStore.getState();
    expect(state.widgets).toHaveLength(4);
  });
});
