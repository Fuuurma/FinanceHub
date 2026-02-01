# FinanceHub Design Standardization Plan

**Document Version:** 1.0  
**Date:** February 1, 2026  
**Author:** MIES (UI/UX Designer)  
**Status:** DRAFT - Awaiting GAUDÍ Approval

---

## Executive Summary

FinanceHub currently operates with **TWO distinct design languages**:
1. **Clean Modern** - shadcn/ui components with 4px radius
2. **Brutalist** - Custom brutalist classes with sharp edges

This document provides a standardization plan to unify the design system.

---

## Current State Analysis

### Files Using Brutalist Styles in Dashboard

| File | Severity | Usage |
|------|----------|-------|
| `ai/page.tsx` | HIGH | Tabs, header, buttons, cards |
| `news/page.tsx` | MEDIUM | Buttons, badges |
| `users/[username]/portfolios/[portfolioId]/page.tsx` | MEDIUM | Header cards |

### Test/Showcase Pages (Intentional)
- `palete/page.tsx` - Design system showcase
- `bruta/page.tsx` - Brutalist showcase  
- `test/page.tsx` - Component testing
- `la/page.tsx` - Layout experiments

---

## Design Language Breakdown

### Clean Modern (shadcn/ui)

**Principles:**
- 4px radius (`--radius: 0.25rem`)
- Subtle shadows
- Muted colors
- Standard spacing (8px grid)

**Usage:**
```tsx
<Card className="rounded-xl">
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
</Card>
```

### Brutalist

**Principles:**
- Sharp edges (`rounded-none`)
- Thick borders (2px-4px)
- Bold shadows (`4px 4px 0px 0px`)
- High contrast
- Uppercase labels

**Usage:**
```tsx
<div className="brutalist-glass border-2 border-foreground">
  <TabsList className="rounded-none border-2 border-foreground">
```

---

## Recommendations

### ⭐ DECISION: UNIFIED BRUTALIST THROUGHOUT ✅ APPROVED

FinanceHub will use a unified brutalist design system throughout the entire application.

**Pros:**
- Distinctive, memorable brand
- Consistent experience
- Easier to maintain one system
- Bold & professional financial aesthetic

**Cons Mitigated:**
- "May feel overwhelming" - Use generous whitespace
- "Accessibility concerns" - Partner with HADI for WCAG compliance

**Implementation:**
1. Create brutalist CVA variants of all shadcn components ✅ IN PROGRESS (Turing)
2. Refactor ai/page.tsx to use standardized brutalist components ✅ PENDING (Turing)
3. Refactor news/page.tsx to use standardized brutalist components ✅ PENDING (Turing)
4. Document brutalist usage rules ✅ COMPLETE (MIES)
5. Verify accessibility with HADI ✅ PENDING (HADI)

---

## Proposed Component Standardization

### Button Component

**Current:**
```tsx
// Standard shadcn
<Button variant="outline">Action</Button>

// Brutalist override  
<Button className="brutalist-interactive rounded-none border-4">Action</Button>
```

**Proposed:**
```tsx
// Add brutalist variant to buttonVariants
const buttonVariants = cva("...", {
  variants: {
    variant: {
      // ... existing variants
      brutalist: "brutalist-interactive rounded-none border-2 border-foreground",
    }
  }
})

// Usage
<Button variant="brutalist">Action</Button>
```

### Tabs Component

**Current:**
```tsx
<TabsList className="h-14 rounded-none border-2 border-foreground bg-muted p-1">
  <TabsTrigger className="rounded-none ...">
```

**Proposed:**
```tsx
// Standard shadcn tabs
<TabsList>
  <TabsTrigger>Tab</TabsTrigger>
</TabsList>

// Brutalist tabs variant
<TabsList variant="brutalist">
  <TabsTrigger variant="brutalist">Tab</TabsTrigger>
</TabsList>
```

### Card Component

**Current:**
```tsx
// Clean
<Card className="rounded-xl">...</Card>

// Brutalist
<div className="brutalist-glass">...</div>
```

**Proposed:**
```tsx
<Card variant="brutalist" className="brutalist-glass">...</Card>
```

---

## Files to Update (If Choosing Option 2)

### Convert to Clean Modern

1. `apps/frontend/src/app/(dashboard)/ai/page.tsx`
   - Remove `rounded-none` from tabs
   - Remove `border-4` from header
   - Use standard `Card` component
   - Remove brutalist button classes

2. `apps/frontend/src/app/(dashboard)/news/page.tsx`
   - Remove `rounded-none` from buttons
   - Remove brutalist badge classes

3. `apps/frontend/src/app/(dashboard)/users/[username]/portfolios/[portfolioId]/page.tsx`
   - Convert brutalist header to standard Card

---

## Accessibility Considerations

### Brutalist Concerns
- Sharp corners may feel harsh (not WCAG violation, but UX concern)
- High contrast is good for visibility
- Ensure focus states remain visible

### Recommendations
- Add `border-radius: 2px` minimum if keeping brutalist
- Test with real users for fatigue
- Consider reducing brutalist intensity in data-heavy areas

---

## Implementation Roadmap

### Week 1
- [ ] GAUDÍ approves design direction
- [ ] Create brutalist component variants
- [ ] Update component library documentation

### Week 2
- [ ] Migrate ai/page.tsx (if Option 2)
- [ ] Migrate news/page.tsx (if Option 2)
- [ ] Update design guidelines

### Week 3-4
- [ ] Complete component standardization
- [ ] Accessibility audit with HADI
- [ ] User feedback collection

---

## Questions for GAUDÍ

1. **Design Direction:** Should FinanceHub use brutalist throughout or only for specific areas?

2. **Timeline:** When should standardization be complete?

3. **Priority:** Is the AI page redesign a priority, or can it wait?

4. **Resources:** Should Turing assist with the frontend changes?

---

## Conclusion

FinanceHub has a distinctive brutalist design language that sets it apart. The key decision is whether to:
- **Embrace it fully** (Option 1) - Distinctive brand, consistent experience
- **Restrict it to marketing** (Option 2) - Better UX for complex features

**Recommendation:** Option 2 with planned brutalist extensions in future phases.

---

**"Less is more. God is in the details."**

- MIES
