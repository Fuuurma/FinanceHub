'use client'

import * as React from 'react'
import {
  Star, TrendingUp, TrendingDown, Plus, MoreHorizontal,
  Wallet, Activity, Zap, RefreshCw, BarChart2
} from 'lucide-react'
import {
  Sidebar, SidebarContent, SidebarHeader, SidebarGroup,
  SidebarGroupLabel, SidebarGroupContent, SidebarMenu,
  SidebarMenuItem, SidebarMenuButton, SidebarSeparator,
  SidebarMenuBadge, SidebarRail,
} from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const portfolios = [
  { name: 'Main_Vault', value: '$125,430.00', change: '+2.34%', pos: true, allocation: 65 },
  { name: 'Alpha_Growth', value: '$42,100.50', change: '-0.45%', pos: false, allocation: 22 },
  { name: 'DeFi_Pool', value: '$24,890.25', change: '+5.12%', pos: true, allocation: 13 },
]

const liveTickers = [
  { symbol: 'BTC', price: 64250.00, change: '+2.98%', vol: '1.2B' },
  { symbol: 'ETH', price: 3450.12, change: '-1.95%', vol: '890M' },
  { symbol: 'SOL', price: 145.80, change: '+5.20%', vol: '234M' },
  { symbol: 'NVDA', price: '875.40', change: '+1.23%', vol: '45M' },
  { symbol: 'TSLA', price: '175.40', change: '-2.15%', vol: '112M' },
]

const watchlists = [
  { name: 'Tech_Titans', count: 12, icon: '🔥' },
  { name: 'DeFi_Perps', count: 8, icon: '⚡' },
  { name: 'Macro_Indices', count: 5, icon: '📊' },
]

export function RightSidebar() {
  return (
    <Sidebar side="right" collapsible="none" className="w-80 border-l-4 border-foreground hidden xl:flex bg-background">
      <SidebarHeader className="h-14 border-b-2 border-foreground flex flex-row items-center justify-between px-4 bg-muted/20">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-green-500 animate-pulse" />
          <h2 className="text-[10px] font-black uppercase tracking-[0.2em] italic">Market_Overview</h2>
        </div>
        <div className="flex items-center gap-2">
          <Button size="icon" variant="ghost" className="h-6 w-6 rounded-none border border-foreground/20">
            <RefreshCw className="h-3 w-3" />
          </Button>
          <Badge className="rounded-none bg-green-500 text-white font-mono text-[9px] font-bold flex items-center gap-1">
            <Zap className="h-3 w-3 fill-white" />LIVE
          </Badge>
        </div>
      </SidebarHeader>

      <SidebarContent className="gap-0">
        <ScrollArea className="flex-1 h-[calc(100vh-3.5rem)]">
          <SidebarGroup className="p-4">
            <div className="flex items-center justify-between mb-3">
              <SidebarGroupLabel className="p-0 h-auto text-[10px] font-black uppercase text-foreground flex items-center gap-2">
                <Wallet className="h-3 w-3" /> Active_Vaults
              </SidebarGroupLabel>
              <Button size="sm" className="h-6 rounded-none border-2 border-foreground text-[9px] font-black uppercase px-2 brutalist-interactive">
                <Plus className="h-3 w-3 mr-1" /> New
              </Button>
            </div>
            <div className="space-y-2">
              {portfolios.map((p) => (
                <div
                  key={p.name}
                  className="p-3 border-2 border-foreground bg-background hover:bg-primary/5 transition-all group relative overflow-hidden cursor-pointer"
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-[9px] font-bold uppercase opacity-50">{p.name}</span>
                    <MoreHorizontal className="h-3 w-3 opacity-20 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <div className="text-lg font-black font-mono tracking-tighter leading-none">{p.value}</div>
                  <div className="flex items-center justify-between mt-2">
                    <div className={`text-[10px] font-bold flex items-center gap-1 ${p.pos ? 'text-green-500' : 'text-red-500'}`}>
                      {p.pos ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                      {p.change}
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="h-1 bg-foreground/20 flex-1 max-w-[60px]">
                        <div
                          className="h-full bg-primary"
                          style={{ width: `${p.allocation}%` }}
                        />
                      </div>
                      <span className="text-[9px] font-mono opacity-40">{p.allocation}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </SidebarGroup>

          <SidebarSeparator className="h-[2px] bg-foreground/10" />

          <SidebarGroup className="p-4">
            <div className="flex items-center justify-between mb-3">
              <SidebarGroupLabel className="px-0 h-auto text-[10px] font-black uppercase text-foreground flex items-center gap-2">
                <BarChart2 className="h-3 w-3" /> Watchlists
              </SidebarGroupLabel>
              <Button size="sm" variant="ghost" className="h-6 rounded-none text-[9px] font-black uppercase px-2">
                <Star className="h-3 w-3 mr-1" /> Manage
              </Button>
            </div>
            <SidebarMenu className="gap-1">
              {watchlists.map((w) => (
                <SidebarMenuItem key={w.name}>
                  <SidebarMenuButton className="rounded-none border-2 border-transparent hover:border-foreground hover:bg-muted font-black text-[11px] uppercase group">
                    <span className="mr-2 text-sm">{w.icon}</span>
                    {w.name}
                    <SidebarMenuBadge className="rounded-none border border-foreground/20 text-[9px] font-mono ml-auto">
                      {w.count}
                    </SidebarMenuBadge>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroup>

          <SidebarSeparator className="h-[2px] bg-foreground/10" />

          <SidebarGroup className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <Activity className="h-3 w-3 text-primary animate-pulse" />
              <span className="text-[10px] font-black uppercase">Ticker_Stream</span>
              <Badge variant="outline" className="ml-auto rounded-none border-green-500/50 text-green-500 text-[9px] font-mono">
                +2.98%
              </Badge>
            </div>
            <div className="divide-y-2 divide-foreground/5">
              {liveTickers.map((ticker) => (
                <div
                  key={ticker.symbol}
                  className="py-2 flex justify-between items-center group cursor-crosshair hover:bg-muted/30 transition-colors px-2 -mx-2"
                >
                  <div>
                    <div className="text-xs font-black italic">{ticker.symbol}/USD</div>
                    <div className="text-[9px] font-mono opacity-40">VOL: {ticker.vol}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-black font-mono">${typeof ticker.price === 'number' ? ticker.price.toLocaleString() : ticker.price}</div>
                    <div className={cn(
                      "text-[9px] font-bold flex items-center justify-end gap-1",
                      ticker.change.includes('+') ? 'text-green-500' : 'text-red-500'
                    )}>
                      {ticker.change.includes('+') ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                      {ticker.change}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </SidebarGroup>

          <div className="p-4 pt-0">
            <div className="brutalist-glass p-3 bg-muted/20 border-2 border-foreground/10">
              <div className="flex items-center justify-between text-[9px] font-mono uppercase font-bold mb-2">
                <span className="opacity-50">System_Status</span>
                <span className="text-green-500">● ONLINE</span>
              </div>
              <div className="space-y-1 text-[10px]">
                <div className="flex justify-between">
                  <span className="opacity-60">Latency</span>
                  <span className="font-mono">14ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="opacity-60">API Health</span>
                  <span className="font-mono text-green-500">100%</span>
                </div>
                <div className="flex justify-between">
                  <span className="opacity-60">WebSocket</span>
                  <span className="font-mono text-green-500">CONNECTED</span>
                </div>
              </div>
            </div>
          </div>
        </ScrollArea>
      </SidebarContent>

      <SidebarRail />
    </Sidebar>
  )
}
