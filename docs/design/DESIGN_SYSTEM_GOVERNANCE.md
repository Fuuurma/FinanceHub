# FinanceHub Design System Governance

**Date:** February 1, 2026  
**Author:** MIES (UI/UX Designer)  
**Status:** PROPOSAL

---

## 1. Purpose

This document establishes governance policies for the FinanceHub Design System to ensure consistency, quality, and maintainability across all UI components.

---

## 2. Design Principles

All components must adhere to:

1. **"Less is more"** - Remove unnecessary complexity
2. **Consistency** - Same patterns everywhere
3. **Accessibility** - WCAG 2.1 Level AA minimum
4. **Performance** - Fast load, smooth interactions
5. **Mobile-first** - Design for small screens first

---

## 3. Component Categories

### 3.1 Core Components (shadcn/ui)

These are the foundation of the design system.

| Status | Description |
|--------|-------------|
| ✅ Stable | Fully tested, documented, used widely |
| 🟡 Beta | Tested but needs more usage |
| 🔴 Experimental | New, limited testing |

**Current State:** 71 components, 65 stable, 6 beta

### 3.2 Feature Components

Domain-specific components built on core components.

| Directory | Purpose |
|-----------|---------|
| ai/ | AI and ML features |
| analytics/ | Financial analytics |
| charts/ | Data visualization |
| holdings/ | Portfolio management |
| trading/ | Trading interfaces |

### 3.3 Design Variants

| Variant | Purpose | Usage |
|---------|---------|-------|
| default | Standard UI | Most pages |
| brutalist | Bold design | Landing pages, AI features |
| clean | Minimalist | Data-heavy pages |

---

## 4. Component Lifecycle

### 4.1 Creation Process

1. **Design Phase**
   - Create wireframes
   - Define props interface
   - Choose base component

2. **Implementation**
   - Use CVA for variants
   - Follow naming conventions
   - Add accessibility attributes

3. **Review**
   - MIES reviews for design consistency
   - HADI reviews for accessibility
   - Turing reviews for implementation

4. **Documentation**
   - Add to DESIGN_SYSTEM.md
   - Create usage examples
   - Document props

### 4.2 Deprecation Process

1. **Mark Deprecated**
   - Add `/** @deprecated */` comment
   - Log in DEPRECATION.md
   - Notify developers

2. **Migration Period**
   - Minimum 30 days
   - Provide migration guide
   - Support both old and new

3. **Removal**
   - Remove from exports
   - Delete file
   - Update documentation

---

## 5. Naming Conventions

### 5.1 Component Names

```tsx
// PascalCase for components
function DataTable() {}
function HoldingsCard() {}

// Variant props in camelCase
<Button variant="default" />
<Button variant="brutalist" />
```

### 5.2 CSS Classes

```css
/* Prefix with component name */
.chart-wrapper {}
.chart-tooltip {}

/* Variants use modifier pattern */
.btn-primary {}
.btn-secondary {}

/* Brutalist uses brutalist- prefix */
.brutalist-glass {}
.brutalist-interactive {}
```

### 5.3 File Names

```
components/
├── ui/
│   ├── button.tsx
│   ├── button.stories.tsx
│   └── button.test.tsx
├── charts/
│   ├── line-chart.tsx
│   └── index.ts
```

---

## 6. Variant Standards

### 6.1 Button Variants

| Variant | Purpose | CSS Classes |
|---------|---------|-------------|
| default | Primary actions | bg-primary text-primary-foreground |
| destructive | Danger actions | bg-destructive text-white |
| outline | Secondary actions | border bg-background |
| ghost | Subtle actions | hover:bg-accent |
| link | Inline links | text-primary underline |
| brutalist | Bold design | rounded-none border-2 shadow-[4px_4px_0px_0px] |
| brutalistOutline | Bold secondary | rounded-none border-2 |

### 6.2 Tabs Variants

| Variant | Purpose | CSS Classes |
|---------|---------|-------------|
| default | Standard tabs | rounded-lg h-9 |
| brutalist | Bold tabs | rounded-none h-14 border-2 |

### 6.3 Badge Variants

| Variant | Purpose | CSS Classes |
|---------|---------|-------------|
| default | Standard badge | rounded-full |
| secondary | Subtle badge | bg-secondary |
| destructive | Error badge | bg-destructive |
| outline | Outline badge | border |
| brutalist | Bold badge | rounded-none border-2 font-mono |

---

## 7. Accessibility Requirements

### 7.1 Mandatory for All Components

- [ ] Keyboard accessible
- [ ] Focus visible (`:focus-visible`)
- [ ] ARIA roles where needed
- [ ] Color contrast 4.5:1 minimum
- [ ] Screen reader compatible

### 7.2 Testing Requirements

| Test Type | Frequency |
|-----------|-----------|
| Keyboard navigation | Every PR |
| Screen reader (NVDA/VoiceOver) | Weekly |
| Color contrast | Every PR |
| Automated accessibility tests | CI/CD |

---

## 8. Code Quality Standards

### 8.1 Props Interface

```tsx
interface ButtonProps {
  /** Button content */
  children: React.ReactNode
  /** Visual variant */
  variant?: 'default' | 'outline' | 'ghost' | 'brutalist'
  /** Size */
  size?: 'default' | 'sm' | 'lg' | 'icon'
  /** Click handler */
  onClick?: () => void
  /** Disabled state */
  disabled?: boolean
}
```

### 8.2 Required Features

- [ ] TypeScript interfaces
- [ ] JSDoc comments
- [ ] Unit tests
- [ ] Storybook stories (optional)
- [ ] Example usage

---

## 9. Review Process

### 9.1 Pull Request Requirements

1. **Design Review (MIES)**
   - Check consistency with design system
   - Verify variant usage
   - Review accessibility

2. **Code Review (Turing)**
   - Check TypeScript types
   - Verify CVA usage
   - Performance considerations

3. **Accessibility Review (HADI)**
   - WCAG compliance
   - Screen reader compatibility
   - Keyboard navigation

### 9.2 Merge Criteria

- [ ] All tests pass
- [ ] Design approved
- [ ] Accessibility approved
- [ ] Documentation updated
- [ ] No eslint errors

---

## 10. Versioning

### 10.1 Version Scheme

```
MAJOR.MINOR.PATCH
│     │     │
│     │     └── Bug fixes
│     └────── New features (backward compatible)
└──────────── Breaking changes
```

### 10.2 Changelog

All changes must be documented in CHANGELOG.md:

```markdown
## [1.0.0] - 2026-02-01

### Added
- Design system documentation
- Brutalist component variants

### Changed
- Updated button variants

### Fixed
- Color contrast issues
```

---

## 11. Resources

### 11.1 Documentation

- DESIGN_SYSTEM.md - Complete reference
- BRUTALIST_COMPONENT_VARIANTS.md - Variant guide
- ACCESSIBILITY_REVIEW.md - WCAG checklist
- UI_REFACTORING_PROPOSAL.md - Architecture

### 11.2 Tools

- CVA (Class Variance Authority) - For variants
- Radix UI - For primitives
- Tailwind CSS - For styling
- Lucide React - For icons

---

## 12. Governance Contacts

| Role | Responsibility |
|------|----------------|
| MIES (UI/UX) | Design consistency, visual quality |
| HADI (A11y) | Accessibility compliance |
| Turing (Frontend) | Implementation quality |

---

**"Less is more."**

**Document Version:** 1.0  
**Next Review:** February 15, 2026

- MIES
