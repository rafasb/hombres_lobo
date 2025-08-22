import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWebSocket, WebSocketManager } from '../websocket/WebSocketManager'
import { useAuthStore, logoutEventBus } from '../stores/authStore'
import type { PlayerStatus } from '../types'

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
  const { createConnection, connectionStatus } = useWebSocket(gameId)
  
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

      console.log('Initializing WebSocket connection for game:', gameId)
      wsManager = createConnection(auth.token)

  await wsManager.connect()
  console.log('WebSocket connection established')
  // Enviar mensaje join_game tras conectar, según la recomendación del backend
  wsManager.send({ type: 'join_game' })

      // Suscribirse a mensajes de estado del juego - adaptador para el backend
      const unsubGameState = wsManager.subscribe('system_message', (message: { message: string; players?: any[]; params?: Record<string, any>; message_key?: string | null } | undefined) => {
        console.log('System message received:', message)
        // Usar message.data.players según la documentación del backend
        const playersList = (message as any)?.data?.players || (message as any)?.players
        if (playersList) {
          const connectedPlayers = (message as any)?.data?.connected_players || (message as any)?.connected_players
          const playersStatus: PlayerStatus[] = playersList.map((player: any) => {
            // Determinar el status real del jugador
            let status: PlayerStatus['status'] = 'disconnected';
            if (player.status && ['active','banned','connected','disconnected','in_game'].includes(player.status)) {
              status = player.status;
            } else if (connectedPlayers?.includes(player.id)) {
              status = 'connected';
            }
            return {
              playerId: player.id,
              username: player.name,
              status,
              isConnected: status === 'connected' || status === 'active' || status === 'in_game',
              lastSeen: new Date()
            }
          })

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

      // Suscribirse a cambios de estado de usuario según la referencia WebSocket
      const unsubUserStatusChanged = wsManager.subscribe('user_status_changed', (data: { user_id: string; old_status?: string; new_status: string; message?: string }) => {
        console.log('User status changed:', data)
        const currentPlayers = [...gameConnectionState.value.playersStatus]
        const existingPlayer = currentPlayers.find(p => p.playerId === data.user_id)
        if (existingPlayer) {
          // Actualizar status y isConnected
          if (['active','banned','connected','disconnected','in_game'].includes(data.new_status)) {
            existingPlayer.status = data.new_status as PlayerStatus['status']
          } else {
            existingPlayer.status = 'disconnected'
          }
          existingPlayer.isConnected = existingPlayer.status === 'connected' || existingPlayer.status === 'active' || existingPlayer.status === 'in_game'
          existingPlayer.lastSeen = new Date()
          // Actualizar el estado global
          gameConnectionState.value.playersStatus = currentPlayers
          gameConnectionState.value.connectedPlayersCount = currentPlayers.filter(p => p.isConnected).length
          gameConnectionState.value.lastUpdate = new Date()
          console.log('Updated connection state:', gameConnectionState.value)
        }
      })

      // Suscribirse a respuestas exitosas de cambio de estado
      const unsubSuccess = wsManager.subscribe('success', (data: { action: string; message: string; data?: Record<string, any> } | undefined) => {
        if (data?.action === 'update_user_status') {
          console.log('Status update success:', data)
          // El estado ya se actualiza con user_status_changed, pero podemos loguear
        }
      })

      // Suscribirse a errores de cambio de estado
      const unsubError = wsManager.subscribe('error', (data: { error_code?: string; message?: string; details?: Record<string, any> } | undefined) => {
        console.error('WebSocket error:', data)
        if (data?.error_code === 'INSUFFICIENT_PERMISSIONS') {
          console.error('Permission error:', data.message)
        }
      })

      // Suscribirse a heartbeat del backend
      const unsubHeartbeat = wsManager.subscribe('heartbeat', (data: { response?: string } | undefined) => {
        // El backend envía heartbeat, no necesitamos responder pong específicamente
        // ya que el backend espera heartbeat de vuelta
        if (data?.response === 'pong') {
          // Este es un pong del servidor, no necesitamos hacer nada
        } else {
          // Este es un ping del servidor, responder con heartbeat
          wsManager?.send({ type: 'heartbeat' })
        }
      })

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
      // Crear mensaje personalizado para cambio de estado
      wsManager.send({
        type: 'update_user_status',
        data: { status },
        status // También en nivel superior por compatibilidad
      } as any) // Usamos any para agregar la propiedad status
    }
  }

  // Notificar que el usuario entró al lobby
  const notifyUserJoinedLobby = () => {
    // Cambiar estado del usuario a 'active' cuando se une al lobby
    updateUserStatus('in_game')
  }

  // Notificar que el usuario salió del lobby
  const notifyUserLeftLobby = () => {
    // Cambiar estado del usuario a 'active' cuando sale del lobby
    updateUserStatus('active')
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
