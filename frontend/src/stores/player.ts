import { defineStore } from 'pinia'
import type { GamePlayer } from '../types/game'
import { logoutEventBus } from './authStore'
import { useWebSocketStore } from '../composables/useWebSocketStore'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    // lista de jugadores en la partida (vacía por defecto)
    players: [] as GamePlayer[],
    loading: false,
    error: null as string | null,
    // Estado adicional para gestión WebSocket
    connectedPlayers: [] as string[], // IDs de jugadores conectados
    lastUpdate: null as Date | null,
  }),

  getters: {
    count: (state) => state.players.length,
    connectedCount: (state) => state.connectedPlayers.length,
    byId: (state) => (id: string) => state.players.find(p => p.id === id) as GamePlayer | undefined,
    
    // Jugadores organizados por estado
    alivePlayers: (state) => state.players.filter(p => p.status === 'alive'),
    deadPlayers: (state) => state.players.filter(p => p.status === 'dead'),
    eliminatedPlayers: (state) => state.players.filter(p => p.status === 'eliminated'),
    
    // Información de conexión
    playersWithConnectionStatus: (state) => state.players.map(player => ({
      ...player,
      isConnected: state.connectedPlayers.includes(player.id)
    })),
  },

  actions: {
    setPlayers(list: GamePlayer[]) {
      this.players = list.slice()
      this.lastUpdate = new Date()
    },
    
    addOrUpdate(player: GamePlayer) {
      const idx = this.players.findIndex(p => p.id === player.id)
      if (idx === -1) {
        this.players.push(player)
      } else {
        this.players.splice(idx, 1, { ...this.players[idx], ...player })
      }
      this.lastUpdate = new Date()
    },
    
    remove(id: string) {
      this.players = this.players.filter(p => p.id !== id)
      this.connectedPlayers = this.connectedPlayers.filter(pid => pid !== id)
      this.lastUpdate = new Date()
    },
    
    updatePlayerStatus(playerId: string, status: string) {
      const player = this.players.find(p => p.id === playerId)
      if (player) {
        player.status = status
        this.lastUpdate = new Date()
      }
    },
    
    updatePlayerRole(playerId: string, role: string) {
      const player = this.players.find(p => p.id === playerId)
      if (player) {
        player.role = role
        this.lastUpdate = new Date()
      }
    },
    
    setConnectedPlayers(playerIds: string[]) {
      this.connectedPlayers = playerIds.slice()
    },
    
    markPlayerConnected(playerId: string) {
      if (!this.connectedPlayers.includes(playerId)) {
        this.connectedPlayers.push(playerId)
      }
    },
    
    markPlayerDisconnected(playerId: string) {
      this.connectedPlayers = this.connectedPlayers.filter(id => id !== playerId)
    },
    
    setLoading(v: boolean) {
      this.loading = v
    },
    
    setError(msg: string | null) {
      this.error = msg
    },
    
    clear() {
      this.players = []
      this.connectedPlayers = []
      this.loading = false
      this.error = null
      this.lastUpdate = null
    },

    /**
     * Inicializar suscripciones WebSocket para este store
     * Debe ser llamado después de que se establezca la conexión WebSocket
     */
    initializeWebSocketSubscriptions() {
      const { subscribeToMessage } = useWebSocketStore()

      // Suscribirse a conexiones/desconexiones de jugadores
      subscribeToMessage('player_connected', (data) => {
        if (data && data.user_id) {
          console.log('[PlayerStore] Jugador conectado:', data)
          this.markPlayerConnected(data.user_id)
          
          // Si tenemos información del jugador, actualizar su información
          if (data.username) {
            const existingPlayer = this.byId(data.user_id)
            if (existingPlayer) {
              this.addOrUpdate({
                ...existingPlayer,
                username: data.username
              })
            }
          }
        }
      })

      subscribeToMessage('player_disconnected', (data) => {
        if (data && data.user_id) {
          console.log('[PlayerStore] Jugador desconectado:', data)
          this.markPlayerDisconnected(data.user_id)
        }
      })

      // Suscribirse a jugadores que dejan el juego
      subscribeToMessage('player_left_game', (data) => {
        if (data && data.playerId) {
          console.log('[PlayerStore] Jugador dejó el juego:', data)
          this.remove(data.playerId)
        }
      })

      // Suscribirse a jugadores baneados
      subscribeToMessage('player_banned', (data) => {
        if (data && data.user_id) {
          console.log('[PlayerStore] Jugador baneado:', data)
          this.markPlayerDisconnected(data.user_id)
          this.updatePlayerStatus(data.user_id, 'banned')
        }
      })

      // Suscribirse a eliminaciones de jugadores
      subscribeToMessage('player_eliminated', (data) => {
        if (data && data.player_id) {
          console.log('[PlayerStore] Jugador eliminado:', data)
          this.updatePlayerStatus(data.player_id, 'eliminated')
          
          // Si se revela el rol, actualizarlo también
          if (data.role) {
            this.updatePlayerRole(data.player_id, data.role)
          }
        }
      })

      // Suscribirse a revelaciones de roles
      subscribeToMessage('player_role_revealed', (data) => {
        if (data && data.player_id && data.role) {
          console.log('[PlayerStore] Rol de jugador revelado:', data)
          this.updatePlayerRole(data.player_id, data.role)
        }
      })

      // Suscribirse a actualizaciones de estado de jugadores
      subscribeToMessage('players_status_update', (data) => {
        if (data && data.playersStatus) {
          console.log('[PlayerStore] Actualización de estado de jugadores:', data)
          
          // Actualizar información de jugadores basándose en el estado recibido
          data.playersStatus.forEach((playerDTO: any) => {
            if (playerDTO.id) {
              const existingPlayer = this.byId(playerDTO.id)
              if (existingPlayer) {
                this.addOrUpdate({
                  ...existingPlayer,
                  username: playerDTO.username || playerDTO.name || existingPlayer.username,
                  status: playerDTO.status || existingPlayer.status
                })
              } else if (playerDTO.username || playerDTO.name) {
                // Agregar nuevo jugador si no existe
                this.addOrUpdate({
                  id: playerDTO.id,
                  username: playerDTO.username || playerDTO.name,
                  status: playerDTO.status || 'alive',
                  role: '', // Se actualizará cuando se revele
                  game_id: '' // Se actualizará desde el gameStore
                })
              }
            }
          })
        }
      })

      // Suscribirse a estado de conexión del juego para obtener información de jugadores
      subscribeToMessage('game_connection_state', (data) => {
        if (data) {
          console.log('[PlayerStore] Estado de conexión del juego:', data)
          
          // Actualizar lista de jugadores conectados
          this.setConnectedPlayers(data.connectedPlayersCount ? [] : []) // TODO: Adjust based on actual data structure
          
          // Actualizar información de jugadores si está disponible
          if (data.playersStatus) {
            data.playersStatus.forEach((playerDTO: any) => {
              if (playerDTO.id) {
                const existingPlayer = this.byId(playerDTO.id)
                if (existingPlayer) {
                  this.addOrUpdate({
                    ...existingPlayer,
                    username: playerDTO.username || playerDTO.name || existingPlayer.username,
                    status: playerDTO.status || existingPlayer.status
                  })
                }
              }
            })
          }
        }
      })

      console.log('[PlayerStore] Suscripciones WebSocket inicializadas')
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
