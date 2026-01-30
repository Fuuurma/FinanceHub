# C-033: Keyboard Shortcuts System

**Priority:** P1 - HIGH  
**Assigned to:** Frontend Coder  
**Estimated Time:** 10-12 hours  
**Dependencies:** C-005 (Frontend Completion), C-016 (Customizable Dashboards)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement comprehensive keyboard shortcuts system for power users, enabling rapid navigation, quick actions, and Bloomberg Terminal-style efficiency without mouse interaction.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 10.1 - Customization):**

- Keyboard shortcuts (power user features)
- Custom layouts save/load
- Mobile responsive design

**From Features Specification (Section 10.2 - Collaboration):**

- Shared portfolios (team/family)
- Shared watchlists

---

## ✅ CURRENT STATE

**What exists:**
- Basic navigation
- Click-based interactions
- Customizable dashboards

**What's missing:**
- Keyboard shortcut system
- Quick actions via keyboard
- Command palette
- Shortcut customization
- Keyboard-driven navigation
- Bloomberg Terminal-style commands

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database & Models** (1-2 hours)

**Backend: Create `apps/backend/src/accounts/models/shortcuts.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class KeyboardShortcut(models.Model):
    """User keyboard shortcut preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='keyboard_shortcuts')
    
    # Custom keybindings (JSON format: {"action": "keystroke"})
    custom_shortcuts = models.JSONField(default=dict)
    # Example: {"search": "Ctrl+K", "portfolio": "Ctrl+P", "alert": "Ctrl+A"}
    
    # Enabled features
    enable_shortcuts = models.BooleanField(default=True)
    show_command_palette = models.BooleanField(default=True)
    show_shortcut_hints = models.BooleanField(default=True)
    
    # Keyboard behavior
    vim_mode = models.BooleanField(default=False)  # Vim-style navigation
    auto_focus_search = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CommandHistory(models.Model):
    """Track command palette usage"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='command_history')
    
    # Command details
    command = models.CharField(max_length=200)
    command_type = models.CharField(max_length=50)  # search, action, navigation
    parameters = models.JSONField(default=dict)
    
    # Execution
    executed_at = models.DateTimeField(auto_now_add=True)
    execution_time_ms = models.IntegerField(null=True)  # Performance tracking
    success = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', '-executed_at']),
            models.Index(fields=['user', 'command', '-executed_at']),
        ]
        ordering = ['-executed_at']

class FavoriteCommand(models.Model):
    """User's favorite commands for quick access"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_commands')
    
    command = models.CharField(max_length=200)
    display_name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'order']),
        ]
        ordering = ['order']
```

---

### **Phase 2: Backend API** (2-3 hours)

**Create `apps/backend/src/api/shortcuts.py`:**

