"""
Data Export Utilities
Export data in CSV, Excel, and JSON formats.
"""

import csv
import json
import logging
from io import BytesIO, StringIO
from datetime import datetime
from typing import List, Dict, Any, Optional, TypeVar, Generic
from dataclasses import dataclass

logger = logging.getLogger(__name__)

ExportFormat = TypeVar('ExportFormat', str, 'csv' | 'excel' | 'json')


@dataclass
class ExportConfig:
    """Configuration for data export."""
    format: str = 'csv'
    columns: Optional[List[str]] = None
    filename: Optional[str] = None
    date_format: str = '%Y-%m-%d'
    datetime_format: str = '%Y-%m-%d %H:%M:%S'
    include_metadata: bool = True


class DataExporter:
    """Handle data export in multiple formats."""

    SUPPORTED_FORMATS = ['csv', 'excel', 'json']

    CONTENT_TYPES = {
        'csv': 'text/csv; charset=utf-8',
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'json': 'application/json; charset=utf-8',
    }

    FILE_EXTENSIONS = {
        'csv': '.csv',
        'excel': '.xlsx',
        'json': '.json',
    }

    def __init__(self, data: List[Dict[str, Any]], config: Optional[ExportConfig] = None):
        self.data = data
        self.config = config or ExportConfig()

        if not self.data:
            self.columns = []
        elif self.config.columns:
            self.columns = self.config.columns
        else:
            self.columns = list(self.data[0].keys()) if self.data else []

    def to_csv(self) -> str:
        """Export data to CSV format."""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=self.columns, extrasaction='ignore')
        writer.writeheader()

        for row in self.data:
            cleaned_row = self._clean_row(row)
            writer.writerow(cleaned_row)

        return output.getvalue()

    def to_excel(self) -> bytes:
        """Export data to Excel format."""
        try:
            import pandas as pd

            df = pd.DataFrame(self.data)

            if self.config.columns:
                existing_cols = [c for c in self.config.columns if c in df.columns]
                df = df[existing_cols]

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data', startrow=1)

                worksheet = writer.sheets['Data']

                if self.config.include_metadata:
                    worksheet['A1'] = f'Generated: {datetime.now().strftime(self.config.datetime_format)}'

            return output.getvalue()
        except ImportError:
            logger.warning('pandas not available, falling back to CSV')
            return self.to_csv().encode('utf-8')

    def to_json(self) -> str:
        """Export data to JSON format."""
        cleaned_data = [self._clean_row(row) for row in self.data]

        return json.dumps(
            cleaned_data,
            indent=2,
            default=self._json_default,
            ensure_ascii=False
        )

    def _clean_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Clean row values for export."""
        cleaned = {}
        for key, value in row.items():
            if key not in self.columns and self.columns:
                continue

            if isinstance(value, datetime):
                cleaned[key] = value.strftime(self.config.datetime_format)
            elif isinstance(value, bytes):
                cleaned[key] = value.decode('utf-8', errors='ignore')
            elif value is None:
                cleaned[key] = ''
            else:
                cleaned[key] = value

        return cleaned

    def _json_default(self, obj: Any) -> str:
        """Default handler for JSON serialization."""
        if isinstance(obj, datetime):
            return obj.strftime(self.config.datetime_format)
        return str(obj)

    def get_content_type(self) -> str:
        """Get content type for export format."""
        return self.CONTENT_TYPES.get(self.config.format, 'text/plain')

    def get_file_extension(self) -> str:
        """Get file extension for export format."""
        return self.FILE_EXTENSIONS.get(self.config.format, '.txt')

    def get_filename(self, base_name: str = 'export') -> str:
        """Get full filename for export."""
        if self.config.filename:
            base = self.config.filename
        else:
            base = base_name

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base}_{timestamp}{self.get_file_extension()}"

    def get_content_disposition(self, base_name: str = 'export') -> str:
        """Get Content-Disposition header for download."""
        filename = self.get_filename(base_name)
        return f'attachment; filename="{filename}"'

    def export(self, base_name: str = 'export') -> tuple[str, str, bytes]:
        """Export data in the configured format."""
        format_lower = self.config.format.lower()

        if format_lower == 'excel':
            content = self.to_excel()
            if isinstance(content, str):
                content = content.encode('utf-8')
        elif format_lower == 'json':
            content = self.to_json().encode('utf-8')
        else:
            content = self.to_csv().encode('utf-8')

        return (
            self.get_content_type(),
            self.get_content_disposition(base_name),
            content
        )


class StreamingDataExporter:
    """Export large datasets using streaming for memory efficiency."""

    def __init__(self, queryset, fields: List[str], batch_size: int = 1000):
        self.queryset = queryset
        self.fields = fields
        self.batch_size = batch_size

    def stream_csv(self) -> str:
        """Stream CSV output for large datasets."""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=self.fields, extrasaction='ignore')
        writer.writeheader()

        for obj in self.queryset.iterator(batch_size=self.batch_size):
            row = {}
            for field in self.fields:
                value = getattr(obj, field, None)
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                row[field] = value
            writer.writerow(row)

        return output.getvalue()


def export_queryset(
    queryset,
    fields: List[str],
    format: str = 'csv',
    filename: str = 'export'
) -> tuple[str, str, bytes]:
    """Quick export for a Django queryset."""
    data = []
    for obj in queryset.values(*fields):
        data.append(obj)

    config = ExportConfig(format=format, columns=fields, filename=filename)
    exporter = DataExporter(data, config)
    return exporter.export(filename)
