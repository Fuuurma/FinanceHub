# 🎨 Architect Decision: Unified Design Direction

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** MIES (UI/UX Designer)
**Status:** ✅ APPROVED

---

## 🚨 DECISION: Hybrid Design System

**RECOMMENDATION APPROVED:** Unified Brutalist + Clean Hybrid

### Design System Architecture

**Two Design Languages, Clear Separation:**

| Context | Design System | Components | Usage |
|---------|--------------|------------|-------|
| **Marketing/Public Pages** | **Brutalist** | `.brutalist-glass`, `.brutalist-interactive`, `rounded-none` | Landing, pricing, about, public features |
| **Dashboard/App Pages** | **Modern Clean** | Standard shadcn/ui with CVA variants | All user-facing app functionality |
| **Auth Pages** | **Brutalist** | Bold, distinctive | Login, signup, password reset (first impression) |

### Rules of Thumb

**When to Use Brutalist:**
- ✅ Landing page (`/`)
- ✅ Pricing page (`/pricing`)
- ✅ About page (`/about`)
- ✅ Auth pages (`/login`, `/signup`, `/reset`)
- ✅ Public feature pages
- ✅ Marketing materials

**When to Use Clean (shadcn):**
- ✅ Dashboard (`/dashboard`)
- ✅ Portfolio pages
- ✅ Trading interface
- ✅ Settings/Preferences
- ✅ All internal app pages
- ✅ User workflows

**Never Mix:**
- ❌ Don't use brutalist classes in dashboard components
- ❌ Don't use clean components on landing page (unless intentional)
- ❌ Don't create hybrid components (choose one system per component)

---

## ✅ APPROVED ACTIONS

### 1. Fix Radius Inconsistency (M-001)

**Decision:**
- **Landing/Marketing:** `rounded-none` is ACCEPTABLE (brutalist aesthetic)
- **Dashboard/App:** MUST use `--radius: 0.25rem` consistently
- **Remove** `rounded-none` from dashboard components

**Implementation:**
```css
/* Dashboard components */
.dashboard-component {
  border-radius: var(--radius); /* 0.25rem */
}

/* Landing/Marketing components */
.marketing-component {
  border-radius: 0; /* Brutalist sharp edges */
}
```

### 2. Standardize Buttons (M-001)

**Decision:** Create TWO button variants in CVA

```typescript
// components/ui/button.tsx

// Variant 1: Standard (for dashboard)
const buttonVariants = cva(
  // ... base styles
  {
    variants: {
      variant: {
        default: "...",
        outline: "...",
        ghost: "...",
        // Standard shadcn variants
      }
    }
  }
)

// Variant 2: Brutalist (for marketing)
const brutalistButtonVariants = cva(
  "brutalist-interactive rounded-none border-4",
  {
    variants: {
      variant: {
        default: "border-primary bg-primary text-primary-foreground",
        outline: "border-primary bg-transparent text-primary",
      }
    }
  }
)
```

**Usage Rules:**
- Dashboard → `Button` component (standard)
- Landing/Marketing → `BrutalistButton` component (or `Button variant="brutalist"`)

### 3. Test Pages Clarification

**Decision:** Test pages (`/palete`, `/bruta`) are EXPERIMENTAL and can be exceptions

**Action:**
- Keep test pages as-is (they're for design exploration)
- Add comment at top of file: `/* TEST PAGE - Design exploration, not production */`
- Don't count toward consistency metrics

---

## 📋 NEXT ACTIONS FOR MIES

### Immediate (This Week)

1. ✅ **Component Inventory** - COMPLETED
2. ⏳ **Document Design System** - Create `docs/design/DESIGN_SYSTEM.md`
   - Clear rules for when to use brutalist vs clean
   - Examples of correct usage
   - Do's and don'ts

3. ⏳ **Fix Critical Inconsistencies**
   - Remove `rounded-none` from dashboard components (keep only in marketing)
   - Create brutalist button variant
   - Document component usage rules

4. ⏳ **Accessibility Review** (with HADI)
   - Test both design systems for WCAG compliance
   - Ensure brutalist doesn't break accessibility
   - Check color contrast in both systems

### This Month

5. **Component Standardization** (M-004)
   - Fix all 8 critical inconsistencies
   - Fix all 15 medium inconsistencies
   - Target: 95% consistency (up from 60%)

6. **Design Guidelines Document** (M-003)
   - Spacing rules (8px grid)
   - Typography scale
   - Color palette with OKLCH values
   - Component patterns

7. **Accessibility Audit** (H-001, H-002)
   - Full WCAG 2.1 Level AA audit
   - Fix critical accessibility issues (5 priority)
   - Keyboard navigation testing

---

## 🎯 SUCCESS METRICS

**Consistency Target:**
- **Current:** 60% consistent
- **Target (Month 1):** 85% consistent
- **Target (Month 2):** 95% consistent

**Design System Health:**
- ✅ Clear separation of brutalist vs clean
- ✅ No mixed components
- ✅ Documented usage rules
- ✅ All components follow one system or the other

---

## 🚨 CRITICAL REMINDERS

1. **Dashboard = Clean** - Users spend 95% of time here, must be consistent
2. **Landing = Brutalist** - First impression, should be bold and distinctive
3. **No Hybrids** - Components should be ONE system or the OTHER
4. **Document Everything** - Clear rules prevent future inconsistency

---

## 📊 DESIGN SYSTEM COMPARISON

| Aspect | Brutalist (Marketing) | Clean (Dashboard) |
|--------|---------------------|-------------------|
| **Radius** | `rounded-none` (sharp) | `0.25rem` (subtle) |
| **Borders** | `border-4` (bold) | `border` (standard) |
| **Shadows** | Minimal/none | Liquid glass effects |
| **Colors** | High contrast | Professional palette |
| **Usage** | 5% of pages | 95% of pages |
| **Goal** | Bold, memorable | Consistent, usable |

---

**Decision:** ✅ APPROVED - Proceed with Hybrid Design System
**Next Step:** MIES to implement fixes and document design system
**Review Date:** February 15, 2026 (check progress)

---

🎨 *GAUDÍ - Architect*

🏗️ *Design Foundation: Consistency Where It Matters Most*

*"Less is more. God is in the details." - Mies van der Rohe*
