# 📋 Task Assignment: Phase 1 Accessibility Audit (C-036, C-037, C-030)

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** HADI (Accessibility Engineer)
**Priority:** HIGH - Phase 1 Accessibility Compliance
**Estimated Effort:** 8-10 hours total
**Timeline:** Start immediately, parallel with design and development

---

## 🎯 OVERVIEW

You are assigned to **accessibility audits for Phase 1 features**:
- C-036: Paper Trading System
- C-037: Social Sentiment Analysis
- C-030: Broker API Integration

**Collaborators:**
- **Turing (Frontend):** Building UI components (needs your guidance)
- **MIES (Design):** Creating UI/UX designs (needs your input)
- **GRACE (QA):** Testing functionality (can test accessibility too)
- **GAUDÍ (Architect):** Strategic direction, WCAG compliance

**Your Role:** Ensure WCAG 2.1 Level AA compliance, provide accessibility guidelines, audit components, test with screen readers.

---

## 📋 YOUR TASKS

### Task 1: C-036 Paper Trading Accessibility Audit (3h)

**Components to Audit:**
- Paper Trading Page
- Portfolio Summary Card
- Order Form
- Position List Table
- Performance Chart

#### 1.1 Keyboard Navigation
**WCAG Criterion:** 2.1.1 Keyboard (Level A)

**Audit Checklist:**
- [ ] **All interactive elements are keyboard accessible**
  - Test: Navigate page using Tab key
  - Expected: Logical tab order (portfolio → order form → positions)
  - Verify: No keyboard traps

- [ ] **Visible focus indicators on all interactive elements**
  - Test: Tab through elements, verify focus visible
  - Expected: Clear outline or background change on focus
  - Verify: Focus indicator meets contrast ratio (3:1)

- [ ] **Skip navigation link provided**
  - Test: Load page, press Tab
  - Expected: First focus is "Skip to main content" link
  - Verify: Link jumps to main content when activated

#### 1.2 Screen Reader Support
**WCAG Criterion:** 1.3.1 Info and Relationships (Level A)

**Audit Checklist:**
- [ ] **Semantic HTML used throughout**
  - Test: View page source, verify semantic elements
  - Expected: `<nav>`, `<main>`, `<section>`, `<h1>-<h6>`
  - Verify: No `<div>` soup (everything has semantic meaning)

- [ ] **Form inputs have proper labels**
  - Test: Use screen reader (NVDA/JAWS) on order form
  - Expected: Each input has associated `<label>` or `aria-label`
  - Verify: Screen reader announces "Symbol, edit text"

- [ ] **Tables have proper headers**
  - Test: Use screen reader on position list table
  - Expected: `<th>` elements for column headers
  - Verify: Screen reader announces column headers

- [ ] **Buttons have accessible names**
  - Test: Use screen reader on buttons
  - Expected: Button text describes purpose
  - Verify: Screen reader announces "Execute Buy Order button"

- [ ] **Dynamic updates announced**
  - Test: Execute order, listen for updates
  - Expected: Portfolio value update announced via `aria-live`
  - Verify: Screen reader announces "Portfolio value updated to $98,500"

#### 1.3 Color Contrast
**WCAG Criterion:** 1.4.3 Contrast (Minimum) (Level AA)

**Audit Checklist:**
- [ ] **Text meets contrast ratio (4.5:1 for normal text, 3:1 for large text)**
  - Test: Use axe DevTools or WAVE to check contrast
  - Expected: All text passes contrast check
  - Verify: No text below contrast ratio

- [ ] **P/L color coding has secondary indicator**
  - Test: View position list, check P/L column
  - Expected: Color + icon (+ or -) or text ("profit"/"loss")
  - Verify: Not just color alone (WCAG 1.4.1)

#### 1.4 Forms and Error Handling
**WCAG Criterion:** 3.3.1 Error Identification (Level A)

**Audit Checklist:**
- [ ] **Form validation errors are announced**
  - Test: Submit invalid order (insufficient funds)
  - Expected: Error message announced via `aria-live` or `role="alert"`
  - Verify: Screen reader announces error

- [ ] **Required fields are indicated**
  - Test: View order form with screen reader
  - Expected: Required fields marked with `aria-required="true"`
  - Verify: Screen reader announces "Symbol, required, edit text"

