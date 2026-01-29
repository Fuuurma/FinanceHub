/**
 * Authentication API
 * All authentication-related API calls
 */

import { apiClient } from './client'
import type { LoginInput, RegisterInput, TokenPair, User, UpdateProfileInput, ChangePasswordInput } from '@/lib/types'

interface RegisterResponse {
  user: User
  message: string
}

interface RefreshResponse {
  access: string
}

interface LogoutResponse {
  message: string
}

interface ChangePasswordResponse {
  message: string
}

export const authApi = {
  register(data: RegisterInput): Promise<RegisterResponse> {
    return apiClient.post('/users/register/', data)
  },

  login(data: LoginInput): Promise<TokenPair> {
    return apiClient.post('/auth/login', data)
  },

  refreshToken(refresh: string): Promise<RefreshResponse> {
    return apiClient.post('/auth/refresh', { refresh })
  },

  logout(): Promise<LogoutResponse> {
    return apiClient.post('/auth/logout')
  },

  getMe(): Promise<User> {
    return apiClient.get('/auth/me')
  },

  updateProfile(data: UpdateProfileInput): Promise<User> {
    return apiClient.patch('/users/me', data)
  },

  changePassword(data: ChangePasswordInput): Promise<ChangePasswordResponse> {
    return apiClient.post('/users/me/change-password', data)
  },
}
