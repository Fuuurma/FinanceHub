/**
 * React Hooks for Authentication
 * Tailwind CSS and Radix UI
 */

import { useCallback } from 'react'
import { useAuth as useAuthContext } from '@/contexts/AuthContext'

interface LoginInput {
  username: string
  password: string
}

interface RegisterInput {
  username: string
  email: string
  password: string
  password_confirm: string
}

export function useLogin() {
  const { login, clearError } = useAuthContext()

  return useCallback(async (credentials: LoginInput) => {
    clearError()

    try {
      await login(credentials.username, credentials.password)
    } catch (error) {
      throw error
    }
  }, [login, clearError])
}

export function useRegister() {
  const { register, clearError } = useAuthContext()

  return useCallback(async (data: RegisterInput) => {
    clearError()

    try {
      await register(data)
    } catch (error) {
      throw error
    }
  }, [register, clearError])
}

export function useLogout() {
  const { logout } = useAuthContext()

  return useCallback(async () => {
    try {
      await logout()
    } catch (error) {
      throw error
    }
  }, [logout])
}

export function useAuthCheck() {
  const { checkAuthStatus } = useAuthContext()
  return checkAuthStatus()
}

export function useCurrentUser() {
  const { user } = useAuthContext()
  return user
}

export function useIsAuthenticated() {
  const { isAuthenticated } = useAuthContext()
  return isAuthenticated
}

export function useAuthLoading() {
  const { isLoading, error } = useAuthContext()
  return isLoading || error !== null
}

export function useAuthError() {
  const { error } = useAuthContext()
  return error
}

export function useAuth() {
  const context = useAuthContext()
  return {
    ...context,
    login: context.login,
    register: context.register,
    logout: context.logout,
    checkAuthStatus: context.checkAuthStatus,
    refreshTokens: context.refreshTokens,
    updateUser: context.updateUser,
  }
}

export function useUpdateProfile() {
  const { updateUser } = useAuthContext()

  return useCallback(async (data: any) => {
    try {
      await updateUser(data)
    } catch (error) {
      throw error
    }
  }, [updateUser])
}

export function useRefreshToken() {
  const { refreshTokens } = useAuthContext()

  return useCallback(() => {
    refreshTokens()
  }, [refreshTokens])
}
