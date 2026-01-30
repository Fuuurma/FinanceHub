'use client'

import { useState, useCallback, useMemo } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { RefreshCw, Clock, Globe } from 'lucide-react'
import type { NewsArticle, NewsFilters } from '@/lib/types/news-sentiment'
import { NewsCard } from './NewsCard'
import { NewsFilters as NewsFiltersComponent } from './NewsFilters'
import { NewsSearch } from './NewsSearch'
import { NewsSentimentPanel } from './NewsSentimentPanel'
import { TrendingTopics } from './TrendingTopics'
import { cn } from '@/lib/utils'

interface NewsFeedProps {
  articles?: NewsArticle[]
  loading?: boolean
  onRefresh?: () => void
  onSymbolClick?: (symbol: string) => void
  className?: string
}

const MOCK_ARTICLES: NewsArticle[] = [
  {
    id: '1',
    title: 'FED CHAIR INDICATES RATE STABILITY THROUGH Q3; EYES INFLATION TARGETS',
    description: 'Federal Reserve officials signal a pause in rate hikes as inflation shows signs of cooling. Markets react positively to the dovish tone.',
    source: 'FED_WIRE',
    author: 'John Smith',
    published_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    url: 'https://example.com/news/1',
    image_url: null,
    symbols: ['DXY', 'SPY', 'TLT'],
    sentiment_score: 0.45,
    sentiment_label: 'NEUTRAL',
    relevance_score: 0.92,
  },
  {
    id: '2',
    title: 'ETHEREUM VITALIK BUTERIN PROPOSES NEW EIP FOR LAYER 2 SCALABILITY OPTIMIZATION',
    description: 'Ethereum co-founder Vitalik Buterin has submitted a new Improvement Proposal aimed at enhancing Layer 2 solutions and reducing gas fees.',
    source: 'BLOCK_REPORT',
    author: 'Sarah Chen',
    published_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    url: 'https://example.com/news/2',
    image_url: null,
    symbols: ['ETH', 'LDO', 'ARB'],
    sentiment_score: 0.72,
    sentiment_label: 'BULLISH',
    relevance_score: 0.88,
  },
  {
    id: '3',
    title: 'NVIDIA ANNOUNCES NEW H200 CHIP ARCHITECTURE; SHIPMENTS STARTING JUNE',
    description: 'NVIDIA unveils its next-generation AI chip architecture, promising 2x performance improvement over current H100 models.',
    source: 'REUTERS_ALPHA',
    author: 'Mike Johnson',
    published_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    url: 'https://example.com/news/3',
    image_url: null,
    symbols: ['NVDA', 'TSMC'],
    sentiment_score: 0.85,
    sentiment_label: 'BULLISH',
    relevance_score: 0.95,
  },
  {
    id: '4',
    title: 'MAJOR EXCHANGE SUSPENDS WITHDRAWALS FOR SCHEDULED DATABASE OPTIMIZATION',
    description: 'A leading cryptocurrency exchange has temporarily suspended withdrawals to complete scheduled database maintenance.',
    source: 'EXCHANGE_ALERTS',
    author: 'Alex Wong',
    published_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    url: 'https://example.com/news/4',
    image_url: null,
    symbols: ['SOL', 'BNB'],
    sentiment_score: -0.35,
    sentiment_label: 'BEARISH',
    relevance_score: 0.75,
  },
  {
    id: '5',
    title: 'OIL PRICES STABILIZE AS MIDDLE EAST TENSIONS EASE; SUPPLY CHAINS RECOVER',
    description: 'Crude oil prices find support as geopolitical tensions show signs of easing and supply chain concerns diminish.',
    source: 'GOLDMAN_SACHS',
    author: 'Emma Davis',
    published_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    url: 'https://example.com/news/5',
    image_url: null,
    symbols: ['USO', 'XLE'],
    sentiment_score: 0.15,
    sentiment_label: 'NEUTRAL',
    relevance_score: 0.68,
  },
  {
    id: '6',
    title: 'APPLE ANNOUNCES RECORD Q1 EARNINGS BEATING WALL STREET EXPECTATIONS',
    description: 'Apple reports record quarterly earnings driven by strong iPhone and services revenue growth.',
    source: 'CNBC',
    author: 'Lisa Park',
    published_at: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    url: 'https://example.com/news/6',
    image_url: null,
    symbols: ['AAPL'],
    sentiment_score: 0.68,
    sentiment_label: 'POSITIVE',
    relevance_score: 0.82,
  },
]

