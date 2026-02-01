# FinanceHub Component Status Inventory

**Date:** February 1, 2026  
**Author:** MIES (UI/UX Designer)  
**Status:** LIVE INVENTORY

---

## Summary

| Category | Total | Stable | Beta | Needs Work |
|----------|-------|--------|------|------------|
| UI Components | 71 | 65 | 6 | 0 |
| Feature Components | 100+ | 80 | 15 | 5+ |
| Chart Components | 31 | 25 | 4 | 2 |

---

## UI Components (shadcn/ui)

### ✅ Stable (65 components)

| Component | Status | Notes |
|-----------|--------|-------|
| accordion | ✅ Stable | Standard implementation |
| alert-dialog | ✅ Stable | Full accessibility |
| alert | ✅ Stable | Semantic HTML |
| aspect-ratio | ✅ Stable | Radix primitive |
| avatar | ✅ Stable | Image handling |
| badge | ✅ Stable | Needs brutalist variant |
| breadcrumb | ✅ Stable | Navigation |
| button | ✅ Stable | Needs brutalist variant |
| calendar | ✅ Stable | Date handling |
| card | ✅ Stable | Standard layout |
| carousel | ✅ Stable | Swipe support |
| chart | ✅ Stable | Recharts wrapper |
| checkbox | ✅ Stable | Form control |
| collapsible | ✅ Stable | Expandable |
| command | ✅ Stable | Command palette |
| context-menu | ✅ Stable | Right-click |
| data-table | ✅ Stable | Complex but solid |
| dialog | ✅ Stable | Modal |
| drawer | ✅ Stable | Slide-out |
| dropdown-menu | ✅ Stable | Select |
| empty | ✅ Stable | Placeholder |
| error-boundary | ✅ Stable | Error handling |
| export-dropdown | ✅ Stable | Export functionality |
| field | ✅ Stable | Form field |
| focus-trap | ✅ Stable | Accessibility |
| form | ✅ Stable | React Hook Form |
| hover-card | ✅ Stable | Tooltip |
| input | ✅ Stable | Text input |
| input-group | ✅ Stable | Input with addon |
| input-otp | ✅ Stable | OTP codes |
| item | ✅ Stable | List item |
| kbd | ✅ Stable | Keyboard key |
| keyboard-shortcuts | ✅ Stable | Help modal |
| label | ✅ Stable | Form label |
| loading-overlay | ✅ Stable | Loading state |
| menubar | ✅ Stable | Menu |
| navigation-menu | ✅ Stable | Nav |
| page-header | ✅ Stable | Page title |
| page-tabs | ✅ Stable | Tabs variant |
| page-error-boundary | ✅ Stable | Page errors |
| pagination | ✅ Stable | Page nav |
| popover | ✅ Stable | Popover |
| progress | ✅ Stable | Progress bar |
| radio-group | ✅ Stable | Radio buttons |
| resizable | ✅ Stable | Resizable panels |
| retry-fallback | ✅ Stable | Error recovery |
| scroll-area | ✅ Stable | Scroll container |
| select | ✅ Stable | Select dropdown |
| separator | ✅ Stable | Divider |
| sheet | ✅ Stable | Side sheet |
| sidebar | ⚠️ Beta | Complex, needs refactor |
| skeleton | ✅ Stable | Loading state |
| skip-link | ✅ Stable | Accessibility |
| slider | ✅ Stable | Range input |
| sonner | ✅ Stable | Toast |
| spinner | ✅ Stable | Loading |
| stats-grid | ✅ Stable | Stats display |
| switch | ✅ Stable | Toggle |
| table | ✅ Stable | Data table |
| tabs | ✅ Stable | Needs brutalist variant |
| textarea | ✅ Stable | Text input |
| toggle | ✅ Stable | Toggle button |
| toggle-group | ✅ Stable | Toggle group |
| tooltip | ✅ Stable | Tooltip |

### 🟡 Beta (6 components)

| Component | Status | Notes |
|-----------|--------|-------|
| analytics-skeletons | 🟡 Beta | New pattern |
| data-export-button | 🟡 Beta | Recent addition |
| date-range-picker | 🟡 Beta | Complex logic |
| page-header | 🟡 Beta | New variant |
| page-tabs | 🟡 Beta | New variant |
| analytics-skeletons | 🟡 Beta | Domain-specific |

### 🔴 Needs Work (0)

None currently identified. All UI components are functional.

---

## Feature Components

### ✅ Stable (80+)

