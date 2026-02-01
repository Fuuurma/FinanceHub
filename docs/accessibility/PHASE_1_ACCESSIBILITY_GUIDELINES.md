# Phase 1 Accessibility Guidelines

**Date:** February 1, 2026
**Author:** HADI (Accessibility Engineer)
**Scope:** C-036, C-037, C-030

---

## General Requirements

- WCAG 2.1 Level AA compliance
- Semantic HTML throughout
- Keyboard navigation support
- Screen reader support (NVDA, JAWS, VoiceOver)
- Color contrast ratios met (4.5:1 normal, 3:1 large text)

---

## Component Specifications

### Buttons

- Icon-only buttons must have `aria-label`
- Focus indicator visible (contrast ratio 3:1)
- Keyboard accessible (Enter/Space to activate)
- Avoid duplicate button groups

```tsx
// Good:
<Button aria-label="Refresh portfolio">
  <RefreshCw className="h-4 w-4" />
</Button>

// Bad:
<Button>
  <RefreshCw className="h-4 w-4" />
</Button>
```

### Forms

- All inputs have `<label htmlFor>` or `aria-label`
- Required fields marked with `aria-required="true"`
- Validation errors announced via `role="alert"` or `aria-live`
- Error messages linked via `aria-describedby`

```tsx
<label htmlFor="symbol" className="block font-bold">
  Symbol <span aria-hidden="true">*</span>
</label>
<Input
  id="symbol"
  aria-required="true"
  aria-invalid={!!error}
  aria-describedby={error ? "symbol-error" : undefined}
/>
{error && (
  <p id="symbol-error" role="alert" className="text-red-600">
    {error}
  </p>
)}
```

### Tables

- `<th>` elements with `scope="col"` or `scope="row"`
- `<caption>` element describing table purpose
- Responsive table (scroll or stack on mobile)

```tsx
<table>
  <caption className="sr-only">Your positions with P&L</caption>
  <thead>
    <tr>
      <th scope="col">Symbol</th>
      <th scope="col">P&L</th>
    </tr>
  </thead>
</table>
```

### Charts

- `role="img"` and `aria-label` describing chart
- Data table alternative below chart
- Colors not sole indicator (use icons/text)

```tsx
<div role="img" aria-label="Performance chart showing gains">
  <LineChart data={data} />
</div>
<table className="sr-only">
  {/* Data table alternative */}
</table>
```

### Modals/Dialogs

- `role="dialog"` or `role="alertdialog"`
- Focus trapped within modal
- Escape key closes modal
- First focusable element receives focus on open
- Never use `window.confirm()` or `window.alert()`

### Color Indicators

- Never use color alone to convey information
- Add icons or text labels for profit/loss
- Green/red indicators need additional visual cues

```tsx
// Good:
<span className="text-green-600">
  <TrendingUp className="inline h-3 w-3 mr-1" aria-hidden="true" />
  +$500
</span>

// Bad:
<span className="text-green-600">+$500</span>
```

### Landmarks

- Use `<main id="main-content">` for main content
- Add skip navigation link
- Use `<nav>` for navigation regions
- Use `<header>`, `<footer>`, `<aside>` appropriately

```tsx
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>
<main id="main-content">
  {/* Page content */}
</main>
```

### Dynamic Updates

- Use `aria-live="polite"` for status updates
- Use `aria-live="assertive"` for errors
- Announce portfolio changes, trade execution

```tsx
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {result && `Order executed. ${result.asset}`}
</div>
```

---

## Testing Checklist

### Pre-Implementation
- [ ] Review designs for accessibility with MIES
- [ ] Verify color contrast in design mockups
- [ ] Check semantic structure in wireframes
- [ ] Plan keyboard navigation flow

### During Development
- [ ] Use semantic HTML elements
- [ ] Associate labels with inputs
- [ ] Add ARIA attributes as needed
- [ ] Test keyboard navigation
- [ ] Run axe DevTools

### Pre-Release
- [ ] Keyboard navigation test (Tab through page)
- [ ] Screen reader test (NVDA on Windows)
- [ ] Color contrast test (axe DevTools)
- [ ] Form validation test
- [ ] Responsive test (320px, 768px, 1024px)
- [ ] Test with real screen reader

---

## Screen Reader Testing

### NVDA (Windows)
1. Navigate to page
2. Press `Tab` to move through interactive elements
3. Press `Arrow keys` to navigate within components
4. Listen for proper announcements
5. Verify form labels, error messages, dynamic updates

### VoiceOver (Mac)
1. Press `Cmd+F5` to activate
2. Use `Ctrl+Option+Arrow keys` to navigate
3. Verify content is announced correctly
4. Test form interactions
5. Test dynamic content

---

## WCAG 2.1 Level AA Quick Reference

### Must Pass
- 1.4.3 Contrast (Minimum): 4.5:1 for normal text
- 2.4.7 Focus Visible: Visible focus indicator
- 3.3.2 Labels or Instructions: Form labels provided

### Should Pass
- 1.1.1 Non-text Content: Alt text, ARIA labels
- 1.3.1 Info and Relationships: Semantic HTML
- 2.4.1 Bypass Blocks: Skip navigation link
- 2.4.3 Focus Order: Logical tab order
- 3.3.1 Error Identification: Errors announced
- 4.1.2 Name, Role, Value: ARIA attributes

---

## Phase 1 Components

### C-036 Paper Trading
- PaperTradingDashboard
- PaperTradeForm
- PaperPortfolioSummary
- PaperTradeHistory
- PaperPerformanceChart
- OrderConfirmationDialog

### C-037 Social Sentiment
- Sentiment Overview Page
- Sentiment Gauge
- Sentiment History Chart
- Trending Assets List
- Social Feed

### C-030 Broker Integration
- Broker Connection Page
- Live Trading Interface
- API Key Form

---

## File Locations

- Audit Reports: `docs/accessibility/C-0XX_*_AUDIT_REPORT.md`
- Guidelines: `docs/accessibility/PHASE_1_ACCESSIBILITY_GUIDELINES.md`
- Testing: `docs/accessibility/SCREEN_READER_TESTING_CHECKLIST.md`

---

**HADI - Accessibility Engineer**

*"Accessibility is not a feature, it's a fundamental aspect of good design."*
