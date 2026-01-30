# Rust-Based Optimization Plan

## Priority Tasks

### P0: Core Data Processing
- [ ] **Real-time Data Pipeline** (Polars)
  - Current: pandas DataFrame operations
  - Target: Polars DataFrame for better performance
  - Files to optimize:
    - `src/lib/realtime/processData.ts`
    - `src/stores/realtimeStore.ts`
    - `src/hooks/useRealtimeData.ts`
  - Expected improvement: 50-100% faster data processing

### P0: Market Data Aggregation
- [ ] **Market Heatmap Generation** (Polars)
  - Current: Python data processing
  - Target: Polars for efficient groupby/agg operations
  - Files to optimize:
    - `src/components/charts/MarketHeatmap.tsx`
    - `src/lib/realtime/marketData.ts`
  - Expected improvement: 60% faster

### P1: Export Functionality
- [ ] **Excel/CSV Export** (Polars)
  - Current: vanilla JS/ExcelJS
  - Target: Polars for large dataset exports
  - Files to optimize:
    - `src/components/analytics/UniversalDataTable.tsx`
    - `src/lib/api/export.ts`
  - Expected improvement: 70% faster on 1000+ rows

### P1: Trading Analytics
- [ ] **Tax Lot Optimization** (Polars)
  - Current: Python backend
  - Target: Python/Polars for client-side optimization
  - Files to optimize:
    - `src/components/analytics/TaxLotOptimizer.tsx`
    - `src/components/analytics/TaxLotTable.tsx`
  - Expected improvement: 80% faster

### P2: Screener Operations
- [ ] **Asset Screener** (Polars)
  - Current: filter/map operations
  - Target: Polars for complex filtering
  - Files to optimize:
    - `src/components/screener/ScreenerPanel.tsx`
    - `src/lib/api/screener.ts`
  - Expected improvement: 50% faster on large datasets

---

## Implementation Steps

### Step 1: Install Dependencies
```bash
cd Frontend/src
pip3 install polars  # or use conda if available
```

### Step 2: Create Helper Functions
```typescript
// src/lib/utils/polars-adapter.ts
// Wrapper for Polars operations
export const polars = {
  filter: (df: any, condition: any) => {},
  groupBy: (df: any, columns: string[]) => {},
  agg: (grouped: any, operations: any) => {},
  toJs: (df: any) => {}
}
```

### Step 3: Migrate Core Functions
- Identify hot paths in data processing
- Replace pandas operations with Polars
- Benchmark before/after performance

### Step 4: Add Error Handling
```typescript
try {
  // Polars operation
} catch (error) {
  // Fallback to pandas
  console.error('Polars error, falling back to pandas:', error)
  return pandasOperation()
}
```

### Step 5: Performance Testing
- Create benchmark suite
- Test with 1000+ asset dataset
- Measure response times
- Document improvements

---

## Files to Optimize

### High Impact (P0)
1. **Real-time Data Processing**
   - `src/lib/realtime/processData.ts`
   - `src/stores/realtimeStore.ts`
   - Impact: High latency reduction

2. **Market Heatmap**
   - `src/components/charts/MarketHeatmap.tsx`
   - `src/lib/realtime/marketData.ts`
   - Impact: Faster rendering, real-time updates

3. **Tax Lot Optimization**
   - `src/components/analytics/TaxLotOptimizer.tsx`
   - `src/components/analytics/TaxLotTable.tsx`
   - Impact: Better UX for large portfolios

### Medium Impact (P1)
4. **Export Functionality**
   - `src/components/analytics/UniversalDataTable.tsx`
   - `src/lib/api/export.ts`
   - Impact: 1000+ rows handled smoothly

5. **Screener Operations**
   - `src/components/screener/ScreenerPanel.tsx`
   - `src/lib/api/screener.ts`
   - Impact: Faster filtering on large datasets

---

## Expected Results

### Performance Improvements
- **Data Processing**: 50-100% faster
- **Real-time Updates**: 30-50% lower latency
- **Large Dataset Handling**: 2-3x faster
- **Export Operations**: 70% faster on 1000+ rows

### User Experience
- **Smoother Real-time Charts**: 16ms vs 32ms latency
- **Instant Heatmap Updates**: <50ms vs 200ms
- **Faster Screener**: <100ms vs 300ms
- **Instant Exports**: <500ms vs 1.5s

---

## Next Steps

1. ✅ Install polars
2. ⏳ Create Polars adapter utilities
3. ⏳ Migrate real-time data processing
4. ⏳ Optimize market heatmap
5. ⏳ Benchmark and document
