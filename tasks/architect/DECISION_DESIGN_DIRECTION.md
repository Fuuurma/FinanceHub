# 🎨 Architect Decision: Unified Design Direction

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** MIES (UI/UX Designer)
**Status:** ✅ APPROVED (REVISED)

---

## 🚨 DECISION: Unified Minimalistic Brutalism

**RECOMMENDATION APPROVED:** Minimalistic Brutalism Across Entire Application

### Design System Architecture

**Single Unified Design Language:**

| Principle | Implementation | Notes |
|-----------|----------------|-------|
| **Brutalist Foundation** | Sharp edges, bold typography, high contrast | Applied consistently across ALL pages |
| **Minimalistic Approach** | Clean spacing, restrained use of brutalist elements | Essential for data-dense interfaces |
| **Unified Experience** | No separation between marketing and dashboard | Seamless transition from landing to app |

### What is "Minimalistic Brutalism"?

**Core Principles:**
1. **Brutalist Base:** Sharp edges (`rounded-none`), bold borders, high contrast
2. **Minimalistic Application:** Use restraint despite data density
3. **Clean Despite Complexity:** Strategic use of whitespace prevents visual chaos
4. **Bold Doesn't Mean Busy:** Brutalist elements used deliberately, not excessively

**Rules of Thumb:**
- ✅ Landing page: Prominent brutalist elements (bold borders, sharp edges)
- ✅ Dashboard: Restrained brutalist (same base, lighter application)
- ✅ Trading interface: Minimal brutalism (focus on data clarity)
- ✅ All pages: Unified design language, no jarring transitions

### Why Minimalistic Brutalism?

**Challenge:** Financial interfaces are data-dense
**Solution:** Brutalist base + minimalistic application
**Result:** Bold, distinctive brand without sacrificing usability

**Example Application:**
```
Landing Page:          Border-4, high contrast, large typography
Dashboard:             Border-2, subtle contrast, medium typography
Trading Interface:     Border-1, standard contrast, focus on data
```

All use brutalist foundation, but with restraint appropriate to context.

---

## ✅ APPROVED ACTIONS

### 1. Delete Test Pages (M-001)

**Decision:** Remove experimental test pages

**Pages to Delete:**
- `apps/frontend/src/app/(dashboard)/palete/page.tsx`
- `apps/frontend/src/app/(dashboard)/bruta/page.tsx`

**Reasoning:**
- Test pages were style exploration for UI
- Design direction now unified (no need for test pages)
- Clean up codebase, remove experimental code

### 2. Unified Button System (M-001)

**Decision:** Create single button system with brutalist variants

```typescript
// components/ui/button.tsx

const buttonVariants = cva(
  "rounded-none", // Brutalist base
  {
    variants: {
      variant: {
        default: "border-2 bg-primary text-primary-foreground",
        outline: "border-2 bg-transparent",
        ghost: "border-0 bg-transparent",
        brutalist: "border-4 bg-primary text-primary-foreground", // For landing
      }
    }
  }
)
```

**Usage Rules:**
- All buttons use brutalist base (`rounded-none`)
- Landing pages: `variant="brutalist"` (bold borders)
- Dashboard: `variant="default"` (standard borders)
- Trading interface: `variant="outline"` (subtle borders)

### 3. Consistent Border System (M-001)

**Decision:** Unified border system across all components

```css
/* Brutalist base - all components */
:root {
  --border-width-landing: 4px;
  --border-width-dashboard: 2px;
  --border-width-subtle: 1px;
}

/* Landing pages */
.landing-element {
  border: var(--border-width-landing) solid var(--primary);
  border-radius: 0;
}

/* Dashboard elements */
.dashboard-element {
  border: var(--border-width-dashboard) solid var(--border);
  border-radius: 0;
}

/* Data-dense elements (trading interface) */
.data-element {
  border: var(--border-width-subtle) solid var(--muted);
  border-radius: 0;
}
```

**Key Point:** All elements have `border-radius: 0` (brutalist), but border width varies by context.

---

## 📋 NEXT ACTIONS FOR MIES

### Immediate (This Week)

1. ✅ **Component Inventory** - COMPLETED
2. 🗑️ **Delete Test Pages** - Remove `/palete` and `/bruta` pages
3. ⏳ **Document Unified Design System** - Create `docs/design/DESIGN_SYSTEM.md`
   - Explain minimalistic brutalism approach
   - Show how to apply restraint despite data density
   - Examples of appropriate use across contexts

4. ⏳ **Implement Unified Button System**
   - Update `components/ui/button.tsx` with brutalist variants
   - Apply `rounded-none` as base for all buttons
   - Create variant system for different contexts

5. ⏳ **Update Component Library**
   - Apply `border-radius: 0` to all components
   - Implement tiered border width system
   - Ensure consistent brutalist foundation

### This Month

6. **Component Standardization** (M-004)
   - Update all components to unified brutalist base
   - Fix inconsistent border radii
   - Target: 95% consistency (up from 60%)

7. **Design Guidelines Document** (M-003)
   - Minimalistic brutalism principles
   - Spacing rules (8px grid)
   - Typography scale
   - Color palette with OKLCH values
   - When to use bold vs subtle brutalism

8. **Accessibility Review** (with HADI)
   - Test brutalist design for WCAG compliance
   - Ensure sharp edges don't break accessibility
   - Check color contrast with bold borders
   - Keyboard navigation testing

---

## 🎯 SUCCESS METRICS

**Consistency Target:**
- **Current:** 60% consistent
- **Target (Month 1):** 85% consistent
- **Target (Month 2):** 95% consistent

**Design System Health:**
- ✅ Unified brutalist foundation across all components
- ✅ Minimalistic application for data-dense interfaces
- ✅ Documented usage rules (when to be bold vs subtle)
- ✅ Seamless user experience (no jarring transitions)

---

## 🚨 CRITICAL REMINDERS

1. **Unified Foundation** - All pages use brutalist base (`rounded-none`)
2. **Contextual Application** - Landing=bold, Dashboard=standard, Trading=subtle
3. **Minimalistic Restraint** - Data density requires careful use of brutalist elements
4. **Document Everything** - Clear examples of appropriate usage
5. **Delete Test Pages** - Remove `/palete` and `/bruta` pages immediately

---

## 📊 DESIGN SYSTEM UNIFICATION

| Aspect | Landing Pages | Dashboard | Trading Interface |
|--------|--------------|-----------|-------------------|
| **Radius** | `rounded-none` | `rounded-none` | `rounded-none` |
| **Borders** | `border-4` (bold) | `border-2` (standard) | `border-1` (subtle) |
| **Typography** | Large, bold | Medium, professional | Standard, data-focused |
| **Contrast** | High contrast | Standard contrast | Careful contrast (data clarity) |
| **Goal** | Bold, memorable | Usable, consistent | Clear, functional |

**Key Insight:** Same brutalist foundation, different level of application based on context.

---

**Decision:** ✅ APPROVED - Proceed with Unified Minimalistic Brutalism
**Next Step:** MIES to delete test pages, update components, document design system
**Review Date:** February 15, 2026 (check progress)

---

🎨 *GAUDÍ - Architect*

🏗️ *Design Foundation: Unified Brutalism with Minimalistic Restraint*

*"Less is more. God is in the details." - Mies van der Rohe*
