'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Search,
  Keyboard,
  Home,
  Briefcase,
  BarChart3,
  Bell,
  Settings,
  ArrowUpRight,
  ArrowDownRight,
  ArrowLeft,
  ArrowRight,
  Plus,
  RefreshCw,
} from 'lucide-react'
import { cn } from '@/lib/utils'

export interface KeyboardShortcut {
  id: string
  key: string
  modifiers?: ('ctrl' | 'alt' | 'shift' | 'meta')[]
  description: string
  category: string
  action?: () => void
}

export interface KeyboardShortcutsProps {
  shortcuts?: KeyboardShortcut[]
  onShortcutExecute?: (shortcutId: string) => void
  className?: string
}

const DEFAULT_SHORTCUTS: KeyboardShortcut[] = [
  { id: 'search', key: '/', modifiers: [], description: 'Focus search bar', category: 'Navigation' },
  { id: 'help', key: '?', modifiers: [], description: 'Show keyboard shortcuts', category: 'Help' },
  { id: 'home', key: 'h', modifiers: ['ctrl'], description: 'Go to home/dashboard', category: 'Navigation' },
  { id: 'portfolios', key: 'p', modifiers: ['ctrl'], description: 'Go to portfolios', category: 'Navigation' },
  { id: 'analytics', key: 'a', modifiers: ['ctrl'], description: 'Go to analytics', category: 'Navigation' },
  { id: 'holdings', key: 'g', modifiers: ['ctrl', 'shift'], description: 'Go to holdings', category: 'Navigation' },
  { id: 'transactions', key: 't', modifiers: ['ctrl', 'shift'], description: 'Go to transactions', category: 'Navigation' },
  { id: 'settings', key: ',', modifiers: ['ctrl'], description: 'Open settings', category: 'Navigation' },
  { id: 'refresh', key: 'r', modifiers: ['ctrl'], description: 'Refresh data', category: 'Actions' },
  { id: 'new-portfolio', key: 'n', modifiers: ['ctrl'], description: 'Create new portfolio', category: 'Actions' },
  { id: 'next-portfolio', key: '1', modifiers: ['ctrl'], description: 'Switch to next portfolio', category: 'Portfolios' },
  { id: 'prev-portfolio', key: '9', modifiers: ['ctrl'], description: 'Switch to previous portfolio', category: 'Portfolios' },
  { id: 'chart-1m', key: '1', modifiers: [], description: 'Switch to 1M chart timeframe', category: 'Charts' },
  { id: 'chart-5m', key: '2', modifiers: [], description: 'Switch to 5M chart timeframe', category: 'Charts' },
  { id: 'chart-1h', key: '3', modifiers: [], description: 'Switch to 1H chart timeframe', category: 'Charts' },
  { id: 'chart-1d', key: '4', modifiers: [], description: 'Switch to 1D chart timeframe', category: 'Charts' },
  { id: 'next-tab', key: 'Tab', modifiers: ['ctrl'], description: 'Next tab', category: 'Navigation' },
  { id: 'prev-tab', key: 'Tab', modifiers: ['ctrl', 'shift'], description: 'Previous tab', category: 'Navigation' },
  { id: 'escape', key: 'Escape', modifiers: [], description: 'Close dialog/cancel', category: 'Actions' },
  { id: 'toggle-sidebar', key: 'b', modifiers: ['ctrl'], description: 'Toggle sidebar', category: 'Navigation' },
]

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  Navigation: Home,
  Help: Keyboard,
  Actions: RefreshCw,
  Portfolios: Briefcase,
  Charts: BarChart3,
}

const formatKey = (key: string) => {
  const keyMap: Record<string, string> = {
    '/': 'Slash',
    ',:': 'Comma',
    'Escape': 'Esc',
    'Tab': 'Tab',
    ' ': 'Space',
  }
  return keyMap[key] || key.toUpperCase()
}

function ShortcutCard({ shortcut }: { shortcut: KeyboardShortcut }) {
  const modifiers = shortcut.modifiers || []

  return (
    <div className="flex items-center justify-between p-2 border border-foreground/10 rounded-lg hover:bg-muted/50 transition-colors">
      <span className="text-sm">{shortcut.description}</span>
      <div className="flex items-center gap-1">
        {modifiers.map((mod) => (
          <kbd key={mod} className="px-2 py-1 text-xs font-mono bg-muted rounded border border-foreground/20">
            {mod === 'ctrl' ? 'Ctrl' : mod === 'meta' ? 'Cmd' : mod.charAt(0).toUpperCase() + mod.slice(1)}
          </kbd>
        ))}
        <kbd className="px-2 py-1 text-xs font-mono bg-background rounded border border-foreground/20">
          {formatKey(shortcut.key)}
        </kbd>
      </div>
    </div>
  )
}

