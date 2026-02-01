# Accessibility Quick Reference for Developers

**For:** Turing, Linus, Guido, and future developers
**Author:** HADI (Accessibility Engineer)
**Purpose:** Quick accessibility checklist for every code change

---

## Before You Write Code

### New Components
- [ ] Use semantic HTML (`<main>`, `<nav>`, `<article>`, `<section>`)
- [ ] Plan keyboard navigation flow
- [ ] Check color contrast in design
- [ ] Identify form fields and their labels

### New Forms
- [ ] Every input needs `<label htmlFor>` or `aria-label`
- [ ] Required fields marked with `aria-required="true"`
- [ ] Error messages use `role="alert"` or `aria-live`
- [ ] Error messages linked via `aria-describedby`

### New Charts/Visualizations
- [ ] Add `role="img"` with `aria-label`
- [ ] Create data table alternative
- [ ] Don't use color alone to convey information

### New Tables
- [ ] Add `<caption>` describing table purpose
- [ ] `<th scope="col">` for column headers
- [ ] `<th scope="row">` for row headers if used

---

## Accessibility Checklist for Every PR

### Required (Must Pass)
- [ ] All form inputs have labels
- [ ] No `window.confirm()` or `window.alert()` - use accessible modals
- [ ] All images/icons have `aria-label` or `aria-hidden="true"`
- [ ] Color is not the only way to show information
- [ ] Focus indicators visible (`:focus-visible` styles)

### Recommended
- [ ] Skip navigation link on pages
- [ ] Main content wrapped in `<main id="main-content">`
- [ ] Dynamic updates announced via `aria-live`
- [ ] Loading states announced

### Testing
- [ ] Keyboard-only test (Tab through component)
- [ ] Check with axe DevTools or similar
- [ ] Verify heading hierarchy (h1 → h2 → h3)

---

## Common Accessibility Patterns

### Accessible Button
```tsx
// Icon-only button
<Button aria-label="Refresh data">
  <RefreshCw className="h-4 w-4" />
</Button>

// Loading button
<Button aria-busy={loading}>
  {loading ? 'Loading...' : 'Submit'}
</Button>
```

### Accessible Form Input
```tsx
<Label htmlFor="email">Email <span aria-hidden="true">*</span></Label>
<Input
  id="email"
  type="email"
  aria-required="true"
  aria-invalid={!!error}
  aria-describedby={error ? "email-error" : undefined}
/>
{error && (
  <p id="email-error" role="alert" className="text-red-600">
    {error}
  </p>
)}
```

### Accessible Table
```tsx
<table>
  <caption className="sr-only">User transactions with date, amount, and status</caption>
  <thead>
    <tr>
      <th scope="col">Date</th>
      <th scope="col">Amount</th>
      <th scope="col">Status</th>
    </tr>
  </thead>
  <tbody>
    {/* rows */}
  </tbody>
</table>
```

### Accessible Chart
```tsx
<div
  role="img"
  aria-label="Line chart showing portfolio growth over 30 days"
>
  <LineChart data={data} />
</div>
{/* Hidden table for screen readers */}
<table className="sr-only">
  <caption>Portfolio data table</caption>
  {/* data */}
</table>
```

### Accessible Modal
```tsx
<Dialog open={open} onOpenChange={setOpen}>
  <DialogContent className="rounded-none border-2">
    <DialogHeader>
      <DialogTitle>Confirm Order</DialogTitle>
    </DialogHeader>
    {/* Content */}
    <DialogFooter>
      <Button variant="outline" onClick={() => setOpen(false)}>
        Cancel
      </Button>
      <Button onClick={confirm}>Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Accessible Dynamic Update
```tsx
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {tradeResult && `Trade executed: ${tradeResult.shares} shares of ${tradeResult.symbol}`}
</div>
```

---

## Color Indicator Pattern (Profit/Loss)

```tsx
// Good - icon + color + text
<span className={pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
  {pnl >= 0 ? <TrendingUp className="inline h-4 w-4" aria-hidden="true" /> : <TrendingDown className="inline h-4 w-4" aria-hidden="true" />}
  {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
</span>

// Bad - color only
<span className={pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
  {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
</span>
```

---

## Keyboard Navigation Checklist

Test with keyboard only (no mouse):

1. **Tab** - Move forward through interactive elements
2. **Shift+Tab** - Move backward
3. **Enter/Space** - Activate buttons, links
4. **Arrow keys** - Navigate within components (menus, lists, tabs)
5. **Escape** - Close modals, dropdowns

**Requirements:**
- [ ] Logical tab order (left-to-right, top-to-bottom)
- [ ] No keyboard traps (you can always Tab out)
- [ ] Visible focus indicator on all focusable elements
- [ ] Skip link to bypass repeated navigation

---

## WCAG Quick Reference

| Criterion | Level | Description |
|-----------|-------|-------------|
| 1.1.1 | A | Non-text content has text alternative |
| 1.3.1 | A | Information through structure (semantic HTML) |
| 1.4.1 | A | Color not used alone for information |
| 1.4.3 | AA | Contrast ratio 4.5:1 (normal text) |
| 2.1.1 | A | Keyboard accessible |
| 2.4.1 | A | Bypass blocks (skip link) |
| 2.4.3 | A | Focus order logical |
| 2.4.6 | AA | Headings and labels descriptive |
| 2.4.7 | AA | Focus visible |
| 3.3.1 | A | Errors identified and described |
| 3.3.2 | A | Labels or instructions provided |
| 4.1.2 | A | Name, role, value exposed to assistive tech |

---

## File Locations

- **Audit Reports:** `docs/accessibility/C-0XX_*_AUDIT_REPORT.md`
- **Guidelines:** `docs/accessibility/PHASE_1_ACCESSIBILITY_GUIDELINES.md`
- **Developer Quick Ref:** `docs/accessibility/DEVELOPER_QUICK_REFERENCE.md`
- **Issue Tracker:** Use GitHub issues with `accessibility` tag

---

**Questions?** Reach out to HADI or check the accessibility guidelines.

*"Accessibility is not a feature, it's a fundamental aspect of good design."*
