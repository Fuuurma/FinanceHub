/**
 * Custom React Hooks for Authentication
 * Provides convenient authentication operations
 */
import { useCallback } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import type { LoginInput, RegisterInput, UpdateProfileInput } from '@/lib/types'

export function useLogin() {
  const { login } = useAuth()
  
  return useCallback(async (credentials: LoginInput) => {
    await login(credentials.username, credentials.password)
  }, [login])
}

export function useRegister() {
  const { register } = useAuth()
  
  return useCallback(async (data: RegisterInput) => {
    await register(data)
  }, [register])
}

export function useLogout() {
  const { logout } = useAuth()
  
  return useCallback(async () => {
    await logout()
  }, [logout])
}

export function useAuthCheck() {
  const { checkAuthStatus } = useAuth()
  
  return useCallback(() => {
    return checkAuthStatus()
  }, [checkAuthStatus])
}

export function useCurrentUser() {
  const { user } = useAuth()
  return user
}

export function useIsAuthenticated() {
  const { isAuthenticated } = useAuth()
  return isAuthenticated
}

export function useAuthLoading() {
  const { isLoading, error } = useAuth()
  return { isLoading, error }
}

export function useUpdateProfile() {
  const { updateUser } = useAuth()
  
  return useCallback(async (data: UpdateProfileInput) => {
    await updateUser(data)
  }, [updateUser])
}

export function useRefreshToken() {
  const { refreshTokens } = useAuth()
  
  return useCallback(async () => {
    await refreshTokens()
  }, [refreshTokens])
}

export function useClearAuthError() {
  const { clearError } = useAuth()
  
  return useCallback(() => {
    clearError()
  }, [clearError])
}
