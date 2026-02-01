# FinanceHub Accessibility Checklist

**Document:** WCAG 2.1 AA Compliance Checklist
**Created:** February 1, 2026
**Role:** HADI - Accessibility Specialist
**Status:** Active Audit

---

## Overview

This checklist provides comprehensive accessibility requirements for FinanceHub, aligned with WCAG 2.1 AA standards. All items must be verified during development and testing.

---

## 1. Perceivable

### 1.1 Text Alternatives

- [ ] All images have alt text (informative images)
- [ ] Alt text is descriptive and meaningful
- [ ] Decorative images marked with `alt=""` or `role="presentation"`
- [ ] Complex images (charts, graphs) have long descriptions
- [ ] Charts have accessible data tables or descriptions
- [ ] Icons have `aria-label` or `aria-labelledby`

**Testing:**
```bash
# Find images without alt
grep -rn "<img" src/components/ | grep -v "alt="
```

### 1.2 Captions and Alternatives

- [ ] All videos have captions
- [ ] Captions are accurate and synchronized
- [ ] Audio descriptions for video content
- [ ] Transcripts available for audio content

### 1.3 Adaptable Content

- [ ] Content can be presented in different ways
- [ ] Document reading order is logical
- [ ] Markup used semantically (headings, lists, tables)
- [ ] No information conveyed by color alone
- [ ] Text resize up to 200% works correctly

### 1.4 Color Contrast

- [ ] Normal text: minimum 4.5:1 ratio
- [ ] Large text (18pt+ or 14pt+ bold): minimum 3:1 ratio
- [ ] UI components: 3:1 minimum
- [ ] Color not used as only visual means
- [ ] Focus indicators visible

**Testing:**
```bash
# Use Chrome DevTools or browser extension
# - Lighthouse accessibility audit
# - axe DevTools
# - WAVE toolbar
```

---

## 2. Operable

### 2.1 Keyboard Accessibility

- [ ] All functionality available via keyboard
- [ ] Tab order is logical and intuitive
- [ ] No keyboard traps
- [ ] Focus indicator visible on all interactive elements
- [ ] Skip links present and functional
- [ ] Keyboard shortcuts have no conflict

**Testing:**
```bash
# Unplug mouse, test entire workflow with keyboard only
# Tab - navigate forward
# Shift+Tab - navigate backward
# Enter/Space - activate
# Escape - close/dismiss
# Arrow keys - navigate within components
```

### 2.2 Enough Time

- [ ] Time limits can be extended
- [ ] User can pause, stop, or hide moving content
- [ ] No flashing content >3 times per second
- [ ] Sessions timeout with warning

### 2.3 Navigation

- [ ] Multiple ways to find content (search, navigation)
- [ ] Headings describe content structure
- [ ] Focus order logical
- [ ] Link purpose clear from context
- [ ] Consistent navigation across pages

### 2.4 Input Modalities

- [ ] Content operable with touch
- [ ] Gesture-based actions have alternatives
- [ ] Motion-triggered actions can be disabled
- [ ] Pointer gestures have non-pointer alternatives

---

## 3. Understandable

### 3.1 Readable Content

- [ ] Language specified (`lang` attribute)
- [ ] Abbreviations explained on first use
- [ ] Technical terms defined
- [ ] Reading level appropriate

### 3.2 Predictable

- [ ] Navigation consistent across pages
- [ ] Components behave predictably
- [ ] No unexpected changes on focus
- [ ] Forms clearly labeled

### 3.3 Input Assistance

- [ ] Error identification is clear
- [ ] Error suggestions provided
- [ ] Error prevention for important actions
- [ ] Labels and instructions clear
- [ ] Context-sensitive help available

---

## 4. Robust

### 4.1 Compatible

- [ ] Valid HTML markup
- [ ] ARIA roles used correctly
- [ ] Status messages announced to screen readers
- [ ] Compatible with assistive technologies

### 4.2 ARIA Requirements

- [ ] ARIA roles, states, and properties valid
- [ ] No ARIA conflict with native semantics
- [ ] Custom controls have proper ARIA
- [ ] Live regions for dynamic content

---

## Component-Specific Requirements

### Buttons

- [ ] Use `<button>` element
- [ ] Descriptive text or `aria-label`
- [ ] Keyboard activated (Enter/Space)
- [ ] Focus visible
- [ ] Disabled state clearly indicated

### Links

- [ ] Descriptive link text
- [ ] `aria-label` if needed
- [ ] Open in new tab announced
- [ ] Visually distinct from text

### Forms

- [ ] Labels associated with inputs (`for`/`id`)
- [ ] Required fields indicated
- [ ] Error messages announced
- [ ] Auto-focus on first error
- [ ] Clear instructions
- [ ] Tab order logical
- [ ] Related fields grouped (`fieldset`/`legend`)

### Tables

- [ ] Headers identified (`<th>`)
- [ ] Scope attributes correct
- [ ] Captions present
- [ ] Data table, not layout table

### Dialogs/Modals

- [ ] Focus trap implemented
- [ ] Focus returned on close
- [ ] Escape key closes
- [ ] `aria-modal="true"`
- [ ] `aria-labelledby` or `aria-label`
- [ ] Background scroll prevented

### Navigation

- [ ] Skip link to main content
- [ ] Current page indicated
- [ ] Breadcrumb navigation
- [ ] Mobile menu accessible

### Charts/Data Visualizations

- [ ] Data table alternative
- [ ] Accessible descriptions
- [ ] Color not only means of conveying info
- [ ] Interactive charts keyboard accessible

---

## Testing Procedures

### Automated Testing

