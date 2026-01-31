# ⌨️ TASK: C-033 - Keyboard Shortcuts System

**Task ID:** C-033
**Created:** February 1, 2026
**Assigned To:** Frontend Coder (Turing)
**Status:** ⏳ PENDING
**Priority:** P2 MEDIUM
**Estimated Time:** 10-12 hours
**Deadline:** February 22, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Implement a comprehensive keyboard shortcuts system to improve user productivity:
- Global shortcuts (navigation, search)
- Page-specific shortcuts
- Customizable shortcuts
- Shortcut reference dialog
- Conflict resolution

---

## 📋 REQUIREMENTS

### 1. Shortcut Registry

**Typescript:**
```typescript
// apps/frontend/src/lib/shortcuts/ShortcutRegistry.ts
interface Shortcut {
  key: string;              // e.g., 'k', 'ctrl+k', 'shift+?'
  description: string;      // e.g., 'Open search'
  action: () => void;       // Function to execute
  category: ShortcutCategory;
  page?: string;            // If undefined, works on all pages
  enabled: boolean;
}

enum ShortcutCategory {
  NAVIGATION = 'navigation',
  SEARCH = 'search',
  ACTIONS = 'actions',
  VIEWS = 'views',
  CUSTOM = 'custom'
}

class ShortcutRegistry {
  private shortcuts: Map<string, Shortcut>;
  
  register(shortcut: Shortcut): void;
  unregister(key: string): void;
  getShortcut(key: string): Shortcut | undefined;
  getPageShortcuts(page: string): Shortcut[];
  getAllShortcuts(): Shortcut[];
  checkConflict(key: string, page?: string): Shortcut | undefined;
}
```

### 2. Global Shortcuts (All Pages)

| Shortcut | Action | Category |
|----------|--------|----------|
| `?` | Show keyboard shortcuts help | NAVIGATION |
| `/` or `Ctrl+K` | Open global search | SEARCH |
| `G` then `P` | Go to portfolios | NAVIGATION |
| `G` then `S` | Go to screener | NAVIGATION |
| `G` then `M` | Go to market overview | NAVIGATION |
| `G` then `N` | Go to news | NAVIGATION |
| `Esc` | Close modal/dropdown | ACTIONS |
| `Ctrl+/` | Toggle theme (dark/light) | VIEWS |

### 3. Page-Specific Shortcuts

**Portfolios Page:**
| Shortcut | Action |
|----------|--------|
| `C` | Create new portfolio |
| `E` | Edit selected portfolio |
| `D` | Delete selected portfolio |
| `R` | Refresh data |
| `A` | Add position |
| `I` | Import CSV |

**Screener Page:**
| Shortcut | Action |
|----------|--------|
| `S` | Run screen |
| `R` | Reset filters |
| `Ctrl+S` | Save screener preset |
| `Ctrl+O` | Load screener preset |
| `E` | Export results |

**Asset Detail Page:**
| Shortcut | Action |
|----------|--------|
| `T` | View chart |
| `F` | View fundamentals |
| `N` | View news |
| `H` | View historical data |
| `A` | Add to watchlist |
| `B` | Buy asset (if trading enabled) |
| `S` | Sell asset (if trading enabled) |

### 4. Shortcut Manager Hook

```typescript
// apps/frontend/src/hooks/useKeyboardShortcuts.ts
import { useEffect } from 'react';

export function useKeyboardShortcuts(
  shortcuts: Shortcut[],
  dependencies: any[] = []
) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check for matches
      // Execute action
      // Prevent default if needed
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts, ...dependencies]);
}

// Usage in components:
export function PortfolioPage() {
  const shortcuts = [
    {
      key: 'c',
      description: 'Create new portfolio',
      action: () => setShowCreateDialog(true),
      category: ShortcutCategory.ACTIONS,
      page: 'portfolio'
    },
    // ... more shortcuts
  ];
  
  useKeyboardShortcuts(shortcuts);
}
```

### 5. Shortcuts Help Dialog

