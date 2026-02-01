# FinanceHub Accessibility Test Cases

**Created:** February 1, 2026
**Author:** HADI - Accessibility Specialist
**Purpose:** Automated and manual accessibility testing

---

## Test Environment

**Before running tests, ensure:**
1. Docker frontend is running: `docker compose up frontend`
2. App accessible at: http://localhost:3000
3. Test with: NVDA (Windows), VoiceOver (Mac), or ChromeVox

---

## Automated Test Cases

### AXT-001: Run axe-core on Homepage

**Test:** Automated accessibility scan
```bash
# Install axe-core if not already installed
cd apps/frontend
npm install @axe-core/react

# Run in browser console or use axe CLI
npx axe http://localhost:3000
```

**Expected Results:**
- 0 critical violations
- 0 high priority violations
- All issues documented and fixed

**Pass Criteria:** ✅ No violations

---

### AXE-002: Run axe-core on All Pages

**Test:** Scan all application pages
```bash
# Pages to test:
# - / (Dashboard)
# - /holdings
# - /trading
# - /research
# - /options
# - /screener
# - /backtesting
# - /alerts
# - /settings
```

**Expected Results:**
- Consistent accessibility across all pages
- Navigation works with keyboard only
- Forms have proper labels

**Pass Criteria:** ✅ All pages pass

---

### ESL-001: Run eslint-plugin-jsx-a11y

**Test:** Linting for accessibility
```bash
cd apps/frontend
npx eslint src/ --plugin jsx-a11y --ext .tsx,.ts
```

**Expected Results:**
- No jsx-a11y errors
- All warnings addressed

**Pass Criteria:** ✅ No errors, warnings resolved

---

## Manual Test Cases

### KBD-001: Keyboard Navigation - Full Workflow

**Test:** Complete user journey without mouse
```
Steps:
1. Press Tab to navigate through page
2. Verify all interactive elements are reachable
3. Verify focus indicator is visible on all elements
4. Press Enter/Space to activate buttons
5. Press Escape to close dialogs
6. Verify Tab order is logical (top to bottom, left to right)
```

**Pages to Test:**
- Dashboard (all widgets)
- Holdings page (sort, filter, pagination)
- Trading page (order entry)
- Options chain (filters, sorting)

**Pass Criteria:** ✅ All elements reachable, logical order

---

### KBD-002: Skip Link Functionality

**Test:** Skip to main content
```
Steps:
1. Press Tab immediately after page load
2. Verify "Skip to main content" link appears
3. Press Enter
4. Verify focus moves to main content
5. Verify visual scroll to top of main content
```

**Pass Criteria:** ✅ Skip link works correctly

---

### KBD-003: Modal/Dialog Keyboard

**Test:** Modal dialog accessibility
```
Steps:
1. Open any dialog (e.g., Add Transaction)
2. Verify focus moves to dialog
3. Verify focus is trapped within dialog
4. Press Tab - verify cycling within dialog
5. Press Escape - verify dialog closes
6. Verify focus returns to trigger element
```

**Pass Criteria:** ✅ Focus trap works, Escape closes, focus returns

---

### SR-001: Screen Reader - Forms

**Test:** Form validation with screen reader
```
Steps:
1. Open form with errors (or create errors)
2. Listen for error announcement
3. Verify error message is read
4. Verify field is marked as invalid
5. Verify error is linked to field (aria-describedby)
```

**Forms to Test:**
- Order Entry Form
- Add Transaction Dialog
- Alert Creation Form

**Pass Criteria:** ✅ Errors announced correctly

---

### SR-002: Screen Reader - Charts

**Test:** Chart data accessibility
```
Steps:
1. Navigate to chart component
2. Verify chart has role="img" and aria-label
3. Check if data table alternative exists
4. Verify keyboard navigation works for chart controls
5. Verify timeframe changes are announced
```

**Charts to Test:**
- AdvancedChart
- MarketHeatmap
- HoldingsAllocationChart