```python
from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from accounts.models.shortcuts import KeyboardShortcut, CommandHistory, FavoriteCommand

router = Router(tags=['shortcuts'])

class ShortcutSchema(Schema):
    action: str
    keystroke: str

@router.get("/shortcuts/preferences")
def get_shortcut_preferences(request):
    """Get user's keyboard shortcut preferences"""
    shortcut, created = KeyboardShortcut.objects.get_or_create(
        user=request.auth
    )
    return {
        'custom_shortcuts': shortcut.custom_shortcuts,
        'enable_shortcuts': shortcut.enable_shortcuts,
        'show_command_palette': shortcut.show_command_palette,
        'show_shortcut_hints': shortcut.show_shortcut_hints,
        'vim_mode': shortcut.vim_mode,
        'auto_focus_search': shortcut.auto_focus_search,
    }

@router.post("/shortcuts/preferences")
def update_shortcut_preferences(request, data: dict):
    """Update keyboard shortcut preferences"""
    shortcut, created = KeyboardShortcut.objects.get_or_create(
        user=request.auth
    )
    
    shortcut.custom_shortcuts = data.get('custom_shortcuts', {})
    shortcut.enable_shortcuts = data.get('enable_shortcuts', True)
    shortcut.show_command_palette = data.get('show_command_palette', True)
    shortcut.show_shortcut_hints = data.get('show_shortcut_hints', True)
    shortcut.vim_mode = data.get('vim_mode', False)
    shortcut.auto_focus_search = data.get('auto_focus_search', True)
    shortcut.save()
    
    return {'status': 'updated'}

@router.post("/shortcuts/command")
def execute_command(request, data: dict):
    """Execute command from command palette"""
    import time
    start = time.time()
    
    command = data.get('command')
    command_type = data.get('command_type', 'action')
    parameters = data.get('parameters', {})
    
    # Log command
    CommandHistory.objects.create(
        user=request.auth,
        command=command,
        command_type=command_type,
        parameters=parameters,
        execution_time_ms=int((time.time() - start) * 1000),
        success=True
    )
    
    # Route command to appropriate handler
    result = _route_command(request.auth, command, command_type, parameters)
    
    return result

def _route_command(user, command: str, command_type: str, parameters: dict):
    """Route command to appropriate handler"""
    if command_type == 'navigation':
        # Navigation commands
        routes = {
            'dashboard': '/',
            'portfolio': '/portfolio',
            'screener': '/screener',
            'news': '/news',
            'alerts': '/alerts',
            'settings': '/settings',
        }
        return {'route': routes.get(command, '/')}
    
    elif command_type == 'search':
        # Search commands
        return {'action': 'search', 'query': parameters.get('query')}
    
    elif command_type == 'action':
        # Quick actions
        actions = {
            'add_to_watchlist': 'ADD_WATCHLIST',
            'create_alert': 'CREATE_ALERT',
            'quick_buy': 'QUICK_BUY',
            'refresh': 'REFRESH',
        }
        return {'action': actions.get(command, 'UNKNOWN')}
    
    return {'error': 'Unknown command'}

@router.get("/shortcuts/history")
def get_command_history(request, limit: int = 20):
    """Get command history for user"""
    history = CommandHistory.objects.filter(
        user=request.auth
    ).order_by('-executed_at')[:limit]
    
    return [
        {
            'command': h.command,
            'command_type': h.command_type,
            'parameters': h.parameters,
            'executed_at': h.executed_at,
            'success': h.success
        }
        for h in history
    ]

@router.get("/shortcuts/favorites")
def get_favorite_commands(request):
    """Get user's favorite commands"""
    favorites = FavoriteCommand.objects.filter(
        user=request.auth
    ).order_by('order')
    
    return [
        {
            'command': f.command,
            'display_name': f.display_name,
            'order': f.order
        }
        for f in favorites
    ]

@router.post("/shortcuts/favorites")
def add_favorite_command(request, data: dict):
    """Add command to favorites"""
    FavoriteCommand.objects.create(
        user=request.auth,
        command=data['command'],
        display_name=data['display_name'],
        order=data.get('order', 0)
    )
    
    return {'status': 'added'}
```

---

### **Phase 3: Frontend - Core Keyboard System** (4-5 hours)

**Create `apps/frontend/src/lib/keyboard/core.ts`:**

