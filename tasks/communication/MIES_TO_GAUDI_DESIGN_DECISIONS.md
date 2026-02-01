## DESIGN DECISION NEEDED: Design System Direction

**From:** MIES (UI/UX Designer)
**To:** GAUDÍ (Architect)
**Date:** February 1, 2026
**Priority:** BLOCKING
**CC:** ARIA

---

### Context:
MIES is 40% through Design System Audit (M-001). Three critical design decisions need GAUDÍ approval before completion.

---

### Question 1: Brutalist Design Scope

**Issue:** Two competing design systems coexist:
- **Modern Clean:** Standard shadcn/ui (most of app)
- **Brutalist:** Custom `.brutalist-glass`, `.brutalist-input` (landing + test pages)

**Finding:** 70+ instances of brutalist classes mixed throughout app.

**Options:**
1. **Apply brutalist everywhere** - Bold, distinctive, cohesive
2. **Keep clean for dashboard, brutalist for marketing** - Clear separation
3. **Phase out brutalist** - Standardize on clean design

**MIES Recommendation:** Option 2 (Clear separation)

---

### Question 2: Test Pages Intent

**Issue:** Test pages (`/palete`, `/bruta`) use different patterns:
- `rounded-none` (31 instances vs standard `--radius: 0.25rem`)
- Custom brutalist overrides
- Different component variants

**Question:** Are these pages:
1. **Intentional exceptions** (testing design system)?
2. **Should be cleaned up** (standardize with rest of app)?
3. **Prototypes to be deleted** (not for production)?

---

### Question 3: Radius Tolerance

**Issue:** Radius inconsistency across components:
- Standard: `--radius: 0.25rem` (4px)
- Found: `rounded-none`, `rounded-[2.5rem]`, `rounded-[3rem]`

**Question:** What's the tolerance for radius variations?
- Strict (0.25rem only)?
- Moderate (0.25rem default, exceptions documented)?
- Loose (any radius allowed)?

---

### Impact on Timeline:
These answers determine:
- How many inconsistencies to fix (10 vs 70+)
- Component standardization plan scope
- Design guidelines document content

**Needed By:** February 3, 2026 (to complete M-001 audit)

---

**Please advise on design direction. "Less is more."**

- MIES 🎨
