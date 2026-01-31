import { useState, useCallback } from 'react';
import { ExportFormat } from './ExportDropdown';

interface UseExportOptions {
  endpoint: string;
  filename?: string;
}

interface UseExportResult {
  exportData: (format: ExportFormat, params?: Record<string, string>) => Promise<void>;
  loading: boolean;
  error: string | null;
}

export function useExport({ endpoint, filename = 'export' }: UseExportOptions): UseExportResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportData = useCallback(
    async (format: ExportFormat, params?: Record<string, string>) => {
      setLoading(true);
      setError(null);

      try {
        const searchParams = new URLSearchParams(params);
        searchParams.set('format', format);

        const response = await fetch(`${endpoint}?${searchParams.toString()}`, {
          method: 'GET',
          headers: {
            Accept: 'application/octet-stream',
          },
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Export failed with status ${response.status}`);
        }

        const blob = await response.blob();

        const contentDisposition = response.headers.get('Content-Disposition');
        let downloadFilename = filename;
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="(.+)"/);
          if (match) {
            downloadFilename = match[1];
          }
        }

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = downloadFilename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Export failed';
        setError(errorMessage);
        console.error('Export error:', err);
      } finally {
        setLoading(false);
      }
    },
    [endpoint, filename]
  );

  return { exportData, loading, error };
}