```typescript
import { useEffect, useCallback, useRef } from 'react';
import type { KeyboardEvent } from 'react';

export interface KeyboardShortcut {
  keys: string[];
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
  action: () => void;
  description: string;
  category: 'navigation' | 'action' | 'search' | 'general';
}

export interface ShortcutConfig {
  enabled: boolean;
  vimMode: boolean;
  showHints: boolean;
}

class KeyboardManager {
  private shortcuts: Map<string, KeyboardShortcut> = new Map();
  private config: ShortcutConfig = {
    enabled: true,
    vimMode: false,
    showHints: true,
  };
  private pressedKeys = new Set<string>();
  private isCommandPaletteOpen = false;

  constructor() {
    this.setupDefaultShortcuts();
    this.attachGlobalListeners();
  }

  private setupDefaultShortcuts(): void {
    // Navigation shortcuts
    this.registerShortcut({
      keys: ['g', 'd'],
      action: () => this.navigate('/'),
      description: 'Go to Dashboard',
      category: 'navigation',
    });

    this.registerShortcut({
      keys: ['g', 'p'],
      action: () => this.navigate('/portfolio'),
      description: 'Go to Portfolio',
      category: 'navigation',
    });

    this.registerShortcut({
      keys: ['g', 's'],
      action: () => this.navigate('/screener'),
      description: 'Go to Screener',
      category: 'navigation',
    });

    this.registerShortcut({
      keys: ['g', 'n'],
      action: () => this.navigate('/news'),
      description: 'Go to News',
      category: 'navigation',
    });

    // Search
    this.registerShortcut({
      keys: ['/'],
      ctrl: false,
      action: () => this.focusSearch(),
      description: 'Focus Search',
      category: 'search',
    });

    this.registerShortcut({
      keys: ['k'],
      ctrl: true,
      meta: true,
      action: () => this.openCommandPalette(),
      description: 'Open Command Palette',
      category: 'search',
    });

    // Actions
    this.registerShortcut({
      keys: ['a'],
      ctrl: true,
      action: () => this.createAlert(),
      description: 'Create Alert',
      category: 'action',
    });

    this.registerShortcut({
      keys: ['w'],
      ctrl: true,
      action: () => this.addToWatchlist(),
      description: 'Add to Watchlist',
      category: 'action',
    });

    this.registerShortcut({
      keys: ['r'],
      ctrl: true,
      action: () => this.refresh(),
      description: 'Refresh',
      category: 'action',
    });

    // General
    this.registerShortcut({
      keys: ['?'],
      action: () => this.showShortcutsHelp(),
      description: 'Show Keyboard Shortcuts',
      category: 'general',
    });

    this.registerShortcut({
      keys: ['Escape'],
      action: () => this.closeModals(),
      description: 'Close Modals',
      category: 'general',
    });
  }

  registerShortcut(shortcut: KeyboardShortcut): void {
    const key = this.generateKey(shortcut);
    this.shortcuts.set(key, shortcut);
  }

  private generateKey(shortcut: KeyboardShortcut): string {
    const parts = [];
    if (shortcut.ctrl) parts.push('ctrl');
    if (shortcut.shift) parts.push('shift');
    if (shortcut.alt) parts.push('alt');
    if (shortcut.meta) parts.push('meta');
    parts.push(...shortcut.keys);
    return parts.join('+').toLowerCase();
  }

  private handleKeyDown = (e: KeyboardEvent): void => {
    if (!this.config.enabled) return;

    // Ignore if user is typing in an input
    const target = e.target as HTMLElement;
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
      // Allow Escape to exit input
      if (e.key !== 'Escape') return;
    }

    this.pressedKeys.add(e.key.toLowerCase());

    // Check for matching shortcuts
    const combination = this.getCurrentCombination();
    const shortcut = this.shortcuts.get(combination);

    if (shortcut) {
      e.preventDefault();
      e.stopPropagation();
      shortcut.action();
    }
  };

  private handleKeyUp = (e: KeyboardEvent): void => {
    this.pressedKeys.delete(e.key.toLowerCase());
  };

  private getCurrentCombination(): string {
    const parts = [];
    if (this.pressedKeys.has('control')) parts.push('ctrl');
    if (this.pressedKeys.has('shift')) parts.push('shift');
    if (this.pressedKeys.has('alt')) parts.push('alt');
    if (this.pressedKeys.has('meta')) parts.push('meta');
    
    // Add non-modifier keys
    this.pressedKeys.forEach(key => {
      if (!['control', 'shift', 'alt', 'meta'].includes(key)) {
        parts.push(key);
      }
    });

    return parts.join('+').toLowerCase();
  }

  private attachGlobalListeners(): void {
    if (typeof window !== 'undefined') {
      window.addEventListener('keydown', this.handleKeyDown);
      window.addEventListener('keyup', this.handleKeyUp);
    }
  }

  private navigate(route: string): void {
    if (typeof window !== 'undefined') {
      window.location.href = route;
    }
  }

  private focusSearch(): void {
    const searchInput = document.querySelector('[data-search-input]') as HTMLInputElement;
    if (searchInput) {
      searchInput.focus();
    }
  }

  private openCommandPalette(): void {
    this.isCommandPaletteOpen = true;
    // Emit event for CommandPalette component
    window.dispatchEvent(new CustomEvent('open-command-palette'));
  }

  private createAlert(): void {
    window.dispatchEvent(new CustomEvent('create-alert'));
  }

  private addToWatchlist(): void {
    window.dispatchEvent(new CustomEvent('add-to-watchlist'));
  }

  private refresh(): void {
    window.dispatchEvent(new CustomEvent('refresh-data'));
  }

  private showShortcutsHelp(): void {
    window.dispatchEvent(new CustomEvent('show-shortcuts-help'));
  }

  private closeModals(): void {
    window.dispatchEvent(new CustomEvent('close-modals'));
  }

  updateConfig(config: Partial<ShortcutConfig>): void {
    this.config = { ...this.config, ...config };
  }

  getShortcuts(): KeyboardShortcut[] {
    return Array.from(this.shortcuts.values());
  }

  getShortcutsByCategory(category: KeyboardShortcut['category']): KeyboardShortcut[] {
    return this.getShortcuts().filter(s => s.category === category);
  }

  destroy(): void {
    if (typeof window !== 'undefined') {
      window.removeEventListener('keydown', this.handleKeyDown);
      window.removeEventListener('keyup', this.handleKeyUp);
    }
  }
}

// Singleton instance
let keyboardManager: KeyboardManager | null = null;

export const getKeyboardManager = (): KeyboardManager => {
  if (!keyboardManager) {
    keyboardManager = new KeyboardManager();
  }
  return keyboardManager;
};

// React hook
export const useKeyboardShortcuts = () => {
  const manager = getKeyboardManager();

  useEffect(() => {
    return () => {
      // Don't destroy singleton, just cleanup
    };
  }, []);

  return {
    registerShortcut: useCallback((shortcut: KeyboardShortcut) => {
      manager.registerShortcut(shortcut);
    }, [manager]),
    
    getShortcuts: useCallback(() => manager.getShortcuts(), [manager]),
    
    getShortcutsByCategory: useCallback((category: KeyboardShortcut['category']) => {
      return manager.getShortcutsByCategory(category);
    }, [manager]),
    
    updateConfig: useCallback((config: Partial<ShortcutConfig>) => {
      manager.updateConfig(config);
    }, [manager]),
  };
};
```

