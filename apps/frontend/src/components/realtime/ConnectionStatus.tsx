'use client'

import { Wifi, WifiOff, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useRealtimeStore } from '@/stores/realtimeStore'
import { getWebSocketClient } from '@/lib/api/websocket'
import { CONNECTION_STATES, CONNECTION_MESSAGES } from '@/lib/constants/realtime'
import type { ConnectionState as ConnectionStateType } from '@/lib/constants/realtime'

export function ConnectionStatus() {
  const { connectionState, error, connect } = useRealtimeStore()
  const wsClient = getWebSocketClient()

  const getStatusColor = (state: ConnectionStateType): string => {
    switch (state) {
      case CONNECTION_STATES.CONNECTED:
        return 'bg-green-500'
      case CONNECTION_STATES.CONNECTING:
        return 'bg-yellow-500'
      case CONNECTION_STATES.DISCONNECTED:
      case CONNECTION_STATES.ERROR:
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusIcon = () => {
    if (connectionState === CONNECTION_STATES.CONNECTED) {
      return <Wifi className="h-4 w-4" />
    } else if (connectionState === CONNECTION_STATES.CONNECTING) {
      return <RefreshCw className="h-4 w-4 animate-spin" />
    } else {
      return <WifiOff className="h-4 w-4" />
    }
  }

  const canReconnect = 
    connectionState === CONNECTION_STATES.DISCONNECTED || 
    connectionState === CONNECTION_STATES.ERROR

  const handleConnect = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || undefined : undefined
    connect(token)
  }

  return (
    <div className="flex items-center gap-3 p-4 border rounded-lg bg-background">
      <div className={`w-3 h-3 rounded-full ${getStatusColor(connectionState)}`} />
      
      <div className="flex items-center gap-2 flex-1">
        <div className="flex items-center gap-2 text-sm">
          {getStatusIcon()}
          <span className="font-medium">
            {CONNECTION_MESSAGES[connectionState]}
          </span>
        </div>

        {error && (
          <Badge variant="destructive" className="text-xs">
            {error}
          </Badge>
        )}

        {connectionState === CONNECTION_STATES.CONNECTED && (
          <span className="text-xs text-muted-foreground">
            Ping: {wsClient.getPingMs()}ms
          </span>
        )}
      </div>

      {canReconnect && (
        <Button
          size="sm"
          onClick={handleConnect}
          disabled={connectionState === 'connecting' as any}
          className="shrink-0"
        >
          <RefreshCw className={`h-4 w-4 ${connectionState === 'connecting' as any ? 'animate-spin' : ''}`} />
        </Button>
      )}
    </div>
  )
}
