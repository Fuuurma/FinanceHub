'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy,
} from '@dnd-kit/sortable';
import { Plus, Save, RotateCcw, Layout, MoreVertical, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { DashboardWidget } from './DashboardWidget';
import { WidgetLibrary } from './WidgetLibrary';
import { WidgetConfig, WidgetSize } from './types';
import { useDashboardStore } from '@/stores/dashboardStore';

export function DashboardLayout() {
  const {
    widgets,
    activeDashboard,
    dashboards,
    isEditMode,
    loadWidgets,
    addWidget,
    updateWidget,
    deleteWidget,
    reorderWidgets,
    setEditMode,
    createDashboard,
    switchDashboard,
    deleteDashboard,
    saveLayout,
  } = useDashboardStore();

  const [showLibrary, setShowLibrary] = useState(false);
  const [newDashboardName, setNewDashboardName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  useEffect(() => {
    loadWidgets();
  }, [activeDashboard]);

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;

      if (over && active.id !== over.id) {
        const oldIndex = widgets.findIndex((w) => w.id === active.id);
        const newIndex = widgets.findIndex((w) => w.id === over.id);
        const newWidgets = arrayMove(widgets, oldIndex, newIndex);
        reorderWidgets(newWidgets);
      }
    },
    [widgets, reorderWidgets]
  );

  const handleAddWidget = useCallback(
    (type: WidgetConfig['type'], title?: string) => {
      const newWidget: WidgetConfig = {
        id: `widget-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type,
        title: title || `${type.charAt(0).toUpperCase() + type.slice(1)} Widget`,
        size: 'medium',
        position: { x: 0, y: 0 },
        config: {},
        visible: true,
      };
      addWidget(newWidget);
      setShowLibrary(false);
    },
    [addWidget]
  );

  const handleResize = useCallback(
    (id: string, size: WidgetSize) => {
      updateWidget(id, { size });
    },
    [updateWidget]
  );

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    try {
      await saveLayout();
    } finally {
      setIsSaving(false);
    }
  }, [saveLayout]);

  const handleCreateDashboard = useCallback(() => {
    if (newDashboardName.trim()) {
      createDashboard(newDashboardName.trim());
      setNewDashboardName('');
      setIsDialogOpen(false);
    }
  }, [newDashboardName, createDashboard]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between p-4 border-b gap-4 flex-wrap">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Layout className="h-5 w-5" />
            <h1 className="text-xl font-semibold">{activeDashboard}</h1>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                {dashboards.map((name) => (
                  <DropdownMenuItem
                    key={name}
                    onClick={() => switchDashboard(name)}
                    className={name === activeDashboard ? 'bg-accent' : ''}
                  >
                    {name}
                  </DropdownMenuItem>
                ))}
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                  <DialogTrigger asChild>
                    <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
                      <Plus className="h-4 w-4 mr-2" />
                      New Dashboard
                    </DropdownMenuItem>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New Dashboard</DialogTitle>
                    </DialogHeader>
                    <div className="flex gap-2 pt-4">
                      <Input
                        placeholder="Dashboard name"
                        value={newDashboardName}
                        onChange={(e) => setNewDashboardName(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleCreateDashboard()}
                      />
                      <Button onClick={handleCreateDashboard}>Create</Button>
                    </div>
                  </DialogContent>
                </Dialog>
                {dashboards.length > 1 && (
                  <DropdownMenuItem
                    onSelect={(e) => e.preventDefault()}
                    className="text-destructive"
                  >
                    <Dialog>
                      <DialogTrigger asChild>
                        <div className="flex items-center w-full text-destructive">
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete Dashboard
                        </div>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Delete Dashboard</DialogTitle>
                        </DialogHeader>
                        <p className="py-4">
                          Are you sure you want to delete &ldquo;{activeDashboard}&rdquo;? This cannot be undone.
                        </p>
                        <div className="flex justify-end gap-2">
                          <Button variant="outline" onClick={() => {}}>
                            Cancel
                          </Button>
                          <Button
                            variant="destructive"
                            onClick={() => {
                              deleteDashboard(activeDashboard);
                            }}
                          >
                            Delete
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={isEditMode ? 'default' : 'outline'}
            size="sm"
            onClick={() => setEditMode(!isEditMode)}
          >
            {isEditMode ? 'Done Editing' : 'Edit Layout'}
          </Button>
          {isEditMode && (
            <>
              <Button variant="outline" size="sm" onClick={() => setShowLibrary(true)}>
                <Plus className="h-4 w-4 mr-1" />
                Add Widget
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadWidgets()}
              >
                <RotateCcw className="h-4 w-4 mr-1" />
                Reset
              </Button>
              <Button size="sm" onClick={handleSave} disabled={isSaving}>
                <Save className="h-4 w-4 mr-1" />
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="flex-1 p-4 overflow-auto">
        {widgets.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <Layout className="h-12 w-12 mb-4 opacity-50" />
            <p className="text-lg mb-2">No widgets yet</p>
            <p className="text-sm mb-4">Add widgets to customize your dashboard</p>
            <Button onClick={() => setShowLibrary(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Widget
            </Button>
          </div>
        ) : (
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <SortableContext
              items={widgets.map((w) => w.id)}
              strategy={rectSortingStrategy}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 auto-rows-min">
                {widgets.map((widget) => (
                  <DashboardWidget
                    key={widget.id}
                    config={widget}
                    onEdit={(id) => console.log('Edit widget:', id)}
                    onDelete={deleteWidget}
                    onResize={handleResize}
                    isEditMode={isEditMode}
                  />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        )}
      </div>

      {showLibrary && (
        <WidgetLibrary
          onSelect={(type, title) => handleAddWidget(type, title)}
          onClose={() => setShowLibrary(false)}
        />
      )}
    </div>
  );
}
