import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWebSocket, WebSocketManager } from '../websocket/WebSocketManager'
import { useAuthStore } from '../stores/authStore'

export interface PlayerConnectionStatus {
  playerId: string
  username: string
  isConnected: boolean
  lastSeen: Date | null
}

export interface GameConnectionState {
  isUserConnected: boolean
  isUserInGame: boolean
  connectedPlayersCount: number
  totalPlayersCount: number
  playersStatus: PlayerConnectionStatus[]
  lastUpdate: Date | null
}

export function useGameConnection(gameId: string) {
  const auth = useAuthStore()
  const { createConnection, getConnection, connectionStatus } = useWebSocket(gameId)
  
  let wsManager: WebSocketManager | null = null
  let unsubscribeFunctions: (() => void)[] = []
  
  // Estado reactivo de la conexión del juego
  const gameConnectionState = ref<GameConnectionState>({
    isUserConnected: false,
    isUserInGame: false,
    connectedPlayersCount: 0,
    totalPlayersCount: 0,
    playersStatus: [],
    lastUpdate: null
  })

  // Computed para mostrar información legible
  const connectionStatusText = computed(() => {
    if (!connectionStatus.value.isConnected) {
      if (connectionStatus.value.isReconnecting) {
        return `Reconectando... (${connectionStatus.value.reconnectAttempts}/5)`
      }
      if (connectionStatus.value.error) {
        return `Error: ${connectionStatus.value.error}`
      }
      return 'Desconectado'
    }
    return 'Conectado'
  })

  const connectionStatusClass = computed(() => {
    if (!connectionStatus.value.isConnected) {
      return connectionStatus.value.isReconnecting ? 'reconnecting' : 'disconnected'
    }
    return 'connected'
  })

  const isUserActiveInLobby = computed(() => {
    return gameConnectionState.value.isUserConnected && gameConnectionState.value.isUserInGame
  })

  const connectionHealthText = computed(() => {
    const state = gameConnectionState.value
    if (!state.isUserConnected) {
      return '❌ No conectado al lobby'
    }
    if (!state.isUserInGame) {
      return '⚠️ Conectado pero no en la partida'
    }
    return '✅ Activo en el lobby'
  })

  // Inicializar conexión WebSocket
  const initializeConnection = async () => {
    try {
      if (!auth.token) {
        throw new Error('No hay token de autenticación')
      }

      wsManager = createConnection(auth.token)
      await wsManager.connect()

      // Suscribirse a mensajes de estado del juego - adaptador para el backend
      const unsubGameState = wsManager.subscribe('system_message', (message: any) => {
        // Adaptar mensajes system_message del backend para simular game_connection_state
        if (message.data && message.data.players) {
          const playersStatus: PlayerConnectionStatus[] = message.data.players.map((player: any) => ({
            playerId: player.id,
            username: player.name,
            isConnected: message.data.connected_players?.includes(player.id) || false,
            lastSeen: new Date()
          }))

          gameConnectionState.value = {
            isUserConnected: true,
            isUserInGame: true,
            connectedPlayersCount: playersStatus.filter(p => p.isConnected).length,
            totalPlayersCount: playersStatus.length,
            playersStatus,
            lastUpdate: new Date()
          }
        }
      })

      // Suscribirse a conexión/desconexión de jugadores
      const unsubPlayerConnected = wsManager.subscribe('player_connected', (data: any) => {
        // Actualizar estado cuando un jugador se conecta
        const currentPlayers = gameConnectionState.value.playersStatus
        const existingPlayer = currentPlayers.find(p => p.playerId === data.user_id)
        if (existingPlayer) {
          existingPlayer.isConnected = true
          existingPlayer.lastSeen = new Date()
        }
        gameConnectionState.value.connectedPlayersCount = currentPlayers.filter(p => p.isConnected).length
        gameConnectionState.value.lastUpdate = new Date()
      })

      const unsubPlayerDisconnected = wsManager.subscribe('player_disconnected', (data: any) => {
        // Actualizar estado cuando un jugador se desconecta
        const currentPlayers = gameConnectionState.value.playersStatus
        const existingPlayer = currentPlayers.find(p => p.playerId === data.user_id)
        if (existingPlayer) {
          existingPlayer.isConnected = false
          existingPlayer.lastSeen = new Date()
        }
        gameConnectionState.value.connectedPlayersCount = currentPlayers.filter(p => p.isConnected).length
        gameConnectionState.value.lastUpdate = new Date()
      })

      // Suscribirse a heartbeat del backend
      const unsubHeartbeat = wsManager.subscribe('heartbeat', (data: any) => {
        // El backend envía heartbeat, no necesitamos responder pong específicamente
        // ya que el backend espera heartbeat de vuelta
        if (data.response === 'pong') {
          // Este es un pong del servidor, no necesitamos hacer nada
        } else {
          // Este es un ping del servidor, responder con heartbeat
          wsManager?.send({ type: 'heartbeat' })
        }
      })

      unsubscribeFunctions = [unsubGameState, unsubPlayerConnected, unsubPlayerDisconnected, unsubHeartbeat]

      // Solicitar el estado inicial del juego
      requestGameState()

    } catch (error) {
      console.error('Error initializing WebSocket connection:', error)
    }
  }

  // Solicitar el estado actual del juego
  const requestGameState = () => {
    // Cambiar 'get_game_state' por 'get_game_status' para coincidir con el backend
    wsManager?.send({
      type: 'get_game_status'
    })
  }

  // Notificar que el usuario entró al lobby
  const notifyUserJoinedLobby = () => {
    // Cambiar 'user_joined_lobby' por 'join_game' para coincidir con el backend
    wsManager?.send({
      type: 'join_game'
    })
  }

  // Notificar que el usuario salió del lobby
  const notifyUserLeftLobby = () => {
    wsManager?.send({
      type: 'user_left_lobby',
      data: { gameId, userId: auth.user?.id }
    })
  }

  // Obtener el estado de un jugador específico
  const getPlayerConnectionStatus = (playerId: string): PlayerConnectionStatus | null => {
    return gameConnectionState.value.playersStatus.find(p => p.playerId === playerId) || null
  }

  // Limpiar conexión
  const cleanup = () => {
    // Notificar que el usuario sale del lobby
    notifyUserLeftLobby()
    
    // Limpiar suscripciones
    unsubscribeFunctions.forEach(unsub => unsub())
    unsubscribeFunctions = []
    
    // Desconectar WebSocket
    wsManager?.disconnect()
    wsManager = null
  }

  // Lifecycle hooks
  onMounted(() => {
    initializeConnection()
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    // Estado
    gameConnectionState: computed(() => gameConnectionState.value),
    connectionStatus,
    
    // Computed
    connectionStatusText,
    connectionStatusClass,
    isUserActiveInLobby,
    connectionHealthText,
    
    // Métodos
    requestGameState,
    notifyUserJoinedLobby,
    notifyUserLeftLobby,
    getPlayerConnectionStatus,
    initializeConnection,
    cleanup
  }
}
