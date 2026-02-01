# Accessibility Audit Report: C-037 Social Sentiment Analysis

**Date:** February 1, 2026
**Auditor:** HADI (Accessibility Engineer)
**Status:** IN PROGRESS

## Executive Summary

| Criterion | Status |
|-----------|--------|
| WCAG 2.1 Level AA | PARTIAL |
| Keyboard Navigation | PARTIAL |
| Screen Reader Support | PARTIAL |
| Color Contrast | PASS |
| Semantic HTML | PARTIAL |
| Interactive Elements | PARTIAL |

**Overall Assessment:** Social Sentiment components have moderate accessibility issues.

**Issues Found:** Critical: 4, High: 6, Medium: 4

## Components Audited

- NewsSentimentPanel.tsx
- NewsFeed.tsx
- NewsCard.tsx
- TrendingTopics.tsx
- Sentiment page (app/(dashboard)/sentiment/page.tsx)

---

## Critical Issues (P0)

### A11Y-037-001: Clickable Divs Need Button Semantics
**WCAG:** 2.1.1 Keyboard (Level A)
**Location:** `NewsSentimentPanel.tsx:188-213`

**Issue:** Hot topic cards use `div` with `onClick` instead of `<button>`.

```tsx
// Current (inaccessible):
<div
  key={topic.topic}
  className="group cursor-pointer border-2 border-foreground px-3 py-2 bg-background hover:bg-muted transition-colors"
  onClick={() => onTopicClick?.(topic.topic)}
>
```

**Remediation:** Use `<button>` or add proper ARIA:
```tsx
<button
  type="button"
  key={topic.topic}
  className="group cursor-pointer border-2 border-foreground px-3 py-2 bg-background hover:bg-muted transition-colors"
  onClick={() => onTopicClick?.(topic.topic)}
>
```

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-002: Sentiment Gauge Not Accessible
**WCAG:** 1.1.1 Non-text Content (Level A)
**Location:** `NewsSentimentPanel.tsx:16-35`

**Issue:** SentimentGauge component lacks accessible name and description.

**Remediation:**
```tsx
<div
  role="img"
  aria-label={`${label}: ${status}, score ${value}%`}
  className="space-y-1"
>
  <div className="flex justify-between text-[10px] font-black uppercase">
    <span aria-hidden="true">{label}</span>
    <span className={cn(color)} aria-hidden="true">{status}</span>
  </div>
  <div
    className="h-4 w-full border-2 border-foreground bg-background p-[2px]"
    aria-hidden="true"
  >
    <div
      className={cn('h-full transition-all', color)}
      style={{ width: `${Math.min(value, 100)}%` }}
    />
  </div>
</div>
```

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-003: Article Items Not In Article Elements
**WCAG:** 1.3.1 Info and Relationships (Level A)
**Location:** `NewsFeed.tsx:226-235`

**Issue:** News articles wrapped in `<div>` instead of `<article>`.

```tsx
// Current:
<div key={article.id} className="group">
  <NewsCard article={article} />
</div>

// Accessible:
<article key={article.id} className="group">
  <NewsCard article={article} />
</article>
```

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-004: Missing Main Content Landmark
**WCAG:** 1.3.1 Info and Relationships (Level A)
**Location:** `NewsFeed.tsx:189-255`

**Issue:** Feed content not wrapped in `<main>` landmark.

**Remediation:**
```tsx
<main id="main-content" className={cn('flex flex-col h-full bg-background', className)}>
```

**Assigned:** Turing
**Status:** OPEN

---

## High-Priority Issues (P1)

### A11Y-037-005: Refresh Button Missing Aria-Label
**WCAG:** 2.4.6 Headings and Labels (Level AA)
**Location:** `NewsFeed.tsx:212-219`

**Issue:** Icon-only refresh button lacks accessible name.

**Remediation:**
```tsx
<Button
  variant="ghost"
  size="icon"
  aria-label="Refresh news feed"
>
  <RefreshCw className="h-4 w-4" />
</Button>
```

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-006: Trending Topics List Semantics
**WCAG:** 1.3.1 Info and Relationships (Level A)
**Location:** `NewsSentimentPanel.tsx:157-174`

