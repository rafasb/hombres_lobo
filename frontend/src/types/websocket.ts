/**
 * Tipos y interfaces relacionados con WebSocket
 * Centralización de definiciones para comunicación en tiexport type WebSocketMessageType =
  // Conexión y estado de usuario
  | 'player_connected'
  | 'player_disconnected'
  | 'player_banned'
  | 'player_left_game'
  | 'user_status_changed'
  | 'user_connection_status'
  // Comandos de juego
  | 'in_game'
  | 'join_game'          // Frontend command (not in backend enum)
  | 'start_game'         // Frontend command (not in backend enum)
  | 'restart_game'
  | 'game_status'
  | 'force_next_phase'   // Frontend command (not in backend enum)*
 * Interfaz base para mensajes de WebSocket
 */
/**
 * Interfaz base para mensajes de WebSocket (genérica)
 * Se sugiere usar `GameWebSocketMessage` (discriminated union) en lugar de esta interfaz directa.
 * Sincronizada con WebSocketMessageV2 en backend que incluye: type, timestamp, data
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
 * Códigos de error WebSocket sincronizados con ErrorCode en backend
 */
export type WebSocketErrorCode =
  | 'INVALID_MESSAGE'
  | 'UNKNOWN_MESSAGE_TYPE'
  | 'INVALID_MESSAGE_TYPE'
  | 'INTERNAL_ERROR'
  | 'GAME_NOT_FOUND'
  | 'GAME_NOT_STARTED'
  | 'USER_NOT_IN_GAME'
  | 'NOT_AUTHORIZED'
  | 'INVALID_ACTION'
  | 'INVALID_PHASE'
  | 'VOTE_NOT_ALLOWED'
  | 'PHASE_CHANGE_FAILED'
  | 'PHASE_FORCE_FAILED'
  | 'PLAYER_NOT_FOUND'
  | 'PLAYER_ALREADY_ELIMINATED'
  | 'ROLE_ACTION_NOT_ALLOWED'
  | 'JOIN_ERROR'
  | 'START_GAME_ERROR'
  | 'RESTART_GAME_ERROR'
  | 'INSUFFICIENT_PERMISSIONS'
  | 'STATUS_ERROR'
  | 'MISSING_FIELD'
  | 'INVALID_CONNECTION'
  | 'INVALID_USER'
  | 'INVALID_STATUS'
  | 'UPDATE_FAILED'

/**
 * Tipos de mensajes del sistema sincronizados con SystemMessageType en backend
 */
export type SystemMessageType =
  | 'info'
  | 'warning'
  | 'error'
  | 'connected_to_game'
  | 'disconnected_from_game'
  | 'player_joined'
  | 'player_left'
  | 'player_banned'
  | 'game_started'
  | 'game_ended'
  | 'phase_changed'
  | 'voting_started'
  | 'voting_ended'
  | 'player_eliminated'

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
 * Sincronizados con MessageType en backend/app/websocket/messages_types.py
 */
export type WebSocketMessageType =
  // Conexión y estado de usuario
  | 'player_connected'
  | 'player_disconnected'
  | 'player_banned'
  | 'player_left_game'
  | 'user_status_changed'
  | 'user_connection_status'
  // Comandos de juego
  | 'in_game'
  | 'join_game'          // Frontend command (not in backend enum)
  | 'start_game'         // Frontend command (not in backend enum)
  | 'restart_game'
  | 'game_status'
  | 'force_next_phase'   // Frontend command (not in backend enum)
  // Fases del juego
  | 'phase_changed'
  | 'phase_timer'
  | 'game_started'
  | 'game_ended'
  | 'game_restarted'
  // Votaciones
  | 'vote_cast'
  | 'voting_started'
  | 'voting_ended'
  | 'voting_results'
  | 'cast_vote'          // Frontend command (not in backend enum)
  | 'get_voting_status'  // Frontend command (not in backend enum)
  // Acciones de roles
  | 'role_action'
  | 'night_action'
  // Eventos del juego
  | 'player_eliminated'
  | 'player_role_revealed'
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
 * Map de payloads por tipo de mensaje. Sincronizado con las clases de mensaje
 * en backend/app/websocket/messages_types.py
 */
export interface WebSocketMessageMap {
  // Aquí se relaciona el TIPO de mensaje con el contenido de DATA
  // Conexión y estado de usuario (WsPlayerConnectionMessage)
  player_connected: { user_id: string; username: string }
  player_disconnected: { user_id: string; username: string }
  player_banned: { user_id: string; username: string }
  player_left_game: { playerId: string }
  user_status_changed: { user_id: string; old_status: string; new_status: string }
  user_connection_status: { isConnected: boolean; isInGame: boolean }

  // Comandos de juego
  in_game: string  // User ID
  join_game: undefined
  start_game: undefined
  restart_game: undefined
  game_status: { 
    game_id: string; 
    name: string;
    creator_id: string;
    creator_name: string;
    status: string;
    current_round: number;
    is_first_night: boolean;
    max_players: number;
    current_players: number;
    players: Array<{ 
      player_id: string; 
      username: string; 
      is_alive: boolean; 
      // is_connected: boolean; ELIMINADO EN BACKEND
      user_status: string; 
    }>;
    eliminated_players: string[];
    connected_players_count: number;
    created_at: string;
    success: boolean;
    message: string;
  }
  force_next_phase: undefined

  // Fases del juego (WsPhaseChangedMessage, WsTimerMessage)
  phase_changed: { previous?: string; current: string; duration: number }
  phase_timer: { phase: string; remainingSeconds: number; game_id?: string; user_id?: string }
  game_started: { 
    players: Array<{ id: string; name: string }>; 
    roles_assigned: boolean 
  }
  game_ended: { 
    winning_team: string; 
    winners: string[]; 
    final_roles: Record<string, string> 
  }
  game_restarted: string  // Message

  // Votaciones (WsVotingStartedMessage, WsVotingEndedMessage, WsVoteMessage)
  vote_cast: { voter_id: string; target_id: string; vote_type: string }
  voting_started: { 
    vote_type: string; 
    duration: number; 
    game_id: string; 
    eligible_voters: string[]; 
    vote_targets: string[] 
  }
  voting_ended: { 
    vote_type: string; 
    game_id: string; 
    results: Record<string, number>; 
    eliminated_player?: string; 
    is_tie: boolean 
  }
  voting_results: { results: Record<string, number> }
  cast_vote: { voter_id: string; target_id: string }
  get_voting_status: undefined

  // Acciones de roles (WsRoleActionMessage)
  role_action: { actor_id: string; action: string; target_id?: string }
  night_action: { actor_id: string; action: string }

  // Eventos del juego (WsPlayerEliminatedMessage)
  player_eliminated: { 
    player_id: string; 
    player_name: string; 
    role?: string; 
    elimination_type: string 
  }
  player_role_revealed: { player_id: string; role: string }

  // Sistema (WsMessageError, WsMessageSuccess, WsSystemMessage)
  heartbeat: { response?: string } | undefined
  error: { error_code: WebSocketErrorCode; message: string; details?: Record<string, unknown> }
  success: { message: string }
  system_message: { 
    message: string; 
    message_key?: SystemMessageType; 
    params?: Record<string, unknown> 
  }

  // Estado de conexión y jugadores (WsGameConnectionStateMessage, WsPlayersStatusUpdateMessage)
  game_connection_state: {
    isUserConnected: boolean
    isUserInGame: boolean
    connectedPlayersCount: number
    totalPlayersCount: number
    playersStatus: PlayerDTO[]
    lastUpdate: string | Date
  }
  players_status_update: { playersStatus: PlayerDTO[] }
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
