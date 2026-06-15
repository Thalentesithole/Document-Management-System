import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import api from '@/services/api'

interface User {
  id: string
  email: string
  full_name?: string
  role: string
  is_active: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => void
  updateProfile: (fullName?: string, password?: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchMe = async () => {
    try {
      const response = await api.get('/auth/me')
      const userData = response.data
      localStorage.setItem('user', JSON.stringify(userData))
      setUser(userData)
    } catch {
      logout()
    }
  }

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')
    if (token) {
      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser))
        } catch {
          // ignore
        }
      }
      fetchMe().finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    // Backend expects OAuth2 form data
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })

    const { access_token } = response.data
    localStorage.setItem('access_token', access_token)
    
    // Fetch profile to get roles and id
    const meRes = await api.get('/auth/me')
    const userData = meRes.data
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }

  const register = async (email: string, password: string, fullName: string) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    })

    const { access_token } = response.data
    localStorage.setItem('access_token', access_token)
    
    // Fetch profile to get roles and id
    const meRes = await api.get('/auth/me')
    const userData = meRes.data
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setUser(null)
  }

  const updateProfile = async (fullName?: string, password?: string) => {
    const response = await api.post('/auth/update-profile', {
      full_name: fullName,
      password: password || undefined,
    })
    const userData = response.data
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateProfile }}>
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

