'use client'

import { useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, Trash2, Edit2, Star, TrendingUp, TrendingDown } from 'lucide-react'
import { cn, formatCurrency } from '@/lib/utils'

export interface WatchlistItem {
  id: string
  symbol: string
  companyName: string
  price: number
  change: number
  changePercent: number
  addedAt: Date
  notes?: string
}

export interface Watchlist {
  id: string
  name: string
  items: WatchlistItem[]
  isDefault: boolean
}

interface WatchlistManagerProps {
  className?: string
}

function WatchlistSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-48" />
      </CardHeader>
      <CardContent className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </CardContent>
    </Card>
  )
}

export function WatchlistManager({ className }: WatchlistManagerProps) {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([
    {
      id: '1',
      name: 'My Watchlist',
      isDefault: true,
      items: [
        { id: '1', symbol: 'AAPL', companyName: 'Apple Inc.', price: 178.72, change: 2.34, changePercent: 1.33, addedAt: new Date() },
        { id: '2', symbol: 'MSFT', companyName: 'Microsoft Corporation', price: 378.91, change: -1.25, changePercent: -0.33, addedAt: new Date() },
        { id: '3', symbol: 'GOOGL', companyName: 'Alphabet Inc.', price: 141.80, change: 3.45, changePercent: 2.49, addedAt: new Date() },
      ],
    },
    {
      id: '2',
      name: 'Tech Stocks',
      isDefault: false,
      items: [
        { id: '4', symbol: 'NVDA', companyName: 'NVIDIA Corporation', price: 721.33, change: 15.67, changePercent: 2.22, addedAt: new Date() },
        { id: '5', symbol: 'META', companyName: 'Meta Platforms Inc.', price: 474.99, change: 8.12, changePercent: 1.74, addedAt: new Date() },
      ],
    },
  ])

  const [newWatchlistName, setNewWatchlistName] = useState('')
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingWatchlist, setEditingWatchlist] = useState<string | null>(null)

  const createWatchlist = useCallback(() => {
    if (!newWatchlistName.trim()) return

    const newWatchlist: Watchlist = {
      id: Date.now().toString(),
      name: newWatchlistName.trim(),
      items: [],
      isDefault: false,
    }

    setWatchlists((prev) => [...prev, newWatchlist])
    setNewWatchlistName('')
    setIsDialogOpen(false)
  }, [newWatchlistName])

  const deleteWatchlist = useCallback((id: string) => {
    setWatchlists((prev) => prev.filter((w) => w.id !== id))
  }, [])

  const addToWatchlist = useCallback((watchlistId: string, item: WatchlistItem) => {
    setWatchlists((prev) =>
      prev.map((w) =>
        w.id === watchlistId ? { ...w, items: [...w.items, item] } : w
      )
    )
  }, [])

  const removeFromWatchlist = useCallback((watchlistId: string, itemId: string) => {
    setWatchlists((prev) =>
      prev.map((w) =>
        w.id === watchlistId ? { ...w, items: w.items.filter((i) => i.id !== itemId) } : w
      )
    )
  }, [])

  return (
    <Card className={cn('', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <Star className="h-5 w-5" />
            Watchlists
          </CardTitle>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" />
                New Watchlist
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Watchlist</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Name</Label>
                  <Input
                    value={newWatchlistName}
                    onChange={(e) => setNewWatchlistName(e.target.value)}
                    placeholder="e.g., Growth Stocks"
                    onKeyDown={(e) => e.key === 'Enter' && createWatchlist()}
                  />
                </div>
                <Button onClick={createWatchlist} className="w-full">
                  Create Watchlist
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue={watchlists[0]?.id}>
          <TabsList className="w-full justify-start mb-4">
            {watchlists.map((watchlist) => (
              <TabsTrigger key={watchlist.id} value={watchlist.id} className="flex items-center gap-2">
                {watchlist.name}
                <Badge variant="secondary" className="text-xs">
                  {watchlist.items.length}
                </Badge>
              </TabsTrigger>
            ))}
          </TabsList>

          {watchlists.map((watchlist) => (
            <TabsContent key={watchlist.id} value={watchlist.id}>
              <div className="space-y-3">
                {watchlist.items.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Star className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>No items in this watchlist</p>
                    <p className="text-sm">Search for symbols to add them</p>
                  </div>
                ) : (
                  watchlist.items.map((item) => (
                    <WatchlistItem
                      key={item.id}
                      item={item}
                      onRemove={() => removeFromWatchlist(watchlist.id, item.id)}
                    />
                  ))
                )}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </CardContent>
    </Card>
  )
}

export default WatchlistManager
