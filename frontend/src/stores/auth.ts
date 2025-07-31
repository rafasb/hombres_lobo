import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

interface User {
  id: number
  username: string
  email: string
  role?: 'admin' | 'player'  // Añadimos role como opcional por si no viene del backend
}

interface LoginCredentials {
  username: string
  password: string
}

interface RegisterData {
  username: string
  email: string
  password: string
}

interface AuthResponse {
  access_token: string
  user: User
}

export const useAuthStore = defineStore('auth', () => {
  // Estado reactivo
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const isLoading = ref(false)
  const error = ref<string>('')
  const isInitialized = ref(false)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Inicialización automática
  const initialize = async () => {
    if (isInitialized.value) return

    if (token.value) {
      await checkAuth()
    }
    isInitialized.value = true
  }

  // Verificar si el token está próximo a expirar
  const isTokenExpiringSoon = () => {
    if (!token.value) return false

    try {
      // Decodificar el token para obtener la fecha de expiración
      const payload = JSON.parse(atob(token.value.split('.')[1]))
      const exp = payload.exp * 1000 // Convertir a millisegundos
      const now = Date.now()
      const timeUntilExpiry = exp - now

      // Si queda menos de 30 minutos, considerar que está expirando pronto
      return timeUntilExpiry < (30 * 60 * 1000)
    } catch {
      return true // Si no se puede decodificar, asumir que está expirado
    }
  }

  // Acciones
  const login = async (credentials: LoginCredentials) => {
    try {
      isLoading.value = true
      error.value = ''

      // Crear FormData para el backend
      const formData = new FormData()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)

      const response = await api.post<{ access_token: string; token_type: string }>('/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      })

      const { access_token } = response.data

      token.value = access_token
      localStorage.setItem('access_token', access_token)

      // Obtener datos del usuario después del login
      await checkAuth()

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error de autenticación'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const register = async (data: RegisterData) => {
    try {
      isLoading.value = true
      error.value = ''

      // Crear FormData para el backend
      const formData = new FormData()
      formData.append('username', data.username)
      formData.append('email', data.email)
      formData.append('password', data.password)

      const response = await api.post<User>('/register', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      })

      user.value = response.data

      // Hacer login automático después del registro
      return await login({ username: data.username, password: data.password })
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error de registro'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    // Redirigir a login si es necesario
  }

  const checkAuth = async () => {
    if (token.value) {
      try {
        const response = await api.get<User>('/users/me')
        user.value = response.data
        return true
      } catch (err) {
        logout()
        return false
      }
    }
    return false
  }

  return {
    // Estado
    user,
    token,
    isLoading,
    error,
    isInitialized,
    // Computed
    isAuthenticated,
    // Acciones
    login,
    register,
    logout,
    checkAuth,
    initialize,
    isTokenExpiringSoon
  }
})
