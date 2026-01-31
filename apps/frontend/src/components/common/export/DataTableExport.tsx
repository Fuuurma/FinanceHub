'use client';

import React from 'react';
import { Download, Calendar, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ExportDropdown, ExportFormat } from './ExportDropdown';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface DataTableExportProps {
  onExport: (format: ExportFormat, options: ExportOptions) => Promise<void>;
  disabled?: boolean;
  showDateRange?: boolean;
  showFilters?: boolean;
  className?: string;
}

interface ExportOptions {
  startDate?: Date;
  endDate?: Date;
  filters?: Record<string, string>;
}

export function DataTableExport({
  onExport,
  disabled = false,
  showDateRange = true,
  showFilters = false,
  className,
}: DataTableExportProps) {
  const [startDate, setStartDate] = React.useState<Date | undefined>();
  const [endDate, setEndDate] = React.useState<Date | undefined>();
  const [filters, setFilters] = React.useState<Record<string, string>>({});

  const handleExport = async (format: ExportFormat) => {
    await onExport(format, {
      startDate,
      endDate,
      filters,
    });
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <ExportDropdown
        onExport={handleExport}
        disabled={disabled}
        buttonText="Export Data"
      />

      {showDateRange && (
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline" size="sm" disabled={disabled}>
              <Calendar className="h-4 w-4 mr-2" />
              {startDate || endDate ? (
                <>
                  {startDate ? new Date(startDate).toLocaleDateString() : 'Start'}
                  {' - '}
                  {endDate ? new Date(endDate).toLocaleDateString() : 'End'}
                </>
              ) : (
                'Date Range'
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-4" align="end">
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Start Date</Label>
                  <CalendarComponent
                    mode="single"
                    selected={startDate}
                    onSelect={setStartDate}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label>End Date</Label>
                  <CalendarComponent
                    mode="single"
                    selected={endDate}
                    onSelect={setEndDate}
                    className="mt-2"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" size="sm" onClick={() => { setStartDate(undefined); setEndDate(undefined); }}>
                  Clear
                </Button>
              </div>
            </div>
          </PopoverContent>
        </Popover>
      )}

      {showFilters && (
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline" size="sm" disabled={disabled}>
              <Filter className="h-4 w-4 mr-2" />
              Filters
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-72" align="end">
            <div className="space-y-4">
              <div>
                <Label>Symbol</Label>
                <Input
                  placeholder="e.g., AAPL"
                  value={filters.symbol || ''}
                  onChange={(e) => setFilters({ ...filters, symbol: e.target.value })}
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Transaction Type</Label>
                <Input
                  placeholder="e.g., BUY, SELL"
                  value={filters.type || ''}
                  onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                  className="mt-1"
                />
              </div>
            </div>
          </PopoverContent>
        </Popover>
      )}
    </div>
  );
}
