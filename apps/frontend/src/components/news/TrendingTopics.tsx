'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Minus, Hash } from 'lucide-react'
import type { TrendingTopic } from '@/lib/types/news-sentiment'
import { cn } from '@/lib/utils'

interface TrendingTopicsProps {
  topics?: TrendingTopic[]
  className?: string
}

const MOCK_TRENDING: TrendingTopic[] = [
  { topic: 'AI ARMS RACE', sentiment_score: 0.85, article_count: 45, related_symbols: ['NVDA', 'MSFT', 'GOOGL'] },
  { topic: 'FED RATE CUTS', sentiment_score: 0.45, article_count: 38, related_symbols: ['SPY', 'QQQ'] },
  { topic: 'BITCOIN ETF', sentiment_score: 0.62, article_count: 32, related_symbols: ['BTC', 'COIN'] },
  { topic: 'EARNINGS SEASON', sentiment_score: 0.58, article_count: 28, related_symbols: ['AAPL', 'AMZN'] },
  { topic: 'GEOPOLITICAL', sentiment_score: -0.32, article_count: 22, related_symbols: ['USO', 'TLT'] },
  { topic: 'CLEAN ENERGY', sentiment_score: 0.41, article_count: 18, related_symbols: ['ENPH', 'SEDG'] },
  { topic: 'SEMICONDUCTORS', sentiment_score: 0.78, article_count: 52, related_symbols: ['NVDA', 'AMD', 'TSM'] },
  { topic: 'RETAIL SALES', sentiment_score: 0.33, article_count: 15, related_symbols: ['WMT', 'COST'] },
]

function getTrendIcon(score: number) {
  if (score >= 0.4) return TrendingUp
  if (score >= 0) return Minus
  return TrendingDown
}

function getTrendColor(score: number) {
  if (score >= 0.6) return 'text-green-600 bg-green-100 border-green-300'
  if (score >= 0.4) return 'text-green-500 bg-green-50 border-green-200'
  if (score >= 0.2) return 'text-yellow-600 bg-yellow-100 border-yellow-300'
  if (score >= 0) return 'text-orange-500 bg-orange-50 border-orange-200'
  return 'text-red-600 bg-red-100 border-red-300'
}

export function TrendingTopics({ topics = MOCK_TRENDING, className }: TrendingTopicsProps) {
  return (
    <Card className={cn('border-2 border-foreground', className)}>
      <CardHeader className="py-3 border-b-2 border-foreground bg-muted/30">
        <CardTitle className="text-sm font-black uppercase flex items-center gap-2">
          <Hash className="h-4 w-4" />
          Trending Topics
        </CardTitle>
      </CardHeader>
      <CardContent className="p-3">
        <div className="space-y-2 max-h-[300px] overflow-y-auto">
          {topics.map((topic, idx) => {
            const Icon = getTrendIcon(topic.sentiment_score)
            const trendColor = getTrendColor(topic.sentiment_score)

            return (
              <div
                key={topic.topic}
                className="group p-3 border border-foreground/20 hover:border-foreground hover:bg-muted/50 transition-all cursor-pointer"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'text-[10px] font-black w-5 h-5 flex items-center justify-center rounded-full',
                      idx < 3 ? 'bg-foreground text-background' : 'bg-muted text-muted-foreground'
                    )}>
                      {idx + 1}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-black uppercase">{topic.topic}</span>
                        <Badge className={cn('text-[10px] h-4', trendColor)}>
                          <Icon className="h-3 w-3 mr-1" />
                          {topic.sentiment_score >= 0 ? '+' : ''}{topic.sentiment_score.toFixed(2)}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[10px] text-muted-foreground">
                          {topic.article_count} articles
                        </span>
                        {topic.related_symbols.length > 0 && (
                          <>
                            <span className="text-[10px] text-muted-foreground">•</span>
                            <div className="flex gap-1">
                              {topic.related_symbols.slice(0, 3).map((symbol) => (
                                <span
                                  key={symbol}
                                  className="text-[10px] font-mono font-bold text-primary"
                                >
                                  ${symbol}
                                </span>
                              ))}
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

export default TrendingTopics
