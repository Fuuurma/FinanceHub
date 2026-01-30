/**
 * API Types
 * Defines all API-related types and interfaces
 */

export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface ApiError {
  detail: string
  code?: string
}

export interface PaginationParams {
  page?: number
  limit?: number
  offset?: number
}

export interface PaginatedResponse<T> {
  count: number
  next?: string
  previous?: string
  results: T[]
}
