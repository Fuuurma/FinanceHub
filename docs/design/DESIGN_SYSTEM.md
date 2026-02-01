# FinanceHub Design System

**Version:** 1.0  
**Created:** February 1, 2026  
**Author:** MIES (UI/UX Designer)

---

## Design Philosophy

**"Less is more"** - Remove everything unnecessary. Form follows function. Consistency over creativity.

---

## Color System (OKLCH)

### Primary
| Token | Light | Dark |
|-------|-------|------|
| `--background` | oklch(0.98 0 0) | oklch(0.12 0 0) |
| `--foreground` | oklch(0.15 0 0) | oklch(0.98 0 0) |
| `--card` | oklch(1 0 0) | oklch(0.16 0 0) |

### Brand
| Token | Light | Dark |
|-------|-------|------|
| `--brand` | oklch(0.55 0.18 250) | oklch(0.65 0.20 250) |

### Semantic
| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--success` | oklch(0.60 0.18 145) | oklch(0.65 0.20 145) | Gains |
| `--destructive` | oklch(0.55 0.22 25) | oklch(0.65 0.22 25) | Errors |
| `--warning` | oklch(0.70 0.18 85) | oklch(0.75 0.20 85) | Warnings |
| `--info` | oklch(0.60 0.15 250) | oklch(0.65 0.18 250) | Info |

### Charts
| Token | Light | Dark |
|-------|-------|------|
| `--chart-1` | oklch(0.60 0.18 250) | oklch(0.65 0.20 250) |
| `--chart-2` | oklch(0.65 0.16 180) | oklch(0.70 0.18 180) |
| `--chart-3` | oklch(0.55 0.15 210) | oklch(0.60 0.17 210) |
| `--chart-4` | oklch(0.70 0.17 160) | oklch(0.75 0.19 160) |
| `--chart-5` | oklch(0.60 0.16 200) | oklch(0.65 0.18 200) |

---

## Typography

### Font Family
- `--font-sans`: var(--font-geist-sans) - Primary text
- `--font-mono`: var(--font-geist-mono) - Code, data

### Text Sizes
| Token | Size | Usage |
|-------|------|-------|
| text-xs | 0.75rem | Labels |
| text-sm | 0.875rem | Secondary |
| text-base | 1rem | Body |
| text-lg | 1.125rem | Lead |
| text-xl | 1.25rem | Heading |
| text-2xl | 1.5rem | Heading |
| text-3xl | 1.875rem | Page title |

### Letter Spacing
| Token | Value | Usage |
|-------|-------|-------|
| tracking-widest | 0.2em | UPPERCASE LABELS |
| tracking-wide | 0.025em | Caps |

---

## Spacing (8px Grid)

| Token | Pixels | Usage |
|-------|--------|-------|
| space-2 | 8px | Standard gap |
| space-3 | 12px | Medium gap |
| space-4 | 16px | Component padding |
| space-6 | 24px | Card padding |
| space-8 | 32px | Section |

---

## Corner Radius

**Base:** `--radius: 0.25rem` (4px)

| Token | Value | Usage |
|-------|-------|-------|
| rounded-sm | calc(var(--radius) - 4px) | Small |
| rounded-md | calc(var(--radius) - 2px) | Buttons |
| rounded-lg | var(--radius) | Cards |
| rounded-xl | calc(var(--radius) + 4px) | Large |

---

## Components (shadcn/ui)

### Buttons
**File:** `components/ui/button.tsx`

| Variant | Usage |
|---------|-------|
| default | Primary actions |
| destructive | Delete/danger |
| outline | Secondary |
| ghost | Subtle |
| link | Inline |

| Size | Class |
|------|-------|
| default | h-9 px-4 py-2 |
| sm | h-8 px-3 |
| lg | h-10 px-6 |
| icon | size-9 |

### Cards
```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content</CardContent>
  <CardFooter>Actions</CardFooter>
</Card>
```

---

## Design Patterns

### Liquid Glass
| Class | Usage |
|-------|-------|
| liquid-glass | Cards, panels |
| liquid-glass-subtle | Subtle backgrounds |
| liquid-glass-strong | Featured cards |
| liquid-glass-positive | Gain indicators |
| liquid-glass-negative | Loss indicators |

```tsx
<div className="liquid-glass p-6">
  Content
