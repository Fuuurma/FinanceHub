'use client';

import React, { useState } from 'react';
import { X, BarChart3, Star, Briefcase, Newspaper, Search, TrendingUp, PieChart, LayoutGrid } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { WidgetType } from './types';

interface WidgetLibraryProps {
  onSelect: (type: WidgetType, title?: string) => void;
  onClose: () => void;
}

interface WidgetOption {
  type: WidgetType;
  title: string;
  description: string;
  icon: React.ReactNode;
  defaultTitle?: string;
}

const WIDGET_OPTIONS: WidgetOption[] = [
  {
    type: 'chart',
    title: 'Price Chart',
    description: 'Interactive price chart for any asset',
    icon: <BarChart3 className="h-6 w-6" />,
    defaultTitle: 'Price Chart',
  },
  {
    type: 'watchlist',
    title: 'Watchlist',
    description: 'Track your favorite assets',
    icon: <Star className="h-6 w-6" />,
    defaultTitle: 'My Watchlist',
  },
  {
    type: 'portfolio',
    title: 'Portfolio',
    description: 'Portfolio overview and holdings',
    icon: <Briefcase className="h-6 w-6" />,
    defaultTitle: 'Portfolio',
  },
  {
    type: 'positions',
    title: 'Positions',
    description: 'Open positions and P&L',
    icon: <LayoutGrid className="h-6 w-6" />,
    defaultTitle: 'Positions',
  },
  {
    type: 'news',
    title: 'News Feed',
    description: 'Latest financial news',
    icon: <Newspaper className="h-6 w-6" />,
    defaultTitle: 'News',
  },
  {
    type: 'screener',
    title: 'Screener',
    description: 'Stock screening results',
    icon: <Search className="h-6 w-6" />,
    defaultTitle: 'Screener Results',
  },
  {
    type: 'performance',
    title: 'Performance',
    description: 'Performance metrics and charts',
    icon: <TrendingUp className="h-6 w-6" />,
    defaultTitle: 'Performance',
  },
  {
    type: 'metrics',
    title: 'Market Metrics',
    description: 'Key market indicators',
    icon: <PieChart className="h-6 w-6" />,
    defaultTitle: 'Market Metrics',
  },
];

export function WidgetLibrary({ onSelect, onClose }: WidgetLibraryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [customTitle, setCustomTitle] = useState('');
  const [selectedType, setSelectedType] = useState<WidgetType | null>(null);

  const filteredWidgets = WIDGET_OPTIONS.filter(
    (widget) =>
      widget.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      widget.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAdd = () => {
    if (selectedType !== null) {
      const widget = WIDGET_OPTIONS.find((w) => w.type === selectedType);
      onSelect(selectedType, customTitle || widget?.defaultTitle);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div
        className="bg-background rounded-lg shadow-lg w-full max-w-2xl max-h-[80vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Add Widget</h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="p-4 border-b">
          <Input
            placeholder="Search widgets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full"
          />
        </div>

        <div className="p-4 overflow-auto max-h-[50vh]">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {filteredWidgets.map((widget) => (
              <button
                key={widget.type}
                className={`
                  flex flex-col items-start p-4 rounded-lg border text-left transition-colors
                  ${
                    selectedType === widget.type
                      ? 'border-primary bg-primary/5'
                      : 'hover:bg-muted'
                  }
                `}
                onClick={() => setSelectedType(widget.type)}
              >
                <div className="mb-2 text-muted-foreground">{widget.icon}</div>
                <h3 className="font-medium text-sm">{widget.title}</h3>
                <p className="text-xs text-muted-foreground mt-1">{widget.description}</p>
              </button>
            ))}
          </div>
        </div>

        {selectedType && (
          <div className="p-4 border-t bg-muted/30">
            <Input
              placeholder={`Custom title (optional)`}
              value={customTitle}
              onChange={(e) => setCustomTitle(e.target.value)}
              className="w-full mb-4"
            />
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button onClick={handleAdd}>
                Add Widget
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
