# Design Accessibility Review - Notes for MIES

**From:** HADI (Accessibility Engineer)
**To:** MIES (Designer)
**Subject:** Phase 1 Design Accessibility Requirements
**Date:** Feb 1, 2026

---

## Purpose

Ensure all Phase 1 designs meet WCAG 2.1 Level AA accessibility standards before implementation.

---

## Key Design Accessibility Requirements

### 1. Color Contrast

**Requirement:** 4.5:1 for normal text, 3:1 for large text (18pt+ or 14pt bold)

**When Designing:**
- [ ] Verify all text colors against backgrounds
- [ ] Use tools: Stark plugin, Color Contrast Accessibility Checker
- [ ] Avoid light gray text on white backgrounds
- [ ] Avoid white text on light gray backgrounds

**Minimum Contrast Ratios:**
- Normal text (under 18pt): **4.5:1**
- Large text (18pt+ or 14pt bold): **3:1**
- UI components (borders, icons): **3:1**

### 2. Color Not Used Alone

**Requirement:** Color cannot be the only visual means of conveying information (WCAG 1.4.1)

**Examples:**
- ❌ **Bad:** Green profit, red loss (color only)
- ✅ **Good:** Green + Up arrow + "+$500", Red + Down arrow + "-$300"
- ❌ **Bad:** Blue links only
- ✅ **Good:** Blue links + underline + different shade on hover

**For Financial Data:**
- P/L indicators: Icon + color + text (e.g., "+$500 (green)", "-$200 (red)")
- Status indicators: Icon + color + text label
- Sentiment: Icon + color + "Bullish/Bearish" label

### 3. Focus Indicators

**Requirement:** Visible focus indicator on all interactive elements (WCAG 2.4.7)

**Design Specs:**
- Outline: 2px solid (high contrast)
- Offset: 2px from element edge
- Color: Must contrast 3:1 with background

**Example CSS:**
```css
*:focus-visible {
  outline: 2px solid hsl(var(--foreground));
  outline-offset: 2px;
}
```

### 4. Touch Target Size

**Requirement:** Minimum 44x44 pixels for interactive elements (mobile)

**For Mobile Designs:**
- Buttons: At least 44x44px
- Form inputs: At least 44px height
- Icons with actions: At least 44x44px with padding

### 5. Text Sizing

**Requirement:** Text should reflow without horizontal scrolling at 320px (WCAG 1.4.10)

**Design Considerations:**
- Avoid fixed widths on text containers
- Use responsive layouts
- Test at 320px width

### 6. Form Labels and Instructions

**Requirement:** Labels visible, instructions clear (WCAG 3.3.2)

**Design Specs:**
- Labels above inputs (not inside)
- Required fields marked with asterisk or "Required" text
- Error messages: Red text + icon, positioned near field
- Placeholder: Supplement, not replacement for label

### 7. Interactive Elements

**Requirement:** All interactive elements clearly identifiable

**Design For:**
- Buttons: Solid background, clear borders
- Links: Underlined or clearly distinguished from text
- Cards with actions: Clear visual hierarchy

---

## Component-Specific Notes

### C-036 Paper Trading

**Issues Found in Current Implementation:**
1. Form labels missing programmatic association
2. Color-only P&L indicators
3. Tables missing captions
4. Chart missing text alternative

**Design Recommendations:**
- P/L column: Use ↑/↓ icons + green/red + text value
- Order form: Clear labels above all inputs
- Tables: Add visual caption header
- Chart: Include data table alternative in design

### C-037 Social Sentiment

**Issues Found:**
1. Clickable areas (hot topics) use divs instead of buttons
2. Sentiment gauge lacks text alternative
3. Color-only sentiment indicators

**Design Recommendations:**
- Hot topics: Design as buttons, not cards
- Sentiment gauge: Always show numerical value + text label
- Sentiment indicators: Icon + color + text label

### C-030 Broker Integration

**Design Requirements:**
1. API key form: Show/hide password toggle
2. Account selection: Clear distinction between test/live
3. Warning modals: Clear visual hierarchy, prominent

---

## Design Review Checklist

Before finalizing any Phase 1 design mockup:

- [ ] All text meets contrast ratios
- [ ] Color not used alone for information
- [ ] Focus indicators designed
- [ ] Touch targets 44x44px minimum
- [ ] Form labels visible and clear
- [ ] Error states designed
- [ ] Loading states designed
- [ ] Responsive at 320px

---

## Resources

- **Contrast Checker:** https://contrast-checker.org/
- **Stark Plugin:** Figma accessibility plugin
- **WCAG 2.1 Quick Reference:** https://www.w3.org/WAI/WCAG21/quickref/

---

## Coordination

**Next Steps:**
1. Review current C-036 designs against checklist
2. Apply fixes to paper trading mockups
3. Apply same principles to C-037 and C-030 designs
4. Share final designs with Turing for implementation

**Questions?** Reach out to HADI or check `docs/accessibility/PHASE_1_ACCESSIBILITY_GUIDELINES.md`

---

*"Accessibility is not a feature, it's a fundamental aspect of good design."*
