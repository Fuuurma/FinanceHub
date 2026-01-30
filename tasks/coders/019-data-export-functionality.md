# 🎯 TASK C-019: Data Export Functionality

**Created:** January 30, 2026
**Assigned To:** Backend + Frontend Coders
**Priority:** P1 - HIGH
**Estimated Time:** 8-12 hours
**Status:** ⏳ PENDING

---

## 📋 OVERVIEW

Implement comprehensive data export functionality allowing users to download:
- Historical price data (OHLCV)
- Portfolio performance data
- Holdings data
- Transaction history
- Screener results
- Analytics data

**Export Formats:** CSV, Excel (XLSX), JSON
**User Value:** Very High - Essential for analysis and reporting
**Complexity:** Medium
**Dependencies:** Backend APIs exist, need export endpoints

---

## 🎯 SUCCESS CRITERIA

### Backend:
- [x] Export API endpoints created for all data types
- [x] Support CSV, Excel, and JSON formats
- [x] Rate limiting on exports (prevent abuse)
- [x] Data validation and sanitization
- [x] Large dataset streaming (for memory efficiency)

### Frontend:
- [x] Export buttons on all relevant pages
- [x] Export format selector (CSV/Excel/JSON)
- [x] Date range selector for exports
- [x] Export progress indicators
- [x] Export history/logs

### User Experience:
- [x] One-click export from data tables
- [x] Customizable export columns
- [x] Export notifications when complete
- [x] Error handling for failed exports

---

## 📁 FILES TO CREATE/MODIFY

### Backend Files:

**1. Create Export Utilities**
```python
# apps/backend/src/utils/export/exporters.py

import csv
import json
from io import StringIO
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

class DataExporter:
    """Handle data export in multiple formats"""
    
    def __init__(self, data: List[Dict[str, Any]], columns: List[str] = None):
        self.data = data
        self.columns = columns or list(data[0].keys()) if data else []
    
    def to_csv(self) -> str:
        """Export data to CSV format"""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=self.columns)
        writer.writeheader()
        writer.writerows(self.data)
        return output.getvalue()
    
    def to_excel(self) -> bytes:
        """Export data to Excel format"""
        df = pd.DataFrame(self.data)
        if self.columns:
            df = df[self.columns]
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        return output.getvalue()
    
    def to_json(self) -> str:
        """Export data to JSON format"""
        return json.dumps(self.data, indent=2, default=str)
    
    @staticmethod
    def get_content_type(format: str) -> str:
        """Get content type for export format"""
        types = {
            'csv': 'text/csv',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'json': 'application/json'
        }
        return types.get(format, 'text/plain')
    
    @staticmethod
    def get_file_extension(format: str) -> str:
        """Get file extension for export format"""
        extensions = {
            'csv': '.csv',
            'excel': '.xlsx',
            'json': '.json'
        }
        return extensions.get(format, '.txt')
```

