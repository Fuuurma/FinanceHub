'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, TrendingUp, Wallet, BarChart3,
  Newspaper, Bell, Layers, ChevronUp,
  Settings, LogOut, Key, Activity, Zap, Target,
  FileText, Search, History, Cpu, Plus
} from 'lucide-react'
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarHeader,
  SidebarGroup, SidebarGroupLabel,
  SidebarMenu, SidebarMenuItem, SidebarMenuButton,
  SidebarMenuBadge, SidebarSeparator, SidebarRail,
  SidebarMenuSub, SidebarMenuSubItem, SidebarMenuSubButton,
} from '@/components/ui/sidebar'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface NavItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  shortcut: string
  description: string
  badge?: string
  submenu?: Array<{ title: string; href: string }>
}

const navItems: NavItem[] = [
  {
    title: 'Terminal',
    href: '/dashboard',
    icon: LayoutDashboard,
    shortcut: '1',
    description: 'Main trading dashboard'
  },
  {
    title: 'Markets',
    href: '/markets',
    icon: TrendingUp,
    shortcut: '2',
    description: 'Market overview & data',
    submenu: [
      { title: 'Overview', href: '/market/overview' },
      { title: 'Stocks', href: '/market/stocks' },
      { title: 'Indices', href: '/market/indices' },
    ]
  },
  {
    title: 'Portfolios',
    href: '/portfolios',
    icon: Wallet,
    shortcut: '3',
    description: 'Portfolio management',
    submenu: [
      { title: 'Holdings', href: '/holdings' },
      { title: 'Transactions', href: '/transactions' },
      { title: 'Performance', href: '/analytics' },
      { title: 'Attribution', href: '/holdings?tab=attribution' },
    ]
  },
  {
    title: 'Charts',
    href: '/charts/advanced',
    icon: BarChart3,
    shortcut: '4',
    description: 'Advanced charting tools'
  },
  {
    title: 'Analysis',
    href: '/analytics',
    icon: BarChart3,
    shortcut: '5',
    description: 'Analytics & reports',
    submenu: [
      { title: 'Performance', href: '/analytics' },
      { title: 'Attribution', href: '/analytics?tab=attribution' },
    ]
  },
  {
    title: 'Fundamentals',
    href: '/fundamentals',
    icon: FileText,
    shortcut: '6',
    description: 'Fundamental analysis'
  },
  {
    title: 'Intelligence',
    href: '/news',
    icon: Newspaper,
    shortcut: '7',
    description: 'News & sentiment',
    submenu: [
      { title: 'News Feed', href: '/news' },
      { title: 'Sentiment', href: '/sentiment' },
    ]
  },
]

const toolItems: NavItem[] = [
  { title: 'Trading', href: '/trading', icon: Activity, shortcut: 'G+T', description: 'Trading interface', badge: 'NEW' },
  { title: 'Screener', href: '/screener', icon: Target, shortcut: 'G+S', description: 'Stock screener', badge: 'NEW' },
  { title: 'Watchlist', href: '/watchlist', icon: History, shortcut: 'G+W', description: 'Watchlist' },
  { title: 'Alerts', href: '/alerts', icon: Bell, shortcut: 'G+A', description: 'Price alerts', badge: '3' },
]

