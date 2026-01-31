'use client'

import { useState, useCallback, useEffect } from 'react'
import {
  CommandDialog, CommandEmpty, CommandGroup, CommandInput,
  CommandItem, CommandList, CommandSeparator,
} from '@/components/ui/command'
import {
  Bitcoin, DollarSign, Newspaper, BarChart3,
  Clock, Star, Search, ArrowRight, Zap
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { useDebounce } from '@/hooks/useDebounce'

const mockAssets = [
  { symbol: 'BTC', name: 'Bitcoin', price: 64250, change: 2.98, type: 'crypto' },
  { symbol: 'AAPL', name: 'Apple Inc.', price: 178.45, change: 1.33, type: 'stock' },
  { symbol: 'SOL', name: 'Solana', price: 145.20, change: -4.5, type: 'crypto' },
]

export function CommandPalette({ open, onOpenChange }: { open: boolean, onOpenChange: (o: boolean) => void }) {
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  // Debounce search input to reduce API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search)
    }, 300)
    return () => clearTimeout(timer)
  }, [search])

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <div className="border-b-4 border-foreground p-2 bg-primary">
         <CommandInput
            placeholder="EXECUTE_COMMAND_OR_SEARCH..."
            value={search}
            onValueChange={setSearch}
            className="border-none focus:ring-0 placeholder:text-primary-foreground/50 text-primary-foreground font-black uppercase"
         />
      </div>
      <CommandList className="max-h-[450px] bg-background">
        <CommandEmpty className="p-8 text-center font-mono text-xs uppercase opacity-50">No_Results_In_Database</CommandEmpty>
        
        <CommandGroup heading={<span className="font-black text-foreground uppercase tracking-widest text-[10px]">Quick_Actions</span>}>
          <CommandItem className="brutalist-interactive m-2 border-2 border-transparent focus:border-foreground focus:bg-primary/10">
            <Zap className="mr-2 h-4 w-4" />
            <span className="font-bold uppercase text-xs">Market Order: Buy BTC</span>
            <kbd className="ml-auto font-mono text-[10px] opacity-40">ALT+B</kbd>
          </CommandItem>
        </CommandGroup>

        <CommandSeparator className="bg-foreground h-1" />

        <CommandGroup heading={<span className="font-black text-foreground uppercase tracking-widest text-[10px]">Market_Assets</span>}>
          {mockAssets.map((asset) => (
            <CommandItem key={asset.symbol} className="m-2 border-2 border-transparent focus:border-foreground focus:bg-muted p-3">
              <div className="flex items-center gap-3 w-full">
                <div className="h-8 w-8 border-2 border-foreground bg-background flex items-center justify-center font-black text-[10px]">
                  {asset.symbol[0]}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-black text-sm uppercase italic">{asset.symbol}</span>
                    <Badge className="rounded-none bg-foreground text-background text-[8px] h-4">{asset.type}</Badge>
                  </div>
                  <p className="text-[10px] font-mono opacity-50 uppercase">{asset.name}</p>
                </div>
                <div className="text-right font-mono">
                  <div className="font-black text-sm">${asset.price.toLocaleString()}</div>
                  <div className={`text-[10px] ${asset.change > 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {asset.change > 0 ? '▲' : '▼'}{Math.abs(asset.change)}%
                  </div>
                </div>
              </div>
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}