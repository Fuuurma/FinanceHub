/**
 * User Types
 * Defines all user-related types and interfaces
 */

export interface User {
  id: string
  username: string
  email: string
  first_name?: string
  last_name?: string
  full_name: string
  is_active: boolean
  is_staff: boolean
  date_joined: Date
  roles: string[]
}

export interface RegisterInput {
  username: string
  email: string
  password: string
  first_name?: string
  last_name?: string
}

export interface LoginInput {
  username: string
  password: string
}

export interface TokenPair {
  access: string
  refresh: string
}

export interface UpdateProfileInput {
  first_name?: string
  last_name?: string
}

export interface ChangePasswordInput {
  current_password: string
  new_password: string
  confirm_new_password: string
}
