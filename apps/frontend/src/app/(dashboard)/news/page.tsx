'use client'

import { useState } from 'react'
import { 
  Search, 
  Filter, 
  Zap, 
  TrendingUp, 
  TrendingDown, 
  Globe, 
  BarChart2, 
  Clock,
  ShieldAlert,
  ArrowUpRight,
  Link2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'

const NEWS_FEED = [
  {
    id: 1,
    time: '14:20:05',
    category: 'MACRO',
    source: 'FED_WIRE',
    headline: 'FED CHAIR INDICATES RATE STABILITY THROUGH Q3; EYES INFLATION TARGETS',
    sentiment: 'NEUTRAL',
    impact: 'HIGH',
    tickers: ['DXY', 'SPY'],
  },
  {
    id: 2,
    time: '14:18:22',
    category: 'CRYPTO',
    source: 'BLOCK_REPORT',
    headline: 'ETHEREUM VITALIK BUTERIN PROPOSES NEW EIP FOR LAYER 2 SCALABILITY OPTIMIZATION',
    sentiment: 'BULLISH',
    impact: 'MEDIUM',
    tickers: ['ETH', 'LDO', 'ARB'],
  },
  {
    id: 3,
    time: '14:15:00',
    category: 'TECH',
    source: 'REUTERS_ALPHA',
    headline: 'NVIDIA ANNOUNCES NEW H200 CHIP ARCHITECTURE; SHIPMENTS STARTING JUNE',
    sentiment: 'BULLISH',
    impact: 'URGENT',
    tickers: ['NVDA', 'TSMC'],
  },
  {
    id: 4,
    time: '14:12:45',
    category: 'SECURITY',
    source: 'EXCHANGE_ALERTS',
    headline: 'MAJOR EXCHANGE SUSPENDS WITHDRAWALS FOR SCHEDULED DATABASE OPTIMIZATION',
    sentiment: 'BEARISH',
    impact: 'HIGH',
    tickers: ['SOL', 'BNB'],
  },
  {
    id: 5,
    time: '14:08:10',
    category: 'COMMODITIES',
    source: 'GOLDMAN_SACHS',
    headline: 'OIL PRICES STABILIZE AS MIDDLE EAST TENSIONS EASE; SUPPLY CHAINS RECOVER',
    sentiment: 'NEUTRAL',
    impact: 'MEDIUM',
    tickers: ['USO', 'XLE'],
  }
]

export default function NewsTerminal() {
  const [filter, setFilter] = useState('ALL')

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-background">
      {/* TERMINAL TOOLBAR */}
      <div className="h-12 border-b-2 border-foreground flex items-center px-4 gap-4 bg-muted/20">
        <div className="flex items-center gap-2 border-r-2 border-foreground/20 pr-4">
          <Globe className="h-4 w-4 text-primary" />
          <span className="text-[10px] font-black uppercase italic tracking-widest">Global_Feed_v1.0</span>
        </div>
        
        <div className="flex gap-2">
          {['ALL', 'URGENT', 'MACRO', 'CRYPTO', 'TECH'].map((t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`text-[9px] font-black uppercase px-3 py-1 border-2 border-foreground transition-all ${
                filter === t ? 'bg-foreground text-background shadow-[2px_2px_0px_0px_var(--primary)]' : 'bg-transparent hover:bg-muted'
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-4">
          <div className="flex items-center gap-2 text-[9px] font-mono opacity-50">
            <Clock className="h-3 w-3" />
            STAMP: {new Date().toLocaleTimeString()} UTC
          </div>
          <Button variant="ghost" size="icon" className="h-8 w-8 border-2 border-foreground rounded-none">
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* MAIN FEED AREA */}
        <ScrollArea className="flex-1 border-r-2 border-foreground">
          <div className="divide-y-2 divide-foreground">
            {NEWS_FEED.map((news) => (
              <div key={news.id} className="group flex hover:bg-primary/5 transition-colors cursor-pointer">
                {/* Sentiment Bar */}
                <div className={`w-1 shrink-0 ${
                  news.sentiment === 'BULLISH' ? 'bg-green-500' : 
                  news.sentiment === 'BEARISH' ? 'bg-red-500' : 'bg-foreground/20'
                }`} />
                
                <div className="flex-1 p-4 flex gap-4">
                  <div className="text-[11px] font-mono font-black opacity-40 shrink-0 pt-0.5">
                    {news.time}
                  </div>
                  
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-3">
                      <Badge className={`rounded-none font-black text-[9px] h-4 ${
                        news.impact === 'URGENT' ? 'bg-red-600 animate-pulse' : 'bg-foreground/10 text-foreground'
                      }`}>
                        {news.impact}
                      </Badge>
                      <span className="text-[10px] font-black text-primary uppercase italic">{news.source}</span>
                    </div>
                    
                    <h3 className="text-sm font-black uppercase leading-tight tracking-tight max-w-3xl group-hover:underline">
                      {news.headline}
                    </h3>

                    <div className="flex gap-2">
                      {news.tickers.map(ticker => (
                        <span key={ticker} className="text-[10px] font-mono font-bold bg-muted px-2 border border-foreground/10">
                          ${ticker}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="hidden md:flex flex-col items-end gap-2 shrink-0">
                    <div className="flex gap-1">
                      <Button size="icon" variant="ghost" className="h-7 w-7 border border-foreground/20 rounded-none"><ArrowUpRight className="h-3 w-3" /></Button>
                      <Button size="icon" variant="ghost" className="h-7 w-7 border border-foreground/20 rounded-none"><Link2 className="h-3 w-3" /></Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* DATA SIDEBAR (Sentiment Aggregator) */}
        <div className="w-80 flex flex-col bg-muted/10">
          <div className="p-4 border-b-2 border-foreground">
            <h4 className="text-[10px] font-black uppercase italic mb-4">Sentiment_Analysis</h4>
            <div className="space-y-4">
              <SentimentGauge label="MARKET_MOOD" value={72} color="bg-green-500" status="GREED" />
              <SentimentGauge label="MACRO_STRESS" value={34} color="bg-orange-500" status="MODERATE" />
            </div>
          </div>

          <div className="p-4 flex-1">
            <h4 className="text-[10px] font-black uppercase italic mb-4">Trending_Topics</h4>
            <div className="flex flex-wrap gap-2">
              {['#FED', '#AI_ARMS_RACE', '#BTC_HALVING', '#ETF_FLOWS', '#LIQUIDITY'].map(tag => (
                <span key={tag} className="text-[9px] font-bold border-2 border-foreground px-2 py-1 bg-background brutalist-interactive cursor-pointer">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div className="p-4 border-t-2 border-foreground bg-primary/5">
            <div className="flex items-center gap-2 text-xs font-black uppercase mb-2">
              <Zap className="h-4 w-4 text-primary" />
              AI_Summary
            </div>
            <p className="text-[10px] font-mono leading-relaxed opacity-70">
              Aggregated sentiment is leaning BULLISH due to NVIDIA's hardware announcement and positive FED outlook. Monitor $NVDA for volatility at open.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function SentimentGauge({ label, value, color, status }: any) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[9px] font-black uppercase">
        <span>{label}</span>
        <span className="text-primary">{status}</span>
      </div>
      <div className="h-4 w-full border-2 border-foreground bg-background p-[2px]">
        <div className={`h-full ${color}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}