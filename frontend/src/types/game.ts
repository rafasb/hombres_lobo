/**
 * Tipos y interfaces relacionados con partidas/juegos
 */

/**
 * Estados posibles de una partida
 */
export type GameStatus = 'waiting' | 'starting' | 'started' | 'night' | 'day' | 'voting' | 'trial' | 'execution' | 'paused' | 'finished'

/**
 * Roles disponibles en el juego
 */
export type Roles = 'villager' | 'seer' | 'sheriff' | 'hunter' | 'witch' | 'wild_child' | 'cupid' | 'warewolf'

/**
 * Información completa del jugador con su rol y estado
 */
export interface PlayerInfo {
  // Campos comunes a todos los roles
  role: Roles
  player_id: string
  is_alive: boolean
  lover_partner_id?: string

  // Campos generales para habilidades nocturnas / tracking
  has_acted_tonight?: boolean
  target_player_id?: string

  // Niño salvaje (Wild Child)
  model_player_id?: string
  has_transformed?: boolean

  // Bruja (Witch)
  has_healing_potion?: boolean
  has_poison_potion?: boolean

  // Alguacil (Sheriff)
  has_double_vote?: boolean
  can_break_ties?: boolean
  successor_id?: string

  // Cazador (Hunter)
  can_revenge_kill?: boolean

  // Cupido
  has_cupid_action?: boolean

  // Permitir campos adicionales para compatibilidad
  [key: string]: any
}

/**
 * Interfaz para un jugador en una partida (datos básicos de usuario)
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
  player_ids: string[] // IDs de jugadores (antes de empezar la partida)
  players: Record<string, PlayerInfo> // Información de roles por player_id
  status: GameStatus
  created_at?: string
  current_round: number
  is_first_night: boolean // Indica si es la primera noche
  night_actions: Record<string, Record<string, string>> // Acciones nocturnas por tipo y jugador
  day_votes: Record<string, string> // Votos diurnos: voter_id -> target_id
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
