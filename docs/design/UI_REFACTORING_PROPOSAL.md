# FinanceHub UI Refactoring Task Proposal

**Date:** February 1, 2026  
**Author:** MIES (UI/UX Designer)  
**Status:** PROPOSAL - Awaiting GAUDÍ Approval

---

## Executive Summary

FinanceHub has a complex component architecture with **69 UI components** and **31 chart components**. This proposal identifies refactoring opportunities to improve maintainability, consistency, and performance.

---

## Component Inventory Analysis

### 1. UI Components Breakdown

| Category | Count | Lines of Code (avg) |
|----------|-------|---------------------|
| Form Controls | 15 | 30-60 |
| Navigation | 8 | 60-726 (sidebar is 726!) |
| Data Display | 12 | 40-100 |
| Feedback | 8 | 30-80 |
| Overlay | 10 | 50-120 |
| Data Entry | 8 | 50-100 |
| Charts | 5 | 40-80 |
| Other | 5 | 40-80 |

### 2. Feature Components Breakdown

| Directory | Components | Largest Component |
|-----------|------------|-------------------|
| charts/ | 31 | AdvancedChart.tsx (954 lines) |
| risk/ | 13 | RiskDashboard.tsx (1271 lines) |
| research/ | 9 | AnalystRatings.tsx (955 lines) |
| economics/ | 8 | EconomicCalendar.tsx (856 lines) |
| options/ | 8 | OptionsChain.tsx (846 lines) |
| ai/ | 13 | SentimentAnalysis.tsx (739 lines) |
| holdings/ | 8 | HoldingsDataTable.tsx (529 lines) |
| analytics/ | 12 | TaxLotTable.tsx (459 lines) |
| trading/ | 8 | OrderList.tsx (704 lines) |

---

## Refactoring Opportunities

### 1. COMPONENT CONSOLIDATION

#### 1.1 Chart Components (31 total)

**Problem:** 31 chart components with potential duplication.

**Current State:**
```
charts/
├── AreaChart.tsx (217 lines)
├── CandlestickChart.tsx (244 lines)
├── LineChart.tsx (206 lines)
├── KagiChart.tsx (190 lines)
├── RenkoChart.tsx (243 lines)
├── HeikinAshiChart.tsx (181 lines)
├── DepthChart.tsx (440 lines)
├── VolumeProfileChart.tsx (622 lines)
├── TradingViewChart.tsx (646 lines)
├── ComparisonChart.tsx (538 lines)
├── MarketHeatmap.tsx (500 lines)
└── ... 20 more
```

**Proposal:** Create a unified chart architecture

```tsx
// NEW: Reusable chart wrapper
interface ChartProps {
  type: 'line' | 'area' | 'candlestick' | 'bar'
  data: DataPoint[]
  options?: ChartOptions
  height?: number
}

// Replace individual chart files with:
<Chart type="candlestick" data={data} height={400} />
```

**Estimated Savings:** 40-60% code reduction

#### 1.2 Data Table Components

**Current State:**
- `ui/data-table.tsx` (511 lines) - Generic data table
- `holdings/HoldingsDataTable.tsx` (529 lines) - Holdings-specific
- `analytics/TaxLotTable.tsx` (459 lines) - Tax lot-specific

**Proposal:** Consolidate into single DataTable with feature configurations

```tsx
// Unified DataTable with presets
<DataTable preset="holdings" />
<DataTable preset="taxlots" />
<DataTable preset="transactions" />
```

---

### 2. PROP DRILLING ELIMINATION

#### 2.1 Sidebar Context (726 lines)

**Current Issue:** Sidebar uses complex context pattern but passes props manually.

**Proposal:** Simplify with better composition

```tsx
// Current: Complex provider pattern
<SidebarProvider>
  <Sidebar>
    <SidebarHeader />
    <SidebarContent />
    <SidebarFooter />
  </Sidebar>
</SidebarProvider>

// Proposed: Simpler composition
<Sidebar>
  <Sidebar.Header />
  <Sidebar.Content />
  <Sidebar.Footer />
</Sidebar>
```

#### 2.2 Chart Configuration

**Current Issue:** ChartControls.tsx (354 lines) passes config to multiple charts.

**Proposal:** Use Zustand store for chart configuration

```tsx
// NEW: Chart configuration store
useChartStore = create((set) => ({
  timeframe: '1d',
  indicators: [],
  setTimeframe: (t) => set({ timeframe: t }),
}))

// All charts subscribe automatically
<TradingViewChart />
<CandlestickChart />
```

---

### 3. CUSTOM HOOK EXTRACTION

#### 3.1 AI Components

**Current State:**
- `ai/SentimentAnalysis.tsx` (739 lines) - Has inline logic
- `ai/PricePrediction.tsx` (502 lines) - Has inline logic
- `ai/forecast-chart.tsx` (193 lines)

**Proposal:** Extract custom hooks

```tsx
// NEW: hooks/useSentiment.ts
export function useSentiment(symbol: string) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // API calls
  }, [symbol])

  return { data, loading, analyze }
}

// NEW: hooks/usePricePrediction.ts
export function usePricePrediction(symbol: string, horizon: string) {
  // Prediction logic
}
```

**Estimated Savings:** 30% reduction in component lines

#### 3.2 Chart Hooks

**Current State:** Each chart has duplicate:
- Data fetching logic
- Resize handlers
- Tooltip handling
- Drawing tools