```typescript
// apps/frontend/src/components/shortcuts/ShortcutHelpDialog.tsx
export function ShortcutHelpDialog() {
  // Display all shortcuts grouped by category
  // Show page-specific shortcuts for current page
  // Show global shortcuts
  // Indicate which shortcuts are customizable
  // Allow users to print/export shortcuts
}
```

### 6. Custom Shortcuts

**User Preferences:**
```typescript
interface UserShortcutPreferences {
  userId: string;
  customShortcuts: {
    originalKey: string;
    customKey: string;
  }[];
}

// API endpoint to save/load custom shortcuts
```

### 7. Conflict Resolution

**Detection:**
```typescript
class ShortcutConflictResolver {
  detectConflicts(shortcuts: Shortcut[]): Conflict[];
  resolveConflict(conflict: Conflict, resolution: Resolution): void;
  warnUser(conflict: Conflict): void;
}
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Global shortcuts work on all pages
- [ ] Page-specific shortcuts work on respective pages
- [ ] Shortcuts help dialog accessible via `?`
- [ ] Shortcuts don't conflict with browser defaults
- [ ] Shortcuts don't conflict with each other
- [ ] Users can customize shortcuts
- [ ] Shortcut conflicts detected and resolved
- [ ] Shortcuts work in all modern browsers
- [ ] Shortcuts are documented in UI
- [ ] Performance: No lag when pressing shortcuts
- [ ] Accessibility: Shortcuts don't interfere with screen readers
- [ ] Tests for shortcut registry
- [ ] Tests for conflict detection

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/frontend/src/lib/shortcuts/ShortcutRegistry.ts`
- `apps/frontend/src/hooks/useKeyboardShortcuts.ts`
- `apps/frontend/src/components/shortcuts/ShortcutHelpDialog.tsx`
- `apps/frontend/src/components/shortcuts/ShortcutCustomizationDialog.tsx`
- `apps/frontend/src/types/shortcuts.ts`

### Modify:
- All major page components (add useKeyboardShortcuts hooks)
- `apps/frontend/src/app/layout.tsx` (global shortcuts)

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- React hooks
- Frontend routing

**Related Tasks:**
- None (standalone UX enhancement)

---

## 🎯 PRIORITY SHORTCUTS

### Phase 1 (Implement First)
1. `?` - Show help dialog
2. `/` or `Ctrl+K` - Open search
3. `Esc` - Close modals
4. Navigation shortcuts (`G` then key)

### Phase 2
5. Page-specific shortcuts (portfolio, screener, etc.)
6. Custom shortcuts
7. Conflict resolution

---

## 📊 DELIVERABLES

1. **Shortcut Registry:** Core shortcut management system
2. **Global Shortcuts:** 10+ global shortcuts
3. **Page Shortcuts:** 5+ shortcuts per major page
4. **Help Dialog:** Accessible via `?`
5. **Customization:** Users can remap shortcuts
6. **Conflict Detection:** Automatic conflict resolution
7. **Tests:** Unit tests for registry
8. **Documentation:** In-app help dialog

---

## 💬 NOTES

**Implementation Approach:**
- Use `keydown` event listener on window
- Support modifier keys: Ctrl, Alt, Shift, Meta (Cmd)
- Handle key combinations: `Ctrl+K`, `Shift+?`
- Prevent default browser behavior when needed
- Support both Mac (Cmd) and Windows (Ctrl)

**Browser Compatibility:**
- `event.key` vs `event.code`
- Mac: Meta key vs Ctrl
- Test on Chrome, Firefox, Safari, Edge

**Accessibility:**
- Ensure shortcuts don't interfere with screen reader shortcuts
- Provide visual indicator when shortcuts are available
- Allow users to disable problematic shortcuts
- Don't override critical browser shortcuts (Ctrl+W, etc.)

**Future Enhancements:**
- Vim-style keybindings
- Emacs-style keybindings
- Shortcut sequences (like `G` then `P`)
- Context-aware shortcuts

---

**Status:** ⏳ READY TO START
**Assigned To:** Frontend Coder (Turing)
**User Value:** HIGH - improves power user productivity

---

⌨️ *C-033: Keyboard Shortcuts System*
*Power user productivity - navigate FinanceHub without a mouse*
