/**
 * Alert Types
 */

export interface PriceAlert {
  id: string
  name: string
  alert_type: string
  symbol: string
  condition_value: number
  condition_operator: string
  status: string
  priority: number
  triggered_count: number
  delivery_channels: string[]
  cooldown_seconds: number
  valid_from: string
  valid_until: string | null
  created_at: string
  last_triggered_at: string | null
}

export type Alert = PriceAlert

export interface AlertHistoryItem {
  id: string
  triggered_at: string
  trigger_value: number
  condition_met: boolean
  notification_sent: boolean
  notification_channels: string[]
}

export interface AlertStats {
  total_alerts: number
  active_alerts: number
  triggered_today: number
  type_distribution: {
    [key: string]: number
  }
}

export interface AlertCreateInput {
  name: string
  alert_type: string
  symbol: string
  condition_value: number
  condition_operator?: string
  delivery_channels?: string[]
  priority?: number
  cooldown_seconds?: number
  valid_until?: string
  description?: string
}

export interface AlertUpdateInput {
  name?: string
  condition_value?: number
  condition_operator?: string
  delivery_channels?: string[]
  priority?: number
  cooldown_seconds?: number
  valid_until?: string
  description?: string
}
