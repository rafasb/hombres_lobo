/**
 * Archivo de índice para tipos
 * Facilita la importación de tipos desde un punto central
 */

// Exportar tipos de usuario
export type {
  BaseUser,
  User,
  AdminUser,
  AuthUser,
  UserRole,
  UserStatus
} from './user'

// Exportar tipos de juego
export type {
  Game,
  GamePlayer,
  GameStatus,
  JoinGameResponse,
  LeaveGameResponse,
  DeleteGameResponse,
  AssignRolesResponse,
  UpdateGameStatusResponse,
  UpdateGameResponse
} from './game'

// Export the additional game-related helper types
export type { VoteCount, CastVoteResponse } from './game'

// Exportar tipos de WebSocket
export type {
  WebSocketMessage,
  ConnectionStatus,
  PlayerStatus,
  PlayerConnectionStatus,
  WebSocketMessageMap,
  WebSocketMessageType,
  GameWebSocketMessage,
  WebSocketConfig,
  MessageHandler,
  MessageHandlersMap
} from './websocket'
