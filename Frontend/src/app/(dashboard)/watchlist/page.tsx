'use client'

import { useEffect, useState } from 'react'
import { watchlistApi } from '@/lib/api/watchlist'
import type { Watchlist } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Skeleton } from '@/components/ui/skeleton'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Trash2, Plus, Edit2, Star, Globe, Lock } from 'lucide-react'

export default function WatchlistPage() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [newWatchlistName, setNewWatchlistName] = useState('')
  const [newWatchlistSymbols, setNewWatchlistSymbols] = useState('')
  const [isPublic, setIsPublic] = useState(false)
  const [selectedWatchlist, setSelectedWatchlist] = useState<Watchlist | null>(null)
  const [editDialogOpen, setEditDialogOpen] = useState(false)

  useEffect(() => {
    fetchWatchlists()
  }, [])

  const fetchWatchlists = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await watchlistApi.list()
      setWatchlists(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch watchlists')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateWatchlist = async (e: React.FormEvent) => {
    e.preventDefault()
    const symbols = newWatchlistSymbols
      .split(',')
      .map((s) => s.trim().toUpperCase())
      .filter((s) => s.length > 0)

    try {
      await watchlistApi.create({
        name: newWatchlistName,
        symbols,
        is_public: isPublic,
      })
      setShowCreateDialog(false)
      setNewWatchlistName('')
      setNewWatchlistSymbols('')
      setIsPublic(false)
      fetchWatchlists()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create watchlist')
    }
  }

  const handleDeleteWatchlist = async (id: string) => {
    if (!confirm('Are you sure you want to delete this watchlist?')) return
    try {
      await watchlistApi.delete(id)
      fetchWatchlists()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete watchlist')
    }
  }

  const handleUpdateWatchlist = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedWatchlist) return

    const symbols = newWatchlistSymbols
      .split(',')
      .map((s) => s.trim().toUpperCase())
      .filter((s) => s.length > 0)

    try {
      await watchlistApi.update(selectedWatchlist.id, {
        name: newWatchlistName,
        symbols,
        is_public: isPublic,
      })
      setEditDialogOpen(false)
      setSelectedWatchlist(null)
      setNewWatchlistName('')
      setNewWatchlistSymbols('')
      setIsPublic(false)
      fetchWatchlists()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update watchlist')
    }
  }

  const handleRemoveAsset = async (watchlistId: string, symbol: string) => {
    try {
      await watchlistApi.removeAsset(watchlistId, symbol)
      fetchWatchlists()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove asset')
    }
  }

  const openEditDialog = (watchlist: Watchlist) => {
    setSelectedWatchlist(watchlist)
    setNewWatchlistName(watchlist.name)
    setNewWatchlistSymbols(watchlist.assets.join(', '))
    setIsPublic(watchlist.is_public)
    setEditDialogOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Watchlists</h1>
          <p className="text-muted-foreground">Manage your asset watchlists</p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Watchlist
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Watchlist</DialogTitle>
              <DialogDescription>Create a new watchlist to track assets</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreateWatchlist} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Watchlist Name</Label>
                <Input
                  id="name"
                  value={newWatchlistName}
                  onChange={(e) => setNewWatchlistName(e.target.value)}
                  placeholder="My Watchlist"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="symbols">Symbols (comma separated)</Label>
                <Input
                  id="symbols"
                  value={newWatchlistSymbols}
                  onChange={(e) => setNewWatchlistSymbols(e.target.value)}
                  placeholder="AAPL, GOOGL, MSFT"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="isPublic"
                  checked={isPublic}
                  onCheckedChange={(checked) => setIsPublic(checked as boolean)}
                />
                <Label htmlFor="isPublic">Make this watchlist public</Label>
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit">Create</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="grid gap-6 md:grid-cols-2">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : watchlists.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Star className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-4">No watchlists yet</p>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Watchlist
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {watchlists.map((watchlist) => (
            <Card key={watchlist.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {watchlist.name}
                      {watchlist.is_public ? (
                        <Globe className="w-4 h-4 text-muted-foreground" />
                      ) : (
                        <Lock className="w-4 h-4 text-muted-foreground" />
                      )}
                    </CardTitle>
                    <CardDescription>
                      {watchlist.assets.length} assets • Created {new Date(watchlist.created_at).toLocaleDateString()}
                    </CardDescription>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => openEditDialog(watchlist)}>
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDeleteWatchlist(watchlist.id)}>
                      <Trash2 className="w-4 h-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {watchlist.assets.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {watchlist.assets.map((symbol) => (
                      <Badge key={symbol} variant="secondary" className="flex items-center gap-1">
                        {symbol}
                        <button
                          onClick={() => handleRemoveAsset(watchlist.id, symbol)}
                          className="ml-1 hover:text-destructive"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No assets in this watchlist</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Watchlist</DialogTitle>
            <DialogDescription>Update your watchlist details</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUpdateWatchlist} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="editName">Watchlist Name</Label>
              <Input
                id="editName"
                value={newWatchlistName}
                onChange={(e) => setNewWatchlistName(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="editSymbols">Symbols (comma separated)</Label>
              <Input
                id="editSymbols"
                value={newWatchlistSymbols}
                onChange={(e) => setNewWatchlistSymbols(e.target.value)}
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="editIsPublic"
                checked={isPublic}
                onCheckedChange={(checked) => setIsPublic(checked as boolean)}
              />
              <Label htmlFor="editIsPublic">Make this watchlist public</Label>
            </div>
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">Save Changes</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