---

### **Phase 4: Frontend - Command Palette** (3-4 hours)

**Create `apps/frontend/src/components/keyboard/CommandPalette.tsx`:**

```typescript
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getKeyboardManager } from '@/lib/keyboard/core';

interface Command {
  id: string;
  label: string;
  type: 'navigation' | 'action' | 'search';
  icon?: string;
  keywords: string[];
  action: () => void;
}

const COMMANDS: Command[] = [
  // Navigation
  {
    id: 'nav-dashboard',
    label: 'Go to Dashboard',
    type: 'navigation',
    icon: 'layout',
    keywords: ['home', 'dashboard', 'main'],
    action: () => window.location.href = '/',
  },
  {
    id: 'nav-portfolio',
    label: 'Go to Portfolio',
    type: 'navigation',
    icon: 'briefcase',
    keywords: ['portfolio', 'holdings', 'positions'],
    action: () => window.location.href = '/portfolio',
  },
  {
    id: 'nav-screener',
    label: 'Go to Stock Screener',
    type: 'navigation',
    icon: 'filter',
    keywords: ['screener', 'screen', 'filter', 'search'],
    action: () => window.location.href = '/screener',
  },
  {
    id: 'nav-news',
    label: 'Go to News',
    type: 'navigation',
    icon: 'newspaper',
    keywords: ['news', 'articles', 'headlines'],
    action: () => window.location.href = '/news',
  },
  {
    id: 'nav-alerts',
    label: 'Go to Alerts',
    type: 'navigation',
    icon: 'bell',
    keywords: ['alerts', 'notifications'],
    action: () => window.location.href = '/alerts',
  },
  {
    id: 'nav-settings',
    label: 'Go to Settings',
    type: 'navigation',
    icon: 'settings',
    keywords: ['settings', 'preferences', 'config'],
    action: () => window.location.href = '/settings',
  },

  // Actions
  {
    id: 'action-add-watchlist',
    label: 'Add to Watchlist',
    type: 'action',
    icon: 'plus',
    keywords: ['add', 'watchlist', 'track'],
    action: () => window.dispatchEvent(new CustomEvent('add-to-watchlist')),
  },
  {
    id: 'action-create-alert',
    label: 'Create Alert',
    type: 'action',
    icon: 'bell-plus',
    keywords: ['alert', 'notify', 'price'],
    action: () => window.dispatchEvent(new CustomEvent('create-alert')),
  },
  {
    id: 'action-refresh',
    label: 'Refresh Data',
    type: 'action',
    icon: 'refresh-cw',
    keywords: ['refresh', 'reload', 'update'],
    action: () => window.dispatchEvent(new CustomEvent('refresh-data')),
  },
  {
    id: 'action-export',
    label: 'Export Data',
    type: 'action',
    icon: 'download',
    keywords: ['export', 'download', 'csv'],
    action: () => window.dispatchEvent(new CustomEvent('export-data')),
  },

  // Search
  {
    id: 'search-symbol',
    label: 'Search Symbol...',
    type: 'search',
    icon: 'search',
    keywords: ['search', 'symbol', 'stock'],
    action: () => {
      // Focus search input
      const searchInput = document.querySelector('[data-search-input]') as HTMLInputElement;
      if (searchInput) searchInput.focus();
    },
  },
];

export const CommandPalette: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const filteredCommands = COMMANDS.filter(cmd =>
    cmd.label.toLowerCase().includes(query.toLowerCase()) ||
    cmd.keywords.some(kw => kw.includes(query.toLowerCase()))
  );

  useEffect(() => {
    const handleOpen = () => {
      setIsOpen(true);
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 0);
    };

    const handleClose = () => setIsOpen(false);

    window.addEventListener('open-command-palette', handleOpen);
    window.addEventListener('close-modals', handleClose);

    return () => {
      window.removeEventListener('open-command-palette', handleOpen);
      window.removeEventListener('close-modals', handleClose);
    };
  }, []);

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(i => Math.min(i + 1, filteredCommands.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(i => Math.max(i - 1, 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        filteredCommands[selectedIndex]?.action();
        setIsOpen(false);
      } else if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, filteredCommands]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-32">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50"
        onClick={() => setIsOpen(false)}
      />

      {/* Command Palette */}
      <div className="relative w-full max-w-xl bg-white dark:bg-gray-800 rounded-lg shadow-2xl overflow-hidden">
        {/* Input */}
        <div className="flex items-center px-4 border-b dark:border-gray-700">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Type a command or search..."
            className="flex-1 px-4 py-4 bg-transparent border-0 outline-none text-gray-900 dark:text-white placeholder-gray-400"
          />
          <kbd className="px-2 py-1 text-xs text-gray-400 bg-gray-100 dark:bg-gray-700 rounded">ESC</kbd>
        </div>

        {/* Results */}
        <div className="max-h-80 overflow-y-auto">
          {filteredCommands.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-400">
              No commands found
            </div>
          ) : (
            <ul>
              {filteredCommands.map((cmd, index) => (
                <li
                  key={cmd.id}
                  onClick={() => {
                    cmd.action();
                    setIsOpen(false);
                  }}
                  className={`px-4 py-3 cursor-pointer transition-colors ${
                    index === selectedIndex
                      ? 'bg-blue-50 dark:bg-blue-900/20'
                      : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-gray-400">
                      {/* Icon placeholder */}
                      {cmd.icon}
                    </span>
                    <span className="flex-1 text-gray-900 dark:text-white">
                      {cmd.label}
                    </span>
                    <span className="text-xs text-gray-400 capitalize">
                      {cmd.type}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t dark:border-gray-700 text-xs text-gray-400">
          <div className="flex items-center justify-between">
            <span>Use ↑↓ to navigate, Enter to select</span>
            <span>Powered by FinanceHub</span>
          </div>
        </div>
      </div>
    </div>
  );
};
```

**Create `apps/frontend/src/components/keyboard/ShortcutHelp.tsx`:**

```typescript
import React, { useState, useEffect } from 'react';
import { getKeyboardManager } from '@/lib/keyboard/core';