</div>
```

### Brutalist (Landing Pages Only)
| Class | Usage |
|-------|-------|
| brutalist-glass | Marketing cards |
| brutalist-interactive | Buttons |
| brutalist-input | Inputs |

**When to use brutalist:**
- Landing page hero
- Marketing pages
- Feature highlights

**When NOT to use brutalist:**
- Dashboard panels
- Data tables
- Forms
- Navigation

---

## Accessibility (WCAG 2.1 AA)

### Contrast Ratios
| Element | Minimum |
|---------|---------|
| Normal text | 4.5:1 |
| Large text | 3:1 |
| UI components | 3:1 |

### Requirements
- All interactive elements keyboard-accessible
- Visible focus states
- Semantic HTML
- ARIA labels where needed

---

## Usage Guidelines

### DO
- Use design tokens (never hardcode colors)
- Use shadcn/ui components
- Maintain 8px grid spacing
- Use semantic colors for feedback

### DON'T
- Use `rounded-none` (breaks consistency)
- Mix brutalist with clean in dashboard
- Hardcode pixel values
- Skip focus states

---

## Minimalistic Brutalism Design System (Phase 1)

**Added:** February 1, 2026
**Author:** MIES (UI/UX Designer)

### Core Principles

1. **Brutalist Foundation:** `rounded-none` everywhere, sharp edges
2. **Tiered Border Widths:**
   - Landing: `border-4` (bold, marketing)
   - Dashboard: `border-2` (standard)
   - Trading: `border-1` (subtle, data-dense)
3. **Clean Despite Complexity:** Strategic whitespace for data interfaces
4. **Data Clarity First:** Financial interfaces require maximum readability

### Border System

| Context | Width | Class | Radius | Usage |
|---------|-------|-------|--------|-------|
| Landing | 4px | `border-4` | `rounded-none` | Hero, marketing cards |
| Dashboard | 2px | `border-2` | `rounded-none` | Standard cards, buttons |
| Trading | 1px | `border-1` | `rounded-none` | Tables, forms, data |
| Subtle | 0.5px | `border-[0.5px]` | `rounded-none` | Grid lines |

### Brutalist Component Classes

#### Buttons
```css
.btn-brutalist {
  @apply rounded-none border-2 border-foreground bg-foreground text-background font-black uppercase shadow-[4px_4px_0px_0px_var(--foreground)] transition-all;
}

.btn-brutalist-outline {
  @apply rounded-none border-2 border-foreground bg-transparent text-foreground font-black uppercase shadow-[3px_3px_0px_0px_var(--foreground)];
}

.btn-trading {
  @apply rounded-none border-1 bg-primary text-primary-foreground;
}
```

#### Cards
```css
.card-landing {
  @apply rounded-none border-4 p-8;
}

.card-dashboard {
  @apply rounded-none border-2 p-6;
}

.card-trading {
  @apply rounded-none border-1 p-4;
}
```

#### Badges
```css
.badge-brutalist {
  @apply rounded-none border-2 border-foreground bg-foreground text-background font-mono uppercase text-[10px];
}

.badge-trading {
  @apply rounded-none border-1 px-2 py-0.5 text-xs;
}
```

### Phase 1 Feature Applications

| Feature | Card Border | Button Style | Table Border |
|---------|-------------|--------------|--------------|
| C-036 Paper Trading | `border-1` | Trading | `border-1` |
| C-037 Social Sentiment | `border-1` | Trading | `border-1` |
| C-030 Broker Integration | `border-2` | Dashboard | `border-1` |

### Accessibility (WCAG 2.1 AA)

- Minimum contrast ratio: 4.5:1
- Focus indicators: `focus-visible:ring-2 focus-visible:ring-offset-2`
- Touch targets: 44x44px minimum
- Keyboard navigation: All interactive elements accessible

### When to Use Brutalist vs Clean

| Context | Style | Example |
|---------|-------|---------|
| Landing pages | Brutalist (border-4) | Hero sections, feature cards |
| Dashboard | Minimalistic (border-2) | Standard cards, nav |
| Trading/Data | Minimalistic (border-1) | Tables, forms, charts |
| AI/News pages | Brutalist variants | Special feature sections |

### Design System Files Updated

- `docs/design/DESIGN_SYSTEM.md` (this file)
- `docs/design/PHASE_1_DESIGN_MOCKUPS.md`
- `docs/design/PHASE_1_COMPONENT_SPECS.md`
- `docs/design/PHASE_1_USER_FLOWS.md`
- `docs/design/PHASE_1_RESPONSIVE_DESIGNS.md`

---

**"God is in the details."**

- MIES
