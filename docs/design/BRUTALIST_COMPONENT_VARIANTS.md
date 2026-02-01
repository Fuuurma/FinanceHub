# Brutalist Component Variants - Implementation Proposal

**Date:** February 1, 2026  
**Author:** MIES (UI/UX Designer)  
**Status:** READY FOR IMPLEMENTATION

---

## 1. Button Component Variants

### Current button.tsx
```tsx
const buttonVariants = cva("...", {
  variants: {
    variant: {
      default: "bg-primary text-primary-foreground hover:bg-primary/90",
      destructive: "bg-destructive text-white...",
      outline: "border bg-background...",
      secondary: "bg-secondary...",
      ghost: "hover:bg-accent...",
      link: "text-primary underline-offset-4...",
    },
    size: {
      default: "h-9 px-4 py-2",
      sm: "h-8 rounded-md...",
      lg: "h-10 rounded-md...",
      icon: "size-9",
    }
  }
})
```

### Proposed Additions
```tsx
const buttonVariants = cva("...", {
  variants: {
    // ...existing variants
    variant: {
      // ...existing
      brutalist: [
        "rounded-none",
        "border-2",
        "border-foreground",
        "bg-foreground",
        "text-background",
        "font-black",
        "uppercase",
        "shadow-[4px_4px_0px_0px_var(--foreground)]",
        "hover:translate-x-[-1px]",
        "hover:translate-y-[-1px]",
        "hover:shadow-[5px_5px_0px_0px_var(--foreground)]",
        "active:translate-x-[2px]",
        "active:translate-y-[2px]",
        "active:shadow-[2px_2px_0px_0px_var(--foreground)]",
        "transition-all",
      ].join(" "),
      brutalistOutline: [
        "rounded-none",
        "border-2",
        "border-foreground",
        "bg-transparent",
        "text-foreground",
        "font-black",
        "uppercase",
        "shadow-[3px_3px_0px_0px_var(--foreground)]",
        "hover:translate-x-[-1px]",
        "hover:translate-y-[-1px]",
        "hover:bg-foreground",
        "hover:text-background",
      ].join(" "),
      brutalistGhost: [
        "rounded-none",
        "font-black",
        "uppercase",
        "hover:bg-muted",
      ].join(" "),
    },
    size: {
      // ...existing
      brutalist: "h-10 px-6 text-xs",
      brutalistSm: "h-8 px-4 text-[10px]",
      brutalistLg: "h-12 px-8 text-sm",
    }
  }
})
```

### Usage Examples
```tsx
// Standard clean button
<Button variant="default">Action</Button>

// Brutalist button (for AI page, marketing)
<Button variant="brutalist">AI Assistant</Button>

// Brutalist outline
<Button variant="brutalistOutline">Secondary</Button>

// Brutalist ghost
<Button variant="brutalistGhost">Subtle</Button>
```

---

## 2. Tabs Component Variants

### Current tabs.tsx
```tsx
function TabsList({ className, ...props }) {
  return (
    <TabsPrimitive.List
      data-slot="tabs-list"
      className={cn(
        "bg-muted text-muted-foreground inline-flex h-9 w-fit items-center justify-center rounded-lg p-[3px]",
        className
      )}
      {...props}
    />
  )
}
```

### Proposed Addition with Variant
```tsx
// Add variant prop to TabsList
function TabsList({
  className,
  variant = "default",
  ...props
}: React.ComponentProps<typeof TabsPrimitive.List> & { variant?: "default" | "brutalist" }) {
  return (
    <TabsPrimitive.List
      data-slot="tabs-list"
      className={cn(
        variant === "brutalist" && [
          "rounded-none",
          "border-2",
          "border-foreground",
          "bg-muted",
          "p-1",
          "h-14",
        ],
        variant === "default" && [
          "bg-muted",
          "rounded-lg",
          "h-9",
        ],
        className
      )}
      {...props}
    />
  )
}

function TabsTrigger({
  className,
  variant = "default",
  ...props
}: React.ComponentProps<typeof TabsPrimitive.Trigger> & { variant?: "default" | "brutalist" }) {
  return (
    <TabsPrimitive.Trigger
      data-slot="tabs-trigger"
      className={cn(
        variant === "brutalist" && [
          "rounded-none",
          "data-[state=active]:bg-foreground",
          "data-[state=active]:text-background",
          "font-black",
          "uppercase",
          "text-xs",
          "px-6",
          "h-10",
        ],
        variant === "default" && [
          "data-[state=active]:bg-background",
          "rounded-md",
        ],
        className
      )}
      {...props}
    />
  )
}
```

