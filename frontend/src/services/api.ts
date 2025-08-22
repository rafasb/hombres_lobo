import axios from 'axios'

// Centralized API client with Authorization interceptor
const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL
})

// Attach access token to every request. Prefer Pinia auth store token when available,
// otherwise fallback to localStorage. Wrapped in try/catch so this module can be imported
// before Pinia is initialized (safe fallback to localStorage).
api.interceptors.request.use((config) => {
  try {
    let token: string | null = null
    try {
      token = localStorage.getItem('access_token')
    } catch (e) {
      token = null
    }

    if (token) {
      config.headers = config.headers || {}
      ;(config.headers as Record<string, string>).Authorization = `Bearer ${token}`
    }
  } catch (e) {
    // ignore any unexpected errors in the interceptor
  }
  return config
})

export default api
