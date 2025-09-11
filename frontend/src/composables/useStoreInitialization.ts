import { onMounted, onUnmounted } from 'vue'
import { useUserStore } from '../stores/userStore'
import { usePlayerStore } from '../stores/playerStore'
import { useGameStore } from '../stores/gameStore'
import { useWebSocketStore } from './useWebSocketStore'

/**
 * Composable para inicializar las suscripciones WebSocket de los stores
 * 
 * Gestiona la inicialización de tres stores diferentes:
 * - UserStore: Información de usuario y autenticación
 * - PlayerStore: Información privada del jugador actual (rol, habilidades, etc.)
 * - GameStore: Información pública de la partida y todos los jugadores
 * 
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
   * 
   * Cada store maneja diferentes tipos de información:
   * - UserStore: Estado de conexión, autenticación, información básica del usuario
   * - PlayerStore: Información privada del jugador actual (rol, habilidades, pociones, etc.)
   * - GameStore: Estado público de la partida (lista de jugadores, fase actual, votaciones, etc.)
   * 
   * Los stores inicializarán sus suscripciones cuando haya una conexión WebSocket disponible
   */
  const initializeStores = async () => {
    try {
      console.log('[StoreInitialization] Inicializando stores con nueva arquitectura...')
      console.log('[StoreInitialization] - UserStore: Maneja autenticación y estado de usuario')
      console.log('[StoreInitialization] - PlayerStore: Maneja información privada del jugador actual')
      console.log('[StoreInitialization] - GameStore: Maneja estado público de la partida')
      
      // Verificar si hay conexión WebSocket activa
      const isConnected = hasActiveConnection()
      const connectionStatus = getConnectionStatus()
      
      console.log('[StoreInitialization] Estado de conexión:', { isConnected, connectionStatus })

      // Inicializar suscripciones de cada store en orden lógico
      // UserStore: Base para autenticación y estado de usuario
      userStore.initializeWebSocketSubscriptions()
      
      // GameStore: Estado público de la partida (debe inicializarse antes que PlayerStore)
      gameStore.initializeWebSocketSubscriptions()
      
      // PlayerStore: Información privada del jugador actual
      playerStore.initializeWebSocketSubscriptions()

      console.log('[StoreInitialization] Stores inicializados correctamente con nueva arquitectura')
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
   * Cargar información específica de la partida desde la API
   * Útil para obtener datos iniciales cuando el usuario entra a una partida
   */
  const loadGameData = async (gameId: string) => {
    try {
      console.log('[StoreInitialization] Cargando datos iniciales de la partida:', gameId)
      
      // Establecer el gameId en el store
      gameStore.setGameId(gameId)
      
      // TODO: Aquí se podría llamar al gameService para obtener:
      // - Información pública de la partida (ya se maneja via WebSocket)
      // - Información privada del jugador actual desde la API
      // 
      // Ejemplo:
      // const playerInfo = await playerService.getCurrentPlayerInfo(gameId)
      // if (playerInfo) {
      //   playerStore.setCurrentPlayer(playerInfo)
      // }
      
      console.log('[StoreInitialization] Datos de partida cargados correctamente')
    } catch (error) {
      console.error('[StoreInitialization] Error cargando datos de partida:', error)
    }
  }

  /**
   * Inicializar automáticamente al montar (para stores globales como navegación)
   * 
   * Útil para componentes que necesitan:
   * - Estado de autenticación (UserStore)
   * - Estado general de conexión
   * - Pero NO información específica de partida
   */
  const initializeGlobalStores = () => {
    onMounted(async () => {
      await initializeStores() // Inicializa todos los stores pero con suscripciones básicas
    })

    onUnmounted(() => {
      cleanup()
    })
  }

  /**
   * Inicializar stores específicos de juego (para componentes dentro de una partida)
   * 
   * Útil para componentes que necesitan:
   * - Información completa del juego (GameStore)
   * - Información privada del jugador actual (PlayerStore)
   * - Estado de autenticación (UserStore)
   * 
   * Debe usarse en GameLobbyView, GameView, y componentes similares
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
    loadGameData,    // Función para cargar datos específicos de partida
    cleanup,
    // Estados reactivos de los stores (sin inicialización automática)
    userStore,      // Información de usuario y autenticación
    playerStore,    // Información privada del jugador actual
    gameStore       // Estado público de la partida
  }
}

/**
 * Composable simplificado para componentes que solo necesitan acceso reactivo a los stores
 * sin inicializar WebSocket (por ejemplo, componentes de navegación, modales, etc.)
 * 
 * Casos de uso:
 * - Navegación que muestra nombre de usuario
 * - Modales que necesitan verificar estado de autenticación
 * - Componentes que solo leen datos ya cargados
 */
export function useStoreAccess() {
  const userStore = useUserStore()
  const playerStore = usePlayerStore() 
  const gameStore = useGameStore()

  return {
    userStore,      // Solo lectura de información de usuario
    playerStore,    // Solo lectura de información privada del jugador
    gameStore       // Solo lectura de estado público de la partida
  }
}