**2. Create Export API Endpoints**
```python
# apps/backend/src/api/exports.py

from ninja import Router
from django.http import HttpResponse
from django.contrib.auth.models import User
from ...utils.export.exporters import DataExporter
from ...investments.models import Asset, Portfolio, Transaction, AssetPricesHistoric

router = Router()
logger = logging.getLogger(__name__)

@router.get("/historical/{asset_id}")
def export_historical_data(
    request,
    asset_id: str,
    format: str = "csv",
    start_date: str = None,
    end_date: str = None
):
    """Export historical price data for an asset"""
    
    # Query data
    queryset = AssetPricesHistoric.objects.filter(asset_id=asset_id)
    
    if start_date:
        queryset = queryset.filter(timestamp__gte=start_date)
    if end_date:
        queryset = queryset.filter(timestamp__lte=end_date)
    
    data = list(queryset.values(
        'timestamp', 'open_price', 'high_price', 
        'low_price', 'close_price', 'volume'
    ).order_by('timestamp'))
    
    # Export
    exporter = DataExporter(data)
    
    if format == 'csv':
        content = exporter.to_csv()
    elif format == 'excel':
        content = exporter.to_excel()
    elif format == 'json':
        content = exporter.to_json()
    else:
        return {"error": "Invalid format"}, 400
    
    response = HttpResponse(
        content,
        content_type=DataExporter.get_content_type(format)
    )
    response['Content-Disposition'] = f'attachment; filename="historical_{asset_id}{DataExporter.get_file_extension(format)}"'
    
    return response

@router.get("/portfolio/{portfolio_id}")
def export_portfolio_data(
    request,
    portfolio_id: str,
    format: str = "csv",
    include_transactions: bool = False
):
    """Export portfolio holdings and optionally transactions"""
    
    portfolio = Portfolio.objects.get(id=portfolio_id, user=request.auth)
    
    # Get holdings
    holdings_data = []
    for position in portfolio.positions.all():
        holdings_data.append({
            'symbol': position.asset.symbol,
            'name': position.asset.name,
            'quantity': position.quantity,
            'average_cost': position.average_cost,
            'current_price': position.asset.current_price,
            'market_value': position.market_value,
            'unrealized_gain_loss': position.unrealized_gain_loss,
            'unrealized_gain_loss_percent': position.unrealized_gain_loss_percent
        })
    
    # Export
    exporter = DataExporter(holdings_data)
    content = exporter.to_csv() if format == 'csv' else exporter.to_excel()
    
    response = HttpResponse(
        content,
        content_type=DataExporter.get_content_type(format)
    )
    response['Content-Disposition'] = f'attachment; filename="portfolio_{portfolio_id}{DataExporter.get_file_extension(format)}"'
    
    return response

@router.get("/transactions/{portfolio_id}")
def export_transactions(
    request,
    portfolio_id: str,
    format: str = "csv",
    start_date: str = None,
    end_date: str = None
):
    """Export transaction history"""
    
    queryset = Transaction.objects.filter(portfolio_id=portfolio_id, portfolio__user=request.auth)
    
    if start_date:
        queryset = queryset.filter(transaction_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(transaction_date__lte=end_date)
    
    transactions_data = list(queryset.values(
        'transaction_date', 'asset__symbol', 'transaction_type',
        'quantity', 'price', 'total_value', 'notes'
    ).order_by('-transaction_date'))
    
    exporter = DataExporter(transactions_data)
    content = exporter.to_csv() if format == 'csv' else exporter.to_excel()
    
    response = HttpResponse(
        content,
        content_type=DataExporter.get_content_type(format)
    )
    response['Content-Disposition'] = f'attachment; filename="transactions_{portfolio_id}{DataExporter.get_file_extension(format)}"'
    
    return response

@router.get("/screener")
def export_screener_results(
    request,
    format: str = "csv",
    filters: dict = None
):
    """Export screener results"""
    
    # Apply filters and query assets
    # ... (screener logic)
    
    assets_data = list(queryset.values(
        'symbol', 'name', 'asset_type', 'exchange__code',
        'current_price', 'market_cap', 'pe_ratio', 'dividend_yield'
    ))
    
    exporter = DataExporter(assets_data)
    content = exporter.to_csv() if format == 'csv' else exporter.to_excel()
    
    response = HttpResponse(
        content,
        content_type=DataExporter.get_content_type(format)
    )
    response['Content-Disposition'] = f'attachment; filename="screener_results{DataExporter.get_file_extension(format)}"'
    
    return response
```

**3. Update URLs**
```python
# apps/backend/src/api/urls.py
from .exports import router as exports_router

api.add_router("/export", exports_router)
```

### Frontend Files:

**4. Create Export Hook**
```typescript
// apps/frontend/src/hooks/useDataExport.ts

import { useState } from 'react';

interface ExportOptions {
  format: 'csv' | 'excel' | 'json';
  startDate?: string;
  endDate?: string;
  includeTransactions?: boolean;
}

export const useDataExport = () => {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportData = async (
    type: 'historical' | 'portfolio' | 'transactions' | 'screener',
    id: string,
    options: ExportOptions
  ) => {
    setIsExporting(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        format: options.format,
        ...(options.startDate && { start_date: options.startDate }),
        ...(options.endDate && { end_date: options.endDate }),
        ...(options.includeTransactions && { include_transactions: 'true' }),
      });

      const response = await fetch(
        `/api/export/${type}/${id}?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) throw new Error('Export failed');

      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
      const filename = filenameMatch?.[1] || `export.${options.format}`;

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      return { success: true, filename };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setIsExporting(false);
    }
  };

  return { exportData, isExporting, error };
};
```

**5. Create Export Button Component**
```typescript
// apps/frontend/src/components/ui/ExportButton.tsx

import { Button } from './button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './dropdown-menu';
import { Download, FileSpreadsheet, FileJson } from 'lucide-react';
import { useDataExport } from '@/hooks/useDataExport';

interface ExportButtonProps {
  type: 'historical' | 'portfolio' | 'transactions' | 'screener';
  id: string;
  startDate?: string;
  endDate?: string;
  includeTransactions?: boolean;
}

