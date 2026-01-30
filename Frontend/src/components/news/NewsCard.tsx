'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import {
  Bookmark,
  BookmarkCheck,
  ExternalLink,
  Link2,
  Clock,
  Globe,
  TrendingUp,
  TrendingDown,
  Minus,
  ArrowUpRight,
} from 'lucide-react'
import type { NewsArticle } from '@/lib/types/news-sentiment'
import { cn, formatDateTime } from '@/lib/utils'

interface NewsCardProps {
  article: NewsArticle
  onBookmark?: (id: string) => void
  onSymbolClick?: (symbol: string) => void
  compact?: boolean
  className?: string
}

const SENTIMENT_CONFIG = {
  bullish: { icon: TrendingUp, color: 'text-green-600', bg: 'bg-green-100', label: 'Bullish' },
  bearish: { icon: TrendingDown, color: 'text-red-600', bg: 'bg-red-100', label: 'Bearish' },
  positive: { icon: TrendingUp, color: 'text-green-600', bg: 'bg-green-100', label: 'Positive' },
  negative: { icon: TrendingDown, color: 'text-red-600', bg: 'bg-red-100', label: 'Negative' },
  neutral: { icon: Minus, color: 'text-gray-600', bg: 'bg-gray-100', label: 'Neutral' },
}

const IMPACT_CONFIG = {
  urgent: { color: 'bg-red-600 animate-pulse', label: 'URGENT' },
  high: { color: 'bg-orange-500', label: 'HIGH' },
  medium: { color: 'bg-yellow-500', label: 'MEDIUM' },
  low: { color: 'bg-blue-500', label: 'LOW' },
}

const CATEGORY_COLORS: Record<string, string> = {
  MACRO: 'bg-purple-100 text-purple-700 border-purple-300',
  CRYPTO: 'bg-orange-100 text-orange-700 border-orange-300',
  TECH: 'bg-blue-100 text-blue-700 border-blue-300',
  COMMODITIES: 'bg-amber-100 text-amber-700 border-amber-300',
  SECURITY: 'bg-red-100 text-red-700 border-red-300',
  EARNINGS: 'bg-emerald-100 text-emerald-700 border-emerald-300',
  ECONOMY: 'bg-indigo-100 text-indigo-700 border-indigo-300',
  GEOPOLITICAL: 'bg-rose-100 text-rose-700 border-rose-300',
  DEFAULT: 'bg-gray-100 text-gray-700 border-gray-300',
}