export function NewsFeed({
  articles = MOCK_ARTICLES,
  loading = false,
  onRefresh,
  onSymbolClick,
  className,
}: NewsFeedProps) {
  const [filters, setFilters] = useState<NewsFilters>({
    category: 'ALL',
    sentiment: 'all',
    impact: 'all',
    timeframe: '24h',
    source: 'all',
  })
  const [searchQuery, setSearchQuery] = useState('')

  const filteredArticles = useMemo(() => {
    return articles.filter((article) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        const matchesTitle = article.title.toLowerCase().includes(query)
        const matchesSymbol = article.symbols.some((s) => s.toLowerCase().includes(query))
        const matchesSource = article.source.toLowerCase().includes(query)
        if (!matchesTitle && !matchesSymbol && !matchesSource) return false
      }

      if (filters.sentiment !== 'all') {
        const sentimentMatch = article.sentiment_label?.toLowerCase() === filters.sentiment
        if (!sentimentMatch) return false
      }

      if (filters.source !== 'all') {
        if (article.source !== filters.source) return false
      }

      return true
    })
  }, [articles, filters, searchQuery])

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query)
  }, [])

  const handleClear = useCallback(() => {
    setSearchQuery('')
  }, [])

  const handleBookmark = useCallback((id: string) => {
    console.log('Bookmark:', id)
  }, [])

  if (loading) {
    return (
      <div className={cn('flex gap-4 h-full', className)}>
        <div className="flex-1 border-2 border-foreground">
          <div className="h-12 border-b-2 border-foreground bg-muted/30 p-4">
            <Skeleton className="h-6 w-48" />
          </div>
          <ScrollArea className="flex-1">
            <div className="divide-y-2 divide-foreground">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="p-4 space-y-3">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
        <div className="w-80 space-y-4">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  return (
    <div className={cn('flex flex-col h-full bg-background', className)}>
      <div className="h-12 border-b-2 border-foreground flex items-center px-4 gap-4 bg-muted/20">
        <div className="flex items-center gap-2 border-r-2 border-foreground/20 pr-4">
          <Globe className="h-4 w-4 text-primary" />
          <span className="text-[10px] font-black uppercase italic tracking-widest">Global_Feed_v2.0</span>
        </div>

        <div className="flex-1 max-w-md">
          <NewsSearch
            onSearch={handleSearch}
            onClear={handleClear}
            placeholder="Search news, symbols..."
          />
        </div>

        <NewsFiltersComponent filters={filters} onFiltersChange={setFilters} />

        <div className="ml-auto flex items-center gap-4">
          <div className="flex items-center gap-2 text-[10px] font-mono opacity-50">
            <Clock className="h-3 w-3" />
            {new Date().toLocaleTimeString()} UTC
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 border-2 border-foreground rounded-none"
            onClick={onRefresh}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <ScrollArea className="flex-1 border-r-2 border-foreground">
          <div className="divide-y-2 divide-foreground">
            {filteredArticles.length > 0 ? (
              filteredArticles.map((article) => (
                <div key={article.id} className="group">
                  <NewsCard
                    article={article}
                    onBookmark={handleBookmark}
                    onSymbolClick={onSymbolClick}
                  />
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-64 text-muted-foreground">
                <div className="text-center">
                  <Globe className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p className="font-black uppercase">No news found</p>
                  <p className="text-sm">Try adjusting your filters</p>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="w-80 flex flex-col bg-muted/10 overflow-y-auto">
          <NewsSentimentPanel />
          <div className="p-4">
            <TrendingTopics />
          </div>
        </div>
      </div>
    </div>
  )
}

export default NewsFeed
