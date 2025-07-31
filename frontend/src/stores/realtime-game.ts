/**
 * Store para manejo de juego en tiempo real con WebSocket
 */
import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import { useWebSocket, type WebSocketMessage } from '@/services/websocket'
import { useAuthStore } from './auth'

export interface GamePlayer {
  id: string
  name: string
  isAlive: boolean
  role?: string
  isConnected: boolean
}

export interface GamePhase {
  current: string
  timeRemaining: number
  duration: number
}

export interface ChatMessage {
  id: string
  senderId: string
  senderName: string
  message: string
  channel: string
  timestamp: string
}

export interface Vote {
  voter_id: string
  target_id: string
  weight: number
  timestamp: string
}

export interface VotingSession {
  session_id: string
  vote_type: string
  status: string
  eligible_voters: string[]
  valid_targets: string[]
  votes: Vote[]
  results?: {
    winner?: string
    tie: boolean
    vote_counts: Record<string, number>
  }
  started_at: string
  ends_at?: string
}

export interface GameState {
  gameId: string | null
  phase: GamePhase
  players: GamePlayer[]
  connectedPlayers: string[]
  livingPlayers: string[]
  deadPlayers: string[]
  chatMessages: ChatMessage[]
  votes: Record<string, string>
  votingSession: VotingSession | null
  userVote: string | null
  isHost: boolean
}