### Usage Examples
```tsx
// Standard clean tabs
<TabsList>
  <TabsTrigger>Tab 1</TabsTrigger>
</TabsList>

// Brutalist tabs
<TabsList variant="brutalist">
  <TabsTrigger variant="brutalist">AI Chat</TabsTrigger>
  <TabsTrigger variant="brutalist">Strategies</TabsTrigger>
</TabsList>
```

---

## 3. Badge Component Variants

### Current badge.tsx
```tsx
const badgeVariants = cva("...", {
  variants: {
    variant: {
      default: "border-transparent bg-primary text-primary-foreground",
      secondary: "border-transparent bg-secondary...",
      destructive: "border-transparent bg-destructive...",
      outline: "text-foreground",
    },
  }
})
```

### Proposed Addition
```tsx
const badgeVariants = cva("...", {
  variants: {
    // ...existing
    variant: {
      // ...existing
      brutalist: [
        "rounded-none",
        "border-2",
        "border-foreground",
        "bg-foreground",
        "text-background",
        "font-mono",
        "uppercase",
        "text-[10px]",
      ].join(" "),
      brutalistOutline: [
        "rounded-none",
        "border-2",
        "border-foreground",
        "bg-transparent",
        "text-foreground",
        "font-mono",
        "uppercase",
        "text-[10px]",
      ].join(" "),
    },
  }
})
```

### Usage Examples
```tsx
// Standard badge
<Badge variant="default">New</Badge>

// Brutalist badge
<Badge variant="brutalist">GLM-4.7</Badge>

// Brutalist outline badge
<Badge variant="brutalistOutline">Beta</Badge>
```

---

## 4. Card Component Classes

### Current Usage
```tsx
<Card className="rounded-xl border shadow-sm">
```

### Proposed Classes (already exist in globals.css)

```css
/* Clean card */
.card-clean {
  @apply rounded-xl border shadow-sm;
}

/* Brutalist card */
.brutalist-card {
  @apply brutalist-glass rounded-none;
}

/* Brutalist card with accent */
.brutalist-card-accent {
  @apply brutalist-glass-accent rounded-none;
}
```

### Usage
```tsx
// Standard clean card
<Card className="card-clean">...</Card>

// Brutalist card
<Card className="brutalist-card">...</Card>
```

---

## 5. Implementation Checklist

- [ ] Update button.tsx with brutalist variants
- [ ] Update tabs.tsx with brutalist variants  
- [ ] Update badge.tsx with brutalist variants
- [ ] Add CSS classes for card variants
- [ ] Update ai/page.tsx to use new variants
- [ ] Update news/page.tsx to use new variants
- [ ] Test all components in both themes
- [ ] Verify accessibility (focus states, keyboard)

---

## 6. Files to Modify

1. `apps/frontend/src/components/ui/button.tsx`
2. `apps/frontend/src/components/ui/tabs.tsx`
3. `apps/frontend/src/components/ui/badge.tsx`
4. `apps/frontend/src/app/globals.css`
5. `apps/frontend/src/app/(dashboard)/ai/page.tsx`
6. `apps/frontend/src/app/(dashboard)/news/page.tsx`

---

## Estimated Effort

| Task | Time |
|------|------|
| Update button.tsx | 30 minutes |
| Update tabs.tsx | 30 minutes |
| Update badge.tsx | 20 minutes |
| Update CSS | 15 minutes |
| Update ai/page.tsx | 45 minutes |
| Update news/page.tsx | 30 minutes |
| **Total** | **~2.5 hours** |

---

**"Less is more."**

**Ready for implementation by Frontend Coder (Turing)**
