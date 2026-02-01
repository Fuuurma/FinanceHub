# Accessibility Best Practices - Existing Code Patterns

**For:** Turing and future developers
**Based on:** FinanceHub codebase accessibility patterns

---

## Reusable Accessibility Components Already Available

### 1. SkipLink Component
**Location:** `components/ui/SkipLink.tsx`

```tsx
import { SkipLink } from '@/components/ui/SkipLink'

// Use at top of every page
export default function Page() {
  return (
    <>
      <SkipLink />
      <main id="main-content">
        {/* Page content */}
      </main>
    </>
  )
}
```

---

### 2. Accessible Form Pattern (react-hook-form + Radix)
**Location:** `components/ui/form.tsx`

The codebase uses `react-hook-form` with Radix UI components:

```tsx
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'

export function AccessibleForm() {
  const form = useForm()

  return (
    <Form {...form}>
      <FormField
        control={form.control}
        name="email"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Email <span aria-hidden="true">*</span></FormLabel>
            <FormControl>
              <Input {...field} aria-required="true" />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </Form>
  )
}
```

---

### 3. Accessible Select (Radix UI)
**Location:** `components/ui/select.tsx`

```tsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

// Always add aria-label to SelectTrigger
<Select>
  <SelectTrigger aria-label="Filter by status">
    <SelectValue placeholder="All" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="all">All</SelectItem>
    <SelectItem value="active">Active</SelectItem>
  </SelectContent>
</Select>
```

---

### 4. Accessible Dialog (Radix UI)
**Location:** `components/ui/dialog.tsx`

```tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'

<Dialog open={open} onOpenChange={setOpen}>
  <DialogContent className="rounded-none border-2">
    <DialogHeader>
      <DialogTitle className="font-black uppercase">Confirm Order</DialogTitle>
      <DialogDescription className="font-mono text-xs">
        Review your order before executing
      </DialogDescription>
    </DialogHeader>
    {/* Content */}
  </DialogContent>
</Dialog>
```

---

### 5. Accessible Button Loading State
```tsx
<Button aria-busy={loading} disabled={loading}>
  {loading ? (
    <>
      <span className="animate-spin mr-2">⟳</span>
      Loading...
    </>
  ) : (
    'Submit'
  )}
</Button>
```

---

### 6. Accessible Alert
```tsx
import { Alert, AlertDescription } from '@/components/ui/alert'

<Alert variant="destructive" role="alert">
  <AlertDescription>
    Error: {errorMessage}
  </AlertDescription>
</Alert>
```

---

### 7. Accessible Table Pattern
```tsx
<table>
  <caption className="sr-only">Transaction history with date, amount, and status</caption>
  <thead>
    <tr>
      <th scope="col">Date</th>
      <th scope="col">Amount</th>
      <th scope="col">Status</th>
    </tr>
  </thead>
  <tbody>
    {/* rows */}
  </tbody>
</table>
```

---

### 8. Accessible Icon-Only Button
```tsx
<Button variant="ghost" size="icon" aria-label="Refresh data">
  <RefreshCw className="h-4 w-4" />
</Button>
```

---

### 9. Accessible Progress Indicator
```tsx
<Progress 
  value={value} 
  aria-label={`Progress: ${value} percent`}
  aria-valuenow={value}
  aria-valuemin={0}
  aria-valuemax={100}
/>
```

---

### 10. Accessible Tabs (Radix UI)
```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'

<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>
```

---

## Quick Copy-Paste Patterns

### Skip Link Pattern
```tsx
import { SkipLink } from '@/components/ui/SkipLink'

<SkipLink />
<main id="main-content">
```

### Accessible P/L Cell
```tsx
import { TrendingUp, TrendingDown } from 'lucide-react'

<td className={pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
  {pnl >= 0 ? <TrendingUp className="inline h-4 w-4 mr-1" aria-hidden="true" /> : <TrendingDown className="inline h-4 w-4 mr-1" aria-hidden="true" />}
  {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
</td>
```

### Accessible Error Message
```tsx
{error && (
  <p id={`${fieldId}-error`} role="alert" className="text-red-600 text-sm mt-1">
    {error}
  </p>
)}
```

### Accessible Loading State
```tsx
{loading ? (
  <div role="status" aria-live="polite" aria-busy={true}>
    <span className="sr-only">Loading data</span>
    {/* Skeleton content */}
  </div>
) : (
  /* Actual content */
)}
```

---

## Resources in Codebase

| Resource | Location |
|----------|----------|
| SkipLink | `components/ui/SkipLink.tsx` |
| Form components | `components/ui/form.tsx` |
| Dialog | `components/ui/dialog.tsx` |
| Select | `components/ui/select.tsx` |
| Tabs | `components/ui/tabs.tsx` |
| Alert | `components/ui/alert.tsx` |
| Progress | `components/ui/progress.tsx` |

---

**Remember:** When in doubt, check existing accessible components in `components/ui/` for patterns to follow.
