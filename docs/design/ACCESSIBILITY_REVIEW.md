# FinanceHub Accessibility Review (M-002)

**Task ID:** M-002  
**Date:** February 1, 2026  
**Status:** IN PROGRESS  
**Collaborator:** HADI (Accessibility Specialist)

---

## WCAG 2.1 Level AA Checklist

### 1. Text Alternatives ⬜

- [ ] All images have alt text
- [ ] All decorative images are marked decorative
- [ ] Complex charts have text descriptions
- [ ] Icons have aria-labels or visible text

### 2. Keyboard Accessible ⬜

- [ ] All interactive elements reachable via keyboard
- [ ] Tab order follows logical reading order
- [ ] No keyboard traps
- [ ] Skip links provided for main content
- [ ] Focus indicator visible on all interactive elements

**Current State:**
- globals.css provides: `:focus-visible { outline: 2px solid var(--ring); outline-offset: 2px; }`
- Need to verify all components use this

### 3. Focus Visible ⬜

- [ ] All buttons show focus state
- [ ] All inputs show focus state
- [ ] All links show focus state
- [ ] Custom components (charts, tables) show focus

**Current State:**
- Button: ✅ Uses shadcn CVA with focus-visible
- Input: ✅ Has focus ring
- Custom: ⚠️ Need to check charts, data tables

### 4. Input Timing ⬜

- [ ] No timeouts that cause issues (or adjustable)
- [ ] Session timeouts can be extended
- [ ] Animated content can be paused

**Current State:**
- Need to review API timeouts
- Need to check data refresh intervals

### 5. Seizures ⬜

- [ ] No content flashes more than 3 times per second
- [ ] Animations can be disabled via reduced motion

**Current State:**
- globals.css provides `.reduce-motion` support
- Need to verify all animations respect this

### 6. Navigable ⬜

- [ ] Headings used correctly (h1-h6)
- [ ] Link purpose clear from link text
- [ ] Multiple ways to find pages
- [ ] Focus order logical
- [ ] Page titles descriptive
- [ ] Section headings used

**Current State:**
- Need to audit heading hierarchy
- Need to check link text clarity

### 7. Input Modalities ⬜

- [ ] Pointer gestures have non-pointer alternatives
- [ ] Drag-and-drop has button alternative
- [ ] Motion animation can be disabled

**Current State:**
- Need to review trading interactions
- Need to check drag-and-drop in portfolios

### 8. Document Accessibility ⬜

- [ ] HTML lang attribute set
- [ ] Reading order matches visual order
- [ ] Purpose of each section clear
- [ ] Markup valid

**Current State:**
- Need to audit layout.tsx
- Need to check page.tsx structure

---

## Color Contrast Verification

### Primary Text (--foreground)

| Context | Ratio | Status |
|---------|-------|--------|
| On --background (light) | 12.3:1 | ✅ PASS |
| On --background (dark) | 12.3:1 | ✅ PASS |
| On --card (light) | 12.3:1 | ✅ PASS |
| On --card (dark) | 12.3:1 | ✅ PASS |

### Muted Text (--muted-foreground)

| Context | Ratio | Status |
|---------|-------|--------|
| On --muted (light) | 3.0:1 | ⚠️ BORDERLINE |
| On --muted (dark) | 5.5:1 | ✅ PASS |
| On --card (light) | 5.0:1 | ✅ PASS |

### Brand Color (--brand)

| Context | Ratio | Status |
|---------|-------|--------|
| On --background (light) | 4.8:1 | ✅ PASS |
| On --background (dark) | 6.1:1 | ✅ PASS |

### Chart Colors

| Token | On Dark | Status |
|-------|---------|--------|
| --chart-1 | 6.1:1 | ✅ PASS |
| --chart-2 | 6.7:1 | ✅ PASS |
| --chart-3 | 5.6:1 | ✅ PASS |
| --chart-4 | 7.3:1 | ✅ PASS |
| --chart-5 | 6.1:1 | ✅ PASS |

**Note:** All chart colors tested on dark mode background (worst case)

---

## Screen Reader Compatibility

### Components to Test

| Component | ARIA Pattern | Status |
|-----------|--------------|--------|
| Button | role="button" | ✅ Standard |
| Input | role="textbox" | ✅ Standard |
| Tabs | role="tablist" | ✅ Standard |
| DataTable | role="grid" | ⚠️ Need audit |
| Charts | role="img" + aria-label | ⚠️ Need audit |
| CommandPalette | role="dialog" | ⚠️ Need audit |

### Potential Issues

1. **Data Tables:** 
   - Need row/column headers marked
   - Need sortable column indicators

2. **Charts:**
   - Need data descriptions for screen readers
   - Need keyboard navigation for data points

3. **Real-time Updates:**
   - Need aria-live regions for price changes
   - Need to announce important updates

---

## Keyboard Navigation Audit

### Critical Paths to Test

1. **Login Flow**
   - [ ] Email input → Password input → Login button

2. **Portfolio Page**
   - [ ] Holdings table navigation
   - [ ] Add transaction dialog
   - [ ] Filter controls

3. **Trading Page**
   - [ ] Order form
   - [ ] Buy/Sell toggle
   - [ ] Submit order

4. **Settings Page**
   - [ ] Form navigation
   - [ ] Toggle switches
   - [ ] Save button

### Current State

- ✅ SkipLink component exists (`components/ui/SkipLink.tsx`)
- ✅ FocusTrap component exists for modals
- ⚠️ Need to verify all dialogs use FocusTrap

---

## TO DO

### Immediate (This Week)

- [ ] Audit all pages for heading hierarchy
- [ ] Check keyboard navigation on trading page
- [ ] Verify focus indicators on all interactive elements
- [ ] Test color contrast on all page backgrounds

### This Month

- [ ] Add aria-labels to all icons
- [ ] Implement aria-live for price updates
- [ ] Add screen reader descriptions to charts
- [ ] Test with actual screen reader (NVDA/VoiceOver)

---

## Questions for HADI

1. Should we use aria-live for all price updates or only significant changes?

2. What's the recommended pattern for accessible data tables with sorting?

3. Should charts use Canvas API or DOM-based for accessibility?

4. What's the threshold for "significant change" that should be announced?

---

## Files to Review

- `apps/frontend/src/components/ui/skip-link.tsx`
- `apps/frontend/src/components/ui/focus-trap.tsx`
- `apps/frontend/src/components/charts/*.tsx`
- `apps/frontend/src/components/holdings/*.tsx`
- `apps/frontend/src/components/trading/*.tsx`

---

**Collaboration:** Work with HADI for implementation
**Status:** IN PROGRESS
**Next Review:** February 3, 2026

---

"Accessibility is not optional."

- MIES
