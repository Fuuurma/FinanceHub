'use client';

import React, { useState } from 'react';
import { Download, FileSpreadsheet, FileText, FileJson, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

export type ExportFormat = 'csv' | 'excel' | 'json';

interface ExportDropdownProps {
  onExport: (format: ExportFormat) => Promise<void>;
  disabled?: boolean;
  filename?: string;
  className?: string;
  buttonText?: string;
  buttonVariant?: 'default' | 'outline' | 'ghost' | 'destructive' | 'secondary' | 'link';
}

const EXPORT_OPTIONS: { format: ExportFormat; label: string; icon: React.ReactNode; extension: string }[] = [
  { format: 'csv', label: 'CSV', icon: <FileText className="h-4 w-4" />, extension: '.csv' },
  { format: 'excel', label: 'Excel', icon: <FileSpreadsheet className="h-4 w-4" />, extension: '.xlsx' },
  { format: 'json', label: 'JSON', icon: <FileJson className="h-4 w-4" />, extension: '.json' },
];

export function ExportDropdown({
  onExport,
  disabled = false,
  filename = 'export',
  className,
  buttonText = 'Export',
  buttonVariant = 'outline',
}: ExportDropdownProps) {
  const [exporting, setExporting] = useState<ExportFormat | null>(null);

  const handleExport = async (format: ExportFormat) => {
    setExporting(format);
    try {
      await onExport(format);
    } finally {
      setExporting(null);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant={buttonVariant}
          disabled={disabled || exporting !== null}
          className={cn('gap-2', className)}
        >
          {exporting ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Download className="h-4 w-4" />
          )}
          {exporting ? `Exporting ${exporting.toUpperCase()}...` : buttonText}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuSeparator />
        {EXPORT_OPTIONS.map((option) => (
          <DropdownMenuItem
            key={option.format}
            onClick={() => handleExport(option.format)}
            disabled={exporting !== null}
            className="gap-2"
          >
            {option.icon}
            <span>{option.label}</span>
            <span className="ml-auto text-xs text-muted-foreground">
              {option.extension}
            </span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
