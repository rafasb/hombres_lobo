/**
 * Tipos y interfaces relacionados con WebSocket
 * Centralización de definiciones para comunicación en tiempo real
 */

/**
 * Interfaz base para mensajes de WebSocket
 */
export interface WebSocketMessage {
  type: string
  data?: any
  timestamp?: string
}

/**
 * Estados específicos de conexión WebSocket
 */
export interface ConnectionStatus {
  isConnected: boolean
  isReconnecting: boolean
  lastConnected: Date | null
  reconnectAttempts: number
  error: string | null
}

/**
 * Estado de un jugador en la conexión
 */
export interface PlayerStatus {
  playerId: string
  username: string
  isConnected: boolean
  lastSeen: Date
}

/**
 * Tipos de mensajes WebSocket específicos del juego
 */
export type WebSocketMessageType = 
  | 'game_update'
  | 'player_joined'
  | 'player_left'
  | 'game_started'
  | 'phase_change'
  | 'vote_cast'
  | 'role_assigned'
  | 'player_eliminated'
  | 'game_ended'
  | 'heartbeat'
  | 'error'

/**
 * Interfaz extendida para mensajes tipados del juego
 */
export interface GameWebSocketMessage extends WebSocketMessage {
  type: WebSocketMessageType
}

/**
 * Configuración para managers de WebSocket
 */
export interface WebSocketConfig {
  url: string
  token?: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
}

/**
 * Interfaz para handlers de mensajes
 */
export type MessageHandler<T = any> = (data: T) => void

/**
 * Mapa de handlers por tipo de mensaje
 */
export type MessageHandlersMap = Map<string, MessageHandler[]>
