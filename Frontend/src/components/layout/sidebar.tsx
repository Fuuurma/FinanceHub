'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, TrendingUp, Wallet, BarChart3,
  Newspaper, Bell, Layers, ChevronUp,
  Settings, LogOut, Key, Activity, Zap, Target,
  FileText, Search, History, Cpu, Plus, ArrowRight,
  PieChart, TrendingUp as TrendingUpIcon, DollarSign,
  BookOpen, Clock, Globe, Cpu as CpuIcon, Radio, User
} from 'lucide-react'
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarHeader,
  SidebarGroup, SidebarGroupLabel,
  SidebarMenu, SidebarMenuItem, SidebarMenuButton,
  SidebarMenuBadge, SidebarSeparator, SidebarRail,
  SidebarMenuSub, SidebarMenuSubItem, SidebarMenuSubButton,
  useSidebar,
} from '@/components/ui/sidebar'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger, DropdownMenuLabel, DropdownMenuGroup } from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface NavItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  shortcut: string
  description: string
  badge?: string
  submenu?: Array<{ title: string; href: string; description?: string }>
}

const navItems: NavItem[] = [
  {
    title: 'Terminal',
    href: '/market/dashboard',
    icon: LayoutDashboard,
    shortcut: '1',
    description: 'Main trading dashboard'
  },
  {
    title: 'Markets',
    href: '/market/overview',
    icon: TrendingUp,
    shortcut: '2',
    description: 'Market overview & data',
    submenu: [
      { title: 'Overview', href: '/market/overview', description: 'Global market summary' },
      { title: 'Stocks', href: '/market/stocks', description: 'Stock listings & data' },
      { title: 'Indices', href: '/market/indices', description: 'Market indices' },
      { title: 'Movers', href: '/market/movers', description: 'Top gainers & losers' },
    ]
  },
  {
    title: 'Portfolios',
    href: '/portfolios',
    icon: Wallet,
    shortcut: '3',
    description: 'Portfolio management',
    submenu: [
      { title: 'All Portfolios', href: '/portfolios', description: 'View all portfolios' },
      { title: 'Holdings', href: '/holdings', description: 'Portfolio holdings' },
      { title: 'Transactions', href: '/transactions', description: 'Transaction history' },
      { title: 'Analytics', href: '/analytics', description: 'Performance analytics' },
    ]
  },
  {
    title: 'Trading',
    href: '/trading',
    icon: Activity,
    shortcut: '4',
    description: 'Trading interface',
    badge: 'NEW'
  },
  {
    title: 'Charts',
    href: '/charts/advanced',
    icon: BarChart3,
    shortcut: '5',
    description: 'Advanced charting tools'
  },
  {
    title: 'Technical',
    href: '/technical',
    icon: TrendingUpIcon,
    shortcut: '6',
    description: 'Technical analysis',
    submenu: [
      { title: 'Scanner', href: '/technical', description: 'Technical indicators' },
      { title: 'By Symbol', href: '/technical/AAPL', description: 'Symbol analysis' },
    ]
  },
  {
    title: 'Fundamentals',
    href: '/fundamentals',
    icon: FileText,
    shortcut: '7',
    description: 'Fundamental analysis',
    submenu: [
      { title: 'Overview', href: '/fundamentals', description: 'Fundamental data' },
      { title: 'IEX Data', href: '/fundamentals/iex', description: 'IEX fundamentals' },
    ]
  },
  {
    title: 'Intelligence',
    href: '/news',
    icon: Newspaper,
    shortcut: '8',
    description: 'News & sentiment',
    submenu: [
      { title: 'News Feed', href: '/news', description: 'Latest news' },
      { title: 'Sentiment', href: '/sentiment', description: 'Sentiment analysis' },
      { title: 'Economics', href: '/economics', description: 'Economic data' },
    ]
  },
]

