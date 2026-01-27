'use client'

import * as React from 'react'
import {
  Star, TrendingUp, TrendingDown, Plus, MoreHorizontal,
  Wallet, ListChecks, Activity, Zap
} from 'lucide-react'
import {
  Sidebar, SidebarContent, SidebarHeader, SidebarGroup,
  SidebarGroupLabel, SidebarGroupContent, SidebarMenu,
  SidebarMenuItem, SidebarMenuButton, SidebarSeparator,
} from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'

const portfolios = [
  { name: 'Main_Vault', value: '$125,430.00', change: '+2.34%', pos: true },
  { name: 'Alpha_Growth', value: '$42,100.50', change: '-0.45%', pos: false },
]

const liveTickers = [
  { symbol: 'BTC', price: 64250.00, change: '+2.98%' },
  { symbol: 'ETH', price: 3450.12, change: '-1.95%' },
  { symbol: 'SOL', price: 145.80, change: '+5.20%' },
]

export function RightSidebar() {
  return (
    <Sidebar side="right" collapsible="none" className="w-80 border-l-4 border-foreground hidden xl:flex bg-background">
      <SidebarHeader className="h-16 border-b-2 border-foreground flex flex-row items-center justify-between px-4 bg-muted/30">
        <h2 className="text-[10px] font-black uppercase tracking-[0.2em] italic">Market_Overview</h2>
        <Badge className="rounded-none bg-green-500 text-white font-mono text-[9px]">LIVE</Badge>
      </SidebarHeader>

      <SidebarContent className="gap-0">
        <ScrollArea className="flex-1">
          {/* ASSET ALLOCATION HUD */}
          <SidebarGroup className="p-4">
            <div className="flex items-center justify-between mb-4">
              <SidebarGroupLabel className="p-0 h-auto text-[10px] font-black uppercase text-foreground">Active_Vaults</SidebarGroupLabel>
              <Button size="icon" className="h-5 w-5 rounded-none border-2 border-foreground brutalist-interactive">
                <Plus className="h-3 w-3" />
              </Button>
            </div>
            <div className="space-y-3">
              {portfolios.map((p) => (
                <div key={p.name} className="p-3 border-2 border-foreground bg-background hover:bg-primary/5 transition-colors group relative overflow-hidden">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-[9px] font-bold uppercase opacity-50">{p.name}</span>
                    <MoreHorizontal className="h-3 w-3 opacity-20 group-hover:opacity-100" />
                  </div>
                  <div className="text-lg font-black font-mono tracking-tighter leading-none">{p.value}</div>
                  <div className={`text-[10px] font-bold mt-2 flex items-center gap-1 ${p.pos ? 'text-green-500' : 'text-red-500'}`}>
                    {p.pos ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    {p.change}
                  </div>
                </div>
              ))}
            </div>
          </SidebarGroup>

          <SidebarSeparator className="h-[2px] bg-foreground/10" />

          {/* WATCHLISTS */}
          <SidebarGroup className="p-4">
            <SidebarGroupLabel className="px-0 h-auto text-[10px] font-black uppercase text-foreground mb-4">Watchlists</SidebarGroupLabel>
            <SidebarMenu className="gap-1">
              {['Tech_Titans', 'DeFi_Perps', 'Macro_Indices'].map((name) => (
                <SidebarMenuItem key={name}>
                  <SidebarMenuButton className="rounded-none border-2 border-transparent hover:border-foreground hover:bg-muted font-black text-[11px] uppercase group">
                    <Star className="h-3 w-3 mr-2 opacity-30 group-hover:text-primary group-hover:opacity-100" />
                    {name}
                    <Badge variant="outline" className="ml-auto rounded-none border-foreground/20 text-[9px] font-mono">12</Badge>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroup>

          <SidebarSeparator className="h-[2px] bg-foreground/10" />

          {/* RAW TICKER STREAM */}
          <SidebarGroup className="p-4">
            <div className="flex items-center gap-2 mb-4">
               <Activity className="h-3 w-3 text-primary" />
               <span className="text-[10px] font-black uppercase">Ticker_Stream</span>
            </div>
            <div className="divide-y-2 divide-foreground/5">
              {liveTickers.map((ticker) => (
                <div key={ticker.symbol} className="py-2 flex justify-between items-center group cursor-crosshair">
                  <div>
                    <div className="text-xs font-black italic">{ticker.symbol}/USD</div>
                    <div className="text-[9px] font-mono opacity-40">VOL: 1.2B</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-black font-mono">${ticker.price.toLocaleString()}</div>
                    <div className={`text-[9px] font-bold ${ticker.change.includes('+') ? 'text-green-500' : 'text-red-500'}`}>
                      {ticker.change}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </SidebarGroup>
        </ScrollArea>
      </SidebarContent>
    </Sidebar>
  )
}