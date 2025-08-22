import api from './api'
import type {
  Game,
  JoinGameResponse,
  LeaveGameResponse,
  DeleteGameResponse,
  AssignRolesResponse,
  UpdateGameStatusResponse,
  UpdateGameResponse
} from '../types'

// base URL is provided by `src/services/api.ts` axios instance

export const gameService = {
  /**
   * Obtiene todas las partidas disponibles
   */
  async getGames(): Promise<Game[]> {
  const response = await api.get(`/games`)
    // La nueva API devuelve una estructura con success, message, games y total_games
    return response.data.games
  },

  /**
   * Obtiene una partida específica por ID
   */
  async getGameById(gameId: string): Promise<Game> {
  const response = await api.get(`/games/${gameId}`)
    // La nueva API devuelve una estructura con success, message y game
    return response.data.game
  },

  /**
   * Crea una nueva partida
   */
  async createGame(name: string, maxPlayers: number, creatorId: string): Promise<Game> {
    const response = await api.post(`/games`, {
      name,
      max_players: maxPlayers,
      creator_id: creatorId
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    // La nueva API devuelve una estructura con success, message y game
    return response.data.game
  },

  /**
   * Unirse a una partida
   */
  async joinGame(gameId: string): Promise<JoinGameResponse> {
  const response = await api.post(`/games/${gameId}/join`)
    // La nueva API devuelve una estructura con success, message, game_id, current_players y max_players
    const { game_id, current_players, max_players } = response.data
    return { game_id, current_players, max_players }
  },

  /**
   * Abandonar una partida
   */
  async leaveGame(gameId: string): Promise<LeaveGameResponse> {
  const response = await api.post(`/games/${gameId}/leave`)
    // La nueva API devuelve una estructura con success, message, game_id y remaining_players
    const { game_id, remaining_players } = response.data
    return { game_id, remaining_players }
  },

  /**
   * Eliminar una partida (solo administradores)
   */
  async deleteGame(gameId: string): Promise<DeleteGameResponse> {
  const response = await api.delete(`/games/${gameId}`)
    // La nueva API devuelve una estructura con success, message y deleted_game_id
    return { deleted_game_id: response.data.deleted_game_id }
  },

  /**
   * Asignar roles a los jugadores y comenzar la partida
   */
  async assignRoles(gameId: string): Promise<AssignRolesResponse> {
  const response = await api.post(`/games/${gameId}/assign-roles`)
    // La nueva API devuelve una estructura con success, message, game, assigned_roles_count y players_with_roles
    const { game, assigned_roles_count, players_with_roles } = response.data
    return { game, assigned_roles_count, players_with_roles }
  },

  /**
   * Actualizar el estado de una partida
   */
  async updateGameStatus(gameId: string, status: string): Promise<UpdateGameStatusResponse> {
    const response = await api.put(`/games/${gameId}/status`, { status }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    // La nueva API devuelve una estructura con success, message, game, previous_status y new_status
    const { game, previous_status, new_status } = response.data
    return { game, previous_status, new_status }
  },

  /**
   * Actualizar propiedades de una partida
   */
  async updateGame(gameId: string, data: any): Promise<UpdateGameResponse> {
    const response = await api.put(`/games/${gameId}`, data, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    // La nueva API devuelve una estructura con success, message, game y updated_fields
    const { game, updated_fields } = response.data
    return { game, updated_fields }
  },

  // Métodos para obtener información de jugadores específica del juego

  /**
   * Obtiene los jugadores vivos en la partida
   */
  async getAlivePlayers(gameId: string): Promise<any[]> {
  const response = await api.get(`/games/${gameId}/alive-players`)
  return response.data
  },

  /**
   * Obtiene los objetivos disponibles para votación
   */
  async getVotingTargets(gameId: string): Promise<any[]> {
  const response = await api.get(`/games/${gameId}/voting-targets`)
  return response.data
  },

  /**
   * Obtiene el recuento actual de votos
   */
  async getVoteCounts(gameId: string): Promise<any[]> {
  const response = await api.get(`/games/${gameId}/vote-counts`)
  return response.data
  },

  /**
   * Emitir un voto durante la fase diurna
   */
  async castDayVote(gameId: string, targetId: string): Promise<any> {
    const response = await api.post(`/games/${gameId}/day-vote`, {
      target_id: targetId
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    return response.data
  }
}
