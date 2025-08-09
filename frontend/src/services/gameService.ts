import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export interface User {
  id: string
  username: string
  email: string
  role: 'admin' | 'player'
  status: 'active' | 'banned' | 'connected' | 'disconnected' | 'in_game'
  in_game: boolean
  game_id: string | null
}

export interface Game {
  id: string
  name: string
  max_players: number
  creator_id: string
  players: string[] // IDs de usuario
  status: 'waiting' | 'started' | 'night' | 'day' | 'paused' | 'finished'
  created_at?: string
  current_round?: number
}

export const gameService = {
  /**
   * Obtiene todas las partidas disponibles
   */
  async getGames(): Promise<Game[]> {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`${API_BASE_URL}/games`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    // La nueva API devuelve una estructura con success, message, games y total_games
    return response.data.games
  },

  /**
   * Obtiene una partida específica por ID
   */
  async getGameById(gameId: string): Promise<Game> {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`${API_BASE_URL}/games/${gameId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    // La nueva API devuelve una estructura con success, message y game
    return response.data.game
  },

  /**
   * Crea una nueva partida
   */
  async createGame(name: string, maxPlayers: number, creatorId: string): Promise<Game> {
    const token = localStorage.getItem('access_token')
    const response = await axios.post(`${API_BASE_URL}/games`, {
      name,
      max_players: maxPlayers,
      creator_id: creatorId
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    // La nueva API devuelve una estructura con success, message y game
    return response.data.game
  },

  /**
   * Unirse a una partida
   */
  async joinGame(gameId: string): Promise<{ game_id: string; current_players: number; max_players: number }> {
    const token = localStorage.getItem('access_token')
    const response = await axios.post(`${API_BASE_URL}/games/${gameId}/join`, {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    // La nueva API devuelve una estructura con success, message, game_id, current_players y max_players
    const { game_id, current_players, max_players } = response.data
    return { game_id, current_players, max_players }
  },

  /**
   * Abandonar una partida
   */
  async leaveGame(gameId: string): Promise<{ game_id: string; remaining_players: number }> {
    const token = localStorage.getItem('access_token')
    const response = await axios.post(`${API_BASE_URL}/games/${gameId}/leave`, {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    // La nueva API devuelve una estructura con success, message, game_id y remaining_players
    const { game_id, remaining_players } = response.data
    return { game_id, remaining_players }
  },

  /**
   * Eliminar una partida (solo administradores)
   */
  async deleteGame(gameId: string): Promise<{ deleted_game_id: string }> {
    const token = localStorage.getItem('access_token')
    const response = await axios.delete(`${API_BASE_URL}/games/${gameId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    // La nueva API devuelve una estructura con success, message y deleted_game_id
    return { deleted_game_id: response.data.deleted_game_id }
  },

  /**
   * Asignar roles a los jugadores y comenzar la partida
   */
  async assignRoles(gameId: string): Promise<{ game: Game; assigned_roles_count: number; players_with_roles: number }> {
    const token = localStorage.getItem('access_token')
    const response = await axios.post(`${API_BASE_URL}/games/${gameId}/assign-roles`, {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    // La nueva API devuelve una estructura con success, message, game, assigned_roles_count y players_with_roles
    const { game, assigned_roles_count, players_with_roles } = response.data
    return { game, assigned_roles_count, players_with_roles }
  },

  /**
   * Actualizar el estado de una partida
   */
  async updateGameStatus(gameId: string, status: string): Promise<{ game: Game; previous_status: string; new_status: string }> {
    const token = localStorage.getItem('access_token')
    const response = await axios.put(`${API_BASE_URL}/games/${gameId}/status`, { status }, {
      headers: {
        'Authorization': `Bearer ${token}`,
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
  async updateGame(gameId: string, data: any): Promise<{ game: Game; updated_fields: string[] }> {
    const token = localStorage.getItem('access_token')
    const response = await axios.put(`${API_BASE_URL}/games/${gameId}`, data, {
      headers: {
        'Authorization': `Bearer ${token}`,
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
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`${API_BASE_URL}/games/${gameId}/alive-players`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.data
  },

  /**
   * Obtiene los objetivos disponibles para votación
   */
  async getVotingTargets(gameId: string): Promise<any[]> {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`${API_BASE_URL}/games/${gameId}/voting-targets`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.data
  },

  /**
   * Obtiene el recuento actual de votos
   */
  async getVoteCounts(gameId: string): Promise<any[]> {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`${API_BASE_URL}/games/${gameId}/vote-counts`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.data
  },

  /**
   * Emitir un voto durante la fase diurna
   */
  async castDayVote(gameId: string, targetId: string): Promise<any> {
    const token = localStorage.getItem('access_token')
    const response = await axios.post(`${API_BASE_URL}/games/${gameId}/day-vote`, {
      target_id: targetId
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    return response.data
  }
}
