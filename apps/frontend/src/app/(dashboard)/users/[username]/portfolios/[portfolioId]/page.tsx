'use client'

import { 
  Wallet, 
  ArrowUpRight, 
  ArrowDownRight, 
  Settings2, 
  ShieldCheck, 
  Zap, 
  Activity, 
  Lock,
  Plus,
  ArrowRightLeft,
  LayoutGrid,
  List
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'

const VAULTS = [
  {
    id: 'V-01',
    name: 'ALPHA_AGGRESSOR',
    balance: '$84,250.00',
    pnl: '+12.4%',
    risk: 'HIGH',
    status: 'ACTIVE',
    strategy: 'Grid_Bot_v4',
    allocation: 65,
  },
  {
    id: 'V-02',
    name: 'STABLE_SHIELD',
    balance: '$142,100.20',
    pnl: '+1.8%',
    risk: 'LOW',
    status: 'ACTIVE',
    strategy: 'Delta_Neutral',
    allocation: 25,
  },
  {
    id: 'V-03',
    name: 'DEFI_FARM_B',
    balance: '$12,400.00',
    pnl: '-4.2%',
    risk: 'MAX',
    status: 'PAUSED',
    strategy: 'Yield_Optimizer',
    allocation: 10,
  }
]

export default function PortfolioManager() {
  return (
    <div className="p-6 space-y-6 bg-background min-h-screen">
      {/* HEADER: TOTAL EQUITY HUD */}
      <header className="brutalist-glass p-8 bg-foreground text-background flex flex-col md:flex-row justify-between items-center gap-8 shadow-[8px_8px_0px_0px_var(--primary)]">
        <div className="space-y-1">
          <p className="text-[10px] font-black uppercase tracking-[0.3em] opacity-70">Total_Net_Worth</p>
          <h1 className="text-5xl font-black font-mono tracking-tighter italic">$238,750.20</h1>
          <div className="flex gap-4 pt-2">
            <span className="text-xs font-bold text-primary flex items-center gap-1">
              <ArrowUpRight className="h-4 w-4" /> +$4,120.00 (24H)
            </span>
            <span className="text-xs font-bold opacity-50 flex items-center gap-1 italic">
              <ShieldCheck className="h-4 w-4" /> VERIFIED_ON_CHAIN
            </span>
          </div>
        </div>
        
        <div className="flex gap-3">
          <Button className="h-12 px-6 rounded-none border-2 border-background bg-transparent hover:bg-background hover:text-foreground font-black uppercase text-xs transition-all">
            <ArrowRightLeft className="mr-2 h-4 w-4" /> Transfer
          </Button>
          <Button className="h-12 px-6 rounded-none bg-primary text-primary-foreground font-black uppercase text-xs shadow-[4px_4px_0px_0px_rgba(255,255,255,0.3)] hover:shadow-none translate-y-[-2px] active:translate-y-0 transition-all">
            <Plus className="mr-2 h-4 w-4" /> Create_Vault
          </Button>
        </div>
      </header>

      {/* VIEW CONTROLS */}
      <div className="flex justify-between items-center border-b-2 border-foreground pb-4">
        <div className="flex gap-4">
          <button className="text-[10px] font-black uppercase border-b-2 border-primary pb-1">Active_Vaults</button>
          <button className="text-[10px] font-black uppercase opacity-40 hover:opacity-100 pb-1">Archive</button>
          <button className="text-[10px] font-black uppercase opacity-40 hover:opacity-100 pb-1">Analytic_Export</button>
        </div>
        <div className="flex border-2 border-foreground">
          <Button variant="ghost" size="icon" className="rounded-none h-8 w-8 bg-foreground text-background"><LayoutGrid className="h-4 w-4"/></Button>
          <Button variant="ghost" size="icon" className="rounded-none h-8 w-8 border-l-2 border-foreground"><List className="h-4 w-4"/></Button>
        </div>
      </div>

      {/* VAULT GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {VAULTS.map((vault) => (
          <div key={vault.id} className="brutalist-glass group relative overflow-hidden flex flex-col">
            {/* Status Light */}
            <div className={`absolute top-0 right-0 px-3 py-1 text-[9px] font-black border-l-2 border-b-2 border-foreground ${
              vault.status === 'ACTIVE' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
            }`}>
              {vault.status}
            </div>

            <div className="p-6 flex-1 space-y-6">
              <div className="space-y-1">
                <span className="text-[9px] font-mono opacity-50">{vault.id}</span>
                <h3 className="text-xl font-black uppercase tracking-tight italic">{vault.name}</h3>
              </div>

              <div className="py-4 border-y-2 border-foreground/10 space-y-4">
                <div className="flex justify-between items-end">
                  <span className="text-[10px] font-black uppercase opacity-40">Value</span>
                  <span className="text-2xl font-black font-mono tracking-tighter">{vault.balance}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-black uppercase opacity-40">PnL_Total</span>
                  <span className={`text-sm font-black font-mono ${vault.pnl.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
                    {vault.pnl}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-[9px] font-black uppercase">
                  <span>Portfolio_Weight</span>
                  <span>{vault.allocation}%</span>
                </div>
                <div className="h-2 w-full bg-muted border border-foreground/20 p-[1px]">
                  <div className="h-full bg-primary" style={{ width: `${vault.allocation}%` }} />
                </div>
              </div>

              <div className="flex items-center gap-3 pt-2 text-[10px] font-bold">
                <Badge variant="outline" className="rounded-none border-foreground/20 text-[9px] uppercase">{vault.risk}_RISK</Badge>
                <div className="flex items-center gap-1 opacity-60">
                  <Zap className="h-3 w-3" /> {vault.strategy}
                </div>
              </div>
            </div>

            {/* ACTION FOOTER */}
            <div className="p-2 bg-muted/30 border-t-2 border-foreground grid grid-cols-2 gap-2">
              <Button variant="outline" className="rounded-none border-2 border-foreground h-9 font-black uppercase text-[10px] brutalist-interactive">
                <Settings2 className="mr-2 h-3 w-3" /> Config
              </Button>
              <Button variant="outline" className="rounded-none border-2 border-foreground h-9 font-black uppercase text-[10px] brutalist-interactive">
                <Activity className="mr-2 h-3 w-3" /> Monitor
              </Button>
            </div>
          </div>
        ))}

        {/* ADD NEW VAULT GHOST CARD */}
        <div className="border-4 border-dashed border-foreground/20 min-h-[400px] flex flex-col items-center justify-center space-y-4 group hover:border-primary/50 cursor-pointer transition-all">
          <div className="h-16 w-16 rounded-none border-4 border-dashed border-foreground/20 flex items-center justify-center group-hover:border-primary group-hover:text-primary">
            <Plus className="h-8 w-8" />
          </div>
          <span className="text-xs font-black uppercase opacity-20 group-hover:opacity-100 group-hover:text-primary">Initialize_New_Vault</span>
        </div>
      </div>
    </div>
  )
}