/**
 * API Client
 * Centralized HTTP client with interceptors and error handling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

interface ApiOptions extends RequestInit {
  headers?: Record<string, string>
  params?: Record<string, string | number>
}

class ApiClient {
  readonly baseUrl: string
  readonly defaultHeaders: Record<string, string>

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    }
  }

  private getAuthHeaders(): Record<string, string> {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token) {
        return {
          Authorization: `Bearer ${token}`,
        }
      }
    }
    return {}
  }

  private buildUrl(endpoint: string, params?: Record<string, string | number>): string {
    const url = new URL(`${this.baseUrl}${endpoint}`)
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.set(key, String(value))
      })
    }
    
    return url.toString()
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type')
    
    if (!response.ok) {
      let errorMessage = 'An error occurred'
      
      if (contentType?.includes('application/json')) {
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch (e) {
        }
      }
      
      throw new ApiError(
        errorMessage,
        response.status,
        response.headers.get('x-error-code') || undefined
      )
    }
    
    if (contentType?.includes('application/json')) {
      return response.json()
    }
    
    return response.text() as unknown as T
  }

  async request<T>(
    method: HttpMethod,
    endpoint: string,
    options: ApiOptions = {}
  ): Promise<T> {
    const { headers, params, body, ...rest } = options
    
    const url = this.buildUrl(endpoint, params)
    const config: RequestInit = {
      method,
      headers: {
        ...this.defaultHeaders,
        ...this.getAuthHeaders(),
        ...headers,
      },
      ...rest,
    }
    
    if (body) {
      config.body = JSON.stringify(body)
    }
    
    try {
      const response = await fetch(url, config)
      return await this.handleResponse<T>(response)
    } catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      
      console.error('API request failed:', error)
      throw new ApiError(
        'Network error occurred',
        0,
        'NETWORK_ERROR'
      )
    }
  }

  async get<T>(endpoint: string, options?: ApiOptions): Promise<T> {
    return this.request<T>('GET', endpoint, options)
  }

  async post<T>(endpoint: string, data?: any, options?: ApiOptions): Promise<T> {
    return this.request<T>('POST', endpoint, { ...options, body: data })
  }

  async put<T>(endpoint: string, data?: any, options?: ApiOptions): Promise<T> {
    return this.request<T>('PUT', endpoint, { ...options, body: data })
  }

  async patch<T>(endpoint: string, data?: any, options?: ApiOptions): Promise<T> {
    return this.request<T>('PATCH', endpoint, { ...options, body: data })
  }

  async delete<T>(endpoint: string, options?: ApiOptions): Promise<T> {
    return this.request<T>('DELETE', endpoint, options)
  }

  setAuthToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token)
    }
  }

  clearAuthToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
    }
  }

  getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token')
    }
    return null
  }

  setRefreshToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', token)
    }
  }

  getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token')
    }
    return null
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_BASE_URL)

export { ApiError }
