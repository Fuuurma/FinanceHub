# 🎯 TASK ASSIGNMENT - Turing (Frontend Coder)

**Date:** February 1, 2026  
**From:** MIES (UI/UX Designer)  
**To:** Turing  
**Priority:** 🔴 CRITICAL  
**Design Decision:** UNIFIED BRUTALIST  

---

## YOUR TASKS

### 🔴 PRIORITY 1: Implement Brutalist CVA Variants (Due: Feb 3)

#### 1.1 Button Component (`components/ui/button.tsx`)

Add these variants to `buttonVariants`:

```tsx
variant: {
  // ... existing variants
  brutalist: "rounded-none border-2 border-foreground bg-foreground text-background font-black uppercase shadow-[4px_4px_0px_0px_var(--foreground)] hover:translate-x-[-1px] hover:translate-y-[-1px] hover:shadow-[5px_5px_0px_0px_var(--foreground)] active:translate-x-[2px] active:translate-y-[2px] transition-all",
  brutalistOutline: "rounded-none border-2 border-foreground bg-transparent text-foreground font-black uppercase shadow-[3px_3px_0px_0px_var(--foreground)] hover:bg-foreground hover:text-background",
  brutalistGhost: "rounded-none font-black uppercase hover:bg-muted",
}

size: {
  // ... existing sizes
  brutalist: "h-10 px-6 text-xs",
  brutalistSm: "h-8 px-4 text-[10px]",
  brutalistLg: "h-12 px-8 text-sm",
}
```

#### 1.2 Tabs Component (`components/ui/tabs.tsx`)

Add variant prop to TabsList and TabsTrigger:

```tsx
interface TabsProps {
  variant?: "default" | "brutalist"
}

function TabsList({ variant = "default", ... }) {
  return (
    <TabsPrimitive.List
      className={cn(
        variant === "brutalist" && "rounded-none border-2 border-foreground bg-muted p-1 h-14",
        variant === "default" && "bg-muted rounded-lg h-9",
        className
      )}
      {...}
    />
  )
}

function TabsTrigger({ variant = "default", ... }) {
  return (
    <TabsPrimitive.Trigger
      className={cn(
        variant === "brutalist" && "rounded-none data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs px-6 h-10",
        variant === "default" && "data-[state=active]:bg-background rounded-md",
        className
      )}
      {...}
    />
  )
}
```

#### 1.3 Badge Component (`components/ui/badge.tsx`)

Add these variants to `badgeVariants`:

```tsx
variant: {
  // ... existing variants
  brutalist: "rounded-none border-2 border-foreground bg-foreground text-background font-mono uppercase text-[10px]",
  brutalistOutline: "rounded-none border-2 border-foreground bg-transparent text-foreground font-mono uppercase text-[10px]",
}
```

---

### 🔴 PRIORITY 2: Refactor ai/page.tsx (Due: Feb 5)

File: `apps/frontend/src/app/(dashboard)/ai/page.tsx`

**Before (current):**
```tsx
<TabsList className="h-14 rounded-none border-2 border-foreground bg-muted p-1">
  <TabsTrigger className="rounded-none data-[state=active]:bg-foreground data-[state=active]:text-background font-black uppercase text-xs px-6 h-10">
```

**After (standardized):**
```tsx
<TabsList variant="brutalist">
  <TabsTrigger variant="brutalist">
```

**Changes needed:**
1. Replace all tab overrides with `variant="brutalist"`
2. Replace brutalist button classes with `variant="brutalist"`
3. Replace brutalist badge classes with `variant="brutalist"`
4. Remove inline brutalist classes (rely on CVA)

---

### 🔴 PRIORITY 3: Refactor news/page.tsx (Due: Feb 7)

File: `apps/frontend/src/app/(dashboard)/news/page.tsx`

**Changes needed:**
1. Replace `rounded-none` buttons with `variant="brutalist"`
2. Replace `rounded-none` badges with `variant="brutalist"`
3. Remove inline brutalist classes

---

### 🟡 PRIORITY 4: Extract Chart Hooks (Due: Feb 10)

Create new hooks:

#### `hooks/useChartData.ts`
```tsx
export function useChartData(symbol: string, type: string, timeframe: string) {
  // Unified data fetching for all charts
}
```

#### `hooks/useChartResize.ts`
```tsx
export function useChartResize(ref: RefObject<HTMLElement>) {
  // Unified resize handling
}
```

#### `hooks/useChartTooltip.ts`
```tsx
export function useChartTooltip() {
  // Unified tooltip logic
}
```

---

### 🟡 PRIORITY 5: Extract AI Hooks (Due: Feb 10)

Create new hooks:

#### `hooks/useSentiment.ts`
```tsx
export function useSentiment(symbol: string) {
  // Sentiment analysis logic
}
```

#### `hooks/usePricePrediction.ts`
```tsx
export function usePricePrediction(symbol: string, horizon: string) {
  // Price prediction logic
}
```

---

## 📋 CHECKLIST

- [ ] button.tsx - Add brutalist variants
- [ ] tabs.tsx - Add brutalist variants
- [ ] badge.tsx - Add brutalist variants
- [ ] ai/page.tsx - Refactor to use variants
- [ ] news/page.tsx - Refactor to use variants
- [ ] useChartData.ts - Create hook
- [ ] useChartResize.ts - Create hook
- [ ] useChartTooltip.ts - Create hook
- [ ] useSentiment.ts - Create hook
- [ ] usePricePrediction.ts - Create hook

---

## 📞 QUESTIONS?

If you have questions:
1. Check docs/design/BRUTALIST_COMPONENT_VARIANTS.md
2. Check docs/design/DESIGN_SYSTEM.md
3. Message me directly

---

## 🎯 SUCCESS

Your tasks are complete when:
1. All brutalist variants implemented
2. ai/page.tsx uses only CVA variants (no inline classes)
3. news/page.tsx uses only CVA variants (no inline classes)
4. All tests pass
5. Design review approved by MIES

---

**"Less is more. God is in the details."**

**START IMMEDIATELY. Deadline: Feb 10.**

- MIES
