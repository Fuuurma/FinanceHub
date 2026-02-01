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

**"God is in the details."**

- MIES