export const ShortcutHelp: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const manager = getKeyboardManager();

  useEffect(() => {
    const handleShow = () => setIsOpen(true);
    const handleClose = () => setIsOpen(false);

    window.addEventListener('show-shortcuts-help', handleShow);
    window.addEventListener('close-modals', handleClose);

    return () => {
      window.removeEventListener('show-shortcuts-help', handleShow);
      window.removeEventListener('close-modals', handleClose);
    };
  }, []);

  if (!isOpen) return null;

  const shortcuts = manager.getShortcutsByCategory('navigation');
  const actions = manager.getShortcutsByCategory('action');
  const general = manager.getShortcutsByCategory('general');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={() => setIsOpen(false)} />
      <div className="relative w-full max-w-2xl bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-6 max-h-[80vh] overflow-y-auto">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Keyboard Shortcuts
        </h2>

        <ShortcutSection title="Navigation" shortcuts={shortcuts} />
        <ShortcutSection title="Actions" shortcuts={actions} />
        <ShortcutSection title="General" shortcuts={general} />

        <button
          onClick={() => setIsOpen(false)}
          className="mt-6 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Close (ESC)
        </button>
      </div>
    </div>
  );
};

const ShortcutSection: React.FC<{ title: string; shortcuts: any[] }> = ({ title, shortcuts }) => (
  <div className="mb-6">
    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">{title}</h3>
    <div className="space-y-2">
      {shortcuts.map((shortcut, index) => (
        <div key={index} className="flex items-center justify-between">
          <span className="text-gray-700 dark:text-gray-300">{shortcut.description}</span>
          <KeyCombo keys={shortcut.keys} />
        </div>
      ))}
    </div>
  </div>
);

