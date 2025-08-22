import { defineStore } from 'pinia'
import { getProfile } from '../services/authService'
import api from '../services/api'
import type { AuthUser } from '../types'

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
    user: null as AuthUser | null,
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
    setUser(user: AuthUser) {
      this.user = user
    },
  async logout() {
      // Emitir evento antes de limpiar los datos
      logoutEventBus.emit()

      // Informar a la API que el usuario está desconectado
      if (this.user && this.token) {
        try {
          // use centralized api client so Authorization header is handled in one place
          await api.put(`/users/${this.user.id}/status`, { status: 'disconnected' })
        } catch (e) {
          // No bloquear el logout si falla
          console.error('No se pudo actualizar el estado del usuario a disconnected', e)
        }
      }

      this.token = ''
      this.user = null
      localStorage.removeItem('access_token')
    },
    async loadUserFromToken() {
      if (this.token && !this.user) {
        this.loadingUser = true
        const profile = await getProfile()
        if (profile && profile.user) {
          // Hacer casting del usuario para asegurar que el role sea del tipo correcto
          this.setUser({
            id: profile.user.id,
            username: profile.user.username,
            role: profile.user.role as 'admin' | 'player'
          })
        } else {
          this.logout()
        }
        this.loadingUser = false
      }
    }
  }
})
