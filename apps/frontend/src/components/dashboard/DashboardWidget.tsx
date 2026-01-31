'use client';

import React from 'react';
import {
  useSortable,
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { X, Maximize2, Minimize2, Settings, GripVertical } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { WidgetConfig, WidgetType } from './types';

interface DashboardWidgetProps {
  config: WidgetConfig;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
  onResize?: (id: string, size: WidgetConfig['size']) => void;
  isEditMode?: boolean;
}

const WIDGET_COMPONENTS: Record<WidgetType, React.FC<{ config: WidgetConfig }>> = {
  chart: ({ config }) => <div className="p-4 text-muted-foreground">Chart Widget</div>,
  watchlist: ({ config }) => <div className="p-4 text-muted-foreground">Watchlist Widget</div>,
  portfolio: ({ config }) => <div className="p-4 text-muted-foreground">Portfolio Widget</div>,
  news: ({ config }) => <div className="p-4 text-muted-foreground">News Widget</div>,
  screener: ({ config }) => <div className="p-4 text-muted-foreground">Screener Widget</div>,
  metrics: ({ config }) => <div className="p-4 text-muted-foreground">Metrics Widget</div>,
  positions: ({ config }) => <div className="p-4 text-muted-foreground">Positions Widget</div>,
  performance: ({ config }) => <div className="p-4 text-muted-foreground">Performance Widget</div>,
};

const SIZE_CLASSES: Record<WidgetConfig['size'], string> = {
  small: 'col-span-1 row-span-1',
  medium: 'col-span-1 md:col-span-2 row-span-1',
  large: 'col-span-1 md:col-span-2 row-span-2',
  full: 'col-span-full row-span-2',
};

const SIZE_LABELS: Record<WidgetConfig['size'], string> = {
  small: 'S',
  medium: 'M',
  large: 'L',
  full: 'F',
};

export function DashboardWidget({
  config,
  onEdit,
  onDelete,
  onResize,
  isEditMode = false,
}: DashboardWidgetProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: config.id, disabled: !isEditMode });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const [isMaximized, setIsMaximized] = React.useState(false);
  const [showSizeMenu, setShowSizeMenu] = React.useState(false);

  const WidgetComponent = WIDGET_COMPONENTS[config.type];

  const toggleSize = () => {
    const sizes: WidgetConfig['size'][] = ['small', 'medium', 'large', 'full'];
    const currentIndex = sizes.indexOf(config.size);
    const nextIndex = (currentIndex + 1) % sizes.length;
    onResize?.(config.id, sizes[nextIndex]);
  };

  if (isMaximized) {
    return (
      <div className="fixed inset-4 z-50 bg-background border rounded-lg shadow-lg">
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            {isEditMode && (
              <div {...attributes} {...listeners} className="cursor-grab">
                <GripVertical className="h-4 w-4 text-muted-foreground" />
              </div>
            )}
            <h3 className="font-semibold">{config.title}</h3>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={toggleSize}>
              <Minimize2 className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => setIsMaximized(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div className="p-4 overflow-auto h-[calc(100%-60px)]">
          <WidgetComponent config={config} />
        </div>
      </div>
    );
  }

  return (
    <Card
      ref={setNodeRef}
      style={style}
      className={`
        ${SIZE_CLASSES[config.size]}
        ${isDragging ? 'opacity-50 ring-2 ring-primary' : ''}
        transition-shadow hover:shadow-md
        flex flex-col overflow-hidden
      `}
    >
      <CardHeader className="p-3 pb-0 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 min-w-0">
            {isEditMode && (
              <div {...attributes} {...listeners} className="cursor-grab flex-shrink-0">
                <GripVertical className="h-4 w-4 text-muted-foreground" />
              </div>
            )}
            <CardTitle className="text-sm font-medium truncate">
              {config.title}
            </CardTitle>
          </div>
          <div className="flex items-center gap-1 flex-shrink-0">
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={() => setIsMaximized(true)}
            >
              <Maximize2 className="h-3 w-3" />
            </Button>
            {isEditMode && (
              <>
                <div className="relative">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    onClick={() => setShowSizeMenu(!showSizeMenu)}
                  >
                    <Settings className="h-3 w-3" />
                  </Button>
                  {showSizeMenu && (
                    <div className="absolute right-0 top-full mt-1 bg-popover border rounded-lg shadow-lg p-1 z-10">
                      {(['small', 'medium', 'large', 'full'] as const).map((size) => (
                        <Button
                          key={size}
                          variant={config.size === size ? 'secondary' : 'ghost'}
                          size="sm"
                          className="w-full justify-start text-xs"
                          onClick={() => {
                            onResize?.(config.id, size);
                            setShowSizeMenu(false);
                          }}
                        >
                          {SIZE_LABELS[size]} - {size}
                        </Button>
                      ))}
                    </div>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 text-destructive hover:text-destructive"
                  onClick={() => onDelete(config.id)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-3 flex-1 overflow-auto">
        <WidgetComponent config={config} />
      </CardContent>
    </Card>
  );
}