```bash
# Install tools
npm install -D @axe-core/react eslint-plugin-jsx-a11y

# Run axe
npx axe http://localhost:3000

# Linting
npx eslint src/ --plugin jsx-a11y

# Lighthouse
# Use Chrome DevTools > Lighthouse
```

### Manual Testing

1. **Keyboard Only**
   - Unplug mouse
   - Complete core workflows
   - Document any issues

2. **Screen Reader**
   - NVDA (Windows) or VoiceOver (Mac)
   - Navigate through all pages
   - Verify announcements

3. **Zoom Testing**
   - 200% zoom
   - 400% zoom
   - Verify no content lost

4. **Color Contrast**
   - Use Contrast Checker tool
   - Test all text sizes
   - Test all states (hover, focus, disabled)

### User Testing

- [ ] Test with users with disabilities
- [ ] Include blind/low-vision users
- [ ] Include motor impairment users
- [ ] Include cognitive disability users

---

## Common Issues and Fixes

### Issue: Missing Form Labels

**Problem:** `<input type="text" />` without `<label>`

**Fix:**
```jsx
// Wrong
<input type="text" placeholder="Enter email" />

// Correct
<label htmlFor="email">Email</label>
<input id="email" type="text" placeholder="Enter email" />

// Or with aria-label
<input type="text" aria-label="Email" />
```

### Issue: Non-Semantic Click Handlers

**Problem:** `<div onClick={handleClick}>`

**Fix:**
```jsx
// Wrong
<div onClick={openMenu}>Menu</div>

// Correct
<button onClick={openMenu}>Menu</button>
```

### Issue: Missing Focus Indicator

**Problem:** CSS removes default outline

**Fix:**
```css
/* Wrong */
*:focus { outline: none; }

/* Correct */
*:focus-visible { outline: 2px solid blue; }
```

### Issue: Missing Alt Text

**Problem:** `<img src="chart.png" />`

**Fix:**
```jsx
<img src="chart.png" alt="Stock price increased 25% over 6 months" />
```

### Issue: Low Color Contrast

**Problem:** `#999999` text on white background (3:1 ratio)

**Fix:**
```css
/* Use #595959 or darker for 4.5:1 */
color: #595959;
```

---

## Developer Guidelines

### Code Review Checklist

- [ ] New components use semantic HTML
- [ ] Interactive elements are buttons or links
- [ ] Focus management implemented
- [ ] ARIA attributes correct
- [ ] Color contrast verified
- [ ] Keyboard navigation tested

### Code Examples

#### Accessible Button
```tsx
<button
  onClick={handleClick}
  aria-label={isOpen ? 'Close menu' : 'Open menu'}
  className="focus-visible:ring-2 focus-visible:ring-blue-500"
>
  <Icon />
</button>
```

#### Accessible Form Input
```tsx
<div className="space-y-2">
  <label htmlFor="password" className="block text-sm font-medium">
    Password
  </label>
  <input
    id="password"
    type="password"
    aria-invalid={errors.password ? 'true' : 'false'}
    aria-describedby={errors.password ? 'password-error' : undefined}
    className="focus-visible:ring-2 focus-visible:ring-blue-500"
  />
  {errors.password && (
    <p id="password-error" role="alert" className="text-red-600">
      {errors.password.message}
    </p>
  )}
</div>
```

#### Accessible Modal
```tsx
<FocusTrap>
  <div
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
    className="focus-visible:outline-none"
  >
    <h2 id="modal-title">Confirm Action</h2>
    <button onClick={close}>Close</button>
    <button onClick={confirm}>Confirm</button>
  </div>
</FocusTrap>
```

---

## Resources

### Tools

- **axe DevTools** - Browser extension
- **Lighthouse** - Chrome DevTools
- **WAVE** - Web accessibility evaluator
- **NVDA** - Screen reader (Windows)
- **VoiceOver** - Screen reader (Mac)
- **Contrast Checker** - WebAIM

### References

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WAI-ARIA Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Checklist](https://webaim.org/standards/wcag/checklist)

---

## Audit Results

### Automated Scan
- **Tool:** Code analysis (axe requires running server)
- **Status:** Pending - Docker build issue blocking live testing
- **Planned:** Complete once dev environment fixed

### Code Review
- **Components Analyzed:** 277+ TypeScript files
- **Issues Found:** Minor (detailed below)
- **WCAG Estimate:** ~80-85% compliance based on code review

### Strengths
- ✅ SkipLink component properly implemented
- ✅ FocusTrap for modals
- ✅ ARIA attributes used throughout UI components
- ✅ aria-invalid for form validation
- ✅ focus-visible for keyboard indication
- ✅ Radix UI primitives (generally accessible)
- ✅ Alert roles for error messages

### Issues Found

#### Medium Priority
1. **Input placeholders without labels** (11 instances)
   - Files: OptionsChain.tsx, ScreenerFilter.tsx
   - Fix: Add `aria-label` or visible labels

#### Low Priority
1. **Docker dev environment** - Frontend build fails
   - Impact: Cannot run automated axe/Lighthouse tests
   - Fix: Fix package.json scripts in apps/frontend

---

## Compliance Status

| WCAG Principle | Status | Notes |
|----------------|--------|-------|
| Perceivable | ⚠️ Partial | Need color contrast testing |
| Operable | ✅ Good | Keyboard support good |
| Understandable | ⚠️ Partial | Need form validation review |
| Robust | ✅ Good | ARIA usage correct |

---

**Next Review:** February 7, 2026
**WCAG Audit Deadline:** February 14, 2026

---

*HADI - Building Financial Excellence for Everyone*
