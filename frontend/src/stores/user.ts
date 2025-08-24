import { defineStore } from 'pinia'
import type { User } from '../types/user'
import { logoutEventBus } from './authStore'

export const useUserStore = defineStore('user', {
  state: () => ({
    // perfil básico del usuario (null cuando no hay sesión)
    user: null as User | null,
    // estado ligero de conexión desde WS
    status: 'disconnected' as 'connected' | 'disconnected' | 'in_game' | 'banned',
    loading: false as boolean,
    error: null as string | null,
  }),

  getters: {
    isConnected: (state) => state.status === 'connected' || state.status === 'in_game',
    isInGame: (state) => state.status === 'in_game',
  },

  actions: {
    setUser(u: User | null) {
      this.user = u
    },
    setStatus(s: 'connected' | 'disconnected' | 'in_game' | 'banned') {
      this.status = s
    },
    setLoading(v: boolean) {
      this.loading = v
    },
    setError(msg: string | null) {
      this.error = msg
    },
    clear() {
      this.user = null
      this.status = 'disconnected'
      this.loading = false
      this.error = null
    }
  }
})

// limpiar store al hacer logout global
logoutEventBus.on(() => {
  try {
    const s = useUserStore()
    s.clear()
  } catch (e) {
    // Ignorar si se ejecuta fuera de contexto de Pinia (tests/u otro runtime)
  }
})

export default useUserStore
