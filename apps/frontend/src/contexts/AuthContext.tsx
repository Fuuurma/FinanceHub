'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'

interface AuthContextType {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface User {
  id: string
  username: string
  email: string
  first_name?: string
  last_name?: string
  full_name: string
  is_active: boolean
  is_staff: boolean
  date_joined: string
  roles: string[]
}

interface AuthContextValue extends AuthContextType {
  login: (username: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => Promise<void>
  refreshTokens: () => Promise<void>
  getMe: () => Promise<void | null | undefined>
  clearError: () => void
  setError: (error: string | null) => void
  checkAuthStatus: () => boolean
  updateUser: (data: any) => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user_data'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthContextType>({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
    error: null
  })

  const login = useCallback(async (username: string, password: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'Login failed')
      }

      const data = await response.json()

      if (data.access && data.refresh) {
        localStorage.setItem(TOKEN_KEY, data.access)
        localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh)
        localStorage.setItem(USER_KEY, JSON.stringify(data.user))
      }

      setState(prev => ({
        ...prev,
        user: data.user,
        token: data.access,
        refreshToken: data.refresh,
        isAuthenticated: true,
        isLoading: false,
        error: null
      }))
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed'
      }))
    }
  }, [])

  const register = useCallback(async (data: any) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await fetch('/api/v1/users/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'Registration failed')
      }

      const responseData = await response.json()

      if (responseData.access && responseData.refresh && responseData.user) {
        localStorage.setItem(TOKEN_KEY, responseData.access)
        localStorage.setItem(REFRESH_TOKEN_KEY, responseData.refresh)
        localStorage.setItem(USER_KEY, JSON.stringify(responseData.user))
      }

      setState(prev => ({
        ...prev,
        user: responseData.user,
        token: responseData.access,
        refreshToken: responseData.refresh,
        isAuthenticated: true,
        isLoading: false,
        error: null
      }))
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Registration failed'
      }))
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

      if (refreshToken) {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${refreshToken}`
          },
          body: JSON.stringify({ refreshToken })
        })
      }

      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      localStorage.removeItem(USER_KEY)

      setState(prev => ({
        ...prev,
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      }))
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Logout failed'
      }))
      return
    }
  }, [])

  const refreshTokens = useCallback(async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

    if (!refreshToken) {
      return
    }

    try {
      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshToken}`
        },
        body: JSON.stringify({ refreshToken })
      })

      if (!response.ok) {
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        throw new Error('Token refresh failed')
      }

      const data = await response.json()

      if (data.access && data.refresh) {
        localStorage.setItem(TOKEN_KEY, data.access)
        localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh)
      }

      setState(prev => ({
        ...prev,
        token: data.access,
        refreshToken: data.refresh,
        isAuthenticated: !!data.access,
        isLoading: false,
        error: null
      }))
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Token refresh failed'
      }))
    }
  }, [])

  const getMe = useCallback(async () => {
    const token = localStorage.getItem(TOKEN_KEY)

    if (!token) {
      return null
    }

    try {
      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch user data')
      }

      const data = await response.json()

      setState(prev => ({
        ...prev,
        user: data,
        token,
        isAuthenticated: !!data,
        isLoading: false,
        error: null
      }))
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch user data'
      }))
      return
    }
  }, [])

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }))
  }, [])

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error }))
  }, [])

  const updateUser = useCallback(async (data: any) => {
    try {
      const token = localStorage.getItem(TOKEN_KEY)
      const response = await fetch('/api/v1/users/me/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        throw new Error('Failed to update user')
      }

      const updatedUser = await response.json()
      setState(prev => ({ ...prev, user: updatedUser }))
      localStorage.setItem(USER_KEY, JSON.stringify(updatedUser))
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Update failed'
      }))
    }
  }, [])

  const checkAuthStatus = useCallback(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    const userData = localStorage.getItem(USER_KEY)
    return !!token && !!userData && JSON.parse(userData)
  }, [state.token, state.user])

  useEffect(() => {
    if (state.token) {
      const refreshTimer = setInterval(() => {
        refreshTokens()
      }, 14 * 60 * 1000)

      return () => {
        clearInterval(refreshTimer)
      }
    }
  }, [state.token, refreshTokens])

  return (
    <AuthContext.Provider value={{
      ...state,
      login,
      register,
      logout,
      refreshTokens,
      getMe,
      clearError,
      setError,
      checkAuthStatus,
      updateUser
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
