// src/app/showcase/page.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { 
  TrendingUp, Search, ShieldAlert, 
  ArrowRight, BarChart3, CreditCard, ChevronDown 
} from 'lucide-react'

export default function BrutalistShowcase() {
  const [isLive, setIsLive] = useState(true)

  return (
    <div className="min-h-screen bg-background text-foreground p-6 md:p-12">
      <div className="max-w-6xl mx-auto space-y-16">
        
        {/* HEADER AREA */}
        <header className="space-y-4">
          <div className="inline-block bg-primary text-primary-foreground px-3 py-1 text-xs font-bold uppercase tracking-widest">
            Financial Terminal v3.0
          </div>
          <h1 className="text-6xl md:text-8xl font-black uppercase tracking-tighter leading-none">
            Brutalist <br /> <span className="text-muted-foreground">Liquid Glass.</span>
          </h1>
        </header>

        {/* 1. INPUT & CONTROLS GRID */}
        <section className="grid md:grid-cols-2 gap-12">
          <div className="space-y-8">
            <h3 className="text-xl font-bold uppercase border-b-2 border-foreground pb-2">Inputs & Search</h3>
            
            {/* Brutalist Glass Input */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5" />
              <input 
                type="text" 
                placeholder="SEARCH TICKER (E.G. NVDA)..." 
                className="brutalist-input pl-12 h-14 font-mono text-lg uppercase font-bold"
              />
            </div>

            {/* Brutalist Switch */}
            <div className="brutalist-glass p-6 flex items-center justify-between">
              <div>
                <p className="font-black uppercase">Live Market Stream</p>
                <p className="text-xs opacity-60">Real-time WebSocket connection</p>
              </div>
              <Switch checked={isLive} onCheckedChange={setIsLive} className="data-[state=checked]:bg-primary" />
            </div>

            {/* Brutalist Select Style */}
            <div className="brutalist-glass p-1 flex">
              <button className="flex-1 p-3 bg-foreground text-background font-bold uppercase text-sm">Buy</button>
              <button className="flex-1 p-3 hover:bg-foreground/10 font-bold uppercase text-sm">Sell</button>
            </div>
          </div>

          <div className="space-y-8">
            <h3 className="text-xl font-bold uppercase border-b-2 border-foreground pb-2">Actions</h3>
            <div className="grid grid-cols-2 gap-4">
              <Button className="h-20 brutalist-glass bg-primary text-primary-foreground hover:bg-primary shadow-none border-2">
                <div className="flex flex-col items-center">
                  <CreditCard className="mb-1" />
                  <span className="font-black text-xs uppercase">Deposit</span>
                </div>
              </Button>
              <Button variant="outline" className="h-20 brutalist-glass hover:bg-accent shadow-none border-2">
                <div className="flex flex-col items-center">
                  <BarChart3 className="mb-1" />
                  <span className="font-black text-xs uppercase">Reports</span>
                </div>
              </Button>
            </div>
          </div>
        </section>

        {/* 2. STATS GRID (THE "STICKER" LOOK) */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <BrutalistCard title="EQUITY" value="$42,069.00" trend="+4.2%" color="bg-green-500" />
          <BrutalistCard title="MARGIN" value="$2,400.00" trend="-1.1%" color="bg-red-500" />
          <BrutalistCard title="POWER" value="4.0X" trend="MAX" color="bg-primary" />
        </section>

        {/* 3. ALERTS & NOTIFICATIONS */}
        <section className="space-y-6">
           <Alert className="brutalist-glass border-destructive bg-destructive/10 shadow-[4px_4px_0px_0px_var(--destructive)]">
              <ShieldAlert className="h-5 w-5" />
              <AlertTitle className="font-black uppercase">Margin Call Warning</AlertTitle>
              <AlertDescription className="font-medium">
                Portfolio maintenance margin is below 25%. Action required immediately.
              </AlertDescription>
           </Alert>
        </section>

        {/* 4. TABLE / LIST DATA */}
        <section className="brutalist-glass overflow-hidden">
          <div className="bg-foreground text-background p-3 font-black uppercase text-xs tracking-widest">
            Recent Executions
          </div>
          <div className="divide-y-2 divide-foreground">
            {[
              { t: 'BTC/USD', v: '0.421', s: 'Filled', p: '$64,200' },
              { t: 'AAPL', v: '10.00', s: 'Pending', p: '$192.10' },
              { t: 'TSLA', v: '5.00', s: 'Filled', p: '$175.40' },
            ].map((row, i) => (
              <div key={i} className="flex p-4 items-center justify-between hover:bg-foreground/5 transition-colors font-mono">
                <span className="font-black">{row.t}</span>
                <span className="opacity-60">{row.v}</span>
                <span className="font-bold">{row.p}</span>
                <Badge variant="outline" className="border-2 border-foreground rounded-none font-black uppercase text-[10px]">
                  {row.s}
                </Badge>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

function BrutalistCard({ title, value, trend, color }: any) {
  return (
    <div className="brutalist-glass p-6 group cursor-pointer">
      <div className="flex justify-between items-start mb-4">
        <span className="text-xs font-black uppercase tracking-widest opacity-60">{title}</span>
        <div className={`px-2 py-1 text-[10px] font-black text-white ${color}`}>
          {trend}
        </div>
      </div>
      <div className="text-4xl font-black tracking-tighter mb-4">{value}</div>
      <div className="flex items-center text-xs font-bold uppercase group-hover:gap-2 transition-all">
        View Chart <ArrowRight className="w-4 h-4 ml-1" />
      </div>
    </div>
  )
}