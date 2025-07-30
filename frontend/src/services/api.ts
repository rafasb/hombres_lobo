import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'

// Configuración base de Axios
const api: AxiosInstance = axios.create({
  baseURL: '/api', // Usa el proxy configurado en Vite
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para requests (agregar token JWT si existe)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para responses (manejo de errores)
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido, limpiar localStorage y redirigir a login
      localStorage.removeItem('access_token')

      // Evitar redirección infinita si ya estamos en login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Funciones de utilidad
export const apiService = {
  get: <T>(url: string) => api.get<T>(url),
  post: <T>(url: string, data?: any) => api.post<T>(url, data),
  put: <T>(url: string, data?: any) => api.put<T>(url, data),
  delete: <T>(url: string) => api.delete<T>(url),
}

export default api
