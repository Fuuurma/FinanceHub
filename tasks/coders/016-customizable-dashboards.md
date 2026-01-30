# C-016: Customizable Dashboards & Layouts

**Priority:** P1 - HIGH  
**Assigned to:** Frontend Coder  
**Estimated Time:** 14-18 hours  
**Dependencies:** C-005 (Frontend Completion)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement fully customizable dashboards with drag-and-drop widgets, layout persistence, and user preferences.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 10.1 - Customization):**

- Customizable dashboards
- Watchlists (multiple)
- Custom layouts save/load
- Dark/light mode
- Keyboard shortcuts
- Mobile responsive design

---

## ✅ CURRENT STATE

**What exists:**
- Basic dashboard layout
- Dark mode toggle
- Watchlist component

**What's missing:**
- Drag-and-drop widgets
- Layout persistence
- Multiple dashboard layouts
- Widget customization

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Dashboard Widget System** (5-6 hours)

**Create `apps/frontend/src/components/dashboard/DashboardWidget.tsx`:**

```typescript
import React, { useState } from 'react';
import { useDraggable } from '@dnd-kit/core';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

export interface WidgetConfig {
  id: string;
  type: 'chart' | 'watchlist' | 'portfolio' | 'news' | 'screener' | 'metrics';
  title: string;
  size: 'small' | 'medium' | 'large';
  position: { x: number; y: number };
  config: Record<string, any>;
}

export const DashboardWidget: React.FC<{
  config: WidgetConfig;
  onEdit: () => void;
  onDelete: () => void;
}> = ({ config, onEdit, onDelete }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id: config.id });
  
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };
  
  const renderWidgetContent = () => {
    switch (config.type) {
      case 'chart':
        return <AssetChart symbol={config.config.symbol} />;
      case 'watchlist':
        return <Watchlist items={config.config.items} />;
      case 'portfolio':
        return <PortfolioSummary portfolioId={config.config.portfolioId} />;
      case 'news':
        return <NewsFeed category={config.config.category} />;
      case 'screener':
        return <ScreenerResults filters={config.config.filters} />;
      case 'metrics':
        return <MarketMetrics />;
      default:
        return <div>Unknown widget type</div>;
    }
  };
  
  const getSizeClasses = () => {
    switch (config.size) {
      case 'small': return 'col-span-1 row-span-1';
      case 'medium': return 'col-span-2 row-span-2';
      case 'large': return 'col-span-3 row-span-3';
      default: return 'col-span-2 row-span-2';
    }
  };
  
  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`dashboard-widget ${getSizeClasses()}`}
      {...attributes}
    >
      <div className="widget-header" {...listeners}>
        <h3>{config.title}</h3>
        <div className="widget-actions">
          <button onClick={onEdit}>Edit</button>
          <button onClick={onDelete}>Delete</button>
        </div>
      </div>
      
      <div className="widget-content">
        {renderWidgetContent()}
      </div>
    </div>
  );
};
```

---

### **Phase 2: Dashboard Layout Manager** (4-5 hours)

**Create `apps/frontend/src/components/dashboard/DashboardLayout.tsx`:**

```typescript
import React, { useState, useEffect } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { DashboardWidget, WidgetConfig } from './DashboardWidget';
import { useDashboardStore } from '@/stores/dashboardStore';
import { WidgetLibrary } from './WidgetLibrary';

export const DashboardLayout: React.FC = () => {
  const { widgets, loadWidgets, addWidget, updateWidget, deleteWidget, reorderWidgets } = useDashboardStore();
  const [showLibrary, setShowLibrary] = useState(false);
  
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );
  
  useEffect(() => {
    loadWidgets();
  }, []);
  
  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    
    if (active.id !== over.id) {
      const oldIndex = widgets.findIndex(w => w.id === active.id);
      const newIndex = widgets.findIndex(w => w.id === over.id);
      reorderWidgets(arrayMove(widgets, oldIndex, newIndex));
    }
  };
  
  const handleAddWidget = (type: WidgetConfig['type']) => {
    const newWidget: WidgetConfig = {
      id: `widget-${Date.now()}`,
      type,
      title: `${type.charAt(0).toUpperCase() + type.slice(1)} Widget`,
      size: 'medium',
      position: { x: 0, y: 0 },
      config: {}
    };
    addWidget(newWidget);
    setShowLibrary(false);
  };
  
  const handleSaveLayout = async () => {
    await fetch('/api/dashboard/save/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ widgets })
    });
  };
  
  return (
    <div className="dashboard-layout">
      <div className="dashboard-toolbar">
        <h2>My Dashboard</h2>
        <div className="actions">
          <button onClick={() => setShowLibrary(true)}>+ Add Widget</button>
          <button onClick={handleSaveLayout}>Save Layout</button>
          <button onClick={() => loadWidgets()}>Reset</button>
        </div>
      </div>
      
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={widgets.map(w => w.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="widget-grid">
            {widgets.map(widget => (
              <DashboardWidget
                key={widget.id}
                config={widget}
                onEdit={() => {/* TODO */}}
                onDelete={() => deleteWidget(widget.id)}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
      
      {showLibrary && (
        <WidgetLibrary
          onSelect={handleAddWidget}
          onClose={() => setShowLibrary(false)}
        />
      )}
    </div>
  );
};
```

---

### **Phase 3: Dashboard State Management** (3-4 hours)

**Create `apps/frontend/src/stores/dashboardStore.ts`:**

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { WidgetConfig } from '@/components/dashboard/DashboardWidget';

interface DashboardState {
  widgets: WidgetConfig[];
  activeDashboard: string;
  dashboards: string[];
  
