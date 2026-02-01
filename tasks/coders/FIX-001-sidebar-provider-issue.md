# Task: Fix Shadcn Sidebar Provider Issue

**Priority:** HIGH
**Status:** OPEN
**Assigned To:** Gaudí
**Created:** February 1, 2026
**Estimated Time:** 2-3 hours

## Problem Description

The frontend is throwing errors related to shadcn's `useSidebar` hook and `SidebarProvider`. The sidebar component builds but cannot be displayed due to incorrect provider/context usage with layouts and children.

### Error Symptoms
- Frontend builds successfully
- Application crashes on load
- Error related to `useSidebar` must be used within `SidebarProvider`
- Issue is in how layouts wrap children components

### Current State
- **Sidebar UI Component:** `/apps/frontend/src/components/ui/sidebar.tsx` (727 lines)
  - Has `SidebarProvider` component (lines 56-152)
  - Has `useSidebar` hook (lines 47-54)
  - `Sidebar` component calls `useSidebar()` internally (line 166)

- **AppSidebar Component:** `/apps/frontend/src/components/layout/sidebar.tsx` (382 lines)
  - Uses `Sidebar`, `SidebarContent`, etc. from ui/sidebar
  - Does NOT wrap itself in provider (relies on parent)

- **Dashboard Layouts:**
  1. `/apps/frontend/src/app/(dashboard)/layout.tsx` - Has `SidebarProvider` wrapping everything
  2. `/apps/frontend/src/components/layout/dashboard-layout.tsx` - Has `SidebarProvider` wrapping everything
  3. Root layout at `/apps/frontend/src/app/layout.tsx` - No sidebar provider

## Investigation Tasks

### 1. Audit All Layouts
Check ALL layout files in the app to find:
- [ ] All files named `layout.tsx`
- [ ] Any component using `AppSidebar`
- [ ] Any component using `useSidebar()` hook
- [ ] Any component using `SidebarTrigger`
- [ ] Verify each has proper `SidebarProvider` wrapper

### 2. Check Component Hierarchy
The shadcn sidebar requires this structure:
```
<SidebarProvider>
  <Sidebar>
    <SidebarContent>
      {/* content */}
    </SidebarContent>
  </Sidebar>
  <SidebarInset>
    <SidebarTrigger />
    {/* page content */}
  </SidebarInset>
</SidebarProvider>
```

Verify that ALL components using sidebar features follow this pattern.

### 3. Review Shadcn Documentation
- Read: https://ui.shadcn.com/docs/components/sidebar
- Check: Provider placement requirements
- Check: Client vs Server component requirements
- Check: Next.js 13+ app directory specific patterns

### 4. Test Current Implementation
- Test: Does `app/(dashboard)/layout.tsx` work?
- Test: Does `components/layout/dashboard-layout.tsx` work?
- Test: Are both being used? Which one is active?
- Test: Check browser console for exact error message

## Implementation Tasks

### Fix 1: Standardize Layout Structure
Choose ONE approach:

**Option A:** Keep sidebar in dashboard layout only
- Keep: `app/(dashboard)/layout.tsx` with provider
- Remove: Duplicate `components/layout/dashboard-layout.tsx`
- Ensure: Root layout doesn't interfere

**Option B:** Create shared layout wrapper
- Create: Single reusable layout component with provider
- Import: Into both locations if needed
- Avoid: Duplicate provider issues

### Fix 2: Ensure Proper Provider Scope
The `SidebarProvider` should:
1. Wrap ONLY routes that need the sidebar
2. Be placed as HIGH in the component tree as possible (but not higher than needed)
3. NOT be duplicated (nested providers cause issues)

### Fix 3: Update 'use client' Directives
Ensure any component using hooks has:
```tsx
'use client'  // Required at top of file
```

Check:
- [ ] `app/(dashboard)/layout.tsx`
- [ ] `components/layout/sidebar.tsx`
- [ ] `components/layout/dashboard-layout.tsx`
- [ ] `components/ui/sidebar.tsx`
- [ ] Any component using `useSidebar()`

### Fix 4: Fix Type Errors (if present)
The user mentioned the frontend has TypeScript errors. Check:
- [ ] Run `npm run typecheck` in apps/frontend
- [ ] Fix any type errors related to sidebar components
- [ ] Ensure proper type exports from ui/sidebar

## Testing Checklist

After fixes, verify:
- [ ] Sidebar opens/closes correctly
- [ ] Mobile sidebar works (sheet mode)
- [ ] Desktop sidebar works (collapse/expand)
- [ ] Sidebar menu items navigate correctly
- [ ] No console errors
- [ ] TypeScript compiles without errors
- [ ] All dashboard routes render properly
- [ ] Hot reload works in dev mode

## Files to Modify

Likely files:
1. `/apps/frontend/src/app/(dashboard)/layout.tsx`
2. `/apps/frontend/src/components/layout/dashboard-layout.tsx`
3. `/apps/frontend/src/components/layout/sidebar.tsx`
4. `/apps/frontend/src/components/ui/sidebar.tsx`
5. Any other layout files found during audit

## Success Criteria

✅ Application loads without sidebar errors
✅ Sidebar is visible and functional on dashboard pages
✅ No duplicate or missing provider errors
✅ TypeScript compiles cleanly
✅ Mobile and desktop sidebar modes work
✅ All navigation works correctly

## Additional Notes

- The sidebar uses shadcn/ui components which require careful context management
- Next.js 13+ app directory has specific requirements for client components
- The `useSidebar` hook MUST be called within `SidebarProvider` context
- Check for hydration errors due to client/server component mismatches

## References

- Shadcn Sidebar Docs: https://ui.shadcn.com/docs/components/sidebar
- Next.js App Router: https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts
- React Context: https://react.dev/learn/scaling-up-with-reducer-and-context
