# FinanceHub Component Usage Audit

**Date:** February 1, 2026  
**Author:** MIES (UI/UX Designer)

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total component usages (variant=) | 528 |
| Files with custom className | 239 |
| Tabs component usages | 319 |
| Brutalist rounded-none instances | 30+ |

---

## Component Pattern Analysis

### Buttons - 528 variant usages

**Standard Pattern (shadcn):**
```tsx
<Button variant="default">Action</Button>
<Button variant="outline">Secondary</Button>
<Button variant="ghost">Subtle</Button>
<Button variant="destructive">Danger</Button>
```

**Brutalist Pattern Found (3+ variants):**
```tsx
// Pattern 1: Full brutalist
<Button className="brutalist-interactive rounded-none border-4 border-foreground bg-foreground text-background font-black uppercase shadow-[6px_6px_0px_0px_var(--foreground)]">

// Pattern 2: Border + uppercase
<Button className="rounded-none border-2 border-foreground h-9 font-black uppercase text-[10px] brutalist-interactive">

// Pattern 3: Shadow push effect
<Button className="h-12 px-6 rounded-none border-2 border-background bg-transparent hover:bg-background hover:text-foreground font-black uppercase text-xs shadow-[4px_4px_0px_0px_var(--foreground)]">
```

### Tabs - 319 usages

**Standard Pattern (shadcn):**
```tsx
<TabsList className="bg-muted rounded-lg h-9">
  <TabsTrigger className="data-[state=active]:bg-background rounded-md">
```

**Brutalist Pattern Found (9+ instances):**
```tsx
// Pattern 1: Sharp tabs (ai/page.tsx)
<TabsList className="h-14 rounded-none border-2 border-foreground bg-muted p-1">
  <TabsTrigger className="rounded-none data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs px-6 h-10">
```

### Cards - Standard pattern

**Standard (shadcn):**
```tsx
<Card className="rounded-xl border shadow-sm">
  <CardHeader>...</CardHeader>
</Card>
```

**Brutalist Pattern Found:**
```tsx
<Card className="brutalist-glass rounded-none">
<div className="brutalist-glass border-4 border-foreground">
```

### Badges - 528+ usages

**Standard (shadcn):**
```tsx
<Badge variant="default">Label</Badge>
<Badge variant="outline">Label</Badge>
```

**Brutalist Pattern Found:**
```tsx
<Badge className="rounded-none border-2 border-green-600 bg-green-600 text-white font-mono text-xs">
<Badge variant="outline" className="rounded-none border-2 border-primary px-3 py-1 font-mono uppercase text-xs">
```

---

## Files Requiring Attention

### Critical (Production Pages)

| File | Severity | Issues |
|------|----------|--------|
| `ai/page.tsx` | HIGH | 9+ brutalist overrides, tabs, buttons, header |
| `news/page.tsx` | MEDIUM | 3+ brutalist buttons/badges |
| `users/[username]/portfolios/[portfolioId]/page.tsx` | MEDIUM | Brutalist headers |

### Test Pages (Intentional)

| File | Purpose |
|------|---------|
| `palete/page.tsx` | Design system showcase |
| `bruta/page.tsx` | Brutalist showcase |
| `test/page.tsx` | Component testing |
| `la/page.tsx` | Layout experiments |

---

## Recommendation Summary

| Component | Current State | Recommended State |
|-----------|---------------|-------------------|
| Button | 2 systems fighting | Add `variant="brutalist"` to CVA |
| Tabs | 2 systems fighting | Add brutalist class variants |
| Badge | 2 systems fighting | Add brutalist variants |
| Card | Mixed usage | Clarify usage rules |

---

**"God is in the details."**

- MIES
