# Priority Accessibility Fixes - Action List for Turing

**From:** HADI (Accessibility Engineer)
**To:** Turing (Frontend Developer)
**Priority:** HIGH - Fix before production
**Date:** Feb 1, 2026

---

## Critical Fixes (Do First - 1-2 hours)

### 1. Fix Form Labels in PaperTradeForm
**File:** `apps/frontend/src/components/paper-trading/PaperTradeForm.tsx`
**Lines:** 184-245

Add `htmlFor` and `id` to all labels/inputs:

```tsx
<label htmlFor="asset-symbol" className="...">Asset Symbol</label>
<Input id="asset-symbol" ... />

<label htmlFor="quantity" className="...">Quantity</label>
<Input id="quantity" ... />

<label htmlFor="order-type" className="...">Order Type</label>
<SelectTrigger id="order-type">...
```

### 2. Fix Charts - Add Text Alternative
**File:** `apps/frontend/src/components/paper-trading/PaperPerformanceChart.tsx`
**Lines:** 196-263

Add accessible wrapper:
```tsx
<div
  role="img"
  aria-label="Performance line chart: Portfolio value vs S&P 500 benchmark"
  className="border-2 border-foreground p-4"
>
```

Add hidden data table for screen readers.

### 3. Add Skip Navigation Link
**File:** `apps/frontend/src/components/paper-trading/PaperTradingDashboard.tsx`

Add at top of component:
```tsx
<a href="#main-content" className="sr-only focus:not-sr-only ...">
  Skip to main content
</a>
<main id="main-content" className="...">
```

### 4. Fix Color-Only P&L Indicators (Multiple Files)
**Files:** 
- `PaperTradeForm.tsx` (lines 296-302)
- `PaperPortfolioSummary.tsx` (lines 173-190, 226-234)
- `PaperTradeHistory.tsx` (lines 177-185)
- `AccountSummary.tsx` (lines 116-117)

Add icons:
```tsx
{profit >= 0 ? (
  <TrendingUp className="inline h-3 w-3 mr-1" aria-hidden="true" />
) : (
  <TrendingDown className="inline h-3 w-3 mr-1" aria-hidden="true" />
)}
{formatCurrency(profit)}
```

### 5. Fix Clickable Divs in Sentiment Panel
**File:** `apps/frontend/src/components/news/NewsSentimentPanel.tsx`
**Lines:** 188-213

Change to `<button>`:
```tsx
<button
  type="button"
  className="..."
  onClick={() => onTopicClick?.(topic.topic)}
>
```

### 6. Fix Tables - Add Captions and Scope
**Files:**
- `PaperPortfolioSummary.tsx` (line 202)
- `PaperTradeHistory.tsx` (line 120)

Add:
```tsx
<caption className="sr-only">Your paper trading positions</caption>
<th scope="col">Symbol</th>
```

---

## High Priority Fixes (2-3 hours)

### 7. Replace window.confirm() with Accessible Modal
**File:** `PaperTradingDashboard.tsx` (line 26-28)

### 8. Add aria-labels to Icon-Only Buttons
**Files:** Multiple

### 9. Add aria-live Regions for Dynamic Updates
**Files:** `PaperTradeForm.tsx`, `AccountSummary.tsx`

### 10. Fix Tables - Use Proper List Semantics
**File:** `Trading page.tsx` (lines 127-166)

---

## Estimated Time

- **Critical fixes:** 1-2 hours
- **High priority:** 2-3 hours
- **Total:** 3-5 hours

---

## Testing After Fixes

1. Keyboard-only navigation test
2. Run axe DevTools
3. Test with screen reader (NVDA/VoiceOver)

---

**Questions?** Check:
- `docs/accessibility/DEVELOPER_QUICK_REFERENCE.md`
- Individual audit reports in `docs/accessibility/`
