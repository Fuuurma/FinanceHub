'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Twitter, MessageCircle, ExternalLink, TrendingUp, Filter, RefreshCw } from 'lucide-react'

interface SocialFeedItem {
  id: string
  source: 'twitter' | 'reddit'
  author: string
  content: string
  timestamp: string
  sentiment_score: number
  sentiment_label: 'bullish' | 'bearish' | 'neutral'
  engagement?: {
    likes?: number
    retweets?: number
    upvotes?: number
    comments?: number
  }
  url: string
}

interface SocialFeedProps {
  symbol: string
  items: SocialFeedItem[]
  isLoading: boolean
  onRefresh?: () => void
  className?: string
}

export function SocialFeed({
  symbol,
  items,
  isLoading,
  onRefresh,
  className
}: SocialFeedProps) {
  const [filter, setFilter] = React.useState<'all' | 'twitter' | 'reddit'>('all')

  const filteredItems = React.useMemo(() => {
    if (filter === 'all') return items
    return items.filter(item => item.source === filter)
  }, [items, filter])

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  }

  const getSentimentColor = (label: string) => {
    switch (label) {
      case 'bullish': return 'bg-green-100 text-green-800 border-green-300'
      case 'bearish': return 'bg-red-100 text-red-800 border-red-300'
      default: return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    }
  }

  if (isLoading) {
    return (
      <Card className={cn('rounded-none border-2 border-foreground', className)}>
        <CardHeader className="border-b-2 border-foreground">
          <Skeleton className="h-8 w-48" />
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('rounded-none border-2 border-foreground', className)}>
      <CardHeader className="border-b-2 border-foreground">
        <div className="flex items-center justify-between">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Social Feed
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="font-mono text-sm">
              {filteredItems.length} posts
            </Badge>
            {onRefresh && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRefresh}
                className="rounded-none border-2 font-bold uppercase"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs value={filter} onValueChange={(v) => setFilter(v as any)} className="border-b-2 border-foreground">
          <TabsList className="rounded-none border-b-0 bg-transparent p-0 h-auto w-full justify-start">
            <TabsTrigger
              value="all"
              className="rounded-none border-2 border-b-0 data-[state=active]:bg-foreground data-[state=active]:text-background px-4 py-2 font-black uppercase"
            >
              All
            </TabsTrigger>
            <TabsTrigger
              value="twitter"
              className="rounded-none border-2 border-b-0 data-[state=active]:bg-foreground data-[state=active]:text-background px-4 py-2 font-black uppercase"
            >
              <Twitter className="h-4 w-4 mr-2" />
              Twitter
            </TabsTrigger>
            <TabsTrigger
              value="reddit"
              className="rounded-none border-2 border-b-0 data-[state=active]:bg-foreground data-[state=active]:text-background px-4 py-2 font-black uppercase"
            >
              <MessageCircle className="h-4 w-4 mr-2" />
              Reddit
            </TabsTrigger>
          </TabsList>

          <TabsContent value={filter} className="p-4">
            {filteredItems.length === 0 ? (
              <div className="text-center py-12">
                <MessageCircle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="font-black uppercase text-lg mb-2">No Posts Found</h3>
                <p className="text-muted-foreground font-mono text-sm">
                  No social media posts for {symbol} in this filter
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredItems.map((item) => (
                  <div
                    key={item.id}
                    className="border-2 border-foreground p-4 hover:bg-muted/30 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {item.source === 'twitter' ? (
                          <Twitter className="h-4 w-4 text-blue-500" />
                        ) : (
                          <MessageCircle className="h-4 w-4 text-orange-500" />
                        )}
                        <span className="font-bold text-sm">@{item.author}</span>
                        <Badge className={cn('text-xs', getSentimentColor(item.sentiment_label))}>
                          {item.sentiment_label}
                        </Badge>
                      </div>
                      <span className="text-xs font-mono text-muted-foreground">
                        {formatTime(item.timestamp)}
                      </span>
                    </div>

                    <p className="text-sm mb-3">{item.content}</p>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        {item.source === 'twitter' && item.engagement && (
                          <>
                            <span>❤️ {item.engagement.likes?.toLocaleString()}</span>
                            <span>🔄 {item.engagement.retweets?.toLocaleString()}</span>
                          </>
                        )}
                        {item.source === 'reddit' && item.engagement && (
                          <>
                            <span>⬆️ {item.engagement.upvotes?.toLocaleString()}</span>
                            <span>💬 {item.engagement.comments?.toLocaleString()}</span>
                          </>
                        )}
                      </div>
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs font-bold uppercase flex items-center gap-1 hover:underline"
                      >
                        <ExternalLink className="h-3 w-3" />
                        View
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