- [ ] **Form instructions provided**
  - Test: View order form
  - Expected: Instructions before form (e.g., "Enter order details")
  - Verify: Instructions associated with form via `aria-describedby`

#### 1.5 Data Tables
**WCAG Criterion:** 1.3.1 Info and Relationships (Level A)

**Audit Checklist:**
- [ ] **Position list table has proper headers**
  - Test: Use screen reader on table
  - Expected: `<th>` elements with `scope="col"`
  - Verify: Screen reader announces column headers

- [ ] **Table has caption**
  - Test: View position list table
  - Expected: `<caption>` element describing table purpose
  - Verify: Caption is "Your paper trading positions"

#### 1.6 Charts and Visualizations
**WCAG Criterion:** 1.1.1 Non-text Content (Level A)

**Audit Checklist:**
- [ ] **Performance chart has text alternative**
  - Test: View chart with screen reader
  - Expected: Chart container has `role="img"` and `aria-label`
  - Verify: Screen reader announces "Line chart showing portfolio value over time"

- [ ] **Chart data available in alternative format**
  - Test: Check for data table below chart
  - Expected: Table with chart data (timestamp, portfolio_value)
  - Verify: Data accessible without chart

#### 1.7 Responsive Design
**WCAG Criterion:** 1.4.10 Reflow (Level AA)

**Audit Checklist:**
- [ ] **No horizontal scrolling at 320px width**
  - Test: Resize browser to 320px width
  - Expected: Content reflows vertically, no horizontal scroll
  - Verify: All content accessible on mobile

---

### Task 2: C-037 Social Sentiment Accessibility Audit (3h)

**Components to Audit:**
- Sentiment Overview Page
- Sentiment Gauge
- Sentiment History Chart
- Trending Assets List
- Social Feed

#### 2.1 Sentiment Gauge
**WCAG Criterion:** 1.1.1 Non-text Content (Level A)

**Audit Checklist:**
- [ ] **Sentiment gauge has text alternative**
  - Test: View gauge with screen reader
  - Expected: Gauge has `role="img"` and descriptive `aria-label`
  - Verify: Screen reader announces "Sentiment gauge: Bullish, score 0.45, 87 mentions"

- [ ] **Sentiment value available as text**
  - Test: View gauge area
  - Expected: Text showing "Bullish (+0.45)" visible
  - Verify: Not just gauge graphic

#### 2.2 Social Feed
**WCAG Criterion:** 2.4.3 Focus Order (Level A)

**Audit Checklist:**
- [ ] **Feed items are logically ordered**
  - Test: Tab through social feed
  - Expected: Tab moves through feed items sequentially
  - Verify: Each feed item is focusable (or heading + content)

- [ ] **Feed items have landmarks**
  - Test: View feed with screen reader
  - Expected: Each feed item in `<article>` tag
  - Verify: Screen reader announces "Article 1 of 10"

- [ ] **Source icons have text labels**
  - Test: View Twitter/Reddit icons with screen reader
  - Expected: Icons have `aria-label="Twitter"` or text "Twitter" visible
  - Verify: Not just icon alone

#### 2.3 Sentiment History Chart
**WCAG Criterion:** 1.1.1 Non-text Content (Level A)

**Audit Checklist:**
- [ ] **Chart has text alternative**
  - Test: View chart with screen reader
  - Expected: Chart has descriptive `aria-label`
  - Verify: Screen reader announces "Sentiment history chart for AAPL over 24 hours"

- [ ] **Data available in alternative format**
  - Test: Check for data table
  - Expected: Table with time series data
  - Verify: Data accessible without chart

---

### Task 3: C-030 Broker Integration Accessibility Audit (2h)

**Components to Audit:**
- Broker Connection Page
- Live Trading Interface

#### 3.1 Broker Connection Form
**WCAG Criterion:** 3.3.2 Labels or Instructions (Level A)

**Audit Checklist:**
- [ ] **API key inputs have proper labels**
  - Test: Use screen reader on connection form
  - Expected: Each input has `<label>` or `aria-label`
  - Verify: Screen reader announces "API Key, password, edit text"

- [ ] **API key inputs are password fields**
  - Test: Type in API key fields
  - Expected: `type="password"` on sensitive fields
  - Verify: Characters obscured

- [ ] **Test vs Live account selection is clear**
  - Test: View account selection radio buttons
  - Expected: Radio buttons have `aria-describedby` with warning text
  - Verify: Screen reader announces "Test account, recommended" vs "Live account, real money"