  loadWidgets: () => Promise<void>;
  addWidget: (widget: WidgetConfig) => void;
  updateWidget: (id: string, updates: Partial<WidgetConfig>) => void;
  deleteWidget: (id: string) => void;
  reorderWidgets: (widgets: WidgetConfig[]) => void;
  
  createDashboard: (name: string) => void;
  switchDashboard: (name: string) => void;
  deleteDashboard: (name: string) => void;
}

export const useDashboardStore = create<DashboardState>()(
  persist(
    (set, get) => ({
      widgets: [],
      activeDashboard: 'Default',
      dashboards: ['Default'],
      
      loadWidgets: async () => {
        try {
          const response = await fetch('/api/dashboard/widgets/');
          const data = await response.json();
          set({ widgets: data.widgets || [] });
        } catch (error) {
          console.error('Failed to load widgets:', error);
        }
      },
      
      addWidget: (widget) => {
        const { widgets } = get();
        set({ widgets: [...widgets, widget] });
      },
      
      updateWidget: (id, updates) => {
        const { widgets } = get();
        set({
          widgets: widgets.map(w =>
            w.id === id ? { ...w, ...updates } : w
          )
        });
      },
      
      deleteWidget: (id) => {
        const { widgets } = get();
        set({ widgets: widgets.filter(w => w.id !== id) });
      },
      
      reorderWidgets: (widgets) => {
        set({ widgets });
      },
      
      createDashboard: (name) => {
        const { dashboards } = get();
        set({ dashboards: [...dashboards, name] });
      },
      
      switchDashboard: (name) => {
        set({ activeDashboard: name });
        // Load widgets for this dashboard
        get().loadWidgets();
      },
      
      deleteDashboard: (name) => {
        const { dashboards, activeDashboard } = get();
        if (name === activeDashboard) {
          set({ activeDashboard: 'Default' });
        }
        set({ dashboards: dashboards.filter(d => d !== name) });
      }
    }),
    {
      name: 'dashboard-storage',
    }
  )
);
```

---

### **Phase 4: Backend API** (2-3 hours)

**Create `apps/backend/src/api/dashboard.py`:**

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from investments.models import DashboardLayout, DashboardWidget

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def dashboard_widgets(request):
    if request.method == 'GET':
        layout = DashboardLayout.objects.filter(
            user=request.user,
            name=request.GET.get('dashboard', 'Default')
        ).first()
        
        if layout:
            widgets = [{
                'id': w.widget_id,
                'type': w.widget_type,
                'title': w.title,
                'size': w.size,
                'position': {'x': w.position_x, 'y': w.position_y},
                'config': w.config
            } for w in layout.widgets.all()]
        else:
            widgets = []
        
        return Response({'widgets': widgets})
    
    elif request.method == 'POST':
        # Save layout
        layout, created = DashboardLayout.objects.get_or_create(
            user=request.user,
            name=request.data.get('dashboard', 'Default')
        )
        
        # Clear existing widgets
        layout.widgets.all().delete()
        
        # Add new widgets
        for widget_data in request.data.get('widgets', []):
            DashboardWidget.objects.create(
                layout=layout,
                widget_id=widget_data['id'],
                widget_type=widget_data['type'],
                title=widget_data['title'],
                size=widget_data['size'],
                position_x=widget_data['position']['x'],
                position_y=widget_data['position']['y'],
                config=widget_data.get('config', {})
            )
        
        return Response({'status': 'saved'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_dashboard(request):
    name = request.data.get('name')
    DashboardLayout.objects.create(user=request.user, name=name)
    return Response({'status': 'created', 'name': name})
```

---

### **Phase 5: Widget Library** (1-2 hours)

**Create `apps/frontend/src/components/dashboard/WidgetLibrary.tsx`:**

```typescript
import React from 'react';

const WIDGET_TYPES = [
  { type: 'chart', icon: '📈', description: 'Price chart for any asset' },
  { type: 'watchlist', icon: '⭐', description: 'Track your favorite assets' },
  { type: 'portfolio', icon: '💼', description: 'Portfolio overview' },
  { type: 'news', icon: '📰', description: 'Latest financial news' },
  { type: 'screener', icon: '🔍', description: 'Stock screening results' },
  { type: 'metrics', icon: '📊', description: 'Market metrics' },
];

export const WidgetLibrary: React.FC<{
  onSelect: (type: any) => void;
  onClose: () => void;
}> = ({ onSelect, onClose }) => {
  return (
    <div className="widget-library-overlay" onClick={onClose}>
      <div className="widget-library" onClick={e => e.stopPropagation()}>
        <div className="library-header">
          <h2>Add Widget</h2>
          <button onClick={onClose}>✕</button>
        </div>
        
        <div className="widget-grid">
          {WIDGET_TYPES.map(widget => (
            <div
              key={widget.type}
              className="widget-type-card"
              onClick={() => onSelect(widget.type as any)}
            >
              <div className="widget-icon">{widget.icon}</div>
              <h3>{widget.type}</h3>
              <p>{widget.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

---

## 📋 DELIVERABLES

- [ ] DashboardWidget component with drag-and-drop
- [ ] DashboardLayout with sortable widgets
- [ ] DashboardStore with persistence
- [ ] WidgetLibrary component
- [ ] Backend API for layout saving
- [ ] 6 widget types implemented
- [ ] Multiple dashboard support
- [ ] Tests

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Widgets can be dragged and reordered
- [ ] Layout persists across page reloads
- [ ] Multiple dashboards can be created
- [ ] 6 widget types available
- [ ] All tests passing
- [ ] Mobile responsive

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/016-customizable-dashboards.md
