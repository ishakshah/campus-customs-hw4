import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { getCurrentUser, logIn, logOut, registerAccount, updatePassword } from './api'
import type { AuthReply } from './api'
import { AuthContext } from './AuthContext'
import type { AuthState } from './AuthContext'
import type { User } from './types'

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [passwordUpdateRequired, setPasswordUpdateRequired] = useState(false)
  const [loading, setLoading] = useState(true)

  const apply = useCallback((reply: AuthReply) => {
    setUser(reply.user)
    setPasswordUpdateRequired(reply.password_update_required)
  }, [])

  // The session lives in an httpOnly cookie, so ask the server who is signed in.
  useEffect(() => {
    getCurrentUser()
      .then(apply)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [apply])

  const login = useCallback<AuthState['login']>(
    async (email, password) => {
      const reply = await logIn(email, password)
      apply(reply)
      return reply.password_update_required
    },
    [apply],
  )

  const register = useCallback<AuthState['register']>(
    async (input) => {
      apply(await registerAccount(input))
    },
    [apply],
  )

  const logout = useCallback<AuthState['logout']>(async () => {
    await logOut()
    setUser(null)
    setPasswordUpdateRequired(false)
  }, [])

  const changePassword = useCallback<AuthState['changePassword']>(
    async (current, next, confirm) => {
      apply(await updatePassword(current, next, confirm))
    },
    [apply],
  )

  const value = useMemo(
    () => ({ user, loading, passwordUpdateRequired, login, register, logout, changePassword }),
    [user, loading, passwordUpdateRequired, login, register, logout, changePassword],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
