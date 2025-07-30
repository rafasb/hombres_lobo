/**
 * Composable para manejar WebSocket de juego
 * Proporciona una interfaz reactiva para la comunicación en tiempo real
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRealtimeGameStore } from '@/stores/realtime-game'
import { useRoute } from 'vue-router'

export function useGameWebSocket() {
  const realtimeGameStore = useRealtimeGameStore()
  const route = useRoute()

  // Estados locales
  const isConnecting = ref(false)
  const connectionAttempts = ref(0)
  const maxAttempts = 3

  /**
   * Conectar automáticamente si estamos en una ruta de juego
   */
  const autoConnect = async () => {
    const gameId = route.params.gameId as string
    if (gameId && !realtimeGameStore.isConnected) {
      await connectToGame(gameId)
    }
  }

  /**
   * Conectar al juego con reintentos
   */
  const connectToGame = async (gameId: string): Promise<boolean> => {
    if (isConnecting.value) return false

    isConnecting.value = true
    connectionAttempts.value = 0

    while (connectionAttempts.value < maxAttempts) {
      try {
        connectionAttempts.value++
        console.log(`Intento de conexión ${connectionAttempts.value}/${maxAttempts}`)

        const success = await realtimeGameStore.connectToGame(gameId)
        if (success) {
          isConnecting.value = false
          connectionAttempts.value = 0
          return true
        }

        // Esperar antes del siguiente intento
        if (connectionAttempts.value < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 2000))
        }

      } catch (error) {
        console.error(`Error en intento ${connectionAttempts.value}:`, error)
      }
    }

    isConnecting.value = false
    return false
  }

  /**
   * Desconectar del juego
   */
  const disconnect = () => {
    realtimeGameStore.disconnectFromGame()
    connectionAttempts.value = 0
    isConnecting.value = false
  }

  /**
   * Enviar mensaje de chat
   */
  const sendChatMessage = (message: string, channel: string = 'all') => {
    if (!realtimeGameStore.isConnected) {
      console.warn('No conectado al WebSocket')
      return false
    }
    return realtimeGameStore.sendMessage(message, channel)
  }

  /**
   * Acciones de juego
   */
  const gameActions = {
    joinGame: () => realtimeGameStore.requestJoinGame(),
    startGame: () => realtimeGameStore.requestStartGame(),
    getStatus: () => realtimeGameStore.requestGameStatus(),
  }

  // Lifecycle hooks
  onMounted(() => {
    // Auto-conectar si estamos en una ruta de juego
    autoConnect()
  })

  onUnmounted(() => {
    // Desconectar al salir del componente
    disconnect()
  })

  // Watch para cambios de ruta
  watch(
    () => route.params.gameId,
    (newGameId, oldGameId) => {
      if (newGameId !== oldGameId) {
        if (oldGameId) {
          disconnect()
        }
        if (newGameId) {
          connectToGame(newGameId as string)
        }
      }
    }
  )

  return {
    // Estado de conexión
    isConnected: realtimeGameStore.isConnected,
    isConnecting,
    connectionError: realtimeGameStore.connectionError,
    connectionAttempts,

    // Estado del juego
    gameState: realtimeGameStore.gameState,
    currentUser: realtimeGameStore.currentUser,
    isUserAlive: realtimeGameStore.isUserAlive,
    canVote: realtimeGameStore.canVote,

    // Acciones
    connectToGame,
    disconnect,
    sendChatMessage,
    ...gameActions
  }
}
