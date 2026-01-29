/**
 * Alerts API
 * All alert-related API calls
 */

import { apiClient } from './client'
import type { Alert, AlertHistoryItem, AlertStats } from '@/lib/types'

interface ListParams {
  status?: string
  symbol?: string
  alert_type?: string
  limit?: number
  offset?: number
}

interface CreateParams {
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

interface UpdateParams {
  name?: string
  condition_value?: number
  condition_operator?: string
  delivery_channels?: string[]
  priority?: number
  cooldown_seconds?: number
  valid_until?: string
  description?: string
}

export const alertsApi = {
  list(params?: ListParams): Promise<Alert[]> {
    return apiClient.get('/alerts/', { params: { limit: 50, offset: 0, ...params } })
  },

  get(id: string): Promise<Alert> {
    return apiClient.get(`/alerts/${id}`)
  },

  create(data: CreateParams): Promise<{ id: string; message: string }> {
    return apiClient.post('/alerts/', data)
  },

  update(id: string, data: UpdateParams): Promise<Alert> {
    return apiClient.put(`/alerts/${id}`, data)
  },

  delete(id: string): Promise<{ message: string }> {
    return apiClient.delete(`/alerts/${id}`)
  },

  enable(id: string): Promise<Alert> {
    return apiClient.post(`/alerts/${id}/enable`, {})
  },

  disable(id: string): Promise<Alert> {
    return apiClient.post(`/alerts/${id}/disable`, {})
  },

  getHistory(alertId: string, limit: number = 20): Promise<AlertHistoryItem[]> {
    return apiClient.get(`/alerts/${alertId}/history`, { params: { limit } })
  },

  getStats(): Promise<AlertStats> {
    return apiClient.get('/alerts/stats')
  },

  test(id: string): Promise<{ success: boolean; message: string; trigger_value?: number }> {
    return apiClient.post(`/alerts/${id}/test`, {})
  },
}
