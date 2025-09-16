/**
 * Composable para integrar stores de Pinia con WebSocket
 * 
 * Proporciona una forma centralizada para que los stores se suscriban
 * a mensajes WebSocket específicos y mantengan su estado actualizado
 * automáticamente basándose en eventos del backend.
 */

import { onUnmounted } from 'vue'
import { useWebSocket } from '../websocket/WebSocketManager'
import type { 
  WebSocketMessageType, 
  WebSocketMessageMap,
  MessageHandler 
} from '../types'

/**
 * Hook para suscribir stores a mensajes WebSocket específicos
 * 
 * @example
 * ```typescript
 * // En un store de Pinia
 * const { subscribeToMessage } = useWebSocketStore()
 * 
 * subscribeToMessage('user_status_changed', (data) => {
 *   // Actualizar estado del store basándose en el mensaje
 *   this.setStatus(data.new_status)
 * })
 * ```
 */
export function useWebSocketStore() {
  const { getConnection } = useWebSocket()
  const unsubscribeFunctions: (() => void)[] = []

  /**
   * Suscribirse a un tipo específico de mensaje WebSocket
   * La suscripción se limpia automáticamente cuando el componente/store se desmonta
   */
  function subscribeToMessage<K extends WebSocketMessageType>(
    messageType: K,
    handler: MessageHandler<WebSocketMessageMap[K]>
  ): () => void {
    const connection = getConnection()
    
    if (!connection) {
      console.warn(`[useWebSocketStore] No hay conexión WebSocket disponible para suscribirse a '${messageType}'`)
      return () => {} // Return a no-op function
    }

    // Crear wrapper del handler para manejar errores
    const safeHandler: MessageHandler<WebSocketMessageMap[K]> = (data) => {
      try {
        handler(data)
      } catch (error) {
        console.error(`[useWebSocketStore] Error in handler for '${messageType}':`, error)
      }
    }

    const unsubscribe = connection.subscribe(messageType, safeHandler)
    unsubscribeFunctions.push(unsubscribe)
    
    return unsubscribe
  }

  /**
   * Suscribirse a múltiples tipos de mensajes con un solo handler
   * Útil cuando varios tipos de mensaje requieren la misma lógica
   */
  function subscribeToMessages<K extends WebSocketMessageType>(
    messageTypes: K[],
    handler: MessageHandler<WebSocketMessageMap[K]>
  ): () => void {
    const unsubscribes = messageTypes.map(type => subscribeToMessage(type, handler))
    
    return () => {
      unsubscribes.forEach(unsub => unsub())
    }
  }

  /**
   * Verificar si hay una conexión WebSocket activa
   */
  function hasActiveConnection(): boolean {
    const connection = getConnection()
    return connection?.status.value.isConnected ?? false
  }

  /**
   * Obtener el estado de la conexión WebSocket
   */
  function getConnectionStatus() {
    const connection = getConnection()
    return connection?.status.value
  }

  // Limpiar todas las suscripciones cuando se desmonta
  onUnmounted(() => {
    unsubscribeFunctions.forEach(unsubscribe => unsubscribe())
    unsubscribeFunctions.length = 0
  })

  return {
    subscribeToMessage,
    subscribeToMessages,
    hasActiveConnection,
    getConnectionStatus
  }
}

/**
 * Tipos de mensajes organizados por categoría para facilitar las suscripciones
 */
export const WebSocketMessageCategories = {
  // Mensajes relacionados con el estado del usuario
  USER_STATUS: [
    'user_status_changed',
    'user_connection_status'
  ] as const,

  // Mensajes relacionados con conexión de jugadores
  PLAYER_CONNECTION: [
    'player_disconnected', 
    'player_banned',
    'player_left_game'
  ] as const,

  // Mensajes relacionados con el estado del juego
  GAME_STATE: [
    'game_started',
    'game_ended',
    'game_restarted',
    'game_status',
    'game_connection_state'
  ] as const,

  // Mensajes relacionados con fases del juego
  GAME_PHASES: [
    'phase_changed',
    'phase_timer'
  ] as const,

  // Mensajes relacionados con votaciones
  VOTING: [
    'voting_started',
    'voting_ended',
    'vote_cast',
    'voting_results'
  ] as const,

  // Mensajes relacionados con roles y acciones
  ROLES: [
    'role_action',
    'night_action',
    'player_eliminated',
    'player_role_revealed'
  ] as const,

  // Mensajes del sistema
  SYSTEM: [
    'error',
    'success',
    'system_message',
    'heartbeat'
  ] as const,

  // Mensajes relacionados con el estado de jugadores
  PLAYERS_STATUS: [
    'players_status_update'
  ] as const
} as const

/**
 * Utility para obtener tipos de mensajes por categoría
 */
export type UserStatusMessages = typeof WebSocketMessageCategories.USER_STATUS[number]
export type PlayerConnectionMessages = typeof WebSocketMessageCategories.PLAYER_CONNECTION[number]
export type GameStateMessages = typeof WebSocketMessageCategories.GAME_STATE[number]
export type GamePhaseMessages = typeof WebSocketMessageCategories.GAME_PHASES[number]
export type VotingMessages = typeof WebSocketMessageCategories.VOTING[number]
export type RoleMessages = typeof WebSocketMessageCategories.ROLES[number]
export type SystemMessages = typeof WebSocketMessageCategories.SYSTEM[number]
export type PlayerStatusMessages = typeof WebSocketMessageCategories.PLAYERS_STATUS[number]