#### 3.2 Live Trading Warnings
**WCAG Criterion:** 2.4.6 Headings and Labels (Level AA)

**Audit Checklist:**
- [ ] **Warning modals use proper heading hierarchy**
  - Test: Open live trading warning modal
  - Expected: Modal has `<h2>` or higher heading
  - Verify: Screen reader announces heading level

- [ ] **Warnings are announced**
  - Test: Open warning modal with screen reader
  - Expected: Modal has `role="alertdialog"`
  - Verify: Screen reader announces alert immediately

---

### Task 4: Accessibility Design Guidelines (1h)

**Deliverables:**
1. **Create `docs/accessibility/PHASE_1_ACCESSIBILITY_GUIDELINES.md`**
2. **Provide component-level accessibility specs**
3. **Create screen reader testing checklist**

#### 4.1 Document Accessibility Requirements

**Create document with:**

```markdown
# Phase 1 Accessibility Guidelines

## General Requirements
- WCAG 2.1 Level AA compliance
- Semantic HTML throughout
- Keyboard navigation support
- Screen reader support (NVDA, JAWS, VoiceOver)
- Color contrast ratios met

## Component Specifications

### Buttons
- `aria-label` if icon-only button
- Focus indicator visible (contrast ratio 3:1)
- Keyboard accessible (Enter/Space to activate)

### Forms
- All inputs have `<label>` or `aria-label`
- Required fields marked with `aria-required="true"`
- Validation errors announced via `aria-live`

### Tables
- `<th>` elements with `scope="col"` or `scope="row"`
- `<caption>` element describing table purpose
- Responsive table (scroll or stack on mobile)

### Charts
- `role="img"` and `aria-label` describing chart
- Data table alternative below chart
- Colors not sole indicator (use icons/text)

### Modals
- `role="dialog"` or `role="alertdialog"`
- Focus trapped within modal
- Escape key closes modal
- First focusable element receives focus on open

## Testing Checklist
- [ ] Keyboard navigation test (Tab through page)
- [ ] Screen reader test (NVDA on Windows, VoiceOver on Mac)
- [ ] Color contrast test (axe DevTools)
- [ ] Form validation test (submit invalid data)
- [ ] Responsive test (320px, 768px, 1024px)
```

#### 4.2 Screen Reader Testing Checklist

**Create checklist:**
- [ ] Test with NVDA (Windows)
- [ ] Test with JAWS (Windows)
- [ ] Test with VoiceOver (Mac)
- [ ] Test with TalkBack (Android)
- [ ] Test with VoiceOver (iOS)

---

## ✅ ACCEPTANCE CRITERIA

Your accessibility work is complete when:

### C-036 Paper Trading
- [ ] All 7 audit categories completed
- [ ] All components tested with screen reader
- [ ] Keyboard navigation verified
- [ ] Color contrast verified (all text passes 4.5:1)
- [ ] Accessibility report generated

### C-037 Social Sentiment
- [ ] All 3 audit categories completed
- [ ] Sentiment gauge accessible
- [ ] Social feed accessible
- [ ] Charts accessible (text alternatives provided)
- [ ] Accessibility report generated

### C-030 Broker Integration
- [ ] All 2 audit categories completed
- [ ] Broker connection form accessible
- [ ] Warning modals accessible
- [ ] Live trading warnings announced
- [ ] Accessibility report generated

### Design Guidelines
- [ ] `docs/accessibility/PHASE_1_ACCESSIBILITY_GUIDELINES.md` created
- [ ] Component accessibility specs documented
- [ ] Screen reader testing checklist created
- [ ] Design review with MIES completed

---

## 📊 SUCCESS METRICS

### Accessibility Metrics
- **WCAG Compliance:** 100% Level AA
- **Keyboard Navigation:** 100% of features accessible via keyboard
- **Screen Reader Support:** All components work with NVDA/JAWS/VoiceOver
- **Color Contrast:** 100% of text passes 4.5:1 ratio
- **Semantic HTML:** 100% of pages use semantic elements

### Testing Metrics
- **Manual Testing:** All components tested manually
- **Screen Reader Testing:** All components tested with NVDA
- **Keyboard Testing:** All flows tested via keyboard
- **Automated Testing:** axe DevTools scan passes (0 errors)

---

## 🚀 NEXT STEPS

