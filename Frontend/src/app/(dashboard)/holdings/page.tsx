'use client'

import { useEffect, useState } from 'react'
import { holdingsApi, Holding } from '@/lib/api/holdings'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Plus, Trash2, Edit2, DollarSign } from 'lucide-react'

interface HoldingsPageProps {
  portfolioId: string
  portfolioName: string
}

export default function HoldingsPage({ portfolioId, portfolioName }: HoldingsPageProps) {
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [newAssetId, setNewAssetId] = useState('')
  const [newQuantity, setNewQuantity] = useState('')
  const [selectedHolding, setSelectedHolding] = useState<Holding | null>(null)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editQuantity, setEditQuantity] = useState('')
  const [editAvgPrice, setEditAvgPrice] = useState('')

  useEffect(() => {
    fetchHoldings()
  }, [portfolioId])

  const fetchHoldings = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await holdingsApi.list(portfolioId)
      setHoldings(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch holdings')
    } finally {
      setLoading(false)
    }
  }

  const handleAddHolding = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await holdingsApi.create(portfolioId, {
        asset_id: newAssetId,
        quantity: newQuantity,
      })
      setShowAddDialog(false)
      setNewAssetId('')
      setNewQuantity('')
      fetchHoldings()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add holding')
    }
  }

  const handleUpdateHolding = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedHolding) return
    try {
      await holdingsApi.update(portfolioId, selectedHolding.id, {
        quantity: editQuantity,
        average_buy_price: editAvgPrice || undefined,
      })
      setEditDialogOpen(false)
      setSelectedHolding(null)
      fetchHoldings()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update holding')
    }
  }

  const handleDeleteHolding = async (holdingId: string) => {
    if (!confirm('Are you sure you want to remove this holding?')) return
    try {
      await holdingsApi.delete(portfolioId, holdingId)
      fetchHoldings()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete holding')
    }
  }

  const openEditDialog = (holding: Holding) => {
    setSelectedHolding(holding)
    setEditQuantity(holding.quantity)
    setEditAvgPrice(holding.average_buy_price || '')
    setEditDialogOpen(true)
  }

  const totalValue = holdings.reduce((sum, h) => sum + (parseFloat(h.current_value || '0')), 0)
  const totalPnl = holdings.reduce((sum, h) => sum + (parseFloat(h.unrealized_pnl || '0')), 0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{portfolioName}</h1>
          <p className="text-muted-foreground">Portfolio Holdings</p>
        </div>
        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Holding
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Holding</DialogTitle>
              <DialogDescription>Add a new asset to your portfolio</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleAddHolding} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="assetId">Asset ID</Label>
                <Input
                  id="assetId"
                  value={newAssetId}
                  onChange={(e) => setNewAssetId(e.target.value)}
                  placeholder="Enter asset UUID"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="quantity">Quantity</Label>
                <Input
                  id="quantity"
                  type="number"
                  step="any"
                  value={newQuantity}
                  onChange={(e) => setNewQuantity(e.target.value)}
                  placeholder="0.00"
                  required
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setShowAddDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit">Add</Button>
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

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardDescription>Total Value</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Total Holdings</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{holdings.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Unrealized P&L</CardDescription>
          </CardHeader>
          <CardContent>
            <p className={`text-3xl font-bold ${totalPnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {totalPnl >= 0 ? '+' : ''}${totalPnl.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </p>
          </CardContent>
        </Card>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : holdings.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <DollarSign className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-4">No holdings in this portfolio</p>
            <Button onClick={() => setShowAddDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Holding
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {holdings.map((holding) => (
            <Card key={holding.id}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-xl font-bold">{holding.asset.ticker}</h3>
                      <Badge variant="outline">{holding.asset.asset_class}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">{holding.asset.name}</p>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Quantity</p>
                        <p className="font-semibold">{parseFloat(holding.quantity).toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Avg. Buy Price</p>
                        <p className="font-semibold">${parseFloat(holding.average_buy_price || '0').toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Current Price</p>
                        <p className="font-semibold">${parseFloat(holding.current_price || '0').toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Current Value</p>
                        <p className="font-semibold">${parseFloat(holding.current_value || '0').toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">P&L</p>
                        <p className={`font-semibold flex items-center ${parseFloat(holding.unrealized_pnl || '0') >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {parseFloat(holding.unrealized_pnl || '0') >= 0 ? (
                            <TrendingUp className="w-4 h-4 mr-1" />
                          ) : (
                            <TrendingDown className="w-4 h-4 mr-1" />
                          )}
                          ${Math.abs(parseFloat(holding.unrealized_pnl || '0')).toFixed(2)}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <Button variant="ghost" size="icon" onClick={() => openEditDialog(holding)}>
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDeleteHolding(holding.id)}>
                      <Trash2 className="w-4 h-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Holding</DialogTitle>
            <DialogDescription>Update holding quantity and average buy price</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUpdateHolding} className="space-y-4">
            <div className="space-y-2">
              <Label>Asset</Label>
              <Input value={selectedHolding?.asset.ticker || ''} disabled />
            </div>
            <div className="space-y-2">
              <Label htmlFor="editQuantity">Quantity</Label>
              <Input
                id="editQuantity"
                type="number"
                step="any"
                value={editQuantity}
                onChange={(e) => setEditQuantity(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="editAvgPrice">Average Buy Price</Label>
              <Input
                id="editAvgPrice"
                type="number"
                step="any"
                value={editAvgPrice}
                onChange={(e) => setEditAvgPrice(e.target.value)}
                placeholder="Optional"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">Save</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