const toolItems: NavItem[] = [
  { title: 'Screener', href: '/screener', icon: Target, shortcut: 'G+S', description: 'Stock screener', badge: 'NEW' },
  { title: 'Watchlist', href: '/watchlist', icon: History, shortcut: 'G+W', description: 'Watchlist' },
  { title: 'Alerts', href: '/alerts', icon: Bell, shortcut: 'G+A', description: 'Price alerts', badge: '3' },
  { title: 'Crypto', href: '/crypto', icon: DollarSign, shortcut: 'G+C', description: 'Cryptocurrency data' },
]

const settingsItems: NavItem[] = [
  { title: 'Settings', href: '/settings', icon: Settings, description: 'App settings' },
  { title: 'Account', href: '/settings#account', icon: User, description: 'Account settings' },
  { title: 'API Keys', href: '/settings#keys', icon: Key, description: 'Manage API keys' },
]

function SidebarNavGroup({ items, title, shortcutHint }: { items: NavItem[]; title: string; shortcutHint?: string }) {
  const pathname = usePathname()
  const { state } = useSidebar()
  const isCollapsed = state === 'collapsed'

  return (
    <SidebarGroup>
      <SidebarGroupLabel className="text-[9px] font-black uppercase text-foreground/40 px-3 mb-1 group-data-[collapsible=icon]:hidden flex items-center justify-between">
        <span>{title}</span>
        {shortcutHint && <kbd className="h-4 px-1 border border-foreground/20 text-[8px] font-mono rounded-none">{shortcutHint}</kbd>}
      </SidebarGroupLabel>
      <SidebarMenu className="px-2 gap-1">
        {items.map((item) => (
          <React.Fragment key={item.title}>
            {item.submenu && item.submenu.length > 0 ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      isActive={pathname === item.href || pathname.startsWith(item.href + '/')}
                      className={cn(
                        "rounded-none border-2 border-transparent data-[active=true]:border-foreground data-[active=true]:bg-primary/10 hover:bg-muted h-10 px-3 transition-all cursor-pointer",
                        "group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-0"
                      )}
                      tooltip={item.description}
                    >
                      <item.icon className="h-4 w-4 shrink-0" />
                      <span className="font-black uppercase text-[11px] tracking-tight group-data-[collapsible=icon]:hidden">{item.title}</span>
                      <ChevronUp className="ml-auto h-3 w-3 rotate-180 transition-transform group-data-[collapsible=icon]:hidden" />
                      {item.badge && (
                        <Badge className="absolute top-1 right-1 h-4 min-w-4 p-0 flex items-center justify-center rounded-none bg-primary text-[8px] group-data-[collapsible=icon]:hidden">
                          {item.badge}
                        </Badge>
                      )}
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  side="right"
                  align="start"
                  sideOffset={8}
                  className="w-72 rounded-none border-4 border-foreground shadow-[8px_8px_0px_0px_var(--foreground)] p-0 bg-background"
                >
                  <div className="p-3 bg-foreground text-background font-black uppercase text-[10px] italic flex items-center gap-2">
                    <item.icon className="h-4 w-4" /> {item.title}
                  </div>
                  {item.submenu.map((sub) => (
                    <DropdownMenuItem key={sub.href} asChild>
                      <Link
                        href={sub.href}
                        className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex flex-col items-start gap-0.5 w-full"
                      >
                        <span className="flex items-center gap-2">
                          <ArrowRight className="h-3 w-3 opacity-50" />
                          {sub.title}
                        </span>
                        {sub.description && (
                          <span className="text-[9px] font-mono opacity-50 ml-5">{sub.description}</span>
                        )}
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <SidebarMenuItem>
                <SidebarMenuButton
                  asChild
                  isActive={pathname === item.href}
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
            )}
          </React.Fragment>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  )
}

export function AppSidebar() {
  const pathname = usePathname()
  const { state } = useSidebar()
  const isCollapsed = state === 'collapsed'

  return (
    <>
      <Sidebar className="border-r-4 border-foreground bg-background" collapsible="icon">
        <SidebarHeader className="h-16 flex items-center justify-center border-b-2 border-foreground bg-primary/5">
          <Link href="/market/dashboard" className="flex items-center gap-3 px-2">
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
          <SidebarNavGroup items={navItems} title="Core_Navigation" shortcutHint="⌘1-8" />

          <SidebarSeparator className="my-2 mx-4 h-[2px] bg-foreground/10" />

          <SidebarNavGroup items={toolItems} title="Tools_&_Utils" />

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
              side="top"
              align="start"
              sideOffset={8}
              className="w-80 rounded-none border-4 border-foreground shadow-[8px_8px_0px_0px_var(--foreground)] p-0 bg-background"
            >
              <DropdownMenuLabel className="font-black uppercase italic bg-foreground text-background p-3 border-b-2 border-foreground flex items-center justify-between">
                <span className="flex items-center gap-2"><Cpu className="h-4 w-4" /> User_Control_Panel</span>
                <Badge className="bg-green-500 text-white text-[8px]">ONLINE</Badge>
              </DropdownMenuLabel>
              
              <div className="p-2">
                <DropdownMenuGroup>
                  <DropdownMenuLabel className="text-[9px] font-black uppercase text-foreground/60 px-2 py-1">Account</DropdownMenuLabel>
                  <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <User className="h-4 w-4" /> Profile_Settings
                  </DropdownMenuItem>
                  <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <Settings className="h-4 w-4" /> App_Settings
                  </DropdownMenuItem>
                  <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <Key className="h-4 w-4" /> API_Keys_Management
                  </DropdownMenuItem>
                </DropdownMenuGroup>
                
                <DropdownMenuSeparator className="bg-foreground h-0.5 my-2" />
                
                <DropdownMenuGroup>
                  <DropdownMenuLabel className="text-[9px] font-black uppercase text-foreground/60 px-2 py-1">Preferences</DropdownMenuLabel>
                  <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <BookOpen className="h-4 w-4" /> Notifications_Prefs
                  </DropdownMenuItem>
                  <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <Clock className="h-4 w-4" /> Display_&_Appearance
                  </DropdownMenuItem>
                  <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <Globe className="h-4 w-4" /> Language_&_Region
                  </DropdownMenuItem>
                  <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <Radio className="h-4 w-4" /> Data_Provider_Status
                  </DropdownMenuItem>
                </DropdownMenuGroup>
                
                <DropdownMenuSeparator className="bg-foreground h-0.5 my-2" />
                
                <DropdownMenuGroup>
                  <DropdownMenuLabel className="text-[9px] font-black uppercase text-foreground/60 px-2 py-1">System</DropdownMenuLabel>
                  <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <PieChart className="h-4 w-4" /> Performance_Metrics
                  </DropdownMenuItem>
                  <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <Zap className="h-4 w-4" /> API_Usage_Stats
                  </DropdownMenuItem>
                  <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <ShieldAlert className="h-4 w-4" /> Security_Vault
                  </DropdownMenuItem>
                </DropdownMenuGroup>
                
                <DropdownMenuSeparator className="bg-foreground h-0.5 my-2" />
                
                <DropdownMenuItem asChild>
                  <Link href="/settings" className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground flex items-center gap-2">
                    <Settings className="h-4 w-4" /> Open_Settings_Page
                  </Link>
                </DropdownMenuItem>
                
                <DropdownMenuSeparator className="bg-foreground h-0.5" />
                
                <DropdownMenuItem className="p-3 font-black uppercase text-xs rounded-none cursor-pointer text-red-500 focus:bg-red-500 focus:text-white flex items-center gap-2">
                  <LogOut className="h-4 w-4" /> Terminate_Session
                </DropdownMenuItem>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarFooter>

        <SidebarRail />
      </Sidebar>
    </>
  )
}
