// app/page.tsx
'use client'

import { useEffect, useState, useRef } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
  ArrowRight, TrendingUp, TrendingDown, Activity, 
  Shield, Zap, TerminalSquare, ArrowUpRight, Check,
  Cpu, Globe, Lock, BarChart3, LineChart, PieChart,
  Zap as ZapIcon, Layers, ChevronRight, Play
} from 'lucide-react'
import { Navbar } from '@/components/layout/navbar'

const markets = [
  { symbol: 'BTC', price: 64250.00, change: '+2.98%', direction: 'up' },
  { symbol: 'ETH', price: 3450.12, change: '-1.95%', direction: 'down' },
  { symbol: 'SPX', price: 5123.45, change: '+0.87%', direction: 'up' },
  { symbol: 'NDX', price: 17845.30, change: '+1.23%', direction: 'up' },
  { symbol: 'TSLA', price: 175.40, change: '-2.15%', direction: 'down' },
  { symbol: 'NVDA', price: 875.40, change: '+1.23%', direction: 'up' },
  { symbol: 'AAPL', price: 189.95, change: '+0.45%', direction: 'up' },
  { symbol: 'EUR/USD', price: 1.0845, change: '+0.12%', direction: 'up' },
]

const portfolioMetrics = [
  { label: 'AUM', value: '$2.4B', change: '+12.4%', icon: Layers },
  { label: 'Daily Vol', value: '$847M', change: '+8.2%', icon: Activity },
  { label: 'Sharpe', value: '2.34', change: '+0.12', icon: LineChart },
  { label: 'Alpha', value: '4.87%', change: '+0.45%', icon: TrendingUp },
]

