import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWebSocketPolling } from '../websocket/WebSocketPollingManager'
import { useAuthStore, logoutEventBus } from '../stores/authStore'
import type { PlayerStatus, PlayerDTO } from '../types'
import type { WebSocketPollingManager } from '../websocket/WebSocketPollingManager'

export interface GameConnectionState {
  isUserConnected: boolean
  isUserInGame: boolean
  connectedPlayersCount: number
  totalPlayersCount: number
  playersStatus: PlayerStatus[]
  lastUpdate: Date | null
}

export function useGameConnection(gameId: string) {
  const auth = useAuthStore()
  const { createConnection, connectionStatus } = useWebSocketPolling(gameId)
  
  let wsManager: WebSocketPollingManager | null = null
  let unsubscribeFunctions: (() => void)[] = []

  const VALID_PLAYER_STATUSES = ['banned', 'connected', 'disconnected', 'in_game'] as const

  const mapRawPlayerToStatus = (raw: any, connectedPlayers?: any[]): PlayerStatus => {
    const player = raw as PlayerDTO
    let status: PlayerStatus['status'] = 'disconnected'

    if (player.status && VALID_PLAYER_STATUSES.includes(player.status as any)) {
      status = player.status as PlayerStatus['status']
    } else if (connectedPlayers && Array.isArray(connectedPlayers) && connectedPlayers.includes(player.id)) {
      status = 'connected'
    }

    return {
      playerId: player.id,
      username: (player as any).name ?? player.username ?? 'unknown',
      status,
      isConnected: status === 'connected' || status === 'in_game',
      lastSeen: new Date()
    }
  }
  
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

  console.log('Initializing WebSocket connection for game:', gameId)
  wsManager = createConnection({ token: auth.token, simulate: false })

  await wsManager.connect()
  console.log('WebSocket connection established')
  // Enviar mensaje join_game tras conectar, según la recomendación del backend
  wsManager.send({ type: 'join_game' })

      // Suscribirse a mensajes de estado del juego - adaptador para el backend
  const handleSystemMessage = (message: unknown) => {
        console.log('System message received:', message)
        const payload = (message ?? {}) as { data?: Record<string, unknown>; players?: unknown }
        const playersListRaw = payload?.data?.players ?? payload?.players
        if (!playersListRaw || !Array.isArray(playersListRaw)) return

        const connectedPlayersRaw = (payload.data && payload.data['connected_players']) ?? undefined
        const connectedPlayers = Array.isArray(connectedPlayersRaw) ? connectedPlayersRaw : undefined
        const playersStatus: PlayerStatus[] = playersListRaw.map((p) => mapRawPlayerToStatus(p, connectedPlayers))

        gameConnectionState.value = {
          isUserConnected: true,
          isUserInGame: true,
          connectedPlayersCount: playersStatus.filter(p => p.isConnected).length,
          totalPlayersCount: playersStatus.length,
          playersStatus,
          lastUpdate: new Date()
        }
      }

  const unsubGameState = wsManager.subscribe('system_message', handleSystemMessage)

      // Suscribirse a cambios de estado de usuario según la referencia WebSocket
  const handleUserStatusChanged = (data: unknown) => {
        const payload = (data ?? {}) as { user_id?: string; old_status?: string; new_status?: string; message?: string }
        if (!payload.user_id) return
        const currentPlayers = [...gameConnectionState.value.playersStatus]
        const existingPlayer = currentPlayers.find(p => p.playerId === payload.user_id)
        if (!existingPlayer) return

        if (VALID_PLAYER_STATUSES.includes(payload.new_status as any)) {
          existingPlayer.status = payload.new_status as PlayerStatus['status']
        } else {
          existingPlayer.status = 'disconnected'
        }
        existingPlayer.isConnected = existingPlayer.status === 'connected' || existingPlayer.status === 'in_game'
        existingPlayer.lastSeen = new Date()

        gameConnectionState.value.playersStatus = currentPlayers
        gameConnectionState.value.connectedPlayersCount = currentPlayers.filter(p => p.isConnected).length
        gameConnectionState.value.lastUpdate = new Date()
      }

  const unsubUserStatusChanged = wsManager.subscribe('user_status_changed', handleUserStatusChanged)

      // Suscribirse a respuestas exitosas de cambio de estado
  const handleSuccess = (data: unknown) => {
        const payload = data as { action?: string; message?: string; data?: Record<string, unknown> } | undefined
        if (payload?.action === 'update_user_status') {
          console.log('Status update success:', payload)
        }
      }

  const unsubSuccess = wsManager.subscribe('success', handleSuccess)

      // Suscribirse a errores de cambio de estado
  const handleError = (data: unknown) => {
        const payload = data as { error_code?: string; message?: string; details?: Record<string, unknown> } | undefined
        console.error('WebSocket error:', payload)
        if (payload?.error_code === 'INSUFFICIENT_PERMISSIONS') {
          console.error('Permission error:', payload.message)
        }
      }

  const unsubError = wsManager.subscribe('error', handleError)

      // Suscribirse a heartbeat del backend
  const handleHeartbeat = (data: unknown) => {
        const payload = data as { response?: string } | undefined
        if (payload?.response === 'pong') return
        wsManager?.send({ type: 'heartbeat' })
      }

  const unsubHeartbeat = wsManager.subscribe('heartbeat', handleHeartbeat)

      unsubscribeFunctions = [unsubGameState, unsubUserStatusChanged, unsubSuccess, unsubError, unsubHeartbeat]

      // Solicitar el estado inicial del juego
      requestGameState()

    } catch (error) {
      console.error('Error initializing WebSocket connection:', error)
    }
  }

  // Inicializar el estado de jugadores con datos del REST API
  const initializePlayersStatus = (players: any[]) => {
    const playersStatus: PlayerStatus[] = players.map((player: any) => ({
      playerId: player.id,
      username: player.username,
      status: 'connected', // Valor por defecto razonable
      isConnected: true, // Asumir conectado por defecto - el WebSocket actualizará el estado real
      lastSeen: new Date()
    }))

    gameConnectionState.value = {
      ...gameConnectionState.value,
      totalPlayersCount: playersStatus.length,
      connectedPlayersCount: playersStatus.filter(p => p.isConnected).length,
      playersStatus,
      lastUpdate: new Date()
    }
    
    console.log('Initialized players status:', gameConnectionState.value)
  }

  // Solicitar el estado actual del juego
  const requestGameState = () => {
    // Cambiar 'get_game_state' por 'get_game_status' para coincidir con el backend
    wsManager?.send({
      type: 'get_game_status'
    })
  }

  // Enviar mensaje de actualización de estado
  const updateUserStatus = (status: string) => {
    if (wsManager && connectionStatus.value.isConnected) {
      // Crear mensaje personalizado para cambio de estado. Incluir gameId cuando el usuario
      // pasa a 'in_game' para que el backend tenga contexto de la partida.
      const data: Record<string, unknown> = { status }
      if (status === 'in_game' && gameId) {
        data['game_id'] = gameId
      }
      wsManager.send({
        type: 'update_user_status',
        data
      })
    }
  }

  // Notificar que el usuario entró al lobby
  const notifyUserJoinedLobby = () => {
    // Cambiar estado del usuario a 'in_game' cuando se une al lobby
    updateUserStatus('in_game')
  }

  // Notificar que el usuario salió del lobby
  const notifyUserLeftLobby = () => {
    // Cambiar estado del usuario a 'connected' cuando sale del lobby
    updateUserStatus('connected')
  }

  // Obtener el estado de un jugador específico
  const getPlayerConnectionStatus = (playerId: string): PlayerStatus | null => {
    return gameConnectionState.value.playersStatus.find(p => p.playerId === playerId) || null
  }

  // Notificar desconexión del usuario (al cerrar ventana, etc.)
  const notifyUserDisconnected = () => {
    // Cambiar estado del usuario a 'disconnected'
    updateUserStatus('disconnected')
  }

  // Limpiar conexión
  const cleanup = () => {
    // Notificar que el usuario sale del lobby
    notifyUserLeftLobby()
    
    // Esperar un poco para que se envíe el mensaje antes de desconectar
    setTimeout(() => {
      // Limpiar suscripciones
      unsubscribeFunctions.forEach(unsub => unsub())
      unsubscribeFunctions = []
      
      // Desconectar WebSocket
      wsManager?.disconnect()
      wsManager = null
    }, 100)
  }

  // Lifecycle hooks
  onMounted(() => {
    initializeConnection()
    
    // Manejar cierre de ventana/pestaña
    const handleBeforeUnload = () => {
      // Enviar notificación de desconexión de forma síncrona
      if (wsManager && connectionStatus.value.isConnected) {
        updateUserStatus('disconnected')
      }
    }
    
    // Manejar logout del usuario
    const handleLogout = () => {
      console.log('User logging out, updating status to disconnected')
      if (wsManager && connectionStatus.value.isConnected) {
        notifyUserDisconnected()
      }
    }
    
    window.addEventListener('beforeunload', handleBeforeUnload)
    const removeLogoutListener = logoutEventBus.on(handleLogout)
    
    // Limpiar listeners al desmontar
    onUnmounted(() => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
      removeLogoutListener()
    })
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
    notifyUserDisconnected,
    getPlayerConnectionStatus,
    initializeConnection,
    initializePlayersStatus,
    cleanup
  }
}