### Immediate (Today)
1. **Review designs** from MIES for accessibility
2. **Provide accessibility guidelines** to MIES (before design finalization)
3. **Set up testing tools** (axe DevTools, NVDA, JAWS)
4. **Create accessibility documentation** template

### This Week
1. **Audit C-036 designs** (provide feedback to MIES)
2. **Audit C-037 designs** (provide feedback to MIES)
3. **Audit C-030 designs** (provide feedback to MIES)
4. **Create accessibility guidelines** document

### Next Week
1. **Test C-036 implementation** as Turing completes frontend
2. **Test C-037 implementation** as Turing completes frontend
3. **Test C-030 implementation** as Turing completes frontend
4. **Document accessibility bugs** for Turing to fix
5. **Verify fixes** and sign off on accessibility

---

## 📞 COMMUNICATION

**Daily Check-ins:**
- MIES: Design accessibility feedback
- Turing: Implementation accessibility testing

**Weekly Updates:**
- Report audit progress to GAUDÍ (Architect)
- Report accessibility bug statistics
- Flag blockers immediately

**Bug Reporting:**
- Create GitHub issues for accessibility bugs
- Tag relevant developer (usually Turing)
- Set priority (P0=critical, P1=high, P2=medium)
- Reference WCAG criterion in bug report
- Provide remediation steps

---

## 🛠️ ACCESSIBILITY TOOLS

### Automated Testing
- **axe DevTools:** Browser extension for accessibility testing
- **WAVE:** Web accessibility evaluation tool
- **Lighthouse:** Accessibility audit in Chrome DevTools
- **pa11y:** Automated accessibility testing

### Manual Testing
- **NVDA:** Free screen reader for Windows
- **JAWS:** Commercial screen reader for Windows
- **VoiceOver:** Built-in screen reader for Mac
- **TalkBack:** Screen reader for Android
- **VoiceOver:** Screen reader for iOS

### Keyboard Testing
- Test all features using only keyboard
- Verify logical tab order
- Verify no keyboard traps
- Verify skip links work

### Color Contrast Testing
- **axe DevTools:** Contrast checker
- **WebAIM Contrast Checker:** Online tool
- **Chrome DevTools:** Color picker with contrast ratio

---

## 📋 ACCESSIBILITY REPORT TEMPLATE

For each feature, create an accessibility report:

```markdown
# Accessibility Audit Report: C-036 Paper Trading System

**Date:** [Date]
**Auditor:** HADI (Accessibility Engineer)
**Status:** [IN PROGRESS / COMPLETE]

## Executive Summary
- [ ] WCAG 2.1 Level AA: [PASS / FAIL]
- [ ] Keyboard Navigation: [PASS / FAIL]
- [ ] Screen Reader Support: [PASS / FAIL]
- [ ] Color Contrast: [PASS / FAIL]

## Findings

### Critical Issues (P0)
None

### High-Priority Issues (P1)
1. **[A11Y-001]** Order form missing required field indicators
   - **WCAG:** 3.3.2 Labels or Instructions
   - **Remediation:** Add `aria-required="true"` to required inputs
   - **Assigned:** Turing
   - **Status:** OPEN

### Medium-Priority Issues (P2)
1. **[A11Y-002]** Performance chart missing text alternative
   - **WCAG:** 1.1.1 Non-text Content
   - **Remediation:** Add `aria-label` to chart container
   - **Assigned:** Turing
   - **Status:** OPEN

### Low-Priority Issues (P3)
None

## Testing Results
- Keyboard Navigation: PASSED
- Screen Reader (NVDA): PASSED
- Color Contrast: PASSED
- Semantic HTML: PASSED
- Form Validation: PASSED

## Recommendations
1. Add skip navigation link to page
2. Ensure all dynamic updates use `aria-live`
3. Add data table alternative to performance chart

## Sign-Off
- [ ] Developer: Turing - [Date]
- [ ] Accessibility: HADI - [Date]
- [ ] Architect: GAUDÍ - [Date]
```

---

**Status:** ✅ Task Assigned
**Timeline:** Start immediately, parallel with design and development
**Collaborators:** MIES, Turing, GRACE

---

♿ *HADI - Accessibility Engineer*

🎯 *Focus: Phase 1 WCAG 2.1 Level AA Compliance*

*"Accessibility is not a feature, it's a fundamental aspect of good design."*