**Proposal:** Create chart hooks

```tsx
// NEW: hooks/useChartData.ts
export function useChartData(symbol: string, type: string, timeframe: string) {
  // Unified data fetching
}

// NEW: hooks/useChartResize.ts
export function useChartResize(ref: RefObject<HTMLElement>) {
  // Unified resize handling
}

// NEW: hooks/useChartTooltip.ts
export function useChartTooltip() {
  // Unified tooltip logic
}
```

---

### 4. PERFORMANCE OPTIMIZATION

#### 4.1 Large Components (500+ lines)

| Component | Lines | Issue | Solution |
|-----------|-------|-------|----------|
| RiskDashboard.tsx | 1271 | Too large | Split into sub-components |
| AnalystRatings.tsx | 955 | Mixed concerns | Separate data/business logic |
| AdvancedChart.tsx | 954 | Duplicate code | Share with other charts |
| EconomicCalendar.tsx | 856 | Complex UI | Lazy load sections |
| OptionsChain.tsx | 846 | Performance | Virtual scrolling |
| SentimentAnalysis.tsx | 739 | Mixed concerns | Extract hooks |

#### 4.2 Memoization Opportunities

**Current State:** Components re-render unnecessarily.

**Proposal:** Add React.memo and useMemo

```tsx
// Before
export function HoldingsTable({ data }) {
  return <DataTable data={data} />
}

// After
export const HoldingsTable = memo(function HoldingsTable({ data }) {
  return <DataTable data={data} />
})
```

---

### 5. DESIGN SYSTEM INTEGRATION

#### 5.1 Brutalist Variants (PROPOSED)

| Component | Current | Proposed |
|-----------|---------|----------|
| Button | 6 variants | 9 variants (+3 brutalist) |
| Tabs | 2 variants | 4 variants (+2 brutalist) |
| Badge | 4 variants | 6 variants (+2 brutalist) |
| Card | Standard only | Standard + brutalist |

#### 5.2 Design Token Cleanup

**Current:** Scattered CSS variables
**Proposed:** Centralized design tokens

```tsx
// NEW: lib/design-tokens.ts
export const tokens = {
  colors: { ... },
  spacing: { ... },
  typography: { ... },
  radius: { ... },
  shadows: { ... },
}
```

---

## Implementation Roadmap

### Phase 1: Quick Wins (Week 1-2)

1. **Extract Chart Hooks**
   - useChartData
   - useChartResize
   - useChartTooltip
   - **Effort:** 4 hours
   - **Impact:** 15% code reduction

2. **Extract AI Hooks**
   - useSentiment
   - usePricePrediction
   - **Effort:** 3 hours
   - **Impact:** 10% code reduction

3. **Add React.memo to Tables**
   - HoldingsDataTable
   - TaxLotTable
   - **Effort:** 1 hour
   - **Impact:** Performance improvement

### Phase 2: Component Consolidation (Week 2-3)

1. **Unified Chart Wrapper**
   - Replace 5 similar charts
   - **Effort:** 8 hours
   - **Impact:** 40% code reduction in charts

2. **DataTable Presets**
   - Consolidate 3+ tables
   - **Effort:** 6 hours
   - **Impact:** 30% code reduction

3. **Sidebar Simplification**
   - Refactor 726-line component
   - **Effort:** 4 hours
   - **Impact:** 50% code reduction

### Phase 3: Architecture (Week 3-4)

1. **Design Tokens**
   - Centralize all tokens
   - **Effort:** 3 hours
   - **Impact:** Maintainability

2. **Component Library Cleanup**
   - Remove unused exports
   - **Effort:** 2 hours
   - **Impact:** Bundle size

---

## Estimated Impact

| Metric | Current | After Refactoring | Improvement |
|--------|---------|-------------------|-------------|
| Total component lines | ~15,000 | ~10,000 | 33% |
| Chart component lines | ~5,000 | ~3,000 | 40% |
| Duplicate code | ~20% | ~5% | 75% |
| Re-renders | High | Medium | 50% |
| Bundle size | ~500KB | ~400KB | 20% |

---

## Files to Modify

### High Priority
1. `components/charts/*.tsx` - Extract hooks, consolidate
2. `components/ai/*.tsx` - Extract hooks
3. `components/ui/button.tsx` - Add brutalist variants
4. `components/ui/tabs.tsx` - Add brutalist variants

### Medium Priority
5. `components/ui/data-table.tsx` - Add presets
6. `components/ui/sidebar.tsx` - Simplify
7. `components/holdings/HoldingsDataTable.tsx` - Memoize

### Low Priority
8. All chart components - Wrap in unified Chart
9. Design tokens - Centralize
10. Unused exports - Remove

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking changes | High | Test thoroughly, feature flags |
| Performance regression | Medium | Benchmark before/after |
| Developer learning curve | Low | Document changes |
| Time investment | High | Phase approach |

---

## Questions for GAUDÍ

1. Should we prioritize refactoring or new features?

2. Which component should be refactored first?

3. Should we create a dedicated "Design System" role?

4. Timeline preference for Phase 1 vs Phase 3?

---

## Conclusion

FinanceHub has significant refactoring opportunities that could reduce code by 30-40% while improving performance and maintainability. The proposed phased approach minimizes risk while delivering incremental value.

**Recommendation:** Approve Phase 1 (Quick Wins) starting immediately.

---

**"God is in the details."**

**Ready for approval and implementation**

- MIES