**Pass Criteria:** ✅ Chart accessible, data available

---

### SR-003: Screen Reader - Tables

**Test:** Data table accessibility
```
Steps:
1. Navigate to any data table (holdings, options chain)
2. Verify table has caption or aria-label
3. Verify th elements have scope
4. Verify pagination announcements
5. Verify sort column announcements
```

**Pass Criteria:** ✅ Table properly marked up

---

### CLR-001: Color Contrast - Normal Text

**Test:** Text color contrast ratio
```
Tool: Chrome DevTools > Elements > Computed > Color
Requirement: 4.5:1 ratio for normal text (below 18pt)
```

**Test Points:**
- Body text (14-16px)
- Button text
- Input placeholder text
- Navigation links

**Pass Criteria:** ✅ All text meets 4.5:1

---

### CLR-002: Color Contrast - Large Text

**Test:** Large text color contrast ratio
```
Requirement: 3:1 ratio for large text (18pt+ or 14pt+ bold)
```

**Test Points:**
- Headings (h1, h2, h3)
- Card titles
- Section headers

**Pass Criteria:** ✅ All large text meets 3:1

---

### CLR-003: Color Meaning

**Test:** Information not conveyed by color alone
```
Verification:
1. Check all color-coded information
2. Verify icons or text also convey meaning
3. Red/Green indicators have icons or labels
4. Status indicators have text labels
```

**Pass Criteria:** ✅ No color-only information

---

### ZOM-001: Zoom 200%

**Test:** Content at 200% zoom
```
Steps:
1. Set browser zoom to 200%
2. Navigate through all pages
3. Verify no horizontal scrolling
4. Verify all content is accessible
5. Verify no overlapping text
```

**Pass Criteria:** ✅ All content usable at 200%

---

### ZOM-002: Zoom 400%

**Test:** Content at 400% zoom
```
Steps:
1. Set browser zoom to 400%
2. Verify core functionality still works
3. Verify navigation is still possible
```

**Pass Criteria:** ✅ Core functionality preserved

---

## Component-Specific Tests

### FRM-001: Form Labels

**Test:** All form inputs have visible labels
```
Verification:
1. Check Input components
2. Check Select components  
3. Check Checkbox/Radio components
4. Verify htmlFor/id matching
```

**Pass Criteria:** ✅ All inputs labeled

---

### FRM-002: Form Validation

**Test:** Validation accessibility
```
Verification:
1. Submit empty required fields
2. Verify error messages appear
3. Verify aria-invalid is set
4. Verify error linked via aria-describedby
5. Verify focus moves to first error
```

**Pass Criteria:** ✅ Validation accessible

---

### NAV-001: Navigation Structure

**Test:** Navigation accessibility
```
Verification:
1. Verify main navigation has nav role
2. Verify current page indicator
3. Verify breadcrumb if available
4. Verify pagination accessibility
```

**Pass Criteria:** ✅ Navigation properly structured

---

### MDE-001: Motion Reduction

**Test:** Respect reduced motion preference
```css
/* Check CSS for reduced motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Verification:**
1. Check animations are disabled with prefers-reduced-motion
2. Verify no flashing content (>3Hz)

**Pass Criteria:** ✅ Respects reduced motion

---

## Test Results Template

### Page/Component: _______________

| Test Case | Expected | Actual | Pass/Fail | Notes |
|-----------|----------|--------|-----------|-------|
| KBD-001   | Keyboard works | | | |
| SR-001    | Screen reader works | | | |
| CLR-001   | 4.5:1 contrast | | | |
| ZOM-001   | 200% zoom works | | | |

**Total:** ___/___ Pass Rate: ___%

---

## Running Tests

```bash
# Run all automated tests
cd apps/frontend
npm run test:a11y

# Run linting
npm run lint

# Run type checking
npm run typecheck

# Build and verify
npm run build
```

---

**Last Updated:** February 1, 2026
**Next Review:** February 7, 2026

---

*HADI - Building Financial Excellence for Everyone*
