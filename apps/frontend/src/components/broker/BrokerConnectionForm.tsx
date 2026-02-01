'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { AlertTriangle, Shield, Key, Building2 } from 'lucide-react'

interface Broker {
  id: string
  name: string
  logo?: string
  description: string
}

interface BrokerConnectionFormProps {
  brokers: Broker[]
  onConnect: (brokerId: string, apiKey: string, apiSecret: string, isTest: boolean) => Promise<void>
  className?: string
}

export function BrokerConnectionForm({ brokers, onConnect, className }: BrokerConnectionFormProps) {
  const [selectedBroker, setSelectedBroker] = React.useState<string | null>(null)
  const [apiKey, setApiKey] = React.useState('')
  const [apiSecret, setApiSecret] = React.useState('')
  const [isTestAccount, setIsTestAccount] = React.useState(true)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const handleConnect = async () => {
    if (!selectedBroker || !apiKey || !apiSecret) {
      setError('Please fill in all fields')
      return
    }

    setError(null)
    setLoading(true)

    try {
      await onConnect(selectedBroker, apiKey, apiSecret, isTestAccount)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className={cn('rounded-none border-2', className)}>
      <CardHeader className="border-b-2">
        <CardTitle className="font-black uppercase flex items-center gap-2">
          <Building2 className="h-5 w-5" aria-hidden="true" />
          Connect Broker
        </CardTitle>
        <CardDescription>
          Link your brokerage account to execute real trades
        </CardDescription>
      </CardHeader>
      <CardContent className="p-6 space-y-6">
        <div>
          <Label className="text-xs font-bold uppercase mb-3 block">
            Select Broker
          </Label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3" role="listbox" aria-label="Available brokers">
            {brokers.map((broker) => (
              <button
                key={broker.id}
                type="button"
                onClick={() => setSelectedBroker(broker.id)}
                className={cn(
                  'p-4 border-2 rounded-none text-left transition-all',
                  selectedBroker === broker.id
                    ? 'border-foreground bg-foreground text-background'
                    : 'border-border hover:border-foreground/50'
                )}
                role="option"
                aria-selected={selectedBroker === broker.id}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Building2 className="h-4 w-4" aria-hidden="true" />
                  <span className="font-black uppercase text-sm">{broker.name}</span>
                </div>
                <p className={cn(
                  'text-xs',
                  selectedBroker === broker.id ? 'text-background/70' : 'text-muted-foreground'
                )}>
                  {broker.description}
                </p>
              </button>
            ))}
          </div>
        </div>

        {selectedBroker && (
          <div className="space-y-4 border-t-2 pt-6">
            <div>
              <Label htmlFor="api-key" className="text-xs font-bold uppercase mb-2 flex items-center gap-2">
                <Key className="h-3 w-3" aria-hidden="true" />
                API Key
              </Label>
              <Input
                id="api-key"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your API key"
                className="rounded-none border-2 font-mono"
                aria-describedby="api-key-hint"
              />
            </div>

            <div>
              <Label htmlFor="api-secret" className="text-xs font-bold uppercase mb-2 flex items-center gap-2">
                <Key className="h-3 w-3" aria-hidden="true" />
                API Secret
              </Label>
              <Input
                id="api-secret"
                type="password"
                value={apiSecret}
                onChange={(e) => setApiSecret(e.target.value)}
                placeholder="Enter your API secret"
                className="rounded-none border-2 font-mono"
                aria-describedby="api-secret-hint"
              />
            </div>

            <div className="flex flex-col gap-3 pt-2">
              <label className="flex items-center gap-3 cursor-pointer">
                <Checkbox
                  checked={isTestAccount}
                  onCheckedChange={(checked) => setIsTestAccount(checked as boolean)}
                  id="test-account"
                  className="rounded-none border-2"
                />
                <span className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-success" aria-hidden="true" />
                  <span className="text-sm font-medium">Test Account</span>
                </span>
                <Badge variant="outline" className="rounded-none text-xs font-mono ml-auto">
                  Recommended
                </Badge>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <Checkbox
                  checked={!isTestAccount}
                  onCheckedChange={(checked) => setIsTestAccount(!(checked as boolean))}
                  id="live-account"
                  className="rounded-none border-2"
                />
                <span className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-destructive" aria-hidden="true" />
                  <span className="text-sm font-medium">Live Account</span>
                </span>
                <Badge variant="destructive" className="rounded-none text-xs font-mono ml-auto">
                  Real Money
                </Badge>
              </label>
            </div>

            {error && (
              <div className="bg-destructive/10 border border-destructive p-3">
                <p className="text-destructive text-sm font-medium">{error}</p>
              </div>
            )}

            <Button
              onClick={handleConnect}
              disabled={loading || !apiKey || !apiSecret}
              className={cn(
                'w-full font-black uppercase rounded-none',
                isTestAccount ? 'bg-primary hover:bg-primary/90' : 'bg-destructive hover:bg-destructive/90'
              )}
            >
              {loading ? (
                <>Connecting...</>
              ) : (
                <>
                  {isTestAccount ? (
                    <>Connect Test Account</>
                  ) : (
                    <>
                      <AlertTriangle className="h-4 w-4 mr-2" aria-hidden="true" />
                      Connect Live Account
                    </>
                  )}
                </>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