function ShortcutCategory({ category, shortcuts }: { category: string; shortcuts: KeyboardShortcut[] }) {
  const Icon = CATEGORY_ICONS[category] || Keyboard

  return (
    <Card className="border-2 border-foreground">
      <CardHeader className="py-3 border-b-2 border-foreground bg-muted/30">
        <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
          <Icon className="h-4 w-4" />
          {category}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-3 space-y-1">
        {shortcuts.map((shortcut) => (
          <ShortcutCard key={shortcut.id} shortcut={shortcut} />
        ))}
      </CardContent>
    </Card>
  )
}

export function KeyboardShortcuts({
  shortcuts = DEFAULT_SHORTCUTS,
  onShortcutExecute,
  className,
}: KeyboardShortcutsProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const categories = [...new Set(shortcuts.map((s) => s.category))]

  const filteredShortcuts = shortcuts.filter((shortcut) => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      shortcut.description.toLowerCase().includes(query) ||
      shortcut.category.toLowerCase().includes(query) ||
      shortcut.key.toLowerCase().includes(query)
    )
  })

  const groupedShortcuts = categories.reduce<Record<string, KeyboardShortcut[]>>((acc, category) => {
    acc[category] = filteredShortcuts.filter((s) => s.category === category)
    return acc
  }, {})

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === '?' && !event.ctrlKey && !event.metaKey && !event.altKey) {
        event.preventDefault()
        setIsOpen((prev) => !prev)
        return
      }

      if (event.key === 'Escape') {
        setIsOpen(false)
        return
      }

      const matchingShortcut = shortcuts.find((shortcut) => {
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase()
        const ctrlMatch = shortcut.modifiers?.includes('ctrl') === event.ctrlKey
        const metaMatch = shortcut.modifiers?.includes('meta') === event.metaKey
        const altMatch = shortcut.modifiers?.includes('alt') === event.altKey
        const shiftMatch = shortcut.modifiers?.includes('shift') === event.shiftKey

        return (
          keyMatch &&
          (!shortcut.modifiers?.length || (ctrlMatch && metaMatch && altMatch && shiftMatch))
        )
      })

      if (matchingShortcut && !event.target?.toString().includes('INPUT') && !event.target?.toString().includes('TEXTAREA')) {
        event.preventDefault()
        matchingShortcut.action?.()
        onShortcutExecute?.(matchingShortcut.id)
      }
    },
    [shortcuts, onShortcutExecute]
  )

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  return (
    <>
      <div className={cn('flex items-center gap-2', className)}>
        <kbd className="px-2 py-1 text-xs font-mono bg-muted rounded border border-foreground/20 hidden sm:inline-flex">
          ?
        </kbd>
        <Button variant="ghost" size="sm" onClick={() => setIsOpen(true)} className="text-muted-foreground">
          <Keyboard className="h-4 w-4 mr-1" />
          Shortcuts
        </Button>
      </div>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col border-2 border-foreground">
          <DialogHeader className="border-b-2 border-foreground pb-4">
            <DialogTitle className="text-lg font-black uppercase flex items-center gap-2">
              <Keyboard className="h-5 w-5" />
              Keyboard Shortcuts
            </DialogTitle>
            <div className="relative mt-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search shortcuts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border-2 border-foreground bg-background rounded-none focus:outline-none focus:ring-2 focus:ring-foreground"
              />
            </div>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {Object.entries(groupedShortcuts)
              .filter(([_, shortcuts]) => shortcuts.length > 0)
              .map(([category, categoryShortcuts]) => (
                <ShortcutCategory
                  key={category}
                  category={category}
                  shortcuts={categoryShortcuts}
                />
              ))}
          </div>

          <div className="border-t-2 border-foreground p-4 bg-muted/30">
            <p className="text-xs text-muted-foreground text-center">
              Press <kbd className="px-2 py-1 text-xs font-mono bg-muted rounded border">?</kbd> to open this dialog anytime
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

export function useKeyboardShortcuts(
  shortcuts: KeyboardShortcut[],
  onExecute?: (id: string) => void
) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const matchingShortcut = shortcuts.find((shortcut) => {
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase()
        const ctrlMatch = shortcut.modifiers?.includes('ctrl') === event.ctrlKey
        const metaMatch = shortcut.modifiers?.includes('meta') === event.metaKey
        const altMatch = shortcut.modifiers?.includes('alt') === event.altKey
        const shiftMatch = shortcut.modifiers?.includes('shift') === event.shiftKey

        return (
          keyMatch &&
          (!shortcut.modifiers?.length || (ctrlMatch && metaMatch && altMatch && shiftMatch))
        )
      })

      if (
        matchingShortcut &&
        !(event.target instanceof HTMLInputElement) &&
        !(event.target instanceof HTMLTextAreaElement)
      ) {
        event.preventDefault()
        matchingShortcut.action?.()
        onExecute?.(matchingShortcut.id)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [shortcuts, onExecute])
}

export default KeyboardShortcuts
