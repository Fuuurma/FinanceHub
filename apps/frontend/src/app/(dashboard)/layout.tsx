// app/(dashboard)/layout.tsx
'use client'

import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/layout/sidebar"
import { Navbar } from "@/components/layout/navbar"
import { RightSidebar } from "@/components/layout/right-sidebar"
import { useEffect, useState } from "react"
import { shortcutRegistry, registerDefaultShortcuts, useGlobalShortcuts, useHelpShortcut } from "@/lib/shortcuts"
import { ShortcutHelpDialog } from "@/lib/shortcuts/ShortcutHelpDialog"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [isHydrated, setIsHydrated] = useState(false)
  const [showHelp, setShowHelp] = useState(false)

  useEffect(() => {
    setIsHydrated(true)
    registerDefaultShortcuts()
  }, [])

  useHelpShortcut(() => setShowHelp(true))

  useGlobalShortcuts([
    {
      key: '?',
      description: 'Show keyboard shortcuts',
      action: () => setShowHelp(true),
    },
    {
      key: 'escape',
      description: 'Close dialog',
      action: () => setShowHelp(false),
    },
  ])

  if (!isHydrated) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-background">
        <div className="flex items-center gap-3">
          <div className="h-6 w-6 border-2 border-foreground animate-spin border-t-transparent" />
          <span className="font-mono text-xs font-black uppercase tracking-widest">INITIALIZING...</span>
        </div>
      </div>
    )
  }

  return (
    <SidebarProvider defaultOpen>
      <div className="flex h-screen w-full overflow-hidden">
        <AppSidebar />
        
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          <Navbar />
          <main className="flex-1 overflow-y-auto bg-background">
            {children}
          </main>
        </div>

        <RightSidebar />
      </div>

      <ShortcutHelpDialog
        open={showHelp}
        onOpenChange={setShowHelp}
      />
    </SidebarProvider>
  )
}
