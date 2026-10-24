import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadMe = async () => {
    const token = localStorage.getItem('agristack_access')
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const { data } = await api.get('/users/me')
      setUser(data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMe()
  }, [])

  const persistTokens = (data) => {
    localStorage.setItem('agristack_access', data.access_token)
    localStorage.setItem('agristack_refresh', data.refresh_token)
  }

  const login = async (email_or_phone, password) => {
    const { data } = await api.post('/auth/login', { email_or_phone, password })
    if (data.mfa_required) return data
    persistTokens(data)
    await loadMe()
    return data
  }

  const register = async (payload) => {
    const { data } = await api.post('/auth/register', payload)
    persistTokens(data)
    await loadMe()
    return data
  }

  const logout = () => {
    localStorage.removeItem('agristack_access')
    localStorage.removeItem('agristack_refresh')
    setUser(null)
  }

  const value = useMemo(() => ({ user, loading, login, register, logout, reload: loadMe }), [user, loading])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
