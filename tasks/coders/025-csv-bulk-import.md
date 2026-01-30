# 🎯 TASK C-025: CSV Bulk Import for Portfolios

**Created:** January 30, 2026
**Assigned To:** Backend + Frontend Coders
**Priority:** P1 - HIGH
**Estimated Time:** 6-8 hours
**Status:** ⏳ PENDING

---

## 📋 OVERVIEW

Implement CSV bulk import functionality allowing users to:
- Import multiple transactions at once
- Import portfolio holdings from other platforms
- Validate imported data before saving
- Preview import before committing
- Handle common CSV formats (brokerage exports)

**User Value:** Very High - Saves hours of manual entry
**Complexity:** Medium
**Dependencies:** Portfolio/transaction models exist

---

## 🎯 SUCCESS CRITERIA

### Backend:
- [x] CSV parsing endpoint created
- [x] Supports multiple CSV formats
- [x] Data validation and error reporting
- [x] Import preview (don't save until confirmed)
- [x] Duplicate detection
- [x] Batch transaction creation

### Frontend:
- [x] CSV upload component with drag-drop
- [x] Format selector (brokerage templates)
- [x] Preview table (show what will be imported)
- [x] Validation errors display
- [x] Confirm/cancel import
- [x] Import progress indicator
- [x] Download CSV template

### User Experience:
- [x] User can download template CSV
- [x] User fills template with their data
- [x] User uploads CSV
- [x] System validates and shows preview
- [x] User confirms import
- [x] Transactions added to portfolio
- [x] Clear error messages for invalid data

---

## 📁 FILES TO CREATE/MODIFY

### Backend Files:

**1. Create CSV Import Utilities**
```python
# apps/backend/src/utils/import/csv_parser.py

import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Tuple
from django.utils.dateparse import parse_date

class CSVImportParser:
    """Parse and validate CSV imports for portfolios"""
    
    # Supported CSV formats
    FORMAT_TEMPLATES = {
        'generic': {
            'required_columns': ['date', 'symbol', 'type', 'quantity', 'price'],
            'optional_columns': ['notes', 'commission'],
            'column_mapping': {
                'date': 'transaction_date',
                'symbol': 'asset_symbol',
                'type': 'transaction_type',
                'quantity': 'quantity',
                'price': 'price_per_share',
                'notes': 'notes',
                'commission': 'commission'
            }
        },
        'schwab': {
            'required_columns': ['Date', 'Action', 'Symbol', 'Quantity', 'Price'],
            'optional_columns': ['Description', 'Commission'],
            'column_mapping': {
                'Date': 'transaction_date',
                'Action': 'transaction_type',
                'Symbol': 'asset_symbol',
                'Quantity': 'quantity',
                'Price': 'price_per_share',
                'Description': 'notes',
                'Commission': 'commission'
            }
        },
        'fidelity': {
            'required_columns': ['Run Date', 'Action', 'Symbol', 'Quantity', 'Price'],
            'optional_columns': ['Description', 'Commission'],
            'column_mapping': {
                'Run Date': 'transaction_date',
                'Action': 'transaction_type',
                'Symbol': 'asset_symbol',
                'Quantity': 'quantity',
                'Price': 'price_per_share',
                'Description': 'notes',
                'Commission': 'commission'
            }
        }
    }
    
    def __init__(self, format_type: str = 'generic'):
        self.format_type = format_type
        self.template = self.FORMAT_TEMPLATES.get(format_type, self.FORMAT_TEMPLATES['generic'])
    
    def parse_csv(self, csv_file: io.StringIO) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Parse CSV file and return (valid_rows, errors)
        
        Returns:
            valid_rows: List of parsed transaction dictionaries
            errors: List of error dictionaries with row number and message
        """
        reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
        valid_rows = []
        errors = []
        
        # Validate required columns
        missing_cols = set(self.template['required_columns']) - set(reader.fieldnames or [])
        if missing_cols:
            errors.append({
                'row': 0,
                'message': f'Missing required columns: {", ".join(missing_cols)}'
            })
            return valid_rows, errors
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                parsed_row = self._parse_row(row)
                validation_errors = self._validate_row(parsed_row)
                
                if validation_errors:
                    errors.extend([
                        {'row': row_num, 'message': error}
                        for error in validation_errors
                    ])
                else:
                    valid_rows.append(parsed_row)
                    
            except Exception as e:
                errors.append({
                    'row': row_num,
                    'message': f'Parse error: {str(e)}'
                })
        
        return valid_rows, errors
    
    def _parse_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Parse a single CSV row using the template mapping"""
        parsed = {}
        
        for csv_col, db_field in self.template['column_mapping'].items():
            value = row.get(csv_col, '').strip()
            
            if not value and csv_col in self.template['required_columns']:
                raise ValueError(f'Missing required value: {csv_col}')
            
            # Type conversions
            if db_field == 'transaction_date':
                parsed[db_field] = self._parse_date(value)
            elif db_field in ['quantity', 'price_per_share', 'commission']:
                parsed[db_field] = float(value) if value else 0.0
            elif db_field == 'transaction_type':
                parsed[db_field] = self._normalize_transaction_type(value)
            else:
                parsed[db_field] = value
        
        # Calculate total value
        parsed['total_value'] = parsed['quantity'] * parsed['price_per_share']
        
        return parsed
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string (handles multiple formats)"""
        if not date_str:
            raise ValueError('Date is required')
        
        # Try common formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y%m%d']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Fallback to Django's dateparse
        parsed = parse_date(date_str)
        if not parsed:
            raise ValueError(f'Invalid date format: {date_str}')
        return parsed
    
    def _normalize_transaction_type(self, type_str: str) -> str:
        """Normalize transaction type to standard values"""
        type_mapping = {
            'buy': 'buy',
            'purchase': 'buy',
            'bought': 'buy',
            'sell': 'sell',
            'sale': 'sell',
            'sold': 'sell',
            'dividend': 'dividend',
            'div': 'dividend',
            'split': 'split',
            'reinvest': 'dividend_reinvest'
        }
        
        normalized = type_str.lower().strip()
        return type_mapping.get(normalized, normalized)
    
    def _validate_row(self, row: Dict[str, Any]) -> List[str]:
        """Validate a parsed row and return list of error messages"""
        errors = []
        
        # Validate date is not in future
        if row['transaction_date'] > datetime.now():
            errors.append('Transaction date cannot be in the future')
        
        # Validate quantity is positive
        if row['quantity'] <= 0:
            errors.append('Quantity must be positive')
        
        # Validate price is positive
        if row['transaction_type'] in ['buy', 'sell'] and row['price_per_share'] <= 0:
            errors.append('Price must be positive for buy/sell transactions')
        
        # Validate transaction type
        valid_types = ['buy', 'sell', 'dividend', 'dividend_reinvest', 'split']
        if row['transaction_type'] not in valid_types:
            errors.append(f'Invalid transaction type: {row["transaction_type"]}')
        
        return errors
    
    @classmethod
    def get_template(cls, format_type: str) -> str:
        """Generate CSV template for download"""
        template = cls.FORMAT_TEMPLATES.get(format_type, cls.FORMAT_TEMPLATES['generic'])
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            *template['required_columns'],
            *template['optional_columns']
        ])
        writer.writeheader()
        
        # Add example rows
        writer.writerow({
            'date': '2024-01-15',
            'symbol': 'AAPL',
            'type': 'buy',
            'quantity': '100',
            'price': '150.25',
            'notes': 'Initial investment',
            'commission': '9.99'
        })
        
        writer.writerow({
            'date': '2024-02-01',
            'symbol': 'MSFT',
            'type': 'buy',
            'quantity': '50',
            'price': '380.50',
            'notes': '',
            'commission': '7.99'
        })
        
        return output.getvalue()
```

**2. Create Import API Endpoints**
```python
# apps/backend/src/api/imports.py

from ninja import Router
from django.http import HttpResponse
from django.contrib.auth.models import User
from ...utils.import.csv_parser import CSVImportParser
from ...investments.models import Portfolio, Transaction, Asset

router = Router()

@router.get("/template/{format}")
def download_csv_template(request, format: str = 'generic'):
    """Download CSV template for import"""
    template = CSVImportParser.get_template(format)
    
    response = HttpResponse(template, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="portfolio_import_{format}.csv"'
    return response

@router.post("/preview")
def preview_import(request, csv_file, format: str = 'generic', portfolio_id: str = None):
    """Preview CSV import without saving (validate first)"""
    
    parser = CSVImportParser(format)
    valid_rows, errors = parser.parse_csv(csv_file)
    
    # Check for duplicate transactions
    if portfolio_id:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.auth)
        # Check for duplicates
        # ...
    
    return {
        'valid_count': len(valid_rows),
        'error_count': len(errors),
        'rows': valid_rows,
        'errors': errors
    }

@router.post("/confirm")
def confirm_import(request, csv_file, format: str = 'generic', portfolio_id: str):
    """Confirm and execute CSV import (save to database)"""
    
    parser = CSVImportParser(format)
    valid_rows, errors = parser.parse_csv(csv_file)
    
    if errors:
        return {'success': False, 'message': 'Cannot import with errors', 'errors': errors}, 400
    
    portfolio = Portfolio.objects.get(id=portfolio_id, user=request.auth)
    created_transactions = []
    
    for row_data in valid_rows:
        # Get or create asset
        asset, _ = Asset.objects.get_or_create(
            symbol=row_data['asset_symbol'],
            defaults={
                'name': row_data['asset_symbol'],
                'asset_type': 'stock'  # Default, can be improved
            }
        )
        
        # Create transaction
        transaction = Transaction.objects.create(
            portfolio=portfolio,
            asset=asset,
            transaction_type=row_data['transaction_type'],
            transaction_date=row_data['transaction_date'],
            quantity=row_data['quantity'],
            price_per_share=row_data['price_per_share'],
            total_value=row_data['total_value'],
            commission=row_data.get('commission', 0),
            notes=row_data.get('notes', '')
        )
        created_transactions.append(transaction)
    
    return {
        'success': True,
        'imported_count': len(created_transactions),
        'transactions': [t.id for t in created_transactions]
    }
```

**3. Update URLs**
```python
# apps/backend/src/api/urls.py
from .imports import router as imports_router

api.add_router("/import", imports_router)
```

### Frontend Files:

**4. Create CSV Import Component**
```typescript
// apps/frontend/src/components/portfolio/CSVImportDialog.tsx

'use client';

import React, { useState, useCallback } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Upload, Download, AlertCircle, CheckCircle2 } from 'lucide-react';

interface CSVImportDialogProps {
  open: boolean;
  onClose: () => void;
  portfolioId: string;
  onImportComplete: () => void;
}

export const CSVImportDialog: React.FC<CSVImportDialogProps> = ({
  open,
  onClose,
  portfolioId,
  onImportComplete
}) => {
  const [step, setStep] = useState<'upload' | 'preview' | 'success'>('upload');
  const [format, setFormat] = useState('generic');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any>(null);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownloadTemplate = async () => {
    const response = await fetch(`/api/import/template/${format}`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portfolio_import_${format}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected && selected.type === 'text/csv') {
      setFile(selected);
      setError(null);
    } else {
      setError('Please select a CSV file');
    }
  };

  const handlePreview = async () => {
    if (!file) return;

    setImporting(true);
    setError(null);

    const formData = new FormData();
    formData.append('csv_file', file);
    formData.append('format', format);
    formData.append('portfolio_id', portfolioId);

    try {
      const response = await fetch('/api/import/preview', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Preview failed');

      const data = await response.json();
      setPreview(data);
      setStep('preview');
    } catch (err) {
      setError(err.message);
    } finally {
      setImporting(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!file) return;

    setImporting(true);

    const formData = new FormData();
    formData.append('csv_file', file);
    formData.append('format', format);
    formData.append('portfolio_id', portfolioId);

    try {
      const response = await fetch('/api/import/confirm', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Import failed');

      const data = await response.json();
      if (data.success) {
        setStep('success');
        setTimeout(() => {
          onImportComplete();
          onClose();
        }, 2000);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setImporting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {step === 'upload' && 'Import Transactions from CSV'}
            {step === 'preview' && 'Review Import'}
            {step === 'success' && 'Import Complete'}
          </DialogTitle>
        </DialogHeader>

        {step === 'upload' && (
          <div className="space-y-4">
            <div>
              <Label>CSV Format</Label>
              <Select value={format} onValueChange={setFormat}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="generic">Generic Format</SelectItem>
                  <SelectItem value="schwab">Charles Schwab</SelectItem>
                  <SelectItem value="fidelity">Fidelity</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={handleDownloadTemplate}>
                <Download className="mr-2 h-4 w-4" />
                Download Template
              </Button>
            </div>

            <div>
              <Label>Upload CSV File</Label>
              <Input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
              />
              {file && (
                <p className="text-sm text-muted-foreground mt-1">
                  Selected: {file.name}
                </p>
              )}
            </div>

            {error && (
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            )}

            <DialogFooter>
              <Button variant="ghost" onClick={onClose}>Cancel</Button>
              <Button
                onClick={handlePreview}
                disabled={!file || importing}
              >
                {importing ? 'Validating...' : 'Preview Import'}
              </Button>
            </DialogFooter>
          </div>
        )}

        {step === 'preview' && preview && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                <span>{preview.valid_count} valid transactions</span>
              </div>
              {preview.error_count > 0 && (
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-destructive" />
                  <span>{preview.error_count} errors</span>
                </div>
              )}
            </div>

            {preview.errors.length > 0 && (
              <div className="bg-destructive/10 p-4 rounded-lg">
                <h4 className="font-semibold mb-2">Errors:</h4>
                <ul className="text-sm space-y-1">
                  {preview.errors.map((err: any, i: number) => (
                    <li key={i}>
                      Row {err.row}: {err.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Symbol</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Quantity</TableHead>
                  <TableHead>Price</TableHead>
                  <TableHead>Total</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {preview.rows.map((row: any, i: number) => (
                  <TableRow key={i}>
                    <TableCell>{row.transaction_date}</TableCell>
                    <TableCell>{row.asset_symbol}</TableCell>
                    <TableCell>{row.transaction_type}</TableCell>
                    <TableCell>{row.quantity}</TableCell>
                    <TableCell>${row.price_per_share}</TableCell>
                    <TableCell>${row.total_value.toFixed(2)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <DialogFooter>
              <Button variant="ghost" onClick={() => setStep('upload')}>
                Back
              </Button>
              <Button
                onClick={handleConfirmImport}
                disabled={preview.error_count > 0 || importing}
              >
                {importing ? 'Importing...' : 'Confirm Import'}
              </Button>
            </DialogFooter>
          </div>
        )}

        {step === 'success' && (
          <div className="text-center py-8">
            <CheckCircle2 className="h-16 w-16 mx-auto text-green-500 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Import Successful!</h3>
            <p className="text-muted-foreground">
              Your transactions have been imported.
            </p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
```

**5. Add Import Button to Portfolio Page**
```typescript
// apps/frontend/src/app/(dashboard)/portfolios/page.tsx

import { CSVImportDialog } from '@/components/portfolio/CSVImportDialog';
import { Upload } from 'lucide-react';

// In component:
const [importDialogOpen, setImportDialogOpen] = useState(false);

// In JSX:
<Button onClick={() => setImportDialogOpen(true)}>
  <Upload className="mr-2 h-4 w-4" />
  Import CSV
</Button>

<CSVImportDialog
  open={importDialogOpen}
  onClose={() => setImportDialogOpen(false)}
  portfolioId={portfolioId}
  onImportComplete={() => {
    // Refresh portfolio data
    window.location.reload();
  }}
/>
```

---

## 🔧 IMPLEMENTATION STEPS

### Phase 1: Backend (3-4 hours)
1. Create `CSVImportParser` utility
2. Create import API endpoints
3. Add CSV template generation
4. Test parsing with various formats
5. Test validation logic

### Phase 2: Frontend Components (2-3 hours)
1. Create `CSVImportDialog` component
2. Add file upload handling
3. Add preview table
4. Add error display
5. Add template download

### Phase 3: Integration (1-2 hours)
1. Add import button to portfolio page
2. Test full import flow
3. Test error handling
4. Test with real CSV files

---

## 📊 API SPECIFICATION

### GET /api/import/template/{format}
**Response:** CSV file download

### POST /api/import/preview
**Request:** FormData with `csv_file`, `format`, `portfolio_id`
**Response:**
```json
{
  "valid_count": 15,
  "error_count": 2,
  "rows": [...],
  "errors": [...]
}
```

### POST /api/import/confirm
**Request:** FormData with `csv_file`, `format`, `portfolio_id`
**Response:**
```json
{
  "success": true,
  "imported_count": 15,
  "transactions": [...]
}
```

---

## 🎯 PRIORITY RATIONALE

**Why P1 (HIGH):**
- Very high user value (saves hours of manual entry)
- Medium implementation complexity
- Builds on existing models
- No external dependencies
- One-time effort, ongoing value

**User Impact:** 10/10 - Essential for portfolio management
**Dev Effort:** 5/10 - Standard CSV parsing
**Risk:** 3/10 - Well-defined patterns exist

---

**Task created by GAUDÍ (Architect)**
**Ready for assignment to Backend + Frontend Coders**
**Part of Portfolio Management Suite**
