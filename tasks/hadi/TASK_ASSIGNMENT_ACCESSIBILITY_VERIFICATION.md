# 🎯 TASK ASSIGNMENT - HADI (Accessibility Specialist)

**Date:** February 1, 2026  
**From:** MIES (UI/UX Designer)  
**To:** HADI  
**Priority:** 🔴 CRITICAL  
**Design Decision:** UNIFIED BRUTALIST  

---

## COLLABORATION: BRUTALIST ACCESSIBILITY VERIFICATION

MIES and HADI will work together to ensure brutalist components meet WCAG 2.1 Level AA standards.

---

## YOUR TASKS

### 🔴 PRIORITY 1: Verify Brutalist CVA Variants (Due: Feb 3)

Review the brutalist variants Turing implements:

#### 1.1 Button Variants

| Variant | Class | Check |
|---------|-------|-------|
| brutalist | `rounded-none border-2 border-foreground` | Focus visible? |
| brutalistOutline | `rounded-none border-2 border-foreground` | Focus visible? |
| brutalistGhost | `rounded-none font-black uppercase` | Focus visible? |

**Verify:**
- [ ] `:focus-visible` outline is visible on all variants
- [ ] Focus ring color contrasts 3:1 minimum
- [ ] Keyboard navigation works
- [ ] No focus trap issues

#### 1.2 Tabs Variants

| State | Class | Check |
|-------|-------|-------|
| Default | `rounded-lg h-9` | Focus visible? |
| Brutalist | `rounded-none h-14 border-2` | Focus visible? |
| Active | `data-[state=active]:bg-foreground` | Color contrast? |

**Verify:**
- [ ] Tab focus indicator visible
- [ ] Arrow key navigation works
- [ ] Tab list keyboard accessible
- [ ] Active tab indicator color1.3 Badge contrast

####  Variants

| Variant | Class | Check |
|---------|-------|-------|
| brutalist | `rounded-none border-2` | Focus visible? |
| brutalistOutline | `rounded-none border-2` | Color contrast? |

**Verify:**
- [ ] Badge focus visible if interactive
- [ ] Text color contrast 4.5:1 minimum

---

### 🔴 PRIORITY 2: Test ai/page.tsx (Due: Feb 5)

File: `apps/frontend/src/app/(dashboard)/ai/page.tsx`

After Turing's refactor, test:

- [ ] All tabs keyboard accessible
- [ ] All buttons keyboard accessible
- [ ] All badges readable (contrast)
- [ ] Focus order logical
- [ ] Skip links work
- [ ] Screen reader can navigate
- [ ] No aria-invalid states triggered
- [ ] Error messages announced (if any)
- [ ] Form labels present (if any)
- [ ] Dynamic updates announced (if any)

---

### 🔴 PRIORITY 3: Test news/page.tsx (Due: Feb 7)

File: `apps/frontend/src/app/(dashboard)/news/page.tsx`

After Turing's refactor, test:

- [ ] All buttons keyboard accessible
- [ ] All badges readable (contrast)
- [ ] Focus order logical
- [ ] Screen reader can navigate

---

### 🟡 PRIORITY 4: Document Accessibility Requirements (Due: Feb 10)

Create `docs/design/BRUTALIST_ACCESSIBILITY.md`:

```markdown
# Brutalist Component Accessibility Requirements

## Button (brutalist variant)

### Focus State
- Always show `:focus-visible` outline
- Outline color: `var(--ring)` on light, `var(--ring)` on dark
- Outline width: 2px minimum
- Outline offset: 2px

### Color Contrast
- Text on background: 12.3:1 (passes AAA)
- Border on background: 3:1 minimum (passes AA)

### Keyboard
- Tab to button
- Enter/Space to activate
- No keyboard traps

## Tabs (brutalist variant)

### Focus State
- Focus indicator on active tab trigger
- Arrow key navigation between tabs

### Color Contrast
- Active tab: foreground on background (12.3:1)
- Inactive tab: foreground on muted (5.0:1)

### Keyboard
- Tab to tab list
- Arrow keys to navigate
- Enter/Space to activate
```

---

## 📋 CHECKLIST

- [ ] button.tsx brutalist variants verified
- [ ] tabs.tsx brutalist variants verified
- [ ] badge.tsx brutalist variants verified
- [ ] ai/page.tsx accessibility test complete
- [ ] news/page.tsx accessibility test complete
- [ ] BRUTALIST_ACCESSIBILITY.md documented

---

## 📞 COLLABORATION WITH MIES

**Weekly Sync:** Friday 4:00 PM

**During sync, discuss:**
1. Accessibility issues found
2. Solutions implemented
3. Pattern updates needed
4. WCAG compliance status

**Communication:**
- Message me directly for design questions
- Tag in PRs for accessibility review
- Update ACCESSIBILITY_REVIEW.md with findings

---

## 🎯 SUCCESS

Your tasks are complete when:
1. All brutalist variants verified WCAG 2.1 AA compliant
2. ai/page.tsx passes accessibility audit
3. news/page.tsx passes accessibility audit
4. BRUTALIST_ACCESSIBILITY.md documented
5. No critical accessibility issues

---

## 📚 REFERENCE

- docs/design/ACCESSIBILITY_REVIEW.md - WCAG checklist
- docs/design/BRUTALIST_COMPONENT_VARIANTS.md - Variant specs
- docs/design/DESIGN_SYSTEM_GOVERNANCE.md - A11y requirements

---

**"Accessibility is not optional."**

**START IMMEDIATELY. Deadline: Feb 10.**

- MIES
