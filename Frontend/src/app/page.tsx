// app/page.tsx
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  ArrowRight, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Shield, 
  Zap, 
  TerminalSquare,
  ArrowUpRight,
  Check
} from 'lucide-react'
import { Navbar } from '@/components/layout/navbar'

export default function HomePage() {
  return (
    // CONTRAST FIX: We use a very subtle off-background color (zinc-50/zinc-950) 
    // and a faint grid pattern to make the glass elements pop.
    <div className="min-h-screen flex flex-col bg-zinc-50 dark:bg-zinc-950 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]">
      {/* ================= MAIN HERO SECTION ================= */}
    {/* Todo: Change for NoAuth NavBar */}
      <Navbar />
      <section className="flex-1 flex items-center pt-20 pb-32 px-6">
        <div className="max-w-7xl mx-auto w-full grid lg:grid-cols-2 gap-16 items-center">
          
          {/* Left: Typography & CTA */}
          <div className="space-y-8">
            <Badge variant="outline" className="rounded-none border-2 border-primary px-4 py-2 font-mono uppercase tracking-widest text-xs font-bold">
              <Zap className="w-4 h-4 mr-2 inline-block" />
              Terminal V3.0 Live
            </Badge>
            
            <h1 className="text-6xl md:text-8xl font-black uppercase tracking-tighter leading-[0.9]">
              Stop Playing. <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-foreground to-muted-foreground">
                Start Trading.
              </span>
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-md font-medium leading-relaxed">
              The institutional-grade terminal for the retail professional. Zero latency. Zero fluff. Pure execution.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="h-14 rounded-none border-2 border-primary bg-primary text-primary-foreground hover:bg-primary/90 font-black uppercase tracking-wider text-sm shadow-[4px_4px_0px_0px_var(--foreground)] hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[8px_8px_0px_0px_var(--foreground)] transition-all">
                Open Terminal <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              <Button size="lg" variant="outline" className="h-14 rounded-none border-2 border-foreground font-black uppercase tracking-wider text-sm shadow-[4px_4px_0px_0px_var(--muted-foreground)] hover:bg-foreground/5">
                Live Demo
              </Button>
            </div>
            
            <div className="flex items-center gap-4 text-xs font-mono uppercase tracking-widest text-muted-foreground">
              <span className="flex items-center"><Shield className="w-4 h-4 mr-2" /> SOC2 Compliant</span>
              <span className="w-px h-4 bg-border"></span>
              <span>Latency: &lt;14ms</span>
            </div>
          </div>

          {/* Right: Brutalist Glass Visualization */}
          <div className="relative hidden lg:block">
            {/* The main glass stack mimicking a terminal window */}
            <div className="brutalist-glass p-2 w-full aspect-square relative z-10">
              <div className="h-full w-full bg-background/50 p-6 flex flex-col">
                {/* Faux Terminal Header */}
                <div className="flex justify-between items-center mb-8 border-b-2 border-foreground/20 pb-4">
                  <div className="flex gap-2">
                    <div className="w-4 h-4 bg-foreground"></div>
                    <div className="w-4 h-4 border-2 border-foreground"></div>
                     <div className="w-4 h-4 border-2 border-foreground"></div>
                  </div>
                  <span className="font-mono uppercase text-xs font-bold">EXECUTION_ENGINE.exe</span>
                </div>

                {/* Faux Data Visualization */}
                <div className="flex-1 space-y-6">
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="font-mono text-xs uppercase opacity-60">Total Liquidity</p>
                      <p className="text-5xl font-black tracking-tighter">$24.5M</p>
                    </div>
                    <Badge className="rounded-none bg-green-500 hover:bg-green-600 font-bold uppercase text-xs">+4.5% TODAY</Badge>
                  </div>
                  
                  {/* Stylized Bar Chart using stacked divs */}
                  <div className="h-32 flex items-end gap-2 border-b-2 border-foreground/20 pb-2">
                    {[45, 70, 30, 90, 60, 85, 50, 95, 40].map((height, i) => (
                      <div key={i} className="flex-1 bg-foreground hover:bg-primary transition-colors relative group" style={{ height: `${height}%` }}>
                        {/* Tooltip effect on hover */}
                        <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-foreground text-background text-[10px] font-bold px-1 font-mono">
                          ${height}K
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="grid grid-cols-3 gap-2 font-mono text-xs uppercase">
                    <div className="brutalist-glass p-2 bg-background/40">
                      <p className="opacity-60">Vol.</p>
                      <p className="font-bold">4.2M</p>
                    </div>
                    <div className="brutalist-glass p-2 bg-background/40">
                      <p className="opacity-60">Open</p>
                      <p className="font-bold">64.2K</p>
                    </div>
                    <div className="brutalist-glass p-2 bg-background/40">
                      <p className="opacity-60">High</p>
                      <p className="font-bold">68.1K</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Decorative underlay element */}
            <div className="absolute inset-0 translate-x-8 translate-y-8 border-2 border-foreground/20 z-0"></div>
          </div>
        </div>
      </section>


      {/* ================= FEATURES / COMPONENT TEST LAB ================= */}
      <section className="py-24 px-6 border-t-2 border-foreground/10 bg-background">
        <div className="max-w-7xl mx-auto space-y-16">
          <div className="md:flex justify-between items-end">
             <h2 className="text-4xl font-black uppercase tracking-tighter max-w-md">
                System Architecture
             </h2>
             <p className="text-muted-foreground font-mono uppercase tracking-widest text-xs mt-4 md:mt-0">
                Component Stress Test // Draggable Elements
             </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1: Direct Access (Testing interactive glass) */}
            <div className="brutalist-glass p-8 group relative overflow-hidden">
               <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-100 transition-opacity">
                  <ArrowUpRight className="w-8 h-8" />
               </div>
               <TerminalSquare className="w-12 h-12 mb-6" />
               <h3 className="text-2xl font-black uppercase mb-4">Direct Market Access</h3>
               <p className="text-muted-foreground font-medium mb-8">Skip the broker. Connect directly to liquidity providers and major exchanges via FIX API.</p>
               <div className="flex flex-col gap-2 font-mono text-xs uppercase font-bold">
                  <div className="flex items-center"><Check className="w-4 h-4 mr-2 text-green-500" /> NYSE Arca</div>
                  <div className="flex items-center"><Check className="w-4 h-4 mr-2 text-green-500" /> Nasdaq</div>
                  <div className="flex items-center"><Check className="w-4 h-4 mr-2 text-green-500" /> CBOE</div>
               </div>
            </div>

            {/* Feature 2: The Order Book (Testing dense data list) */}
            <div className="brutalist-glass p-1 md:col-span-2 grid md:grid-cols-2 divide-x-2 divide-foreground/20 bg-background/60">
              {/* BIDS */}
               <div className="p-6">
                  <h4 className="font-mono uppercase text-xs font-bold text-green-500 mb-4">/// BIDS (BUY)</h4>
                  <div className="space-y-1 font-mono text-sm">
                     <div className="flex justify-between opacity-60 text-xs mb-2"><span>Size</span><span>Price</span></div>
                     {[
                        {s: '4.214', p: '64,210.50'},
                        {s: '1.500', p: '64,209.00'},
                        {s: '10.00', p: '64,205.25'},
                        {s: '0.550', p: '64,200.00'},
                        {s: '2.125', p: '64,195.50'},
                     ].map((order, i) => (
                        <div key={i} className="flex justify-between hover:bg-green-500/10 px-1 py-0.5 cursor-crosshair">
                           <span className="font-bold">{order.s}</span>
                           <span className="text-green-600 dark:text-green-400">{order.p}</span>
                        </div>
                     ))}
                  </div>
               </div>
               {/* ASKS */}
               <div className="p-6">
                  <h4 className="font-mono uppercase text-xs font-bold text-red-500 mb-4">/// ASKS (SELL)</h4>
                  <div className="space-y-1 font-mono text-sm">
                  <div className="flex justify-between opacity-60 text-xs mb-2"><span>Price</span><span>Size</span></div>
                     {[
                        {s: '0.100', p: '64,215.00'},
                        {s: '5.000', p: '64,218.50'},
                        {s: '2.200', p: '64,220.75'},
                        {s: '1.100', p: '64,225.00'},
                        {s: '0.450', p: '64,230.25'},
                     ].map((order, i) => (
                        <div key={i} className="flex justify-between hover:bg-red-500/10 px-1 py-0.5 cursor-crosshair">
                           <span className="text-red-600 dark:text-red-400">{order.p}</span>
                           <span className="font-bold">{order.s}</span>
                        </div>
                     ))}
                  </div>
               </div>
            </div>
          </div>
        </div>
      </section>

       {/* ================= TICKER STRIP (Testing horizontal glass) ================= */}
       <div className="brutalist-glass border-x-0 border-y-2 py-4 overflow-hidden flex gap-8 items-center font-mono uppercase text-sm font-bold tracking-widest whitespace-nowrap">
          <div className="animate-marquee flex gap-8">
            <span className="flex items-center">BTC/USD <span className="text-green-500 ml-2">$64,210.50</span> <TrendingUp className="h-4 w-4 text-green-500 ml-1"/></span>
            <span className="flex items-center">ETH/USD <span className="text-red-500 ml-2">$4,120.10</span> <TrendingDown className="h-4 w-4 text-red-500 ml-1"/></span>
            <span className="flex items-center">SPX <span className="text-green-500 ml-2">5,100.20</span> <TrendingUp className="h-4 w-4 text-green-500 ml-1"/></span>
            <span className="flex items-center">TSLA <span className="text-red-500 ml-2">$175.40</span> <TrendingDown className="h-4 w-4 text-red-500 ml-1"/></span>
             {/* Repeat for infinite scroll illusion */}
             <span className="flex items-center">BTC/USD <span className="text-green-500 ml-2">$64,210.50</span> <TrendingUp className="h-4 w-4 text-green-500 ml-1"/></span>
            <span className="flex items-center">ETH/USD <span className="text-red-500 ml-2">$4,120.10</span> <TrendingDown className="h-4 w-4 text-red-500 ml-1"/></span>
          </div>
       </div>


      {/* ================= CTA SECTION ================= */}
      <section className="py-32 px-6">
         <div className="max-w-5xl mx-auto brutalist-glass p-12 md:p-20 text-center space-y-8 border-4">
            <Activity className="w-16 h-16 mx-auto mb-8" />
            <h2 className="text-5xl md:text-7xl font-black uppercase tracking-tighter leading-none">
               Ready to deploy?
            </h2>
            <p className="text-xl text-muted-foreground max-w-lg mx-auto">
               Accounts are manually reviewed. Institutional capital requirements apply.
            </p>
            
            <div className="flex flex-col md:flex-row justify-center gap-4 max-w-md mx-auto">
               <Input placeholder="ENTER WORK EMAIL" className="brutalist-input h-14 text-lg font-mono uppercase placeholder:text-muted-foreground/50" />
               <Button size="lg" className="h-14 rounded-none border-2 border-primary bg-primary text-primary-foreground hover:bg-primary/90 font-black uppercase tracking-wider text-sm shadow-[4px_4px_0px_0px_var(--foreground)] hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[8px_8px_0px_0px_var(--foreground)] transition-all px-8">
                  Request Access
               </Button>
            </div>
         </div>
      </section>


      {/* ================= FOOTER ================= */}
      <footer className="py-12 px-6 border-t-4 border-foreground bg-background z-10">
         <div className="max-w-7xl mx-auto grid md:grid-cols-4 gap-12">
            <div className="space-y-4">
               <div className="font-black text-2xl uppercase tracking-tighter flex items-center gap-2">
                  <div className="w-6 h-6 bg-foreground"></div>
                  FIN_HUB.
               </div>
               <p className="font-mono text-xs uppercase text-muted-foreground">
                  © 2024 Execution Systems.<br />All rights reserved.
               </p>
            </div>

            <div>
               <h4 className="font-black uppercase tracking-widest text-sm mb-4">Platform</h4>
               <ul className="space-y-2 font-mono text-sm uppercase font-bold">
                  <li><Link href="#" className="hover:underline decoration-2 underline-offset-4">Terminal</Link></li>
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
                <div className="brutalist-glass p-4 bg-background/50 text-xs font-mono uppercase space-y-2">
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