export const ExportButton: React.FC<ExportButtonProps> = ({
  type,
  id,
  startDate,
  endDate,
  includeTransactions
}) => {
  const { exportData, isExporting } = useDataExport();

  const handleExport = async (format: 'csv' | 'excel' | 'json') => {
    await exportData(type, id, {
      format,
      startDate,
      endDate,
      includeTransactions,
    });
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" disabled={isExporting}>
          <Download className="mr-2 h-4 w-4" />
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => handleExport('csv')}>
          <FileSpreadsheet className="mr-2 h-4 w-4" />
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('excel')}>
          <FileSpreadsheet className="mr-2 h-4 w-4" />
          Export as Excel
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('json')}>
          <FileJson className="mr-2 h-4 w-4" />
          Export as JSON
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
```

**6. Add Export Buttons to Pages**

```typescript
// apps/frontend/src/app/(dashboard)/portfolios/page.tsx
// Add export button to portfolio view

<ExportButton
  type="portfolio"
  id={portfolioId}
  includeTransactions={false}
/>

// For transaction history
<ExportButton
  type="transactions"
  id={portfolioId}
  startDate={startDate}
  endDate={endDate}
/>

// apps/frontend/src/app/(dashboard)/screener/page.tsx
// Add export button to screener results

<ExportButton
  type="screener"
  id={screenerId}
/>

// apps/frontend/src/app/(dashboard)/assets/[assetId]/page.tsx
// Add export button to asset details

<ExportButton
  type="historical"
  id={assetId}
  startDate={startDate}
  endDate={endDate}
/>
```

---

## 🔧 IMPLEMENTATION STEPS

### Phase 1: Backend (4-5 hours)
1. Create `DataExporter` utility class
2. Create export API endpoints
3. Add rate limiting (use existing C-008 rate limiter)
4. Test exports with various data sizes
5. Test all three formats (CSV, Excel, JSON)

### Phase 2: Frontend Hook (1-2 hours)
1. Create `useDataExport` hook
2. Handle file downloads
3. Add error handling
4. Add loading states

### Phase 3: UI Components (2-3 hours)
1. Create `ExportButton` component
2. Add export buttons to portfolio pages
3. Add export buttons to screener page
4. Add export buttons to asset detail pages
5. Style buttons to match design system

### Phase 4: Integration & Testing (1-2 hours)
1. Test exports from all pages
2. Test large datasets (10K+ rows)
3. Test rate limiting
4. Test with different date ranges
5. Test format compatibility (open in Excel, etc.)

---

## 🧪 TESTING CHECKLIST

### Backend Tests:
- [ ] CSV export produces valid CSV
- [ ] Excel export produces valid XLSX
- [ ] JSON export produces valid JSON
- [ ] Large exports (>1MB) handled without memory issues
- [ ] Rate limiting enforced
- [ ] User cannot export other users' data
- [ ] Date filters work correctly
- [ ] Empty datasets handled gracefully

### Frontend Tests:
- [ ] Export button triggers download
- [ ] File has correct name and extension
- [ ] Downloaded file opens correctly in Excel/Numbers
- [ ] Loading state shown during export
- [ ] Error message shown on failure
- [ ] Multiple exports can be queued

### E2E Tests:
- [ ] User exports portfolio holdings as Excel
- [ ] User exports transaction history with date range
- [ ] User exports screener results as CSV
- [ ] User exports historical data as JSON
- [ ] Exported data matches screen data

---

## 📊 API SPECIFICATION

### GET /api/export/historical/{asset_id}
**Query Parameters:**
- `format`: csv | excel | json (default: csv)
- `start_date`: ISO date string (optional)
- `end_date`: ISO date string (optional)

**Response:** File download with appropriate Content-Type

### GET /api/export/portfolio/{portfolio_id}
**Query Parameters:**
- `format`: csv | excel | json (default: csv)
- `include_transactions`: boolean (default: false)

**Response:** File download

---

## 📦 DEPENDENCIES

### Backend:
```bash
pip install openpyxl pandas xlsxwriter
```

### Frontend:
```bash
npm install lucide-react
```

---

## 🚀 FUTURE ENHANCEMENTS

**Phase 2:**
- PDF export for reports (task C-037)
- Scheduled exports (email reports)
- Export history/logs
- Export templates
- Bulk exports
- API-based export (webhook delivery)

---

## 🎯 PRIORITY RATIONALE

**Why P1 (HIGH):**
- Very high user value (essential for analysis)
- Medium implementation complexity
- Builds on existing backend APIs
- No external API dependencies
- Reusable across multiple pages

**User Impact:** 10/10 - Critical feature for serious users
**Dev Effort:** 5/10 - Standard export functionality
**Risk:** 3/10 - Low risk, well-understood pattern

---

**Task created by GAUDÍ (Architect)**
**Ready for assignment to Backend + Frontend Coders**
**Part of Data Export Suite**
