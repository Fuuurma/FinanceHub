'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, TrendingUp, Wallet, Search, BarChart3,
  Newspaper, MessageSquare, ChevronUp, User2, Bell, AlertCircle, Layers
} from 'lucide-react'
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarHeader,
  SidebarGroup, SidebarGroupLabel, SidebarGroupContent,
  SidebarMenu, SidebarMenuItem, SidebarMenuButton,
  SidebarMenuBadge, SidebarSeparator,
} from '@/components/ui/sidebar'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'

const navItems = [
  { title: 'Terminal', href: '/dashboard', icon: LayoutDashboard },
  { title: 'Markets', href: '/markets', icon: TrendingUp },
  { title: 'Liquidity', href: '/portfolios', icon: Wallet },
  { title: 'Analysis', href: '/analytics', icon: BarChart3 },
  { title: 'Intelligence', href: '/news', icon: Newspaper },
]

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar collapsible="icon" className="border-r-4 border-foreground bg-background">
      <SidebarHeader className="h-16 flex items-center justify-center border-b-2 border-foreground bg-primary/10">
        <div className="flex items-center gap-3 px-2">
          <div className="h-8 w-8 bg-foreground text-background flex items-center justify-center border-2 border-foreground group-data-[collapsible=icon]:h-10 group-data-[collapsible=icon]:w-10 transition-all">
            <Layers className="h-5 w-5" />
          </div>
          <span className="font-black text-sm uppercase tracking-tighter truncate group-data-[collapsible=icon]:hidden italic">
            Liquid_System
          </span>
        </div>
      </SidebarHeader>

      <SidebarContent className="gap-0 py-4">
        <SidebarGroup>
          <SidebarGroupLabel className="text-[9px] font-black uppercase text-foreground/40 px-4 mb-2 group-data-[collapsible=icon]:hidden">Core_Navigation</SidebarGroupLabel>
          <SidebarMenu className="px-2 gap-1">
            {navItems.map((item) => (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton
                  asChild
                  isActive={pathname === item.href}
                  className="rounded-none border-2 border-transparent data-[active=true]:border-foreground data-[active=true]:bg-primary/10 hover:bg-muted h-10"
                  tooltip={item.title}
                >
                  <Link href={item.href} className="flex items-center gap-3">
                    <item.icon className="h-4 w-4 shrink-0" />
                    <span className="font-black uppercase text-[11px] tracking-tight">{item.title}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>

        <SidebarSeparator className="my-4 mx-4 h-[2px] bg-foreground/10" />

        <SidebarGroup>
          <SidebarGroupLabel className="text-[9px] font-black uppercase text-foreground/40 px-4 mb-2 group-data-[collapsible=icon]:hidden">Live_Signals</SidebarGroupLabel>
          <SidebarMenu className="px-2 gap-1">
            {[
              { title: 'Alerts', icon: AlertCircle, badge: '3', color: 'text-orange-500' },
              { title: 'Logs', icon: MessageSquare, badge: '12', color: 'text-blue-500' }
            ].map((item) => (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton className="rounded-none hover:bg-muted h-10" tooltip={item.title}>
                  <item.icon className={`h-4 w-4 shrink-0 ${item.color}`} />
                  <span className="font-bold uppercase text-[10px] tracking-wide">{item.title}</span>
                  <SidebarMenuBadge className="rounded-none bg-foreground text-background font-mono text-[9px] group-data-[collapsible=icon]:hidden">
                    {item.badge}
                  </SidebarMenuBadge>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-2 border-t-2 border-foreground bg-muted/20">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton size="lg" className="rounded-none border-2 border-foreground bg-background hover:bg-primary/5 transition-all">
              <div className="h-8 w-8 bg-primary/20 flex items-center justify-center border border-foreground/20">
                <User2 className="h-4 w-4" />
              </div>
              <div className="flex flex-col gap-0.5 leading-none group-data-[collapsible=icon]:hidden">
                <span className="font-black uppercase text-[10px]">Auth_Admin_01</span>
                <span className="text-[9px] font-mono text-primary font-bold">VIP_ACCESS</span>
              </div>
              <ChevronUp className="ml-auto h-4 w-4 group-data-[collapsible=icon]:hidden opacity-40" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent side="right" align="end" className="w-56 rounded-none border-4 border-foreground shadow-[8px_8px_0px_0px_var(--foreground)] p-0">
            <div className="p-3 bg-foreground text-background font-black uppercase text-[10px] italic">Access_Protocol</div>
            <DropdownMenuItem className="p-3 font-bold uppercase text-xs rounded-none cursor-pointer focus:bg-primary focus:text-primary-foreground">Settings</DropdownMenuItem>
            <DropdownMenuItem className="p-3 font-black uppercase text-xs rounded-none cursor-pointer text-red-500 focus:bg-red-500 focus:text-white border-t-2 border-foreground">Log_Out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarFooter>
    </Sidebar>
  )
}