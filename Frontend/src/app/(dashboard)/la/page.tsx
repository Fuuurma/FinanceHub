// src/app/showcase/page.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  TrendingUp, 
  TrendingDown, 
  Wallet,
  BarChart3,
  ArrowUpRight,
  ShieldCheck,
  Zap,
  Briefcase
} from 'lucide-react'

export default function ShowcasePage() {
  const [sliderValue, setSliderValue] = useState([75])

  return (
    <div className="min-h-screen bg-[#050505] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-zinc-900 via-black to-black text-zinc-100 p-4 md:p-12 font-sans selection:bg-white selection:text-black">
      
      {/* 1. HERO SECTION - Liquid Glass Core */}
      <section className="max-w-7xl mx-auto mb-20">
        <div className="liquid-glass p-8 md:p-12 rounded-[2.5rem] flex flex-col md:flex-row items-center justify-between gap-12 border-white/5">
          <div className="space-y-6 max-w-2xl">
            <Badge className="bg-white/10 hover:bg-white/20 text-white border-white/10 backdrop-blur-md px-4 py-1">
              v2.0 Liquid System
            </Badge>
            <h1 className="text-5xl md:text-7xl font-bold tracking-tighter leading-none">
              Professional <br /> <span className="text-zinc-500">Market Analysis.</span>
            </h1>
            <p className="text-lg text-zinc-400 max-w-md leading-relaxed">
              A design system built for speed and clarity. High-refraction components designed for complex financial data.
            </p>
            <div className="flex gap-4">
              <Button size="lg" className="rounded-full px-8 bg-white text-black hover:bg-zinc-200">
                Deploy Terminal
              </Button>
              <Button size="lg" variant="outline" className="rounded-full px-8 border-white/10 hover:bg-white/5">
                Documentation
              </Button>
            </div>
          </div>
          
          {/* Abstract Glass Shape (Demonstrating Refraction) */}
          <div className="relative w-72 h-72 hidden lg:block">
             <div className="absolute inset-0 bg-gradient-to-tr from-zinc-500 to-white rounded-full blur-3xl opacity-20 animate-pulse" />
             <div className="liquid-glass refractive w-full h-full rounded-[3rem] border-white/10 rotate-12 flex items-center justify-center">
                <BarChart3 className="w-24 h-24 text-white opacity-50" />
             </div>
          </div>
        </div>
      </section>

      {/* 2. LIVE DATA CARDS - Positive/Negative Glass */}
      <section className="max-w-7xl mx-auto mb-20 grid md:grid-cols-3 gap-6">
        <GlassMetricCard 
          title="Total Equity" 
          value="$1,240,592.12" 
          change="+12.5%" 
          trend="up" 
          icon={<Wallet className="w-5 h-5" />}
        />
        <GlassMetricCard 
          title="Daily Margin" 
          value="-$2,400.00" 
          change="-0.8%" 
          trend="down" 
          icon={<Zap className="w-5 h-5 text-red-400" />}
        />
        <GlassMetricCard 
          title="Active Risk" 
          value="Moderate" 
          change="Stability: 88%" 
          trend="neutral" 
          icon={<ShieldCheck className="w-5 h-5 text-zinc-400" />}
        />
      </section>

      {/* 3. COMPONENT TABBED VIEW */}
      <section className="max-w-7xl mx-auto">
        <Tabs defaultValue="overview" className="space-y-8">
          <div className="flex justify-center">
            <TabsList className="liquid-glass border-white/5 bg-black/20 p-1 rounded-full h-14">
              <TabsTrigger value="overview" className="rounded-full px-8 data-[state=active]:bg-white data-[state=active]:text-black">Overview</TabsTrigger>
              <TabsTrigger value="analysis" className="rounded-full px-8 data-[state=active]:bg-white data-[state=active]:text-black">Analysis</TabsTrigger>
              <TabsTrigger value="market" className="rounded-full px-8 data-[state=active]:bg-white data-[state=active]:text-black">Markets</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="overview">
            <div className="grid lg:grid-cols-2 gap-8">
              {/* Asset Card */}
              <Card className="liquid-glass border-none rounded-[2rem] p-4">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-3xl font-bold tracking-tight">Portfolio Alpha</CardTitle>
                      <CardDescription className="text-zinc-500 text-lg">Managed Institutional Assets</CardDescription>
                    </div>
                    <Briefcase className="w-8 h-8 opacity-20" />
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                   <div className="h-48 w-full bg-gradient-to-t from-zinc-900 to-transparent rounded-2xl border border-white/5 flex items-end p-4">
                      <div className="flex gap-1 w-full items-end h-full">
                        {[40, 70, 45, 90, 65, 80, 30, 95].map((h, i) => (
                          <div key={i} className="flex-1 bg-white/10 rounded-t-sm hover:bg-white/40 transition-colors" style={{ height: `${h}%` }} />
                        ))}
                      </div>
                   </div>
                   <div className="flex justify-between text-sm font-medium">
                      <span className="text-zinc-500">Yield Strategy</span>
                      <span className="text-white">Aggressive Growth</span>
                   </div>
                </CardContent>
              </Card>

              {/* Data Grid Card */}
              <div className="grid gap-4">
                <div className="liquid-glass liquid-glass-shimmer rounded-2xl p-6 flex justify-between items-center group cursor-pointer border-white/5">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <ArrowUpRight className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="font-bold text-lg">Market Execution</p>
                      <p className="text-sm text-zinc-500">Latency: 14ms</p>
                    </div>
                  </div>
                  <Badge variant="outline" className="border-white/20">Operational</Badge>
                </div>
                {/* Repeatable small glass items */}
                {[1, 2, 3].map((i) => (
                   <div key={i} className="liquid-glass rounded-2xl p-6 flex justify-between items-center border-white/5">
                      <div className="h-4 w-32 bg-white/5 rounded animate-pulse" />
                      <div className="h-4 w-12 bg-white/10 rounded" />
                   </div>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </section>
    </div>
  )
}

function GlassMetricCard({ title, value, change, trend, icon }: any) {
  const isUp = trend === 'up'
  const isDown = trend === 'down'
  
  return (
    <div className={`
      liquid-glass liquid-glass-hover p-8 rounded-[2rem] border-white/5
      ${isUp ? 'liquid-glass-positive' : ''}
      ${isDown ? 'liquid-glass-negative' : ''}
    `}>
      <div className="flex justify-between items-start mb-6">
        <div className="p-3 bg-white/5 rounded-2xl border border-white/10">
          {icon}
        </div>
        <Badge className={`
          rounded-full px-3 
          ${isUp ? 'bg-green-500/20 text-green-400' : isDown ? 'bg-red-500/20 text-red-400' : 'bg-white/10 text-white'}
        `}>
          {change}
        </Badge>
      </div>
      <p className="text-zinc-500 font-medium mb-1">{title}</p>
      <p className="text-4xl font-bold tracking-tighter tabular-nums">{value}</p>
    </div>
  )
}