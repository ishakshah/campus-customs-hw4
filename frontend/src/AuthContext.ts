import { createContext, useContext } from 'react'
import type { RegisterInput, User } from './types'

export interface AuthState {
  user: User | null
  loading: boolean
  /** True when the signed-in shopper's password no longer meets the current rules and they should update it. */
  passwordUpdateRequired: boolean
  /** Resolves to true if the shopper should now be asked to update their password. */
  login: (email: string, password: string) => Promise<boolean>
  register: (input: RegisterInput) => Promise<void>
  logout: () => Promise<void>
  changePassword: (current: string, next: string, confirm: string) => Promise<void>
}

export const AuthContext = createContext<AuthState | null>(null)

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
