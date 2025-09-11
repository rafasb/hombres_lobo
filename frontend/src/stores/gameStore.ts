// Store de Pinia para almacenar y gestionar el estado de la partida
// El store se encarga de:
// - Mantener la información de la partida (id, estado, jugadores, fase actual, etc.)
// - Gestionar errores y estados de carga relacionados con la partida
// - Suscribirse a mensajes WebSocket relevantes para actualizar el estado de la partida en tiempo real
// - Proveer getters para acceder a información derivada del estado de la partida

import { defineStore } from 'pinia'
import { logoutEventBus } from './authStore'
import { useWebSocketStore } from '../composables/useWebSocketStore'
import type { PublicPlayerInfo, PlayerStatus } from '../types/game'

/**
 * Store para gestionar la información de la partida cuando el usuario está dentro de una partida.
 * Principios SOLID aplicados de forma pragmática:
 * - Single Responsibility: este store solo gestiona el estado de la partida en cliente.
 * - Dependency Inversion: dependemos de la abstracción `logoutEventBus` para limpiar estado al logout.
 * - Open/Closed: el store expone acciones que permiten extensión sin cambiar su implementación interna.
 * 
 * Ahora integrado con WebSocket para recibir actualizaciones en tiempo real del backend.
 */

export const useGameStore = defineStore('game', {
  state: () => ({
    gameId: '' as string, // id de la partida a la que pertenece el usuario
    // players contiene los demás jugadores (excluye al usuario local si es necesario)
    players: [] as PublicPlayerInfo[],
    // Flags y mensajes para manejo de carga/errores desde la UI
    loadingPlayers: false,
    loadingAction: false,
    errorMessage: null as string | null,
    
    // Estado del juego desde WebSocket
    currentPhase: '' as string,
    timeRemaining: 0 as number,
    isFirstNight: false as boolean,
    gameStatus: 'waiting' as string, // waiting, started, ended
    
    // Estado de votaciones
    isVotingActive: false as boolean,
    currentVoteType: '' as string,
    eligibleVoters: [] as string[],
    voteTargets: [] as string[],
    votingTimeRemaining: 0 as number,
    currentVotes: {} as Record<string, number>, // target_id -> vote_count
    
    // Información de final de juego
    winningTeam: '' as string,
    winners: [] as string[],
    finalRoles: {} as Record<string, string>, // user_id -> role
    
    // Conexión y jugadores
    connectedPlayersCount: 0 as number,
    totalPlayersCount: 0 as number,
    livingPlayers: [] as string[],
    deadPlayers: [] as string[],
    
    // Timestamps para tracking
    lastUpdate: null as Date | null,
    lastPhaseChange: null as Date | null,
  }),

  getters: {
    inGame(state) {
      return state.gameId !== ''
    },
    
    isGameActive(state) {
      return state.gameStatus === 'started'
    },
    
    isGameEnded(state) {
      return state.gameStatus === 'ended'
    },
    
    // Devuelve solo los ids de los jugadores
    playerIds: (state) => state.players.map(p => p.player_id),
    
    // Mapa rápido id -> jugador
    playersById: (state) => state.players.reduce<Record<string, PublicPlayerInfo>>((acc, p) => {
      acc[p.player_id] = p
      return acc
    }, {}),
    
    // Información de votación
    hasActiveVoting: (state) => state.isVotingActive,
    canVote: (state) => (userId: string) => state.eligibleVoters.includes(userId),
    canBeVoted: (state) => (userId: string) => state.voteTargets.includes(userId),
    
    // Información de fase
    isNightPhase: (state) => state.currentPhase.toLowerCase().includes('night'),
    isDayPhase: (state) => state.currentPhase.toLowerCase().includes('day'),
    
    // Estadísticas del juego
    alivePlayersCount: (state) => state.livingPlayers.length,
    deadPlayersCount: (state) => state.deadPlayers.length,
    connectionRate: (state) => state.totalPlayersCount > 0 
      ? state.connectedPlayersCount / state.totalPlayersCount 
      : 0,
  },

  actions: {
    setGameId(id: string) {
      this.gameId = id
      this.lastUpdate = new Date()
    },

    setPlayers(players: PublicPlayerInfo[]) {
      // Reemplaza la lista completa de jugadores
      this.players = players.slice()
      this.lastUpdate = new Date()
    },

    addOrUpdatePlayer(player: PublicPlayerInfo) {
      const idx = this.players.findIndex(p => p.player_id === player.player_id)
      if (idx === -1) {
        this.players.push(player)
      } else {
        // Mantener inmutabilidad parcial: reemplazar el objeto en su posición
        this.players.splice(idx, 1, { ...this.players[idx], ...player })
      }
      this.lastUpdate = new Date()
    },

    removePlayer(playerId: string) {
      this.players = this.players.filter(p => p.player_id !== playerId)
      this.lastUpdate = new Date()
    },

    updatePlayerStatus(playerId: string, partial: Partial<PublicPlayerInfo>) {
      const idx = this.players.findIndex(p => p.player_id === playerId)
      if (idx !== -1) {
        this.players.splice(idx, 1, { ...this.players[idx], ...partial })
        this.lastUpdate = new Date()
      }
    },

    // Gestión de estado del juego
    setGameStatus(status: string) {
      this.gameStatus = status
      this.lastUpdate = new Date()
    },
    
    setCurrentPhase(phase: string, duration?: number) {
      this.currentPhase = phase
      if (duration !== undefined) {
        this.timeRemaining = duration
      }
      this.lastPhaseChange = new Date()
      this.lastUpdate = new Date()
    },
    
    setTimeRemaining(seconds: number) {
      this.timeRemaining = seconds
    },
    
    setFirstNight(isFirst: boolean) {
      this.isFirstNight = isFirst
    },

    // Gestión de votaciones
    startVoting(voteType: string, duration: number, eligibleVoters: string[], voteTargets: string[]) {
      this.isVotingActive = true
      this.currentVoteType = voteType
      this.votingTimeRemaining = duration
      this.eligibleVoters = eligibleVoters.slice()
      this.voteTargets = voteTargets.slice()
      this.currentVotes = {}
      this.lastUpdate = new Date()
    },
    
    endVoting(results: Record<string, number>, eliminatedPlayer?: string) {
      this.isVotingActive = false
      this.currentVoteType = ''
      this.votingTimeRemaining = 0
      this.currentVotes = results
      this.eligibleVoters = []
      this.voteTargets = []
      
      // Actualizar estado del jugador eliminado si aplica
      if (eliminatedPlayer) {
        this.updatePlayerStatus(eliminatedPlayer, { user_status: 'eliminated' })
        
        // Remover de jugadores vivos y agregar a muertos
        this.livingPlayers = this.livingPlayers.filter(id => id !== eliminatedPlayer)
        if (!this.deadPlayers.includes(eliminatedPlayer)) {
          this.deadPlayers.push(eliminatedPlayer)
        }
      }
      
      this.lastUpdate = new Date()
    },
    
    updateVotingTimer(seconds: number) {
      this.votingTimeRemaining = seconds
    },

    // Gestión de final de juego
    setGameEnded(winningTeam: string, winners: string[], finalRoles: Record<string, string>) {
      this.gameStatus = 'ended'
      this.winningTeam = winningTeam
      this.winners = winners.slice()
      this.finalRoles = { ...finalRoles }
      this.lastUpdate = new Date()
    },

    // Gestión de conexión y jugadores
    setConnectionInfo(connectedCount: number, totalCount: number) {
      this.connectedPlayersCount = connectedCount
      this.totalPlayersCount = totalCount
      this.lastUpdate = new Date()
    },
    
    setPlayerLists(living: string[], dead: string[]) {
      this.livingPlayers = living.slice()
      this.deadPlayers = dead.slice()
      this.lastUpdate = new Date()
    },

    // Flags y errores
    setLoadingPlayers(v: boolean) {
      this.loadingPlayers = v
    },
    
    setLoadingAction(v: boolean) {
      this.loadingAction = v
    },
    
    setError(message: string | null) {
      this.errorMessage = message
    },

    clear() {
      this.gameId = ''
      this.players = []
      this.loadingPlayers = false
      this.loadingAction = false
      this.errorMessage = null
      
      // Limpiar estado del juego
      this.currentPhase = ''
      this.timeRemaining = 0
      this.isFirstNight = false
      this.gameStatus = 'waiting'
      
      // Limpiar votaciones
      this.isVotingActive = false
      this.currentVoteType = ''
      this.eligibleVoters = []
      this.voteTargets = []
      this.votingTimeRemaining = 0
      this.currentVotes = {}
      
      // Limpiar final de juego
      this.winningTeam = ''
      this.winners = []
      this.finalRoles = {}
      
      // Limpiar conexión
      this.connectedPlayersCount = 0
      this.totalPlayersCount = 0
      this.livingPlayers = []
      this.deadPlayers = []
      
      // Limpiar timestamps
      this.lastUpdate = null
      this.lastPhaseChange = null
    },

    /**
     * Inicializar suscripciones WebSocket para este store
     * Debe ser llamado después de que se establezca la conexión WebSocket
     */
    initializeWebSocketSubscriptions() {
      const { subscribeToMessage } = useWebSocketStore()

      // Suscribirse a estado del juego
      subscribeToMessage('game_status', (data) => {
        if (data) {
          console.log('[GameStore] Estado del juego recibido:', data)
          
          if (data.game_id) this.setGameId(data.game_id)
          if (data.status) this.setGameStatus(data.status)
          if (data.current_round !== undefined) this.setCurrentPhase(`Round ${data.current_round}`)
          if (data.is_first_night !== undefined) this.setFirstNight(data.is_first_night)
          
          // Actualizar players directamente con PublicPlayerInfo
          if (data.players) {
            // Asegurar que user_status sea del tipo correcto
            const validatedPlayers = data.players.map(player => ({
              ...player,
              user_status: player.user_status as PlayerStatus
            }))
            this.setPlayers(validatedPlayers)
          }
          
          // Actualizar información de conexión
          if (data.connected_players_count !== undefined && data.current_players !== undefined) {
            this.setConnectionInfo(data.connected_players_count, data.current_players)
          }
          
          // Actualizar listas de jugadores vivos/muertos basado en players
          if (data.players) {
            const livingPlayers = data.players.filter(p => p.is_alive).map(p => p.player_id)
            const deadPlayers = data.players.filter(p => !p.is_alive).map(p => p.player_id)
            this.setPlayerLists(livingPlayers, deadPlayers)
          }
        }
      })

      // Suscribirse a cambios de fase
      subscribeToMessage('phase_changed', (data) => {
        if (data && typeof data === 'string') {
          console.log('[GameStore] Fase cambiada:', data)
          this.setCurrentPhase(data)
        } else if (data && typeof data === 'object' && 'current' in data) {
          console.log('[GameStore] Fase cambiada:', data)
          this.setCurrentPhase(data.current, data.duration)
        }
      })

      // Suscribirse a timer de fase
      subscribeToMessage('phase_timer', (data) => {
        if (data && typeof data === 'number') {
          this.setTimeRemaining(data)
        } else if (data && typeof data === 'object' && 'remainingSeconds' in data) {
          this.setTimeRemaining(data.remainingSeconds)
        }
      })

      // Suscribirse a inicio de juego
      subscribeToMessage('game_started', (data) => {
        if (data) {
          console.log('[GameStore] Juego iniciado:', data)
          this.setGameStatus('started')
          
          if (data.players) {
            // Convertir estructura {id, name} a PublicPlayerInfo
            const convertedPlayers: PublicPlayerInfo[] = data.players.map((p: any) => ({
              player_id: p.id,
              username: p.name,
              is_alive: true, // Por defecto al iniciar el juego
              is_connected: true, // Asumimos conectados al iniciar
              user_status: 'in_game' as PlayerStatus
            }))
            this.setPlayers(convertedPlayers)
          }
        }
      })

      // Suscribirse a final de juego
      subscribeToMessage('game_ended', (data) => {
        if (data) {
          console.log('[GameStore] Juego terminado:', data)
          this.setGameEnded(data.winning_team, data.winners, data.final_roles)
        }
      })

      // Suscribirse a reinicio de juego
      subscribeToMessage('game_restarted', (data) => {
        console.log('[GameStore] Juego reiniciado:', data)
        this.clear()
        this.setGameStatus('waiting')
      })

      // Suscripciones de votación
      subscribeToMessage('voting_started', (data) => {
        if (data) {
          console.log('[GameStore] Votación iniciada:', data)
          this.startVoting(
            data.vote_type,
            data.duration,
            data.eligible_voters,
            data.vote_targets
          )
        }
      })

      subscribeToMessage('voting_ended', (data) => {
        if (data) {
          console.log('[GameStore] Votación terminada:', data)
          this.endVoting(data.results, data.eliminated_player)
        }
      })

      subscribeToMessage('vote_cast', (data) => {
        if (data) {
          console.log('[GameStore] Voto emitido:', data)
          // Aquí podríamos actualizar un contador de votos en tiempo real si fuera necesario
        }
      })

      subscribeToMessage('voting_results', (data) => {
        if (data && data.results) {
          console.log('[GameStore] Resultados de votación:', data)
          this.currentVotes = data.results
        }
      })

      // Suscribirse a estado de conexión del juego
      subscribeToMessage('game_connection_state', (data) => {
        if (data) {
          console.log('[GameStore] Estado de conexión del juego:', data)
          this.setConnectionInfo(data.connectedPlayersCount, data.totalPlayersCount)
          
          if (data.playersStatus) {
            // Actualizar información de jugadores
            data.playersStatus.forEach((playerDTO: any) => {
              if (playerDTO.id) {
                this.addOrUpdatePlayer({
                  player_id: playerDTO.id,
                  username: playerDTO.username || playerDTO.name || '',
                  is_alive: playerDTO.status === 'alive',
                  is_connected: playerDTO.is_connected ?? true,
                  user_status: 'in_game' as PlayerStatus
                })
              }
            })
          }
        }
      })

      // Suscribirse a mensajes de error relacionados con el juego
      subscribeToMessage('error', (data) => {
        if (data && data.error_code) {
          console.error('[GameStore] Error recibido:', data)
          
          // Manejar errores específicos del juego
          switch (data.error_code) {
            case 'GAME_NOT_FOUND':
            case 'GAME_NOT_STARTED':
            case 'INVALID_PHASE':
            case 'VOTE_NOT_ALLOWED':
            case 'PHASE_CHANGE_FAILED':
            case 'START_GAME_ERROR':
            case 'RESTART_GAME_ERROR':
              this.setError(data.message || 'Error en el juego')
              break
            default:
              // No manejar otros tipos de error aquí
              break
          }
        }
      })

      console.log('[GameStore] Suscripciones WebSocket inicializadas')
    }
  }
})

// Limpiar el store cuando se hace logout globalmente
// Se usa una suscripción ligera para mantener separación de responsabilidades
const unsubscribe = logoutEventBus.on(() => {
  try {
    const store = useGameStore()
    store.clear()
  } catch (e) {
    // Ignorar si se ejecuta fuera de un contexto activo de Pinia
    // (por ejemplo durante tests o en servidor)
  }
})

export { unsubscribe as unsubscribeGameStoreOnLogout }
