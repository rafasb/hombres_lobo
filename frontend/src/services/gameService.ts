import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export interface User {
  username: string
  email: string
  id: string
  role: 'admin' | 'player'
  status: 'active' | 'inactive' | 'banned'
}

export interface Game {
  name: string
  max_players: number
  id: string
  creator_id: string
  players: User[]
  status: 'waiting' | 'started' | 'night' | 'day' | 'paused' | 'finished'
  created_at: string
  current_round: number
  is_first_night: boolean
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
    return response.data
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
    return response.data
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
    return response.data
  },

  /**
   * Unirse a una partida
   */
  async joinGame(gameId: string): Promise<void> {
    const token = localStorage.getItem('access_token')
    await axios.post(`${API_BASE_URL}/games/${gameId}/join`, {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  /**
   * Abandonar una partida
   */
  async leaveGame(gameId: string): Promise<void> {
    const token = localStorage.getItem('access_token')
    await axios.post(`${API_BASE_URL}/games/${gameId}/leave`, {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }
}
