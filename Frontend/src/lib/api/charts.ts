import { apiClient } from './client'

export interface ChartDataPoint {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface ChartDrawing {
  id: string
  user: string
  symbol: string
  timeframe: string
  drawing_type: 'horizontal_line' | 'vertical_line' | 'trend_line' | 'fibonacci' | 'rectangle' | 'text'
  coordinates: Record<string, any>
  parameters?: Record<string, any>
  color: string
  is_visible: boolean
  created_at: string
  updated_at: string
}

export interface TechnicalIndicatorValue {
  id: string
  symbol: string
  timeframe: string
  indicator_type: string
  timestamp: string
  value: number
  signal?: string
  additional_data?: Record<string, any>
}

export interface ChartDrawingManager {
  id: string
  user: string
  name: string
  description?: string
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface DrawingCreateInput {
  symbol: string
  timeframe: string
  drawing_type: 'horizontal_line' | 'vertical_line' | 'trend_line' | 'fibonacci' | 'rectangle' | 'text'
  coordinates: Record<string, any>
  parameters?: Record<string, any>
  color: string
}

export interface DrawingUpdateInput {
  coordinates?: Record<string, any>
  parameters?: Record<string, any>
  color?: string
  is_visible?: boolean
}

class ChartsApi {
  async getHistoricalData(
    symbol: string,
    timeframe: string = '1h',
    limit: number = 100
  ): Promise<ChartDataPoint[]> {
    const params = new URLSearchParams()
    params.append('timeframe', timeframe)
    params.append('limit', limit.toString())
    
    const response = await apiClient.get<ChartDataPoint[]>(
      `/charts/historical/${symbol}?${params.toString()}`
    )
    return response
  }

  async listDrawings(symbol: string, timeframe?: string): Promise<ChartDrawing[]> {
    const params = new URLSearchParams()
    if (timeframe) params.append('timeframe', timeframe)
    
    const response = await apiClient.get<ChartDrawing[]>(
      `/charts/drawings/${symbol}?${params.toString()}`
    )
    return response
  }

  async getDrawing(id: string): Promise<ChartDrawing> {
    return apiClient.get<ChartDrawing>(`/charts/drawings/by-id/${id}`)
  }

  async createDrawing(data: DrawingCreateInput): Promise<ChartDrawing> {
    return apiClient.post<ChartDrawing>(`/charts/drawings/${data.symbol}`, data)
  }

  async updateDrawing(id: string, data: DrawingUpdateInput): Promise<ChartDrawing> {
    return apiClient.put<ChartDrawing>(`/charts/drawings/by-id/${id}`, data)
  }

  async deleteDrawing(id: string): Promise<void> {
    return apiClient.delete<void>(`/charts/drawings/by-id/${id}`)
  }

  async getIndicatorValues(
    symbol: string,
    indicatorType: string,
    timeframe?: string,
    limit?: number
  ): Promise<TechnicalIndicatorValue[]> {
    const params = new URLSearchParams()
    if (timeframe) params.append('timeframe', timeframe)
    if (limit) params.append('limit', limit.toString())
    
    const response = await apiClient.get<TechnicalIndicatorValue[]>(
      `/charts/indicators/${symbol}/${indicatorType}?${params.toString()}`
    )
    return response
  }

  async listLayouts(): Promise<ChartDrawingManager[]> {
    return apiClient.get<ChartDrawingManager[]>('/charts/layouts')
  }

  async getLayout(id: string): Promise<ChartDrawingManager> {
    return apiClient.get<ChartDrawingManager>(`/charts/layouts/${id}`)
  }

  async createLayout(data: { name: string; description?: string }): Promise<ChartDrawingManager> {
    return apiClient.post<ChartDrawingManager>('/charts/layouts', data)
  }

  async updateLayout(
    id: string,
    data: { name?: string; description?: string; is_default?: boolean }
  ): Promise<ChartDrawingManager> {
    return apiClient.put<ChartDrawingManager>(`/charts/layouts/${id}`, data)
  }

  async deleteLayout(id: string): Promise<void> {
    return apiClient.delete<void>(`/charts/layouts/${id}`)
  }
}

export const chartsApi = new ChartsApi()
