/**
 * React Hooks for Authentication
 * Tailwind CSS and Radix UI
 */
'use client'

import { useCallback } from 'react'
import { useAuth as useAuthContext } from '@/contexts/AuthContext'
import type { LoginInput, RegisterInput } from '@/lib/types'

export function useLogin() {
  const { login, setIsLoading, clearError } = useAuthContext()

  return useCallback(async (credentials: LoginInput) => {
    clearError()
    setIsLoading(true)

    try {
      await login(credentials.username, credentials.password)
    } catch (error) {
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [login, setIsLoading, clearError])
}

export function useRegister() {
  const { register, setIsLoading, clearError } = useAuthContext()

  return useCallback(async (data: RegisterInput) => {
    clearError()
    setIsLoading(true)

    try {
      await register(data)
    } catch (error) {
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [register, setIsLoading, clearError])
}

export function useLogout() {
  const { logout, setError } = useAuthContext()

  return useCallback(async () => {
    setError(null)

    try {
      await logout()
    } catch (error) {
      throw error
    }
  }, [logout, setError])
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