export const useRealtimeGameStore = defineStore('realtimeGame', () => {
  const authStore = useAuthStore()
  const { connectionState, connect, disconnect, on, off, sendChatMessage, joinGame, startGame, getGameStatus } = useWebSocket()

  // Estado del juego
  const gameState = ref<GameState>({
    gameId: null,
    phase: {
      current: 'waiting',
      timeRemaining: 0,
      duration: 0
    },
    players: [],
    connectedPlayers: [],
    livingPlayers: [],
    deadPlayers: [],
    chatMessages: [],
    votes: {},
    votingSession: null,
    userVote: null,
    isHost: false
  })

  // Estados de carga y error
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computeds
  const isConnected = computed(() => connectionState.value.connected)
  const isConnecting = computed(() => connectionState.value.connecting)
  const connectionError = computed(() => connectionState.value.error)

  const currentUser = computed(() => authStore.user)
  const isUserAlive = computed(() => {
    if (!currentUser.value) return false
    return gameState.value.livingPlayers.includes(currentUser.value.id.toString())
  })

  const canVote = computed(() => {
    return isUserAlive.value && gameState.value.phase.current === 'voting'
  })

  const isVotingActive = computed(() => {
    return gameState.value.votingSession?.status === 'active'
  })

  const hasUserVoted = computed(() => {
    return gameState.value.userVote !== null
  })

  const votingTimeRemaining = computed(() => {
    if (!gameState.value.votingSession?.ends_at) return 0
    const endTime = new Date(gameState.value.votingSession.ends_at).getTime()
    const now = Date.now()
    return Math.max(0, Math.floor((endTime - now) / 1000))
  })

  const validVotingTargets = computed(() => {
    if (!gameState.value.votingSession) return []
    return gameState.value.players.filter(player =>
      gameState.value.votingSession?.valid_targets.includes(player.id)
    )
  })

  const voteResults = computed(() => {
    return gameState.value.votingSession?.results || null
  })

  /**
   * Conectar al juego
   */
  async function connectToGame(gameId: string): Promise<boolean> {
    if (!authStore.token) {
      error.value = 'No hay token de autenticación'
      return false
    }

    try {
      isLoading.value = true
      error.value = null

      const success = await connect(gameId, authStore.token)
      if (success) {
        gameState.value.gameId = gameId
        setupEventHandlers()

        // Solicitar estado inicial
        setTimeout(() => {
          getGameStatus()
        }, 1000)
      }

      return success
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error de conexión'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Desconectar del juego
   */
  function disconnectFromGame(): void {
    disconnect()
    resetGameState()
  }

  /**
   * Configurar event handlers para WebSocket
   */
  function setupEventHandlers(): void {
    // Handler para mensajes del sistema
    on('system_message', handleSystemMessage)

    // Handler para cambios de fase
    on('phase_changed', handlePhaseChanged)

    // Handler para mensajes de chat
    on('chat_message', handleChatMessage)

    // Handler para conexión/desconexión de jugadores
    on('player_connected', handlePlayerConnected)
    on('player_disconnected', handlePlayerDisconnected)

    // Handler para inicio de juego
    on('game_started', handleGameStarted)

    // Handler para eliminación de jugadores
    on('player_eliminated', handlePlayerEliminated)

    // Handlers para votación
    on('voting_started', handleVotingStarted)
    on('vote_cast', handleVoteCast)
    on('voting_results', handleVotingResults)
    on('voting_status', handleVotingStatus)

    // Handler para errores
    on('error', handleError)

    // Handler genérico para debugging
    on('*', (message) => {
      console.log('WebSocket message:', message)
    })
  }  /**
   * Limpiar event handlers
   */
  function cleanupEventHandlers(): void {
    off('system_message')
    off('phase_changed')
    off('chat_message')
    off('player_connected')
    off('player_disconnected')
    off('game_started')
    off('player_eliminated')
    off('voting_started')
    off('vote_cast')
    off('voting_results')
    off('voting_status')
    off('error')
    off('*')
  }

  /**
   * Event Handlers
   */
  function handleSystemMessage(message: WebSocketMessage): void {
    console.log('System message:', message.message)
    console.log('System message data:', message.data)

    // Actualizar estado del juego si viene información
    if (message.data) {
      updateGameStateFromData(message.data)
    }
  }

  function handlePhaseChanged(message: WebSocketMessage): void {
    gameState.value.phase = {
      current: message.phase || 'waiting',
      timeRemaining: message.time_remaining || 0,
      duration: message.duration || 0
    }

    console.log(`Fase cambiada a: ${message.phase}`)
  }

  function handleChatMessage(message: WebSocketMessage): void {
    const chatMsg: ChatMessage = {
      id: Date.now().toString(),
      senderId: message.sender_id || '',
      senderName: message.sender_name || 'Unknown',
      message: message.message || '',
      channel: message.channel || 'all',
      timestamp: message.timestamp || new Date().toISOString()
    }

    gameState.value.chatMessages.push(chatMsg)

    // Mantener solo los últimos 100 mensajes
    if (gameState.value.chatMessages.length > 100) {
      gameState.value.chatMessages = gameState.value.chatMessages.slice(-100)
    }
  }

  function handlePlayerConnected(message: WebSocketMessage): void {
    const userId = message.user_id
    if (userId && !gameState.value.connectedPlayers.includes(userId)) {
      gameState.value.connectedPlayers.push(userId)
    }
  }

  function handlePlayerDisconnected(message: WebSocketMessage): void {
    const userId = message.user_id
    if (userId) {
      const index = gameState.value.connectedPlayers.indexOf(userId)
      if (index > -1) {
        gameState.value.connectedPlayers.splice(index, 1)
      }
    }
  }

  function handleGameStarted(message: WebSocketMessage): void {
    if (message.players) {
      gameState.value.players = message.players.map((p: any) => ({
        id: p.id,
        name: p.name,
        isAlive: true,
        isConnected: gameState.value.connectedPlayers.includes(p.id)
      }))

      gameState.value.livingPlayers = gameState.value.players.map(p => p.id)
      gameState.value.deadPlayers = []
    }

    console.log('¡Juego iniciado!')
  }

  function handlePlayerEliminated(message: WebSocketMessage): void {
    const playerId = message.player_id
    if (playerId) {
      // Mover de vivos a muertos
      const index = gameState.value.livingPlayers.indexOf(playerId)
      if (index > -1) {
        gameState.value.livingPlayers.splice(index, 1)
        gameState.value.deadPlayers.push(playerId)
      }

      // Actualizar estado del jugador
      const player = gameState.value.players.find(p => p.id === playerId)
      if (player) {
        player.isAlive = false
        if (message.role) {
          player.role = message.role
        }
      }
    }
  }

  function handleError(message: WebSocketMessage): void {
    error.value = message.message || 'Error desconocido'
    console.error('WebSocket error:', message)
  }

  /**
   * Handlers para votación
   */
  function handleVotingStarted(message: WebSocketMessage): void {
    console.log('Votación iniciada:', message.data)

    if (message.data) {
      gameState.value.votingSession = {
        session_id: message.data.session_id || '',
        vote_type: message.data.vote_type || 'day_vote',
        status: 'active',
        eligible_voters: message.data.eligible_voters || [],
        valid_targets: message.data.valid_targets || [],
        votes: [],
        started_at: message.data.started_at || new Date().toISOString(),
        ends_at: message.data.ends_at
      }

      // Reset user vote
      gameState.value.userVote = null
    }
  }

  function handleVoteCast(message: WebSocketMessage): void {
    console.log('Voto emitido:', message.data)

    if (message.data && gameState.value.votingSession) {
      // Agregar o actualizar voto en la sesión
      const existingVoteIndex = gameState.value.votingSession.votes.findIndex(
        vote => vote.voter_id === message.data.voter_id
      )

      const newVote: Vote = {
        voter_id: message.data.voter_id,
        target_id: message.data.target_id,
        weight: message.data.weight || 1,
        timestamp: message.data.timestamp || new Date().toISOString()
      }

      if (existingVoteIndex >= 0) {
        gameState.value.votingSession.votes[existingVoteIndex] = newVote
      } else {
        gameState.value.votingSession.votes.push(newVote)
      }

      // Si es el voto del usuario actual, actualizar userVote
      if (currentUser.value && message.data.voter_id === currentUser.value.id.toString()) {
        gameState.value.userVote = message.data.target_id
      }
    }
  }

  function handleVotingResults(message: WebSocketMessage): void {
    console.log('Resultados de votación:', message.data)

    if (message.data && gameState.value.votingSession) {
      gameState.value.votingSession.results = {
        winner: message.data.winner,
        tie: message.data.tie || false,
        vote_counts: message.data.vote_counts || {}
      }

      gameState.value.votingSession.status = 'finished'
    }
  }

  function handleVotingStatus(message: WebSocketMessage): void {
    console.log('Estado de votación:', message.data)

    if (message.data) {
      gameState.value.votingSession = message.data

      // Actualizar userVote si existe
      if (currentUser.value) {
        const userVote = message.data.votes?.find(
          (vote: Vote) => vote.voter_id === currentUser.value!.id.toString()
        )
        gameState.value.userVote = userVote?.target_id || null
      }
    }
  }

  /**
   * Actualizar estado del juego desde datos del servidor
   */
  function updateGameStateFromData(data: any): void {
    console.log('Actualizando estado del juego con data:', data)

    if (data.phase) {
      gameState.value.phase.current = data.phase
    }

    // Procesar jugadores si vienen en los datos
    if (data.players) {
      console.log('Procesando jugadores:', data.players)
      gameState.value.players = data.players.map((p: any) => ({
        id: p.id,
        name: p.name || p.username,
        isAlive: p.is_alive !== false, // Por defecto vivo si no se especifica
        isConnected: gameState.value.connectedPlayers.includes(p.id),
        role: p.role
      }))

      // Actualizar listas de jugadores vivos/muertos basado en los jugadores
      gameState.value.livingPlayers = gameState.value.players
        .filter(p => p.isAlive)
        .map(p => p.id)
      gameState.value.deadPlayers = gameState.value.players
        .filter(p => !p.isAlive)
        .map(p => p.id)
    }

    if (data.connected_players) {
      gameState.value.connectedPlayers = data.connected_players
      // Actualizar estado de conexión de jugadores
      gameState.value.players.forEach(player => {
        player.isConnected = gameState.value.connectedPlayers.includes(player.id)
      })
    }

    if (data.living_players) {
      gameState.value.livingPlayers = data.living_players
    }

    if (data.dead_players) {
      gameState.value.deadPlayers = data.dead_players
    }

    if (data.time_remaining !== undefined) {
      gameState.value.phase.timeRemaining = data.time_remaining
    }

    console.log('Estado del juego actualizado:', {
      players: gameState.value.players.length,
      living: gameState.value.livingPlayers.length,
      connected: gameState.value.connectedPlayers.length
    })
  }

  /**
   * Funciones de votación
   */
  function castVote(targetPlayerId: string): void {
    if (!canVote.value) {
      error.value = 'No puedes votar en este momento'
      return
    }

    if (!gameState.value.votingSession?.valid_targets.includes(targetPlayerId)) {
      error.value = 'Objetivo de voto inválido'
      return
    }

    gameState.value.userVote = targetPlayerId
    const { castVote: sendVote } = useWebSocket()
    sendVote(targetPlayerId)
  }

  function getVotingStatus(): void {
    const { getVotingStatus: requestStatus } = useWebSocket()
    requestStatus()
  }

  function forceNextPhase(): void {
    if (!gameState.value.isHost) {
      error.value = 'Solo el host puede forzar la siguiente fase'
      return
    }

    const { forceNextPhase: sendForce } = useWebSocket()
    sendForce()
  }

  /**
   * Acciones del juego
   */
  function sendMessage(message: string, channel: string = 'all'): boolean {
    return sendChatMessage(message, channel)
  }

  function requestJoinGame(): boolean {
    return joinGame()
  }

  function requestStartGame(): boolean {
    return startGame()
  }

  function requestGameStatus(): void {
    getGameStatus()
  }

  /**
   * Resetear estado del juego
   */
  function resetGameState(): void {
    gameState.value = {
      gameId: null,
      phase: {
        current: 'waiting',
        timeRemaining: 0,
        duration: 0
      },
      players: [],
      connectedPlayers: [],
      livingPlayers: [],
      deadPlayers: [],
      chatMessages: [],
      votes: {},
      votingSession: null,
      userVote: null,
      isHost: false
    }
    error.value = null
    cleanupEventHandlers()
  }

  return {
    // Estado
    gameState,
    isLoading,
    error,
    isConnected,
    isConnecting,
    connectionError,

    // Computeds
    currentUser,
    isUserAlive,
    canVote,
    isVotingActive,
    hasUserVoted,
    votingTimeRemaining,
    validVotingTargets,
    voteResults,

    // Acciones
    connectToGame,
    disconnectFromGame,
    sendMessage,
    requestJoinGame,
    requestStartGame,
    requestGameStatus,
    resetGameState,

    // Acciones de votación
    castVote,
    getVotingStatus,
    forceNextPhase
  }
})
