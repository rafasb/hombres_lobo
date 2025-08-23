/**
 * Tipos y interfaces relacionados con WebSocket
 * Centralización de definiciones para comunicación en tiempo real
 */

/**
 * Interfaz base para mensajes de WebSocket
 */
/**
 * Interfaz base para mensajes de WebSocket (genérica)
 * Se sugiere usar `GameWebSocketMessage` (discriminated union) en lugar de esta interfaz directa.
 */
export interface WebSocketMessage<T = unknown> {
  type: string
  data?: T
  timestamp?: string
}

/** DTO para representar jugadores en mensajes del backend. */
export interface PlayerDTO {
  id: string
  username?: string
  name?: string
  status?: string
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
  status: 'banned' | 'connected' | 'disconnected' | 'in_game'
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
/**
 * Map de payloads por tipo de mensaje. Añadir o ajustar interfaces aquí según
 * lo que envía el backend (sincronizar con openapi.json / backend).
 */
export interface WebSocketMessageMap {
  // Conexión y estado de usuario
  player_connected: { playerId: string; username: string }
  player_disconnected: { playerId: string }
  player_left_game: { playerId: string }
  user_status_changed: { user_id: string; old_status?: string; new_status: string; message?: string }
  update_user_status: { status: string }
  user_status_update: { user_id: string; status: string }
  user_connection_status: { isConnected: boolean; isInGame: boolean }

  // Comandos de juego (generalmente sin payload)
  join_game: undefined
  start_game: undefined
  restart_game: undefined
  get_game_status: undefined
  force_next_phase: undefined

  // Fases del juego
  phase_changed: { previous: string; current: string }
  phase_timer: { remainingSeconds: number }

  // Votaciones
  cast_vote: { voter_id: string; target_id: string }
  get_voting_status: undefined
  vote_cast: { voter_id: string; target_id: string }
  voting_started: { options?: Record<string, unknown> }
  voting_ended: { results?: Record<string, unknown> }
  voting_results: { results: Record<string, number> }

  // Acciones de roles
  role_action: { actor_id: string; action: string; target_id?: string }
  night_action: { actor_id: string; action: string }

  // Eventos del juego
  player_eliminated: { player_id: string; player_name?: string; role?: string; elimination_type?: string }
  player_role_revealed: { player_id: string; role: string }
  game_started: { startedAt?: string }
  game_ended: { winner?: string }

  // Sistema
  heartbeat: { response?: string } | undefined
  error: { error_code: string; message: string; details?: Record<string, unknown> }
  success: { action: string; message: string; data?: Record<string, unknown> }
  system_message: { message: string; message_key?: string | null; params?: Record<string, unknown>; players?: PlayerDTO[] }

  // Estado de conexión y jugadores
  game_connection_state: {
    isUserConnected: boolean
    isUserInGame: boolean
    connectedPlayersCount: number
    totalPlayersCount: number
    playersStatus: PlayerDTO[]
    lastUpdate: string | Date
  }
  players_status_update: PlayerDTO[]
}

/**
 * Discriminated union para mensajes del juego: garantiza `type` y el tipo de `data`.
 */
export type GameWebSocketMessage = {
  [K in keyof WebSocketMessageMap]: {
    type: K
    data: WebSocketMessageMap[K]
    timestamp?: string
  }
}[keyof WebSocketMessageMap]

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
export type MessageHandler<T = unknown> = (data: T) => void

/**
 * Mapa de handlers por tipo de mensaje tipado.
 * Usamos Map<WebSocketMessageType, MessageHandler<any>[]> por compatibilidad con
 * implementaciones existentes; los métodos de subscribe pueden refinar el tipo.
 */
export type MessageHandlersMap = Map<WebSocketMessageType, MessageHandler<any>[]>
