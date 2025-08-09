import { defineStore } from 'pinia'
import { getProfile } from '../services/authService'

interface User {
  id: string
  username: string
  role: string
}

// Event bus simple para comunicar logout
export const logoutEventBus = {
  listeners: [] as (() => void)[],
  emit() {
    this.listeners.forEach(callback => callback())
  },
  on(callback: () => void) {
    this.listeners.push(callback)
    // Devolver función para remover el listener
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback)
    }
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    user: null as User | null,
    loadingUser: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
  },
  actions: {
    setToken(token: string) {
      this.token = token
      localStorage.setItem('access_token', token)
    },
    setUser(user: User) {
      this.user = user
    },
    logout() {
      // Emitir evento antes de limpiar los datos
      logoutEventBus.emit()
      
      this.token = ''
      this.user = null
      localStorage.removeItem('access_token')
    },
    async loadUserFromToken() {
      if (this.token && !this.user) {
        this.loadingUser = true
        const profile = await getProfile()
        if (profile && profile.user) {
          this.setUser(profile.user)
        } else {
          this.logout()
        }
        this.loadingUser = false
      }
    }
  }
})
