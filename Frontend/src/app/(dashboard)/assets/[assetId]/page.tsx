'use client'

import { useState } from 'react'
import { 
  TrendingUp, Activity, Globe, Info, 
  Zap, BarChart3, ShieldCheck, ZapOff 
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function AssetDetail() {
  return (
    <div className="space-y-6 p-6">
      {/* HEADER HUD */}
      <section className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 brutalist-glass p-8 bg-primary/5">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 bg-foreground text-background flex items-center justify-center font-black text-2xl border-4 border-foreground shadow-[4px_4px_0px_0px_var(--primary)]">
              B
            </div>
            <div>
              <h1 className="text-4xl font-black uppercase italic leading-none">Bitcoin</h1>
              <span className="text-xs font-mono font-bold opacity-50">BTC / USD / PERPETUAL</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-8 w-full md:w-auto font-mono">
          <div>
            <p className="text-[10px] font-black opacity-50 uppercase">Mark_Price</p>
            <p className="text-2xl font-black tracking-tighter">$64,210.50</p>
          </div>
          <div>
            <p className="text-[10px] font-black opacity-50 uppercase">24h_Change</p>
            <p className="text-2xl font-black tracking-tighter text-green-500">+4.2%</p>
          </div>
          <div className="hidden md:block">
            <p className="text-[10px] font-black opacity-50 uppercase">Funding_Rate</p>
            <p className="text-2xl font-black tracking-tighter text-primary">0.0100%</p>
          </div>
        </div>
      </section>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* LEFT: CHART & TOOLS (3/4 Width) */}
        <div className="lg:col-span-3 space-y-6">
          <div className="brutalist-glass aspect-video bg-zinc-900 flex flex-col items-center justify-center relative overflow-hidden">
             {/* Mock Chart Area */}
             <div className="absolute inset-0 opacity-20 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] pointer-events-none" />
             <BarChart3 className="h-24 w-24 text-primary opacity-20 animate-pulse" />
             <span className="font-mono text-[10px] uppercase font-black tracking-[0.4em] opacity-40">Loading_TradingView_Engine...</span>
             
             {/* Overlay HUD */}
             <div className="absolute top-4 left-4 flex gap-2">
                {['1M', '5M', '15M', '1H', '1D'].map(t => (
                  <Button key={t} variant="outline" className="h-7 rounded-none border-2 border-foreground bg-background font-black text-[10px]">{t}</Button>
                ))}
             </div>
          </div>

          {/* FUNDAMENTAL ANALYSIS MODULE */}
          <div className="grid md:grid-cols-3 gap-6">
             <Tile label="Market_Cap" value="$1.2T" sub="Rank #1" />
             <Tile label="Circ_Supply" value="19.6M" sub="93% Issued" />
             <Tile label="Volatility" value="Low" sub="Standard Deviation" />
          </div>
        </div>

        {/* RIGHT: STRATEGY & EXECUTION (1/4 Width) */}
        <div className="space-y-6">
          <section className="brutalist-glass p-6 space-y-6">
            <h3 className="font-black uppercase text-xs italic border-b-2 border-foreground pb-2">Execution_Logic</h3>
            <Tabs defaultValue="limit" className="w-full">
              <TabsList className="w-full rounded-none bg-muted h-10 border-2 border-foreground p-1">
                <TabsTrigger value="limit" className="flex-1 rounded-none font-black text-[10px] uppercase">Limit</TabsTrigger>
                <TabsTrigger value="market" className="flex-1 rounded-none font-black text-[10px] uppercase">Market</TabsTrigger>
              </TabsList>
              <div className="py-4 space-y-4">
                <div className="space-y-2">
                  <label className="text-[9px] font-black uppercase opacity-50">Entry_Price</label>
                  <input className="brutalist-input font-mono text-sm" placeholder="64000.00" />
                </div>
                <div className="space-y-2">
                  <label className="text-[9px] font-black uppercase opacity-50">Size_BTC</label>
                  <input className="brutalist-input font-mono text-sm" placeholder="0.00" />
                </div>
                <Button className="w-full h-14 rounded-none border-4 border-foreground bg-green-500 text-white font-black uppercase tracking-tighter shadow-[4px_4px_0px_0px_var(--foreground)] active:shadow-none translate-y-[-2px] transition-all">
                  Long_Position
                </Button>
              </div>
            </Tabs>
          </section>

          <section className="brutalist-glass-ghost p-6 border-2 border-dashed border-foreground/30">
            <h3 className="font-black uppercase text-[10px] mb-4 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4" /> Risk_Assessment
            </h3>
            <div className="space-y-2 text-[10px] font-mono opacity-60">
              <p>• Max Drawdown: 12.4%</p>
              <p>• Sharpe Ratio: 2.1</p>
              <p>• Liquidation: $42,000</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

function Tile({ label, value, sub }: any) {
  return (
    <div className="brutalist-glass p-6 group">
      <p className="text-[9px] font-black uppercase opacity-50 mb-1 tracking-widest">{label}</p>
      <p className="text-2xl font-black font-mono tracking-tighter group-hover:text-primary transition-colors">{value}</p>
      <p className="text-[9px] font-bold opacity-40 uppercase mt-2">{sub}</p>
    </div>
  )
}