export function NewsCard({
  article,
  onBookmark,
  onSymbolClick,
  compact = false,
  className,
}: NewsCardProps) {
  const [isBookmarked, setIsBookmarked] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  const sentimentKey = (article.sentiment_label?.toLowerCase() || 'neutral') as keyof typeof SENTIMENT_CONFIG
  const sentiment = SENTIMENT_CONFIG[sentimentKey] || SENTIMENT_CONFIG.neutral

  const handleBookmark = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsBookmarked(!isBookmarked)
    onBookmark?.(article.id)
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return formatDateTime(dateString)
  }

  if (compact) {
    return (
      <Card
        className={cn(
          'border-l-4 border-l-foreground/20 hover:border-l-primary transition-all cursor-pointer p-3',
          className
        )}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <CardContent className="p-0 space-y-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>{formatTime(article.published_at)}</span>
            <span className="font-black text-foreground/40">|</span>
            <Globe className="h-3 w-3" />
            <span>{article.source}</span>
          </div>
          <h4 className="text-sm font-medium line-clamp-2 group-hover:text-primary transition-colors">
            {article.title}
          </h4>
          {article.symbols.length > 0 && (
            <div className="flex gap-1 flex-wrap">
              {article.symbols.slice(0, 3).map((symbol) => (
                <Badge
                  key={symbol}
                  variant="outline"
                  className="text-[10px] font-bold cursor-pointer hover:bg-primary hover:text-primary-foreground"
                  onClick={(e) => {
                    e.stopPropagation()
                    onSymbolClick?.(symbol)
                  }}
                >
                  ${symbol}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <TooltipProvider>
      <Card
        className={cn(
          'border-2 border-foreground transition-all hover:shadow-[4px_4px_0px_0px_var(--foreground)]',
          article.sentiment_score && article.sentiment_score > 0 && 'border-l-4 border-l-green-500',
          article.sentiment_score && article.sentiment_score < 0 && 'border-l-4 border-l-red-500',
          !article.sentiment_score && 'border-l-4 border-l-foreground/20',
          className
        )}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <CardContent className="p-4">
          <div className="flex items-start gap-4">
            <div className="flex-1 space-y-2">
              <div className="flex items-center gap-2 flex-wrap">
                <Badge className={cn('rounded-none font-black text-[10px] h-5', IMPACT_CONFIG.urgent.color)}>
                  URGENT
                </Badge>
                <Badge className={cn('rounded-none font-black text-[10px] h-5 border-2', CATEGORY_COLORS[article.sentiment_label || 'DEFAULT'] || CATEGORY_COLORS.DEFAULT)}>
                  {article.source}
                </Badge>
                <span className="text-[11px] font-mono text-muted-foreground flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {formatTime(article.published_at)}
                </span>
              </div>

              <h3 className="text-base font-black uppercase leading-tight tracking-tight">
                {article.title}
              </h3>

              {article.description && (
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {article.description}
                </p>
              )}

              <div className="flex items-center gap-4 pt-2">
                {article.symbols.length > 0 && (
                  <div className="flex gap-1 flex-wrap">
                    {article.symbols.map((symbol) => (
                      <Badge
                        key={symbol}
                        variant="outline"
                        className={cn(
                          'text-xs font-bold cursor-pointer hover:bg-primary hover:text-primary-foreground border-foreground',
                          isHovered && 'border-primary'
                        )}
                        onClick={(e) => {
                          e.stopPropagation()
                          onSymbolClick?.(symbol)
                        }}
                      >
                        ${symbol}
                      </Badge>
                    ))}
                  </div>
                )}

                {article.sentiment_score !== null && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className={cn('flex items-center gap-1 text-xs font-bold', sentiment.color)}>
                        <sentiment.icon className="h-4 w-4" />
                        <span>{sentiment.label}</span>
                        <span className="font-mono">
                          {article.sentiment_score >= 0 ? '+' : ''}{article.sentiment_score.toFixed(2)}
                        </span>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent className="border-2 border-foreground bg-background">
                      <p className="text-xs font-mono">Sentiment Score: {article.sentiment_score.toFixed(3)}</p>
                    </TooltipContent>
                  </Tooltip>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-2 shrink-0">
              <div className="flex gap-1">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-8 w-8 border-2 border-foreground/20 hover:border-foreground rounded-none"
                      onClick={handleBookmark}
                    >
                      {isBookmarked ? (
                        <BookmarkCheck className="h-4 w-4" />
                      ) : (
                        <Bookmark className="h-4 w-4" />
                      )}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent className="border-2 border-foreground">
                    <p className="text-xs font-black uppercase">
                      {isBookmarked ? 'Remove Bookmark' : 'Bookmark'}
                    </p>
                  </TooltipContent>
                </Tooltip>

                {article.url && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-8 w-8 border-2 border-foreground/20 hover:border-foreground rounded-none"
                        onClick={() => window.open(article.url!, '_blank')}
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent className="border-2 border-foreground">
                      <p className="text-xs font-black uppercase">Open Source</p>
                    </TooltipContent>
                  </Tooltip>
                )}

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-8 w-8 border-2 border-foreground/20 hover:border-foreground rounded-none"
                    >
                      <Link2 className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent className="border-2 border-foreground">
                    <p className="text-xs font-black uppercase">Copy Link</p>
                  </TooltipContent>
                </Tooltip>
              </div>

              {article.relevance_score !== null && (
                <div className="text-center">
                  <span className="text-[10px] font-mono text-muted-foreground">
                    Relevance: {Math.round(article.relevance_score * 100)}%
                  </span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </TooltipProvider>
  )
}

export default NewsCard
