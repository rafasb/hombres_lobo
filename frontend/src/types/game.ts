/**
 * Tipos y interfaces relacionados con partidas/juegos
 */

/**
 * Estados posibles de una partida
 */
export type GameStatus = 'waiting' | 'started' | 'night' | 'day' | 'paused' | 'finished'

/**
 * Interfaz para un jugador en una partida
 */
export interface GamePlayer {
  id: string
  username: string
  [key: string]: any // Para permitir propiedades adicionales
}

/**
 * Interfaz para una partida
 */
export interface Game {
  id: string
  name: string
  max_players: number
  creator_id: string
  players: GamePlayer[] // Array de objetos jugador
  status: GameStatus
  created_at?: string
  current_round?: number
}

/**
 * Respuesta del servicio al unirse a una partida
 */
export interface JoinGameResponse {
  game_id: string
  current_players: number
  max_players: number
}

/**
 * Respuesta del servicio al abandonar una partida
 */
export interface LeaveGameResponse {
  game_id: string
  remaining_players: number
}

/**
 * Respuesta del servicio al eliminar una partida
 */
export interface DeleteGameResponse {
  deleted_game_id: string
}

/**
 * Respuesta del servicio al asignar roles
 */
export interface AssignRolesResponse {
  game: Game
  assigned_roles_count: number
  players_with_roles: number
}

/**
 * Respuesta del servicio al actualizar estado de partida
 */
export interface UpdateGameStatusResponse {
  game: Game
  previous_status: string
  new_status: string
}

/**
 * Respuesta del servicio al actualizar propiedades de partida
 */
export interface UpdateGameResponse {
  game: Game
  updated_fields: string[]
}

/**
 * Recuento de votos para un objetivo
 */
export interface VoteCount {
  target_id: string
  votes: number
}

/**
 * Respuesta genérica para el voto
 */
export interface CastVoteResponse {
  success?: boolean
  error?: string
}