**Issue:** Trending symbols list uses `div` instead of `<ul>` with `<li>`.

**Remediation:**
```tsx
<ul className="space-y-2" role="list">
  {marketTrends.trending_symbols.map((item, idx) => (
    <li key={item.symbol} className="flex items-center justify-between p-2 border border-foreground/10">
```

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-007: Color-Only Sentiment Indicators
**WCAG:** 1.4.1 Use of Color (Level A)
**Location:** `NewsSentimentPanel.tsx:94-105`

**Issue:** Sentiment icons use color alone to indicate positive/negative.

**Remediation:**
```tsx
const getSentimentIcon = (score: number) => {
  if (score >= 0.4) return { Icon: TrendingUp, label: 'positive' }
  if (score >= 0) return { Icon: Minus, label: 'neutral' }
  return { Icon: TrendingDown, label: 'negative' }
}

// In render:
<Icon
  className={cn('h-4 w-4', score >= 0.4 ? 'text-green-600' : 'text-red-600')}
  aria-label={label}
/>
```

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-008: Loading State Not Announced
**WCAG:** 4.1.3 Status Messages (Level AA)
**Location:** `NewsFeed.tsx:162-187`

**Issue:** Loading skeleton not announced to screen readers.

**Remediation:**
```tsx
{loading ? (
  <div role="status" aria-live="polite" aria-busy={true}>
    <span className="sr-only">Loading news feed</span>
    {/* Skeleton content */}
  </div>
) : (
  <main id="main-content">
```

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-009: Progress Indicators Need Labels
**WCAG:** 1.3.1 Info and Relationships (Level A)
**Location:** `NewsSentimentPanel.tsx:169`

**Issue:** Progress component lacks accessible label.

**Remediation:**
```tsx
<Progress
  value={(item.article_count / 60) * 100}
  aria-label={`${item.article_count} articles`}
  className="h-1 w-16 mt-1"
/>
```

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-010: Symbol Badges Need Context
**WCAG:** 2.4.6 Headings and Labels (Level AA)
**Location:** `NewsSentimentPanel.tsx:164`

**Issue:** Symbol badges may lack context for screen readers.

**Remediation:**
```tsx
<Badge variant="outline" className="font-bold" aria-label={`Symbol: ${item.symbol}`}>
  ${item.symbol}
</Badge>
```

**Assigned:** Turing
**Status:** OPEN

---

## Medium-Priority Issues (P2)

### A11Y-037-011: Skip Navigation Link
**WCAG:** 2.4.1 Bypass Blocks (Level A)

**Remediation:** Add skip link to sentiment page.

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-012: Sentiment Distribution Colors
**WCAG:** 1.4.1 Use of Color (Level A)
**Location:** `NewsSentimentPanel.tsx:132-145`

**Issue:** Positive/neutral/negative distribution uses color alone.

**Remediation:** Add text labels or icons.

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-013: Card Title Heading Levels
**WCAG:** 1.3.1 Info and Relationships (Level A)

**Remediation:** Verify CardTitle uses correct heading level.

**Assigned:** Turing
**Status:** OPEN

---

### A11Y-037-014: Focus Indicators
**WCAG:** 2.4.7 Focus Visible (Level AA)

**Remediation:** Verify focus styles on all interactive elements.

**Assigned:** Turing
**Status:** OPEN

---

## Testing Results

| Test | Status |
|------|--------|
| Keyboard Navigation | PARTIAL |
| Screen Reader (NVDA) | PARTIAL |
| Color Contrast | PASS |
| Semantic HTML | PARTIAL |

---

## Recommendations

1. **Immediate:** Fix clickable divs (P0)
2. **This Week:** Fix all P1 issues
3. **Next Week:** Verify with screen readers

---

## Sign-Off

- [ ] Developer: Turing - [Date]
- [ ] Accessibility: HADI - [Date]
- [ ] Architect: GAUDÍ - [Date]