const aiItems: NavItem[] = [
  { title: 'AI Advisor', href: '/ai', icon: Cpu, shortcut: 'G+A', description: 'AI-powered insights', badge: 'GLM-4.7' },
]

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <>
      <Sidebar className="border-r-4 border-foreground bg-background" collapsible="icon">
        <SidebarHeader className="h-16 flex items-center justify-center border-b-2 border-foreground bg-primary/5">
          <Link href="/dashboard" className="flex items-center gap-3 px-2">
            <div className="h-9 w-9 bg-foreground text-background flex items-center justify-center border-2 border-foreground shadow-[3px_3px_0px_0px_var(--muted-foreground)] transition-all group-data-[collapsible=icon]:h-10 group-data-[collapsible=icon]:w-10 hover:translate-x-[-1px] hover:translate-y-[-1px] hover:shadow-[4px_4px_0px_0px_var(--muted-foreground)]">
              <Layers className="h-5 w-5" />
            </div>
            <div className="flex flex-col group-data-[collapsible=icon]:hidden">
              <span className="font-black text-xs uppercase tracking-tighter italic leading-none">Liquid_System</span>
              <span className="text-[9px] font-mono text-primary font-bold">V3.1.4a</span>
            </div>
          </Link>
        </SidebarHeader>

        <SidebarContent className="gap-0 py-2">
          <SidebarGroup>
            <SidebarGroupLabel className="text-[9px] font-black uppercase text-foreground/40 px-3 mb-1 group-data-[collapsible=icon]:hidden flex items-center justify-between">
              <span>Core_Navigation</span>
              <kbd className="h-4 px-1 border border-foreground/20 text-[8px] font-mono rounded-none">⌘1-7</kbd>
            </SidebarGroupLabel>
            <SidebarMenu className="px-2 gap-1">
              {navItems.map((item) => (
                <React.Fragment key={item.title}>
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      asChild
                      isActive={pathname === item.href || pathname.startsWith(item.href + '/')}
                      className={cn(
                        "rounded-none border-2 border-transparent data-[active=true]:border-foreground data-[active=true]:bg-primary/10 hover:bg-muted h-10 px-3 transition-all",
                        "group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-0"
                      )}
                      tooltip={item.description}
                    >
                      <Link href={item.href} className="flex items-center gap-3 w-full">
                        <item.icon className="h-4 w-4 shrink-0" />
                        <span className="font-black uppercase text-[11px] tracking-tight group-data-[collapsible=icon]:hidden">{item.title}</span>
                        <kbd className="ml-auto h-5 min-w-5 px-1 border border-foreground/20 text-[9px] font-mono flex items-center justify-center rounded-none group-data-[collapsible=icon]:hidden">
                          {item.shortcut}
                        </kbd>
                        {item.badge && (
                          <Badge className="absolute top-1 right-1 h-4 min-w-4 p-0 flex items-center justify-center rounded-none bg-primary text-[8px] group-data-[collapsible=icon]:hidden">
                            {item.badge}
                          </Badge>
                        )}
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </React.Fragment>
              ))}
            </SidebarMenu>
          </SidebarGroup>

          <SidebarSeparator className="my-2 mx-4 h-[2px] bg-foreground/10" />

          <SidebarGroup>
            <SidebarGroupLabel className="text-[9px] font-black uppercase text-foreground/40 px-3 mb-1 group-data-[collapsible=icon]:hidden">
              Tools_&_Utils
            </SidebarGroupLabel>
            <SidebarMenu className="px-2 gap-1">
              {toolItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.href}
                    className="rounded-none border-2 border-transparent hover:bg-muted h-10"
                    tooltip={item.title}
                  >
                    <Link href={item.href} className="flex items-center gap-3">
                      <item.icon className="h-4 w-4 shrink-0" />
                      <span className="font-bold uppercase text-[10px] tracking-wide">{item.title}</span>
                      {item.badge && (
                        <SidebarMenuBadge className="rounded-none bg-primary text-background font-mono text-[9px] group-data-[collapsible=icon]:hidden">
                          {item.badge}
                        </SidebarMenuBadge>
                      )}
                      <kbd className="ml-auto h-5 px-1 border border-foreground/20 text-[9px] font-mono flex items-center rounded-none group-data-[collapsible=icon]:hidden">
                        {item.shortcut}
                      </kbd>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroup>

          <SidebarSeparator className="my-2 mx-4 h-[2px] bg-foreground/10" />

          <SidebarGroup>
            <SidebarGroupLabel className="text-[9px] font-black uppercase text-foreground/40 px-3 mb-1 group-data-[collapsible=icon]:hidden">
              Intelligence
            </SidebarGroupLabel>
            <SidebarMenu className="px-2 gap-1">
              {aiItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.href}
                    className="rounded-none border-2 border-transparent hover:bg-muted h-10"
                    tooltip={item.title}
                  >
                    <Link href={item.href} className="flex items-center gap-3">
                      <item.icon className="h-4 w-4 shrink-0 text-primary" />
                      <span className="font-bold uppercase text-[10px] tracking-wide">{item.title}</span>
                      {item.badge && (
                        <SidebarMenuBadge className="rounded-none bg-primary text-background font-mono text-[9px] group-data-[collapsible=icon]:hidden">
                          {item.badge}
                        </SidebarMenuBadge>
                      )}
                      <kbd className="ml-auto h-5 px-1 border border-foreground/20 text-[9px] font-mono flex items-center rounded-none group-data-[collapsible=icon]:hidden">
                        {item.shortcut}
                      </kbd>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroup>

          <SidebarSeparator className="my-2 mx-4 h-[2px] bg-foreground/10" />

          <SidebarGroup>
            <SidebarGroupLabel className="text-[9px] font-black uppercase text-foreground/40 px-3 mb-1 group-data-[collapsible=icon]:hidden">
              Quick_Actions
            </SidebarGroupLabel>
            <SidebarMenu className="px-2 gap-1">
              <SidebarMenuItem>
                <SidebarMenuButton className="rounded-none border-2 border-dashed border-foreground/20 hover:border-foreground hover:bg-muted h-10" tooltip="Quick Search">
                  <Search className="h-4 w-4 shrink-0" />
                  <span className="font-bold uppercase text-[10px] tracking-wide">Search</span>
                  <kbd className="ml-auto h-5 px-1 border border-foreground/20 text-[9px] font-mono flex items-center rounded-none">⌘K</kbd>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter className="p-2 border-t-2 border-foreground bg-muted/10">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <SidebarMenuButton
                size="lg"
                className={cn(
                  "rounded-none border-2 border-foreground bg-background hover:bg-primary/5 transition-all cursor-pointer",
                  "group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-0"
                )}
              >
                <div className="h-8 w-8 bg-primary/20 flex items-center justify-center border border-foreground/20 relative">
                  <Activity className="h-4 w-4" />
                  <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 bg-green-500 border border-foreground animate-pulse" />
                </div>
                <div className="flex flex-col gap-0.5 leading-none group-data-[collapsible=icon]:hidden text-left">
                  <span className="font-black uppercase text-[10px]">Auth_Admin_01</span>
                  <span className="text-[9px] font-mono text-primary font-bold flex items-center gap-1">
                    <Zap className="h-3 w-3 fill-primary" />VIP_ACCESS
                  </span>
                </div>
                <ChevronUp className="ml-auto h-4 w-4 group-data-[collapsible=icon]:hidden opacity-40" />
              </SidebarMenuButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              side="right"
              align="start"
              sideOffset={8}
              className="w-64 rounded-none border-4 border-foreground shadow-[8px_8px_0px_0px_var(--foreground)] p-0 bg-background"
            >
              <div className="p-3 bg-foreground text-background font-black uppercase text-[10px] italic flex items-center gap-2">
                <Cpu className="h-4 w-4" /> Access_Protocol
              </div>
              <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                <Settings className="h-4 w-4" /> Settings
              </DropdownMenuItem>
              <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                <Key className="h-4 w-4" /> API_Keys
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-foreground h-0.5" />
              <DropdownMenuItem className="p-3 font-black uppercase text-xs rounded-none cursor-pointer text-red-500 focus:bg-red-500 focus:text-white flex items-center gap-2">
                <LogOut className="h-4 w-4" /> Terminate_Session
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarFooter>

        <SidebarRail />
      </Sidebar>
    </>
  )
}