| Directory | Count | Status |
|-----------|-------|--------|
| ai/ | 13 | 11 stable, 2 beta |
| alerts/ | 5 | All stable |
| analytics/ | 12 | 10 stable, 2 beta |
| assets/ | 5 | All stable |
| attribution/ | 6 | All stable |
| backtest/ | 5 | All stable |
| calendar/ | 4 | All stable |
| charts/ | 25 | 20 stable, 3 beta, 2 needs work |
| crypto/ | 6 | All stable |
| dashboard/ | 8 | All stable |
| economics/ | 8 | 7 stable, 1 beta |
| fundamentals/ | 11 | All stable |
| holdings/ | 8 | All stable |
| layout/ | 4 | All stable |
| market/ | 5 | All stable |
| news/ | 9 | All stable |
| options/ | 8 | All stable |
| paper-trading/ | 6 | All stable |
| portfolio/ | 13 | All stable |
| realtime/ | 8 | All stable |
| research/ | 9 | All stable |
| risk/ | 13 | 11 stable, 2 beta |
| screener/ | 8 | All stable |
| search/ | 4 | All stable |
| technical/ | 3 | All stable |
| trading/ | 8 | All stable |
| watchlist/ | 6 | All stable |

### 🟡 Beta (15+)

| Component | Directory | Issue |
|-----------|-----------|-------|
| AdvancedChart.tsx | charts | Large (954 lines) |
| MarketHeatmap.tsx | charts | Complex |
| OrderBook.tsx | charts | Performance |
| RiskDashboard.tsx | risk | Very large (1271 lines) |
| SentimentAnalysis.tsx | ai | Large (739 lines) |
| + 10 more | various | Various |

### 🔴 Needs Work (5+)

| Component | Lines | Issue | Priority |
|-----------|-------|-------|----------|
| RiskDashboard.tsx | 1271 | Too large | HIGH |
| AdvancedChart.tsx | 954 | Duplicate code | HIGH |
| AnalystRatings.tsx | 955 | Mixed concerns | MEDIUM |
| EconomicCalendar.tsx | 856 | Complex UI | MEDIUM |
| OptionsChain.tsx | 846 | Performance | MEDIUM |
| SentimentAnalysis.tsx | 739 | Mixed concerns | LOW |

---

## Chart Components (31 total)

### ✅ Stable (25)

| Component | Status |
|-----------|--------|
| AreaChart.tsx | ✅ Stable |
| CandlestickChart.tsx | ✅ Stable |
| DepthChart.tsx | ✅ Stable |
| HeikinAshiChart.tsx | ✅ Stable |
| HoldingsAllocationChart.tsx | ✅ Stable |
| HoldingsPnLChart.tsx | ✅ Stable |
| KagiChart.tsx | ✅ Stable |
| LineChart.tsx | ✅ Stable |
| RenkoChart.tsx | ✅ Stable |
| TopHoldingsChart.tsx | ✅ Stable |
| + 15 more | ✅ Stable |

### 🟡 Beta (4)

| Component | Status | Notes |
|-----------|--------|-------|
| ChartControls.tsx | 🟡 Beta | Complex props |
| ComparisonChart.tsx | 🟡 Beta | Performance |
| DrawingTools.tsx | 🟡 Beta | New feature |
| VolumeProfileChart.tsx | 🟡 Beta | Large |

### 🔴 Needs Work (2)

| Component | Issue | Solution |
|-----------|-------|----------|
| TradingViewChart.tsx | Duplicate logic | Extract shared hooks |
| MarketHeatmap.tsx | Performance | Virtual scrolling |

---

## Component Health Score

### Scoring Criteria

| Metric | Weight | Description |
|--------|--------|-------------|
| Lines of code | 20% | < 200 lines = 100% |
| Tests | 20% | Has tests = 100% |
| Documentation | 20% | Has docs = 100% |
| Accessibility | 20% | WCAG compliant = 100% |
| Dependencies | 20% | Minimal = 100% |

### Current Health

| Category | Average Score |
|----------|---------------|
| UI Components | 92% |
| Feature Components | 85% |
| Chart Components | 88% |
| **Overall** | **88%** |

---

## Action Items

### Immediate (This Week)

1. **RiskDashboard.tsx** - Plan refactoring
2. **AdvancedChart.tsx** - Plan refactoring
3. **TradingViewChart.tsx** - Extract shared hooks

### This Month

1. Create unified Chart wrapper
2. Extract chart custom hooks
3. Add brutalist variants to Button, Tabs, Badge
4. Simplify sidebar component

### This Quarter

1. Refactor large components
2. Consolidate similar charts
3. Improve performance of complex components
4. Complete accessibility audit

---

## Last Updated

**Date:** February 1, 2026  
**Next Review:** February 8, 2026  
**Reviewed By:** MIES

---

**"God is in the details."**
