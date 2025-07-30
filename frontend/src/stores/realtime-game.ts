/**
 * Store para manejo de juego en tiempo real con WebSocket
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
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

export interface GameState {
  gameId: string | null
  phase: GamePhase
  players: GamePlayer[]
  connectedPlayers: string[]
  livingPlayers: string[]
  deadPlayers: string[]
  chatMessages: ChatMessage[]
  votes: Record<string, string>
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
    return isUserAlive.value && gameState.value.phase.current === 'day'
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
   * Configurar event handlers
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

    // Handler para errores
    on('error', handleError)

    // Handler genérico para debugging
    on('*', (message) => {
      console.log('WebSocket message:', message)
    })
  }

  /**
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
    off('error')
    off('*')
  }

  /**
   * Event Handlers
   */
  function handleSystemMessage(message: WebSocketMessage): void {
    console.log('System message:', message.message)

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
   * Actualizar estado del juego desde datos del servidor
   */
  function updateGameStateFromData(data: any): void {
    if (data.phase) {
      gameState.value.phase.current = data.phase
    }

    if (data.connected_players) {
      gameState.value.connectedPlayers = data.connected_players
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

  function requestGameStatus(): boolean {
    return getGameStatus()
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

    // Acciones
    connectToGame,
    disconnectFromGame,
    sendMessage,
    requestJoinGame,
    requestStartGame,
    requestGameStatus,
    resetGameState
  }
})
