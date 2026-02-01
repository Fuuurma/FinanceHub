'use client';

import React, { useState } from 'react';
import { Bell, BellOff, Trash2, Edit, Pause, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';

interface Alert {
  id: number;
  name: string;
  alert_type: string;
  status: string;
  asset_symbol: string | null;
  condition_value: number;
  condition_operator: string;
  frequency: string;
  send_email: boolean;
  send_push: boolean;
  send_sms: boolean;
  send_in_app: boolean;
  created_at: string;
  last_triggered_at: string | null;
  trigger_count: number;
}

interface AlertListProps {
  alerts: Alert[];
  onCreate: (alert: Partial<Alert>) => Promise<void>;
  onUpdate: (id: number, alert: Partial<Alert>) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onPause: (id: number) => Promise<void>;
  onResume: (id: number) => Promise<void>;
  className?: string;
}

const ALERT_TYPES = [
  { value: 'price_above', label: 'Price Above' },
  { value: 'price_below', label: 'Price Below' },
  { value: 'percent_change', label: 'Percent Change' },
  { value: 'volume_above', label: 'Volume Above' },
  { value: 'portfolio_change', label: 'Portfolio Value Change' },
];

const OPERATORS = [
  { value: '>', label: '>' },
  { value: '>=', label: '>=' },
  { value: '<', label: '<' },
  { value: '<=', label: '<=' },
];

const FREQUENCIES = [
  { value: 'once', label: 'One Time' },
  { value: 'always', label: 'Every Time' },
  { value: 'daily', label: 'Daily Max' },
  { value: 'hourly', label: 'Hourly Max' },
];

export function AlertList({
  alerts,
  onCreate,
  onUpdate,
  onDelete,
  onPause,
  onResume,
  className,
}: AlertListProps) {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingAlert, setEditingAlert] = useState<Alert | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    const formData = new FormData(e.currentTarget);
    try {
      await onCreate({
        alert_type: formData.get('alert_type') as string,
        name: formData.get('name') as string,
        condition_value: parseFloat(formData.get('condition_value') as string),
        condition_operator: formData.get('condition_operator') as string,
        frequency: formData.get('frequency') as string,
        send_email: formData.get('send_email') === 'on',
        send_push: formData.get('send_push') === 'on',
        send_sms: formData.get('send_sms') === 'on',
        send_in_app: formData.get('send_in_app') === 'on',
      });
      setShowCreateDialog(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!editingAlert) return;
    setIsLoading(true);
    const formData = new FormData(e.currentTarget);
    try {
      await onUpdate(editingAlert.id, {
        name: formData.get('name') as string,
        condition_value: parseFloat(formData.get('condition_value') as string),
        condition_operator: formData.get('condition_operator') as string,
      });
      setEditingAlert(null);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-500">Active</Badge>;
      case 'paused':
        return <Badge variant="secondary">Paused</Badge>;
      case 'triggered':
        return <Badge className="bg-blue-500">Triggered</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className={className}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Alerts</h2>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Bell className="h-4 w-4 mr-2" />
          Create Alert
        </Button>
      </div>

      {alerts.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <BellOff className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No alerts configured</p>
            <Button variant="outline" className="mt-4" onClick={() => setShowCreateDialog(true)}>
              Create Your First Alert
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <Card key={alert.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      {alert.status === 'active' ? (
                        <Bell className="h-5 w-5 text-green-500" />
                      ) : (
                        <BellOff className="h-5 w-5 text-muted-foreground" />
                      )}
                      <div>
                        <p className="font-medium">{alert.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {ALERT_TYPES.find(t => t.value === alert.alert_type)?.label || alert.alert_type}
                          {alert.asset_symbol && ` • ${alert.asset_symbol}`}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    {getStatusBadge(alert.status)}

                    <div className="text-sm text-muted-foreground">
                      {alert.condition_operator} {alert.condition_value}
                    </div>

                    <div className="flex items-center gap-1">
                      {alert.send_in_app && <span className="text-xs bg-muted px-1 rounded">In-App</span>}
                      {alert.send_email && <span className="text-xs bg-muted px-1 rounded">Email</span>}
                      {alert.send_push && <span className="text-xs bg-muted px-1 rounded">Push</span>}
                    </div>

                    <div className="flex items-center gap-1">
                      {alert.status === 'active' ? (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => onPause(alert.id)}
                        >
                          <Pause className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => onResume(alert.id)}
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setEditingAlert(alert)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-destructive hover:text-destructive"
                        onClick={() => onDelete(alert.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="mt-2 text-xs text-muted-foreground flex items-center gap-4">
                  <span>Created: {new Date(alert.created_at).toLocaleDateString()}</span>
                  {alert.last_triggered_at && (
                    <span>Last triggered: {new Date(alert.last_triggered_at).toLocaleString()}</span>
                  )}
                  <span>Triggered: {alert.trigger_count} times</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Alert</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <Label htmlFor="name">Alert Name</Label>
              <Input id="name" name="name" placeholder="My Alert" required />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="alert_type">Alert Type</Label>
                <Select name="alert_type" required defaultValue="price_above">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {ALERT_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="frequency">Frequency</Label>
                <Select name="frequency" defaultValue="once">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {FREQUENCIES.map((freq) => (
                      <SelectItem key={freq.value} value={freq.value}>
                        {freq.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="condition_operator">Operator</Label>
                <Select name="condition_operator" defaultValue=">=">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {OPERATORS.map((op) => (
                      <SelectItem key={op.value} value={op.value}>
                        {op.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="col-span-2">
                <Label htmlFor="condition_value">Value</Label>
                <Input
                  id="condition_value"
                  name="condition_value"
                  type="number"
                  step="0.01"
                  placeholder="100.00"
                  required
                />
              </div>
            </div>

            <div>
              <Label>Notification Channels</Label>
              <div className="flex items-center gap-4 mt-2">
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="send_in_app" defaultChecked />
                  <span className="text-sm">In-App</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="send_push" defaultChecked />
                  <span className="text-sm">Push</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="send_email" />
                  <span className="text-sm">Email</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="send_sms" />
                  <span className="text-sm">SMS</span>
                </label>
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Creating...' : 'Create Alert'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={!!editingAlert} onOpenChange={() => setEditingAlert(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Alert</DialogTitle>
          </DialogHeader>
          {editingAlert && (
            <form onSubmit={handleUpdate} className="space-y-4">
              <div>
                <Label htmlFor="edit_name">Alert Name</Label>
                <Input
                  id="edit_name"
                  name="name"
                  defaultValue={editingAlert.name}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit_condition_operator">Operator</Label>
                  <Select
                    name="condition_operator"
                    defaultValue={editingAlert.condition_operator}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {OPERATORS.map((op) => (
                        <SelectItem key={op.value} value={op.value}>
                          {op.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="edit_condition_value">Value</Label>
                  <Input
                    id="edit_condition_value"
                    name="condition_value"
                    type="number"
                    step="0.01"
                    defaultValue={editingAlert.condition_value}
                    required
                  />
                </div>
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setEditingAlert(null)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Saving...' : 'Save Changes'}
                </Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
