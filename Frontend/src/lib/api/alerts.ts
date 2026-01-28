/**
 * Alerts API
 * All alert-related API calls
 */

import { apiClient } from './client'
import type { Alert, AlertHistoryItem, AlertStats } from '../types'

export const alertsApi = {
  /**
   * List user's alerts with optional filters
   */
  list: (params?: {
    status?: string
    symbol?: string
    alert_type?: string
    limit?: number
    offset?: number
  }) => Promise<Alert[]> =>
    apiClient.get('/alerts/', { params: { limit: 50, offset: 0, ...params } }),

  /**
   * Get alert details by ID
   */
  get: (id: string) => Promise<Alert> =>
    apiClient.get(`/alerts/${id}`),

  /**
   * Create a new alert
   */
  create: (data: {
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
  }) => Promise<{ id: string; message: string }> =>
    apiClient.post('/alerts/', data),

  /**
   * Update an existing alert
   */
  update: (
    id: string,
    data: {
      name?: string
      condition_value?: number
      condition_operator?: string
      delivery_channels?: string[]
      priority?: number
      cooldown_seconds?: number
      valid_until?: string
      description?: string
    }
  ) => Promise<Alert> =>
    apiClient.put(`/alerts/${id}`, data),

  /**
   * Delete an alert
   */
  delete: (id: string) => Promise<{ message: string }> =>
    apiClient.delete(`/alerts/${id}`),

  /**
   * Enable an alert
   */
  enable: (id: string) => Promise<Alert> =>
    apiClient.post(`/alerts/${id}/enable`, {}),

  /**
   * Disable an alert
   */
  disable: (id: string) => Promise<Alert> =>
    apiClient.post(`/alerts/${id}/disable`, {}),

  /**
   * Get alert history
   */
  getHistory: (alertId: string, limit: number = 20) => Promise<AlertHistoryItem[]> =>
    apiClient.get(`/alerts/${alertId}/history`, { params: { limit } }),

  /**
   * Get alert statistics
   */
  getStats: () => Promise<AlertStats> =>
    apiClient.get('/alerts/stats'),

  /**
   * Test an alert (trigger without saving)
   */
  test: (id: string) => Promise<{ success: boolean; message: string; trigger_value?: number }> =>
    apiClient.post(`/alerts/${id}/test`, {}),
}
