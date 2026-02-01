'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ExternalLink, MessageSquare, Twitter, MessageSquare } from 'lucide-react'

interface SocialPost {
  id: string
  platform: 'twitter' | 'reddit'
  username: string
  content: string
  sentiment: number
  sentimentLabel: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
  timestamp: string
  url: string
}

interface SocialFeedProps {
  posts: SocialPost[]
  filter?: 'all' | 'twitter' | 'reddit'
  onFilterChange?: (filter: 'all' | 'twitter' | 'reddit') => void
  onPostClick?: (post: SocialPost) => void
  className?: string
}

const SENTIMENT_STYLES = {
  BULLISH: 'bg-success/10 border-success text-success',
  BEARISH: 'bg-destructive/10 border-destructive text-destructive',
  NEUTRAL: 'bg-muted/50 border-border text-muted-foreground'
}

export function SocialFeed({ posts, filter = 'all', onFilterChange, onPostClick, className }: SocialFeedProps) {
  const filteredPosts = React.useMemo(() => {
    if (filter === 'all') return posts
    return posts.filter(post => post.platform === filter)
  }, [posts, filter])

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    
    if (hours < 1) return `${Math.floor(diff / (1000 * 60))}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${Math.floor(hours / 24)}d ago`
  }

  return (
    <Card className={cn('rounded-none border-1', className)}>
      <CardHeader className="border-b-1 pb-0">
        <div className="flex items-center justify-between">
          <CardTitle className="font-black uppercase flex items-center gap-2">
            <MessageSquare className="h-5 w-5" aria-hidden="true" />
            Social Feed
          </CardTitle>
          <span className="text-xs text-muted-foreground font-mono">
            {filteredPosts.length} posts
          </span>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs value={filter} onValueChange={(v) => onFilterChange?.(v as 'all' | 'twitter' | 'reddit')}>
          <TabsList className="rounded-none border-b-1 bg-transparent p-0 h-auto w-full justify-start">
            <TabsTrigger 
              value="all" 
              className={cn(
                'rounded-none border-b-2 border-t-2 border-x-2 border-transparent data-[state=active]:border-foreground data-[state=active]:bg-transparent px-4 py-2 font-black uppercase text-xs'
              )}
            >
              All
            </TabsTrigger>
            <TabsTrigger 
              value="twitter"
              className={cn(
                'rounded-none border-b-2 border-t-2 border-x-2 border-transparent data-[state=active]:border-foreground data-[state=active]:bg-transparent px-4 py-2 font-black uppercase text-xs flex items-center gap-2'
              )}
            >
              <Twitter className="h-3 w-3" aria-hidden="true" />
              Twitter
            </TabsTrigger>
            <TabsTrigger 
              value="reddit"
              className={cn(
                'rounded-none border-b-2 border-t-2 border-x-2 border-transparent data-[state=active]:border-foreground data-[state=active]:bg-transparent px-4 py-2 font-black uppercase text-xs flex items-center gap-2'
              )}
            >
              <MessageSquare className="h-3 w-3" aria-hidden="true" />
              MessageSquare
            </TabsTrigger>
          </TabsList>

          <TabsContent value={filter} className="m-0">
            <div className="divide-y-1" role="feed" aria-label="Social media posts">
              {filteredPosts.length === 0 ? (
                <div className="p-8 text-center">
                  <p className="font-mono text-sm text-muted-foreground">
                    No posts found
                  </p>
                </div>
              ) : (
                filteredPosts.map((post) => (
                  <article 
                    key={post.id} 
                    className="p-4 hover:bg-muted/50 transition-colors cursor-pointer"
                    onClick={() => onPostClick?.(post)}
                    role="listitem"
                    aria-label={`Post by ${post.username}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={cn(
                        'flex-shrink-0 w-8 h-8 rounded-none flex items-center justify-center',
                        post.platform === 'twitter' ? 'bg-blue-500/10' : 'bg-orange-500/10'
                      )}>
                        {post.platform === 'twitter' ? (
                          <Twitter className="h-4 w-4 text-blue-500" aria-hidden="true" />
                        ) : (
                          <MessageSquare className="h-4 w-4 text-orange-500" aria-hidden="true" />
                        )}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-bold text-sm uppercase">{post.username}</span>
                          <Badge className={cn('rounded-none border-1 px-2 py-0 text-xs font-mono', SENTIMENT_STYLES[post.sentimentLabel])}>
                            {post.sentiment >= 0 ? '+' : ''}{post.sentiment.toFixed(1)}
                          </Badge>
                          <time className="text-xs text-muted-foreground font-mono">
                            {formatTime(post.timestamp)}
                          </time>
                        </div>
                        
                        <p className="text-sm leading-relaxed mb-2">
                          {post.content}
                        </p>
                        
                        <a 
                          href={post.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                          onClick={(e) => e.stopPropagation()}
                          aria-label={`View original ${post.platform} post`}
                        >
                          <ExternalLink className="h-3 w-3" aria-hidden="true" />
                          View original
                        </a>
                      </div>
                    </div>
                  </article>
                ))
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
