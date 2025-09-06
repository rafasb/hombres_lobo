import { onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../stores/user'
import { usePlayerStore } from '../stores/player'
import { useGameStore } from '../stores/gameStore'
import { useWebSocketStore } from './useWebSocketStore'

/**
 * Composable para inicializar las suscripciones WebSocket de los stores
 * Debe ser llamado en componentes que necesiten datos reactivos del WebSocket
 */
export function useStoreInitialization() {
  const userStore = useUserStore()
  const playerStore = usePlayerStore()
  const gameStore = useGameStore()
  const { hasActiveConnection, getConnectionStatus } = useWebSocketStore()

  let cleanupFunctions: (() => void)[] = []

  /**
   * Inicializar todos los stores con suscripciones WebSocket
   * Los stores inicializarán sus suscripciones cuando haya una conexión WebSocket disponible
   */
  const initializeStores = async () => {
    try {
      console.log('[StoreInitialization] Inicializando stores...')
      
      // Verificar si hay conexión WebSocket activa
      const isConnected = hasActiveConnection()
      const connectionStatus = getConnectionStatus()
      
      console.log('[StoreInitialization] Estado de conexión:', { isConnected, connectionStatus })

      // Inicializar suscripciones de cada store
      // Los stores manejarán internamente si hay o no conexión WebSocket
      userStore.initializeWebSocketSubscriptions()
      playerStore.initializeWebSocketSubscriptions()
      gameStore.initializeWebSocketSubscriptions()

      console.log('[StoreInitialization] Stores inicializados correctamente')
    } catch (error) {
      console.error('[StoreInitialization] Error inicializando stores:', error)
    }
  }

  /**
   * Limpiar suscripciones al desmontar el componente
   */
  const cleanup = () => {
    cleanupFunctions.forEach(fn => fn())
    cleanupFunctions = []
    console.log('[StoreInitialization] Cleanup completado')
  }

  /**
   * Inicializar automáticamente al montar (solo stores globales)
   */
  const initializeGlobalStores = () => {
    onMounted(async () => {
      await initializeStores() // Sin gameId para stores globales
    })

    onUnmounted(() => {
      cleanup()
    })
  }

  /**
   * Inicializar stores específicos de juego
   */
  const initializeGameStores = () => {
    onMounted(async () => {
      await initializeStores()
    })

    onUnmounted(() => {
      cleanup()
    })
  }

  return {
    initializeStores,
    initializeGlobalStores,
    initializeGameStores,
    cleanup,
    // Estados reactivos de los stores
    userStore,
    playerStore,
    gameStore
  }
}

/**
 * Composable simplificado para componentes que solo necesitan acceso reactivo a los stores
 * sin inicializar WebSocket (por ejemplo, componentes de navegación)
 */
export function useStoreAccess() {
  const userStore = useUserStore()
  const playerStore = usePlayerStore() 
  const gameStore = useGameStore()

  return {
    userStore,
    playerStore,
    gameStore
  }
}
