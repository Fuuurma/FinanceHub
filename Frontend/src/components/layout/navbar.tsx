'use client'

import { useState, useEffect } from 'react'
import { Search, User, LogOut, ShieldAlert, Settings, Moon, Sun, PanelLeft, Menu } from 'lucide-react'
import { useTheme } from 'next-themes'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { CommandPalette } from '../search/command-palette'
import { SignalCenter } from './navbar/signal-center'
import { useSidebar, SidebarTrigger } from '@/components/ui/sidebar'

export function Navbar() {
  const { setTheme, theme } = useTheme()
  const [commandOpen, setCommandOpen] = useState(false)
  const { isMobile } = useSidebar()

  return (
    <>
      <header className="sticky top-0 z-50 w-full h-16 border-b-4 border-foreground bg-background/95 backdrop-blur-md flex items-center px-6">
        <div className="flex items-center gap-4 flex-1">
          <SidebarTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-10 w-10 border-2 border-foreground rounded-none hover:bg-foreground hover:text-background transition-colors shadow-[2px_2px_0px_0px_var(--foreground)]"
            >
              <Menu className="h-4 w-4" />
            </Button>
          </SidebarTrigger>
          <div className="hidden lg:flex flex-col">
            <span className="text-[9px] font-black uppercase tracking-[0.2em] leading-none opacity-50">Network_Health</span>
            <div className="flex items-center gap-2">
               <div className="h-2 w-2 bg-green-500 animate-pulse" />
               <span className="text-xs font-mono font-bold">STABLE_14MS</span>
            </div>
          </div>
        </div>

        <div className="flex-2 max-w-xl">
          <button 
            onClick={() => setCommandOpen(true)}
            className="w-full h-10 bg-muted/30 border-2 border-foreground px-4 flex items-center justify-between group hover:bg-background transition-all"
          >
            <div className="flex items-center gap-3">
              <Search className="h-4 w-4 opacity-40 group-hover:opacity-100" />
              <span className="font-mono text-[10px] font-black uppercase opacity-40 group-hover:opacity-100">Execute Command (⌘K)</span>
            </div>
            <div className="flex gap-1">
               <kbd className="h-5 px-1.5 border border-foreground/30 text-[9px] flex items-center bg-background font-mono">⌘</kbd>
               <kbd className="h-5 px-1.5 border border-foreground/30 text-[9px] flex items-center bg-background font-mono">K</kbd>
            </div>
          </button>
        </div>

        <div className="flex items-center gap-3 flex-1 justify-end">
          <SignalCenter />
          
          <Button 
            variant="ghost" size="icon" 
            className="h-10 w-10 border-2 border-foreground rounded-none brutalist-interactive"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button className="h-10 px-4 border-2 border-foreground rounded-none bg-foreground text-background font-black uppercase text-xs hover:bg-primary hover:text-primary-foreground transition-colors">
                ADMIN_01
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-64 rounded-none border-4 border-foreground shadow-[10px_10px_0px_0px_var(--foreground)]">
              <DropdownMenuLabel className="font-black uppercase italic bg-primary text-primary-foreground p-3 border-b-2 border-foreground">Session_Identity</DropdownMenuLabel>
              <DropdownMenuItem className="p-3 font-bold uppercase text-xs focus:bg-foreground focus:text-background"><User className="mr-2 h-4 w-4"/> Profile_Settings</DropdownMenuItem>
              <DropdownMenuItem className="p-3 font-bold uppercase text-xs focus:bg-foreground focus:text-background"><ShieldAlert className="mr-2 h-4 w-4"/> Security_Vault</DropdownMenuItem>
              <DropdownMenuSeparator className="bg-foreground h-0.5" />
              <DropdownMenuItem className="p-3 font-black uppercase text-xs text-red-500 focus:bg-red-500 focus:text-white"><LogOut className="mr-2 h-4 w-4"/> Terminate_All</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <CommandPalette open={commandOpen} onOpenChange={setCommandOpen} />
    </>
  )
}