export default function HomePage() {
  const [mounted, setMounted] = useState(false)
  const [animatedValues, setAnimatedValues] = useState<Record<string, number>>({})
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    setMounted(true)
    
    const targetValues: Record<string, number> = {}
    markets.forEach(m => {
      targetValues[m.symbol] = m.price
    })
    setAnimatedValues(targetValues)
  }, [])

  useEffect(() => {
    if (!mounted || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationId: number
    let offset = 0
    const data = Array.from({ length: 60 }, () => Math.random() * 60 + 20)

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      ctx.strokeStyle = 'rgba(0, 255, 136, 0.3)'
      ctx.lineWidth = 1
      ctx.beginPath()
      
      const step = canvas.width / (data.length - 1)
      offset = (offset + 0.5) % step
      
      data.forEach((y, i) => {
        const x = i * step - offset
        if (i === 0) {
          ctx.moveTo(x, canvas.height - (y / 100) * canvas.height)
        } else {
          ctx.lineTo(x, canvas.height - (y / 100) * canvas.height)
        }
      })
      ctx.stroke()
      
      animationId = requestAnimationFrame(draw)
    }

    const resize = () => {
      canvas.width = canvas.parentElement?.clientWidth || 400
      canvas.height = canvas.parentElement?.clientHeight || 200
    }
    resize()
    window.addEventListener('resize', resize)
    draw()

    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('resize', resize)
    }
  }, [mounted])

  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-pulse font-mono text-xs font-black uppercase tracking-widest">
          INITIALIZING...
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <Navbar />
      
      {/* ================= HERO SECTION ================= */}
      <section className="relative min-h-[90vh] flex items-center overflow-hidden bg-background">
        {/* Animated Background Grid */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:80px_80px]" />
        </div>

        {/* Floating Orbs */}
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-green-500/5 rounded-full blur-[100px]" />

        <div className="relative z-10 max-w-[90rem] mx-auto w-full px-6 py-20">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            
            {/* Left: Typography & CTA */}
            <div className="space-y-8">
              <Badge variant="outline" className="rounded-none border-2 border-primary px-4 py-2 font-mono uppercase tracking-widest text-xs font-bold">
                <ZapIcon className="w-3 h-3 mr-2 inline-block fill-primary" />
                Terminal V3.1.4a // INSTITUTIONAL GRADE
              </Badge>
              
              <h1 className="text-6xl md:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-[0.9]">
                Control <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-foreground via-primary to-foreground">
                  The Markets
                </span>
              </h1>
              
              <p className="text-xl text-muted-foreground max-w-lg font-medium leading-relaxed">
                Institutional-grade infrastructure for serious capital. 
                Direct market access. Sub-millisecond latency. Zero compromise.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/dashboard">
                  <Button size="lg" className="h-14 rounded-none border-2 border-primary bg-primary text-primary-foreground hover:bg-primary/90 font-black uppercase tracking-wider text-sm shadow-[4px_4px_0px_0px_var(--foreground)] hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[8px_8px_0px_0px_var(--foreground)] transition-all">
                    <TerminalSquare className="mr-2 w-5 h-5" />
                    Launch Terminal
                  </Button>
                </Link>
                <Button size="lg" variant="outline" className="h-14 rounded-none border-2 border-foreground font-black uppercase tracking-wider text-sm hover:bg-foreground/5">
                  <Play className="mr-2 w-4 h-4" />
                  View Documentation
                </Button>
              </div>
              
              <div className="flex items-center gap-6 pt-4">
                <div className="flex -space-x-2">
                  {['JP', 'MS', 'GS', 'BLK'].map((org, i) => (
                    <div key={org} className="h-8 w-8 rounded-none border-2 border-background bg-foreground flex items-center justify-center text-[9px] font-black uppercase">
                      {org}
                    </div>
                  ))}
                </div>
                <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  Trusted by 2,400+ institutional clients
                </div>
              </div>
            </div>

            {/* Right: Professional Terminal Visualization */}
            <div className="relative">
              {/* Terminal Frame */}
              <div className="brutalist-glass border-4 border-foreground bg-background shadow-[20px_20px_0px_0px_var(--muted-foreground)]">
                {/* Terminal Header */}
                <div className="h-10 border-b-2 border-foreground flex items-center px-3 gap-3 bg-muted/20">
                  <div className="flex gap-1.5">
                    <div className="h-3 w-3 border border-foreground/30" />
                    <div className="h-3 w-3 border border-foreground/30" />
                    <div className="h-3 w-3 border border-foreground/30" />
                  </div>
                  <div className="flex-1 text-center font-mono text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                    LIQUID_SYSTEM_TERMINAL_V3.1.4A
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 bg-green-500 animate-pulse" />
                    <span className="text-[9px] font-mono font-bold text-green-500">CONNECTED</span>
                  </div>
                </div>

                {/* Terminal Content */}
                <div className="p-4 grid grid-cols-2 gap-4">
                  {/* Portfolio Metrics */}
                  <div className="col-span-2 grid grid-cols-4 gap-2">
                    {portfolioMetrics.map((metric) => (
                      <div key={metric.label} className="border-2 border-foreground/20 p-3 bg-muted/10">
                        <div className="flex items-center gap-2 mb-2">
                          <metric.icon className="h-3 w-3 text-primary" />
                          <span className="text-[9px] font-mono uppercase opacity-50">{metric.label}</span>
                        </div>
                        <div className="text-2xl font-black tracking-tighter">{metric.value}</div>
                        <div className="text-[9px] font-mono text-green-500 flex items-center gap-1">
                          <TrendingUp className="h-2 w-2" /> {metric.change}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Live Chart */}
                  <div className="border-2 border-foreground/20 p-3 bg-muted/10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-black uppercase">Portfolio_Equity</span>
                      <span className="text-[9px] font-mono text-green-500">+12.4% YTD</span>
                    </div>
                    <div className="relative h-32">
                      <canvas ref={canvasRef} className="absolute inset-0" />
                    </div>
                  </div>

                  {/* Order Book Preview */}
                  <div className="border-2 border-foreground/20 p-3 bg-muted/10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-black uppercase">Order_Book</span>
                      <span className="text-[9px] font-mono opacity-50">BTC/USD</span>
                    </div>
                    <div className="space-y-1 font-mono text-[10px]">
                      <div className="flex justify-between text-red-500">
                        <span>64,250.50</span>
                        <span className="opacity-50">4.214</span>
                      </div>
                      <div className="flex justify-between text-red-500">
                        <span>64,249.00</span>
                        <span className="opacity-50">1.500</span>
                      </div>
                      <div className="flex justify-between border-t border-foreground/20 pt-1 text-green-500">
                        <span>64,248.25</span>
                        <span className="opacity-50">2.125</span>
                      </div>
                      <div className="flex justify-between text-green-500">
                        <span>64,247.00</span>
                        <span className="opacity-50">0.550</span>
                      </div>
                    </div>
                  </div>

                  {/* Market Tickers */}
                  <div className="col-span-2 border-2 border-foreground/20 p-3 bg-muted/10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-black uppercase">Live_Markets</span>
                      <span className="text-[9px] font-mono text-primary animate-pulse">REAL-TIME</span>
                    </div>
                    <div className="grid grid-cols-4 gap-2">
                      {markets.slice(0, 8).map((market) => (
                        <div key={market.symbol} className="flex items-center justify-between p-2 bg-background/50">
                          <div>
                            <div className="text-xs font-black">{market.symbol}</div>
                            <div className="text-[9px] font-mono opacity-50">
                              ${typeof market.price === 'number' ? market.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : market.price}
                            </div>
                          </div>
                          <div className={`text-[9px] font-bold flex items-center gap-0.5 ${market.direction === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                            {market.direction === 'up' ? <TrendingUp className="h-2.5 w-2.5" /> : <TrendingDown className="h-2.5 w-2.5" />}
                            {market.change}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Decorative Elements */}
              <div className="absolute -top-4 -right-4 w-24 h-24 border-4 border-primary/30 flex items-center justify-center">
                <ZapIcon className="h-8 w-8 text-primary animate-pulse" />
              </div>
              <div className="4 -left-4 pxabsolute -bottom--4 py-2 bg-foreground text-background font-mono text-xs font-black uppercase tracking-widest">
                LATENCY: 14MS
              </div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
          <span className="text-[9px] font-mono uppercase tracking-widest opacity-50">Scroll to explore</span>
          <div className="h-12 w-6 border-2 border-foreground/30 rounded-none flex items-start justify-center p-1">
            <div className="h-2 w-2 bg-foreground animate-bounce" />
          </div>
        </div>
      </section>


      {/* ================= FEATURES SECTION ================= */}
      <section className="py-32 px-6 border-t-2 border-foreground bg-muted/5">
        <div className="max-w-[90rem] mx-auto">
          <div className="mb-16">
            <Badge variant="outline" className="rounded-none border-2 border-primary px-3 py-1 font-mono uppercase text-xs mb-4">
              SYSTEM_CAPABILITIES
            </Badge>
            <h2 className="text-5xl md:text-6xl font-black uppercase tracking-tighter">
              Institutional <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-foreground to-muted-foreground">
                Infrastructure
              </span>
            </h2>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Feature 1: Direct Market Access */}
            <div className="brutalist-glass p-8 border-2 border-foreground bg-background group hover:translate-y-[-4px] transition-all duration-300">
              <div className="h-14 w-14 border-2 border-foreground flex items-center justify-center mb-6 group-hover:bg-foreground group-hover:text-background transition-colors">
                <Globe className="h-6 w-6" />
              </div>
              <h3 className="text-2xl font-black uppercase mb-4">Direct Access</h3>
              <p className="text-muted-foreground font-medium mb-6">
                Bypass intermediaries with direct connections to major exchanges via FIX API. 
                NYSE, Nasdaq, CBOE, and 40+ venues globally.
              </p>
              <ul className="space-y-2 font-mono text-xs uppercase font-bold">
                <li className="flex items-center gap-2">
                  <div className="h-1 w-1 bg-green-500" /> Sub-millisecond execution
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1 w-1 bg-green-500" /> Smart order routing
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1 w-1 bg-green-500" /> 99.999% uptime SLA
                </li>
              </ul>
            </div>

            {/* Feature 2: Portfolio Management */}
            <div className="brutalist-glass p-8 border-2 border-foreground bg-background group hover:translate-y-[-4px] transition-all duration-300">
              <div className="h-14 w-14 border-2 border-foreground flex items-center justify-center mb-6 group-hover:bg-foreground group-hover:text-background transition-colors">
                <BarChart3 className="h-6 w-6" />
              </div>
              <h3 className="text-2xl font-black uppercase mb-4">Portfolio Engine</h3>
              <p className="text-muted-foreground font-medium mb-6">
                Real-time portfolio analytics with multi-asset support. 
                Automated rebalancing, risk monitoring, and compliance checks.
              </p>
              <ul className="space-y-2 font-mono text-xs uppercase font-bold">
                <li className="flex items-center gap-2">
                  <div className="h-1 w-1 bg-green-500" /> $2.4B AUM capacity
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1 w-1 bg-green-500" /> Real-time P&L
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1 w-1 bg-green-500" /> Multi-currency support
                </li>
              </ul>
            </div>

            {/* Feature 3: Security */}
            <div className="brutalist-glass p-8 border-2 border-foreground bg-background group hover:translate-y-[-4px] transition-all duration-300">
              <div className="h-14 w-14 border-2 border-foreground flex items-center justify-center mb-6 group-hover:bg-foreground group-hover:text-background transition-colors">
                <Lock className="h-6 w-6" />
              </div>
              <h3 className="text-2xl font-black uppercase mb-4">Security First</h3>
              <p className="text-muted-foreground font-medium mb-6">
                Bank-grade security with SOC2 Type II certification. 
                Encrypted data flow, MFA, and role-based access control.
              </p>
              <ul className="space-y-2 font-mono text-xs uppercase font-bold">
                <li className="flex items-center gap-2">
                  <div className="h-1 w-1 bg-green-500" /> SOC2 Type II certified
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1 w-1 bg-green-500" /> End-to-end encryption
                </li>
                <li className="flex items-center gap-2">
                  <div className="h-1 w-1 bg-green-500" /> Audit trails
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>


      {/* ================= TICKER STRIP ================= */}
      <div className="brutalist-glass border-x-0 border-y-2 py-4 overflow-hidden flex gap-8 items-center font-mono uppercase text-xs font-bold tracking-widest whitespace-nowrap bg-foreground text-background">
        <div className="flex animate-marquee gap-16">
          {markets.map((m, i) => (
            <span key={i} className="flex items-center gap-3">
              <span>{m.symbol}/USD</span>
              <span className={m.direction === 'up' ? 'text-green-400' : 'text-red-400'}>
                ${typeof m.price === 'number' ? m.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : m.price}
              </span>
              <span className={m.direction === 'up' ? 'text-green-400' : 'text-red-400'}>{m.change}</span>
            </span>
          ))}
          {/* Duplicate for smooth scroll */}
          {markets.map((m, i) => (
            <span key={`dup-${i}`} className="flex items-center gap-3">
              <span>{m.symbol}/USD</span>
              <span className={m.direction === 'up' ? 'text-green-400' : 'text-red-400'}>
                ${typeof m.price === 'number' ? m.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : m.price}
              </span>
              <span className={m.direction === 'up' ? 'text-green-400' : 'text-red-400'}>{m.change}</span>
            </span>
          ))}
        </div>
      </div>


      {/* ================= CTA SECTION ================= */}
      <section className="py-32 px-6">
        <div className="max-w-4xl mx-auto brutalist-glass p-12 md:p-20 text-center space-y-8 border-4 border-foreground bg-background">
          <div className="inline-flex items-center gap-2 px-4 py-2 border-2 border-primary text-primary font-mono text-xs font-bold uppercase tracking-widest">
            <Cpu className="h-4 w-4" /> Ready for Production
          </div>
          
          <h2 className="text-5xl md:text-7xl font-black uppercase tracking-tighter leading-none">
            Deploy <br />
            Capital
          </h2>
          
          <p className="text-xl text-muted-foreground max-w-lg mx-auto">
            Accounts are manually reviewed. Institutional capital requirements apply.
            Get access within 48 hours.
          </p>
          
          <div className="flex flex-col md:flex-row justify-center gap-4 max-w-md mx-auto pt-4">
            <Input 
              placeholder="INSTITUTIONAL EMAIL" 
              className="h-14 text-lg font-mono uppercase placeholder:text-muted-foreground/50 border-2 border-foreground rounded-none"
            />
            <Button size="lg" className="h-14 rounded-none border-2 border-primary bg-primary text-primary-foreground hover:bg-primary/90 font-black uppercase tracking-wider text-sm shadow-[4px_4px_0px_0px_var(--foreground)] hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[8px_8px_0px_0px_var(--foreground)] transition-all px-8">
              Request Access <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </div>
        </div>
      </section>


      {/* ================= FOOTER ================= */}
      <footer className="py-12 px-6 border-t-4 border-foreground bg-background z-10">
        <div className="max-w-[90rem] mx-auto grid md:grid-cols-4 gap-12">
           <div className="space-y-4">
              <div className="font-black text-2xl uppercase tracking-tighter flex items-center gap-2">
                 <div className="w-6 h-6 bg-foreground" />
                 FIN_HUB.
              </div>
              <p className="font-mono text-xs uppercase text-muted-foreground">
                 © 2024 Execution Systems.<br />All rights reserved.
              </p>
           </div>

           <div>
              <h4 className="font-black uppercase tracking-widest text-sm mb-4">Platform</h4>
              <ul className="space-y-2 font-mono text-sm uppercase font-bold">
                 <li><Link href="/dashboard" className="hover:underline decoration-2 underline-offset-4">Terminal</Link></li>
                 <li><Link href="#" className="hover:underline decoration-2 underline-offset-4">API Docs</Link></li>
                 <li><Link href="#" className="hover:underline decoration-2 underline-offset-4">Status</Link></li>
              </ul>
           </div>
           <div>
              <h4 className="font-black uppercase tracking-widest text-sm mb-4">Company</h4>
              <ul className="space-y-2 font-mono text-sm uppercase font-bold">
                 <li><Link href="#" className="hover:underline decoration-2 underline-offset-4">About</Link></li>
                 <li><Link href="#" className="hover:underline decoration-2 underline-offset-4">Careers</Link></li>
                 <li><Link href="#" className="hover:underline decoration-2 underline-offset-4">Legal</Link></li>
              </ul>
           </div>
           <div>
              <h4 className="font-black uppercase tracking-widest text-sm mb-4">System</h4>
               <div className="brutalist-glass p-4 bg-muted/20 border-2 border-foreground/10 text-xs font-mono uppercase space-y-2">
                 <div className="flex justify-between"><span>Build:</span> <span>v3.1.4a</span></div>
                 <div className="flex justify-between"><span>Region:</span> <span className="text-green-500">US-EAST</span></div>
                 <div className="flex justify-between"><span>Uptime:</span> <span>99.99%</span></div>
               </div>
           </div>
        </div>
      </footer>
    </div>
  )
}
