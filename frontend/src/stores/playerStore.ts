import { defineStore } from 'pinia'
import type { PlayerInfo, Roles } from '../types/game'
import { logoutEventBus } from './authStore'
import { useWebSocketStore } from '../composables/useWebSocketStore'

// Store para gestionar la información privada del jugador actual
// El store se encarga de:
// - Mantener la información completa y privada del jugador actual (rol, habilidades, etc.)
// - Gestionar errores y estados de carga relacionados con el jugador actual
// - Suscribirse a mensajes WebSocket relevantes para actualizar la información privada del jugador
// 
// NOTA: La información pública de todos los jugadores está en GameStore

export const usePlayerStore = defineStore('player', {
  state: () => ({
    // Información privada del jugador actual
    currentPlayer: null as PlayerInfo | null,
    loading: false,
    error: null as string | null,
    lastUpdate: null as Date | null,
  }),

  getters: {
    // Información del jugador actual
    hasPlayer: (state) => state.currentPlayer !== null,
    isAlive: (state) => state.currentPlayer?.is_alive ?? false,
    role: (state) => state.currentPlayer?.role,
    playerId: (state) => state.currentPlayer?.player_id,
    
    // Habilidades específicas por rol
    hasHealingPotion: (state) => state.currentPlayer?.has_healing_potion ?? false,
    hasPoisonPotion: (state) => state.currentPlayer?.has_poison_potion ?? false,
    hasActedTonight: (state) => state.currentPlayer?.has_acted_tonight ?? false,
    canRevengeKill: (state) => state.currentPlayer?.can_revenge_kill ?? false,
    hasDoubleVote: (state) => state.currentPlayer?.has_double_vote ?? false,
    canBreakTies: (state) => state.currentPlayer?.can_break_ties ?? false,
    
    // Estados especiales
    loverPartnerId: (state) => state.currentPlayer?.lover_partner_id,
    modelPlayerId: (state) => state.currentPlayer?.model_player_id,
    hasTransformed: (state) => state.currentPlayer?.has_transformed ?? false,
  },

  actions: {
    setCurrentPlayer(player: PlayerInfo) {
      this.currentPlayer = player
      this.lastUpdate = new Date()
    },

    updatePlayer(partial: Partial<PlayerInfo>) {
      if (this.currentPlayer) {
        this.currentPlayer = { ...this.currentPlayer, ...partial }
        this.lastUpdate = new Date()
      }
    },
    
    updateRole(role: Roles) {
      if (this.currentPlayer) {
        this.currentPlayer.role = role
        this.lastUpdate = new Date()
      }
    },
    
    updateStatus(isAlive: boolean) {
      if (this.currentPlayer) {
        this.currentPlayer.is_alive = isAlive
        this.lastUpdate = new Date()
      }
    },
    
    // Acciones específicas por rol
    useHealingPotion() {
      if (this.currentPlayer) {
        this.currentPlayer.has_healing_potion = false
        this.currentPlayer.has_acted_tonight = true
        this.lastUpdate = new Date()
      }
    },
    
    usePoisonPotion() {
      if (this.currentPlayer) {
        this.currentPlayer.has_poison_potion = false
        this.currentPlayer.has_acted_tonight = true
        this.lastUpdate = new Date()
      }
    },
    
    markAsActed() {
      if (this.currentPlayer) {
        this.currentPlayer.has_acted_tonight = true
        this.lastUpdate = new Date()
      }
    },
    
    resetNightActions() {
      if (this.currentPlayer) {
        this.currentPlayer.has_acted_tonight = false
        this.lastUpdate = new Date()
      }
    },
    
    setLoverPartner(partnerId: string) {
      if (this.currentPlayer) {
        this.currentPlayer.lover_partner_id = partnerId
        this.lastUpdate = new Date()
      }
    },
    
    setModel(modelId: string) {
      if (this.currentPlayer) {
        this.currentPlayer.model_player_id = modelId
        this.lastUpdate = new Date()
      }
    },
    
    transform() {
      if (this.currentPlayer) {
        this.currentPlayer.has_transformed = true
        this.currentPlayer.role = 'warewolf' // El niño salvaje se convierte en hombre lobo
        this.lastUpdate = new Date()
      }
    },
    
    setLoading(v: boolean) {
      this.loading = v
    },
    
    setError(msg: string | null) {
      this.error = msg
    },
    
    clear() {
      this.currentPlayer = null
      this.loading = false
      this.error = null
      this.lastUpdate = null
    },

    /**
     * Inicializar suscripciones WebSocket para la información privada del jugador actual
     * Debe ser llamado después de que se establezca la conexión WebSocket
     */
    initializeWebSocketSubscriptions() {
      const { subscribeToMessage } = useWebSocketStore()

      // Suscribirse a eliminación del jugador actual
      subscribeToMessage('player_eliminated', (data) => {
        if (data && typeof data === 'object' && 'player_id' in data) {
          console.log('[PlayerStore] Jugador eliminado:', data)
          // Solo actualizar si es el jugador actual
          if (this.currentPlayer && this.currentPlayer.player_id === data.player_id) {
            this.updateStatus(false) // Marcar como muerto
          }
        }
      })

      // Suscribirse a asignación de roles (esto debería llegar del backend cuando se asignen los roles)
      subscribeToMessage('game_started', (data) => {
        console.log('[PlayerStore] Juego iniciado, esperando información del rol:', data)
        // La información del rol debería llegar en un mensaje separado
        // o ser cargada desde la API después del inicio del juego
      })

      // Suscribirse a reset de acciones nocturnas al inicio de cada noche
      subscribeToMessage('phase_changed', (data) => {
        console.log('[PlayerStore] Cambio de fase:', data)
        if (data && typeof data === 'object' && 'current' in data) {
          if (data.current === 'night') {
            this.resetNightActions()
          }
        } else if (typeof data === 'string' && (data as string).toLowerCase().includes('night')) {
          this.resetNightActions()
        }
      })

      // Para información privada específica, usaremos mensajes genéricos por ahora
      // hasta que el backend implemente mensajes específicos para roles
      subscribeToMessage('error', (data) => {
        if (data && typeof data === 'object' && 'message' in data) {
          console.error('[PlayerStore] Error relacionado con el jugador:', data)
          this.setError(data.message)
        }
      })

      console.log('[PlayerStore] Suscripciones WebSocket para jugador actual inicializadas')
    }
  }
})

// limpiar store al hacer logout global
logoutEventBus.on(() => {
  try {
    const s = usePlayerStore()
    s.clear()
  } catch (e) {
    // noop
  }
})

export default usePlayerStore
