'use client'

import { Bell, Zap, ShieldAlert, Activity, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'

const SIGNALS: {
  trades: Array<{ id: number; title: string; desc: string; time: string; type: string; tx: string }>
  security: Array<{ id: number; title: string; desc: string; time: string; type: string }>
} = {
  trades: [
    { id: 1, title: 'BTC/USDT Fill', desc: '0.450 BTC @ 64,120.00', time: '1m ago', type: 'success', tx: '0x4...21' },
    { id: 2, title: 'Stop Loss Triggered', desc: 'ETH/USD closed at 3,210.00', time: '14m ago', type: 'error', tx: '0x8...ab' },
  ],
  security: [
    { id: 3, title: 'New API Key', desc: 'Permissions: Trade, Read', time: '2h ago', type: 'warning' },
    { id: 4, title: 'Login Detected', desc: 'IP: 192.168.1.45 (NYC)', time: '1d ago', type: 'info' },
  ],
}

export function SignalCenter() {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative h-10 w-10 border-2 border-foreground rounded-none bg-background hover:bg-muted brutalist-interactive">
          <Bell className="h-5 w-5" />
          <div className="absolute -top-1 -right-1 h-5 w-5 bg-primary text-primary-foreground border-2 border-foreground flex items-center justify-center text-[10px] font-black">
            3
          </div>
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-105 p-0 rounded-none border-4 border-foreground bg-background shadow-[12px_12px_0px_0px_rgba(0,0,0,1)]">
        <Tabs defaultValue="trades" className="w-full">
          <div className="p-4 border-b-4 border-foreground bg-foreground text-background flex items-center justify-between">
            <h3 className="font-black uppercase italic tracking-tighter text-lg">Signal_Hub</h3>
            <TabsList className="bg-background/20 rounded-none p-1 h-auto">
              <TabsTrigger value="trades" className="rounded-none text-[9px] font-black uppercase data-[state=active]:bg-background">Trades</TabsTrigger>
              <TabsTrigger value="security" className="rounded-none text-[9px] font-black uppercase data-[state=active]:bg-background">Security</TabsTrigger>
            </TabsList>
          </div>
          <ScrollArea className="h-100">
            {Object.entries(SIGNALS).map(([key, logs]) => (
              <TabsContent key={key} value={key} className="m-0 focus-visible:outline-none">
                <div className="divide-y-2 divide-foreground">
                  {logs.map((log) => (
                    <div key={log.id} className="p-4 hover:bg-primary/5 transition-colors">
                      <div className="flex gap-4">
                        <div className={`h-10 w-10 shrink-0 border-2 border-foreground flex items-center justify-center
                          ${log.type === 'success' ? 'bg-green-500' : log.type === 'error' ? 'bg-red-500' : 'bg-orange-500'}`}>
                          {log.type === 'success' ? <Zap className="text-white h-5 w-5" /> : <ShieldAlert className="text-white h-5 w-5" />}
                        </div>
                        <div className="flex-1 space-y-1">
                          <div className="flex justify-between">
                            <h4 className="font-black uppercase text-xs">{log.title}</h4>
                            <span className="text-[9px] font-mono opacity-50">{log.time}</span>
                          </div>
                          <p className="text-[11px] font-mono opacity-70 italic">{log.desc}</p>
                          <div className="flex gap-2 pt-2">
                            <Button size="sm" className="h-6 rounded-none border-2 border-foreground bg-background text-foreground text-[8px] font-black uppercase brutalist-interactive">ACKNOWLEDGE</Button>
                            {'tx' in log && log.tx && <Button size="sm" className="h-6 rounded-none border-2 border-foreground bg-background text-foreground text-[8px] font-black uppercase brutalist-interactive"><ExternalLink className="h-3 w-3 mr-1"/> TX</Button>}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>
            ))}
          </ScrollArea>
        </Tabs>
      </PopoverContent>
    </Popover>
  )
}