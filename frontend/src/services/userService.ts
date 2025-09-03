import api from './api'
import { extractErrorMessage } from './errorHelper'
import type { User, UserRole } from '../types'

const API_URL = '/admin/users'

export async function adminFetchUsers(search = ''): Promise<{ users?: User[]; error?: string }> {
  try {
    const response = await api.get(`${API_URL}`)
    let users: User[] = response.data
    if (search) {
      users = users.filter((u: User) => u.username.toLowerCase().includes(search.toLowerCase()))
    }
    return { users }
  } catch (error: unknown) {
    console.error('Error fetching users:', error)
    return { error: extractErrorMessage(error, 'Error al obtener usuarios.') }
  }
}

/**
 * Obtener información de los usuarios que participan en una partida
 * Usa el endpoint `/games/{game_id}` para obtener la partida y luego hace requests
 * individuales para obtener información de usuarios usando `/users/{user_id}`.
 * Como fallback, crea objetos User con información mínima si no se puede obtener
 * los datos completos del usuario.
 */
export async function fetchUsers(gameId: string): Promise<{ users?: User[]; error?: string }> {
  try {
    const response = await api.get(`/games/${gameId}`)
    const game = response.data.game || response.data
    
    if (!game.player_ids || !Array.isArray(game.player_ids)) {
      return { users: [] }
    }

    const users: User[] = []
    
    // Intentar obtener información de cada usuario
    for (const playerId of game.player_ids) {
      try {
        const userResponse = await api.get(`/users/${playerId}`)
        const userData = userResponse.data.user || userResponse.data
        users.push({
          id: userData.id,
          username: userData.username,
          email: userData.email || '',
          role: userData.role || 'player',
          status: userData.status || 'disconnected',
          in_game: userData.status === 'in_game',
          game_id: userData.game_id || gameId
        })
      } catch (userError) {
        // Si no se puede obtener la información del usuario, crear un objeto mínimo
        console.warn(`Could not fetch user data for ${playerId}:`, userError)
        users.push({
          id: playerId,
          username: `Player ${playerId.slice(-4)}`, // Mostrar últimos 4 caracteres del ID
          email: '',
          role: 'player',
          status: 'disconnected',
          in_game: false,
          game_id: gameId
        })
      }
    }

    return { users }
  } catch (error: unknown) {
    return { error: extractErrorMessage(error, 'Error al obtener jugadores de la partida.') }
  }
}

export async function deleteUser(userId: string): Promise<{ error?: string }> {
  try {
    await api.delete(`${API_URL}/${userId}`)
    return {}
  } catch (error: unknown) {
    return { error: extractErrorMessage(error, 'Error al eliminar usuario.') }
  }
}

export async function toggleUserRole(userId: string, newRole: UserRole): Promise<{ error?: string }> {
  try {
    await api.put(`${API_URL}/${userId}/role?role=${encodeURIComponent(newRole)}`, null)
    return {}
  } catch (error: unknown) {
    return { error: extractErrorMessage(error, 'Error al cambiar el rol.') }
  }
}

export async function updateUserStatus(userId: string, statusUpdate: { status: string, game_id?: string }) {
  // Actualiza el estado del usuario
  try {
    const response = await api.put(`/users/${userId}/status`, statusUpdate)
    return response.data
  } catch (error: unknown) {
    return { error: extractErrorMessage(error, 'Error al actualizar el estado del usuario.') }
  }
}
