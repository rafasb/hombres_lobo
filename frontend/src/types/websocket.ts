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
 * Interfaz unificada para diferentes contextos de conexión
 */
export interface PlayerStatus {
  playerId: string
  username: string
  status: 'active' | 'banned' | 'connected' | 'disconnected' | 'in_game'
  isConnected: boolean
  lastSeen: Date | null  // null cuando nunca se ha conectado
}

/**
 * Alias para compatibilidad con componentes que usan nomenclatura específica
 * @deprecated Use PlayerStatus directamente
 */
export type PlayerConnectionStatus = PlayerStatus

/**
 * Tipos de mensajes WebSocket específicos del juego
 * Deben estar sincronizados con MessageType en backend/app/websocket/messages.py
 */
export type WebSocketMessageType =
  // Conexión y estado de usuario
  | 'player_connected'
  | 'player_disconnected'
  | 'player_left_game'
  | 'user_status_changed'
  | 'update_user_status'
  | 'user_status_update'
  | 'user_connection_status'
  // Comandos de juego
  | 'join_game'
  | 'start_game'
  | 'restart_game'
  | 'get_game_status'
  | 'force_next_phase'
  // Fases del juego
  | 'phase_changed'
  | 'phase_timer'
  // Votaciones
  | 'cast_vote'
  | 'get_voting_status'
  | 'vote_cast'
  | 'voting_started'
  | 'voting_ended'
  | 'voting_results'
  // Acciones de roles
  | 'role_action'
  | 'night_action'
  // Eventos del juego
  | 'player_eliminated'
  | 'player_role_revealed'
  | 'game_started'
  | 'game_ended'
  // Sistema
  | 'heartbeat'
  | 'error'
  | 'success'
  | 'system_message'
  // Estado de conexión y jugadores
  | 'game_connection_state'
  | 'players_status_update'

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