const KeyCombo: React.FC<{ keys: string[] }> = ({ keys }) => (
  <div className="flex gap-1">
    {keys.map(key => (
      <kbd key={key} className="px-2 py-1 text-sm bg-gray-100 dark:bg-gray-700 rounded">
        {key.toUpperCase()}
      </kbd>
    ))}
  </div>
);
```

---

## 📋 DELIVERABLES

- [ ] Backend: KeyboardShortcut, CommandHistory, FavoriteCommand models
- [ ] Backend: 6 API endpoints for shortcuts
- [ ] Frontend: KeyboardManager class with full shortcut system
- [ ] Frontend: CommandPalette component
- [ ] Frontend: ShortcutHelp component
- [ ] Frontend: React hooks (useKeyboardShortcuts)
- [ ] 30+ default keyboard shortcuts
- [ ] Database migrations
- [ ] Unit tests (coverage >80%)

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Command palette opens with Ctrl+K (Cmd+K on Mac)
- [ ] All navigation works via keyboard
- [ ] Quick actions accessible via shortcuts
- [ ] Shortcuts help modal displays all shortcuts
- [ ] User can customize shortcuts (backend support)
- [ ] Command palette fuzzy search working
- [ ] Keyboard hints show when shortcuts available
- [ ] Vim mode optional for navigation
- [ ] All modals close with Escape
- [ ] No conflict with browser defaults
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- Command palette latency <100ms
- 30+ keyboard shortcuts available
- User can navigate entire app without mouse
- Shortcut customization saves correctly
- Keyboard hints displayed contextually

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/033-keyboard-shortcuts-system.md
