# Accessibility Skill

## Overview
Accessibility ensures that applications are usable by people with disabilities, following WCAG (Web Content Accessibility Guidelines) standards.

## Key Concepts
- **WCAG 2.2**: Latest Web Content Accessibility Guidelines
- **ARIA (Accessible Rich Internet Applications)**: Attributes that make web apps accessible
- **Semantic HTML**: Using proper HTML elements for accessibility
- **Keyboard Navigation**: All functionality accessible via keyboard
- **Screen Readers**: Assistive technology that reads content aloud
- **Color Contrast**: Minimum contrast ratios for readability
- **Focus Management**: Visible focus indicators, logical tab order
- **Alt Text**: Descriptive text for images
- **Labels**: Form inputs need proper labels

## Learning Resources
- [WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Accessibility Checklist](https://webaim.org/standards/wcag/checklist)
- [React Accessibility](https://react.dev/learn/accessibility)

## Best Practices
- **Semantic HTML**: Use `<button>`, `<nav>`, `<main>`, not `<div>` for everything
- **ARIA Labels**: `aria-label`, `aria-labelledby`, `aria-describedby` for context
- **Roles**: `role="button"`, `role="navigation"`, `role="dialog"` when needed
- **Keyboard**: All interactive elements must be keyboard accessible
- **Focus**: Visible focus indicators (`focus-visible` in Tailwind)
- **Color**: Minimum 4.5:1 contrast for normal text, 3:1 for large text
- **Forms**: All inputs need `<label>` or `aria-label`
- **Images**: Meaningful images need `alt=""`, decorative images need `alt=""` (empty)
- **Headings**: Proper heading hierarchy (h1 → h2 → h3)
- **Landmarks**: Use `<header>`, `<nav>`, `<main>`, `<footer>`, `<aside>`, `<section>`

## Tools
- **Lighthouse**: Built-in Chrome accessibility audit
- **axe DevTools**: Browser extension for accessibility testing
- **WAVE**: WebAIM's accessibility evaluation tool
- **Screen Readers**: NVDA (Windows), VoiceOver (Mac), JAWS
- **Keyboard Only**: Unplug mouse, test with keyboard only
- **Color Contrast Analyzer**: Chrome extension

## Common Issues
- **Missing Alt Text**: Images without descriptive `alt` attribute
- **Poor Contrast**: Light gray text on white background
- **No Focus Indicators**: Can't see which element has focus
- **Keyboard Traps**: Can't navigate out of modals/menus with keyboard
- **Empty Links**: `<a href="#">` without text or aria-label
- **Form Labels**: Inputs without proper labels
- **Heading Hierarchy**: Skipping heading levels (h1 → h3)

## WCAG 2.2 Principles
1. **Perceivable**: Information must be presentable in ways users can perceive
2. **Operable**: Interface components must be operable
3. **Understandable**: Information and operation must be understandable
4. **Robust**: Content must be robust enough for assistive technologies

## Testing Checklist
- [ ] Can I navigate the entire site with keyboard only?
- [ ] Can I see where focus is at all times?
- [ ] Do all images have meaningful alt text?
- [ ] Do all form inputs have labels?
- [ ] Is color contrast sufficient (4.5:1 minimum)?
- [ ] Does screen reader read content correctly?
- [ ] Are heading levels logical (h1 → h2 → h3)?
- [ ] Can I escape modals/dialogs with ESC key?
- [ ] Do links describe their destination (not "click here")?
- [ ] Are error messages announced to screen readers?

## React + Next.js Accessibility
```tsx
// Good - Semantic HTML with ARIA
<button
  aria-label="Close dialog"
  onClick={onClose}
  className="focus-visible:ring-2"
>
  <XIcon aria-hidden="true" />
</button>

// Good - Form with labels
<label htmlFor="email">Email</label>
<input
  id="email"
  type="email"
  aria-describedby="email-hint"
/>
<span id="email-hint" className="text-sm">
  We'll never share your email
</span>

// Good - Keyboard navigation
useEffect(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose()
  }
  document.addEventListener('keydown', handleEscape)
  return () => document.removeEventListener('keydown', handleEscape)
}, [onClose])

// Good - Skip to main content link
<a href="#main-content" className="sr-only">
  Skip to main content
</a>

// Good - Focus trap in modal
const modalRef = useRef<HTMLDivElement>(null)
useFocusTrap(modalRef)
```

## Context for FinanceHub
**Relevance:** Critical - Financial platform must be accessible to all traders

**Priority Areas:**
- Trading forms (order entry, limit orders)
- Charts and data visualizations (screen reader alternatives)
- Real-time updates (ARIA live regions)
- Portfolio tables (keyboard navigation)
- Notifications and alerts (ARIA alerts)

**Usage:**
- Design phase: Accessibility requirements in specs
- Development: Implement ARIA attributes, semantic HTML
- Testing: Keyboard navigation, screen reader testing
- Audit: Regular WCAG compliance checks

**Updates:**
- WCAG 2.2 released 2023 (new success criteria)
- New focus appearance requirements
- Improved drag-and-drop requirements
- Target size minimum (24x24px)

**Notes:**
- Accessibility is a legal requirement (ADA, EAA)
- 15% of world population has some form of disability
- Accessible design benefits everyone (not just disabled users)
- Test with real assistive technology, not just automated tools
- Accessibility is ongoing, not one-time fix
