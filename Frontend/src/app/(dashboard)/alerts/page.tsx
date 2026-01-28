'use client'

import { useEffect, useState } from 'react'
import { alertsApi } from '@/lib/api/alerts'
import type { Alert, AlertCreateInput, AlertHistoryItem, AlertStats } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { AlertCircle, Check, X, Plus, RefreshCw, Play, Pause, Trash2 } from 'lucide-react'

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [stats, setStats] = useState<AlertStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('list')
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const [showHistory, setShowHistory] = useState<string | null>(null)
  const [history, setHistory] = useState<AlertHistoryItem[]>([])

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    setLoading(true)
    setError('')
    
    try {
      const [alertsData, statsData] = await Promise.all([
        alertsApi.list({ status: filter }),
        alertsApi.getStats(),
      ])
      setAlerts(alertsData)
      setStats(statsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch alerts')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const data: AlertCreateInput = {
      name: formData.get('name') as string,
      alert_type: formData.get('alert_type') as string,
      symbol: formData.get('symbol') as string,
      condition_value: Number(formData.get('condition_value')),
      condition_operator: formData.get('condition_operator') as string || '>=',
      delivery_channels: formData.get('delivery_channel') ? [formData.get('delivery_channel') as string] : undefined,
      priority: Number(formData.get('priority')) || 5,
      cooldown_seconds: Number(formData.get('cooldown_seconds')) || 300,
    }

    try {
      await alertsApi.create(data)
      setShowCreateDialog(false)
      fetchAlerts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create alert')
    }
  }

  const handleDeleteAlert = async (id: string) => {
    try {
      await alertsApi.delete(id)
      fetchAlerts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete alert')
    }
  }

  const handleToggleAlert = async (alert: Alert) => {
    try {
      if (alert.status === 'active') {
        await alertsApi.disable(alert.id)
      } else {
        await alertsApi.enable(alert.id)
      }
      fetchAlerts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle alert')
    }
  }

  const handleTestAlert = async (id: string) => {
    try {
      const result = await alertsApi.test(id)
      if (result.success) {
        alert(`Alert test successful! Trigger value: ${result.trigger_value}`)
      } else {
        alert(`Alert test failed: ${result.message}`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to test alert')
    }
  }

  const handleViewHistory = async (alertId: string) => {
    setShowHistory(alertId)
    try {
      const historyData = await alertsApi.getHistory(alertId)
      setHistory(historyData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch history')
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800">Active</Badge>
      case 'disabled':
        return <Badge variant="secondary">Disabled</Badge>
      case 'triggered':
        return <Badge className="bg-blue-100 text-blue-800">Triggered</Badge>
      case 'expired':
        return <Badge className="bg-red-100 text-red-800">Expired</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const filteredAlerts = alerts.filter((alert) => {
    const matchesSearch = alert.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          alert.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filter === 'all' || alert.status === filter
    return matchesSearch && matchesFilter
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Alerts</h1>
          <p className="text-muted-foreground">Manage and monitor price alerts</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Alert
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Alert</DialogTitle>
                <DialogDescription>Set up a new price alert for any asset</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreateAlert} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Alert Name</Label>
                  <Input id="name" name="name" placeholder="My Alert" required />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="symbol">Symbol</Label>
                    <Input id="symbol" name="symbol" placeholder="AAPL" required className="uppercase" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="alert_type">Alert Type</Label>
                    <Select name="alert_type" defaultValue="price_above">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="price_above">Price Above</SelectItem>
                        <SelectItem value="price_below">Price Below</SelectItem>
                        <SelectItem value="percent_change">Percent Change</SelectItem>
                        <SelectItem value="volume_spike">Volume Spike</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="condition_value">Trigger Value</Label>
                    <Input id="condition_value" name="condition_value" type="number" step="0.01" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="condition_operator">Operator</Label>
                    <Select name="condition_operator" defaultValue=">=">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value=">=">&gt;=</SelectItem>
                        <SelectItem value="&lt;=">&lt;=</SelectItem>
                        <SelectItem value="==">==</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="priority">Priority</Label>
                    <Input id="priority" name="priority" type="number" min="1" max="10" defaultValue="5" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cooldown_seconds">Cooldown (seconds)</Label>
                    <Input id="cooldown_seconds" name="cooldown_seconds" type="number" min="0" defaultValue="300" />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Create Alert</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
          <Button variant="outline" onClick={fetchAlerts} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader>
              <CardDescription>Total Alerts</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{stats.total_alerts}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardDescription>Active Alerts</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-green-600">{stats.active_alerts}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardDescription>Triggered Today</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-blue-600">{stats.triggered_today}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardDescription>Success Rate</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {stats.active_alerts > 0
                  ? `${((stats.total_alerts - stats.active_alerts) / (stats.total_alerts - stats.active_alerts + stats.triggered_today) * 100).toFixed(0)}%`
                  : '0%'}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="list">Alert List</TabsTrigger>
          <TabsTrigger value="create">Create New</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="space-y-4">
          <div className="flex gap-4 mb-4">
            <Input
              placeholder="Search alerts by name or symbol..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="disabled">Disabled</SelectItem>
                <SelectItem value="triggered">Triggered</SelectItem>
                <SelectItem value="expired">Expired</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {error && (
            <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
              <p>{error}</p>
            </div>
          )}

          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <Card key={i}>
                  <CardContent className="pt-6">
                    <Skeleton className="h-20 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : filteredAlerts.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <AlertCircle className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No alerts found</p>
                <Button onClick={() => setShowCreateDialog(true)}>Create Your First Alert</Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {filteredAlerts.map((alert) => (
                <Card key={alert.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-semibold text-lg">{alert.name}</h3>
                        <p className="text-sm text-muted-foreground">{alert.symbol}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusBadge(alert.status)}
                        <Badge variant="outline">{alert.priority}</Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Type</p>
                        <p className="font-medium">{alert.alert_type}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Trigger Condition</p>
                        <p className="font-medium">
                          {alert.condition_operator} {alert.condition_value}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Triggered</p>
                        <p className="font-medium">{alert.triggered_count} times</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Created</p>
                        <p className="font-medium">{new Date(alert.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>

                    {alert.last_triggered_at && (
                      <div className="mb-4">
                        <p className="text-sm text-muted-foreground">Last Triggered</p>
                        <p className="font-medium">{new Date(alert.last_triggered_at).toLocaleString()}</p>
                      </div>
                    )}

                    <div className="flex gap-2">
                      {alert.status === 'active' && (
                        <Button size="sm" variant="outline" onClick={() => handleToggleAlert(alert)}>
                          <Pause className="w-4 h-4 mr-2" />
                          Disable
                        </Button>
                      )}
                      {alert.status === 'disabled' && (
                        <Button size="sm" variant="outline" onClick={() => handleToggleAlert(alert)}>
                          <Play className="w-4 h-4 mr-2" />
                          Enable
                        </Button>
                      )}
                      <Button size="sm" variant="outline" onClick={() => handleViewHistory(alert.id)}>
                        View History
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => handleTestAlert(alert.id)}>
                        Test
                      </Button>
                      <Button size="sm" variant="destructive" onClick={() => handleDeleteAlert(alert.id)}>
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="create">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-8">
                <AlertCircle className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground mb-6">Create alert from the list tab or use the button above</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {showHistory && (
        <Dialog open={!!showHistory} onOpenChange={() => setShowHistory(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Alert History</DialogTitle>
              <DialogDescription>Trigger history for this alert</DialogDescription>
            </DialogHeader>
            <div className="max-h-96 overflow-y-auto">
              {history.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No trigger history</p>
              ) : (
                <div className="space-y-2">
                  {history.map((item) => (
                    <div key={item.id} className="flex items-center justify-between border-b py-2">
                      <div>
                        <p className="font-medium">Trigger Value: {item.trigger_value}</p>
                        <p className="text-sm text-muted-foreground">{new Date(item.triggered_at).toLocaleString()}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {item.condition_met ? (
                          <Badge className="bg-green-100 text-green-800">Condition Met</Badge>
                        ) : (
                          <Badge variant="secondary">Not Met</Badge>
                        )}
                        {item.notification_sent ? (
                          <Check className="w-4 h-4 text-green-600" />
                        ) : (
                          <X className="w-4 h-4 text-red-600" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="flex justify-end pt-4">
              <Button variant="outline" onClick={() => setShowHistory(null)}>Close</Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}
