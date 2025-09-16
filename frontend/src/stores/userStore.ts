import { defineStore } from 'pinia'
import type { User } from '../types/user'
import { logoutEventBus } from './authStore'
import { useWebSocketStore } from '../composables/useWebSocketStore'

// Store para gestionar el estado del usuario y su conexión WebSocket
// El store se encarga de:
// - Mantener el perfil básico del usuario
// - Mantener el estado ligero de conexión (connected, disconnected, in_game, banned)
// - Gestionar errores y estados de carga relacionados con el usuario
// - Suscribirse a mensajes WebSocket relevantes para actualizar el estado del usuario en tiempo real

export const useUserStore = defineStore('user', {
  state: () => ({
    // perfil básico del usuario (null cuando no hay sesión)
    user: null as User | null,
    // estado ligero de conexión desde WS
    status: 'disconnected' as 'connected' | 'disconnected' | 'in_game' | 'banned',
    loading: false as boolean,
    error: null as string | null,
    // Estado adicional para gestión WebSocket
    isWebSocketConnected: false,
    lastStatusUpdate: null as Date | null,
  }),

  getters: {
    isConnected: (state) => state.status === 'connected' || state.status === 'in_game',
    isInGame: (state) => state.status === 'in_game',
    isBanned: (state) => state.status === 'banned',
    canJoinGame: (state) => state.status === 'connected' && !state.loading,
  },

  actions: {
    setUser(u: User | null) {
      this.user = u
    },
    
    setStatus(s: 'connected' | 'disconnected' | 'in_game' | 'banned') {
      const oldStatus = this.status
      this.status = s
      this.lastStatusUpdate = new Date()
      
      // Log cambios de estado para debugging
      if (oldStatus !== s) {
        console.log(`[UserStore] Estado cambiado de '${oldStatus}' a '${s}'`)
      }
    },
    
    setLoading(v: boolean) {
      this.loading = v
    },
    
    setError(msg: string | null) {
      this.error = msg
    },
    
    setWebSocketConnected(connected: boolean) {
      this.isWebSocketConnected = connected
    },
    
    clear() {
      this.user = null
      this.status = 'disconnected'
      this.loading = false
      this.error = null
      this.isWebSocketConnected = false
      this.lastStatusUpdate = null
    },

    /**
     * Inicializar suscripciones WebSocket para este store
     * Debe ser llamado después de que se establezca la conexión WebSocket
     */
    initializeWebSocketSubscriptions() {
      const { subscribeToMessage } = useWebSocketStore()

      // Suscribirse a cambios de estado del usuario
      subscribeToMessage('user_status_changed', (data) => {
        if (data && this.user && data.user_id === this.user.id) {
          console.log('[UserStore] Recibido cambio de estado:', data)
          this.setStatus(data.new_status as any)
        }
      })


      // Suscribirse a estado de conexión del usuario
      subscribeToMessage('user_connection_status', (data) => {
        if (data) {
          console.log('[UserStore] Recibido estado de conexión:', data)
          this.setWebSocketConnected(data.isConnected)
          
          // Si el usuario está en juego según WebSocket, actualizar estado local
          if (data.isInGame && this.status !== 'in_game') {
            this.setStatus('in_game')
          } else if (!data.isInGame && this.status === 'in_game') {
            this.setStatus('connected')
          }
        }
      })

      // NOTA: La funcionalidad de usuario baneado ahora se maneja 
      // a través del estado general del juego en lugar de mensajes específicos
      
      // Suscribirse a mensajes de error para manejar errores relacionados con el usuario
      subscribeToMessage('error', (data) => {
        if (data && data.error_code) {
          console.error('[UserStore] Error recibido:', data)
          
          // Manejar errores específicos del usuario
          switch (data.error_code) {
            case 'INVALID_USER':
            case 'USER_NOT_IN_GAME':
            case 'NOT_AUTHORIZED':
              this.setError(data.message || 'Error de autorización')
              break
            case 'STATUS_ERROR':
              this.setError(data.message || 'Error de estado de usuario')
              break
            default:
              // No manejar otros tipos de error aquí
              break
          }
        }
      })

      console.log('[UserStore] Suscripciones WebSocket inicializadas')
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
