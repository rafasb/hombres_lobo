/**
 * Tipos y interfaces relacionados con partidas/juegos
 */

/**
 * Estados posibles de una partida
 */
export type GameStatus = 'waiting' | 'starting' | 'started' | 'night' | 'day' | 'voting' | 'trial' | 'execution' | 'paused' | 'finished'

/**
 * Estados de un jugador en la partida
 */
export type PlayerStatus = 'banned' | 'connected' | 'disconnected' | 'in_game' | 'eliminated'

/**
 * Roles disponibles en el juego
 */
export type Roles = 'villager' | 'seer' | 'sheriff' | 'hunter' | 'witch' | 'wild_child' | 'cupid' | 'warewolf'

/**
 * Información completa del jugador con su rol y estado
 * NOTA: Esta información solo está disponible para el propio jugador y contiene datos sensibles.
 */
export interface PlayerInfo {
  // Campos comunes a todos los jugadores
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
 * Información pública de un jugador que puede ser compartida con todos los participantes.
 * Esta es la información que recibe el frontend desde GameResponse.
 */
export interface PublicPlayerInfo {
  player_id: string
  username: string
  is_alive: boolean
  is_connected: boolean
  user_status: PlayerStatus
}

/**
 * Interfaz para una partida - coincide con GameResponse del backend.
 * Esta es la información pública que recibe el frontend del endpoint GET /game/{game_id}
 */
export interface Game {
  // Información básica de la partida
  game_id: string
  name: string
  creator_id: string
  creator_name: string
  
  // Estado actual de la partida
  status: GameStatus
  current_round: number
  is_first_night: boolean
  
  // Información de jugadores
  max_players: number
  current_players: number
  players: PublicPlayerInfo[]  // Lista de información pública de jugadores
  eliminated_players: string[]  // IDs de jugadores eliminados
  connected_players_count: number
  
  // Información temporal
  created_at: string | null
  
  // Metadatos
  success: boolean
  message: string
}

/**
 * Respuesta simplificada para actualizaciones de estado del juego via WebSocket.
 * Coincide con GameStateUpdateResponse del backend.
 */
export interface GameStateUpdate {
  game_id: string
  status: GameStatus
  current_round: number
  current_players: number
  connected_players_count: number
  players: PublicPlayerInfo[]
  eliminated_players: string[]
  
  // Tipo de actualización para el frontend
  update_type: string
  timestamp: string | null
}

/** Respuesta del servicio para listar partidas */
export interface GameSummary {
  id: string
  name: string
  creator_name: string
  creator_id: string
  created_at: string | null
  current_round: number | null
  current_players: number
  max_players: number
  status: string
  player_ids: string[] // Opcional, para validaciones de permisos
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
 * Interfaz temporal para mantener compatibilidad con endpoints que aún devuelven
 * el objeto Game completo del backend (con información sensible).
 * TODO: Migrar estos endpoints para que usen GameResponse en su lugar.
 */
export interface LegacyGame {
  id: string
  name: string
  max_players: number
  creator_id: string
  player_ids: string[] // IDs de jugadores (antes de empezar la partida)
  players: Record<string, PlayerInfo> // Información de roles por player_id
  status: GameStatus
  created_at: string // Required in API
  current_round: number
  is_first_night: boolean // Indica si es la primera noche
  night_actions: Record<string, Record<string, string>> // Acciones nocturnas por tipo y jugador
  eliminated_players: string[] // Jugadores eliminados - según API
  connected_players: string[] // Jugadores conectados - según API  
  votes: Record<string, string> // Votos actuales: voter_id -> target_id (según API, no day_votes)
}

/**
 * Respuesta del servicio al asignar roles
 * TODO: Migrar para usar GameResponse en lugar de LegacyGame
 */
export interface AssignRolesResponse {
  game: LegacyGame
  assigned_roles_count: number
  players_with_roles: number
}

/**
 * Respuesta del servicio al actualizar estado de partida
 * TODO: Migrar para usar GameResponse en lugar de LegacyGame
 */
export interface UpdateGameStatusResponse {
  game: LegacyGame
  previous_status: string
  new_status: string
}

/**
 * Respuesta del servicio al actualizar propiedades de partida
 * TODO: Migrar para usar GameResponse en lugar de LegacyGame
 */
export interface UpdateGameResponse {
  game: LegacyGame
  updated_fields: string[]
}

/**
 * Recuento de votos para un objetivo según la API
 */
export interface VoteCount {
  player_id: string
  username: string
  vote_count: number
}

/**
 * Respuesta genérica para el voto
 */
export interface CastVoteResponse {
  success?: boolean
  error?: string
}
