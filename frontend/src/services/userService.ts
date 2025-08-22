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
 * Obtener información de los usuarios que participan en una partida (para usuarios no admin)
 * Usa el endpoint `/games/{game_id}` y devuelve una lista de usuarios mapeada a la interfaz `User`.
 * Nota: el endpoint de juego puede devolver sólo datos parciales de jugador; aquí hacemos un mapeo
 * de "mejor esfuerzo" para devolver `User[]` con campos por defecto cuando no estén presentes.
 */
export async function fetchUsers(gameId: string): Promise<{ users?: User[]; error?: string }> {
  try {
    const response = await api.get(`/games/${gameId}`)
    const game = response.data.game || response.data
    const players = game.players || []

    interface PlayerFromGame {
      id: string
      username: string
      role?: 'admin' | 'player'
      status?: string
    }

    const users: User[] = (players as PlayerFromGame[]).map((p) => {
      const status = (p.status as User['status']) || 'disconnected'
      const role = (p.role as User['role']) || 'player'
      return {
        id: p.id,
        username: p.username,
        role,
        email: '', // not provided by /games endpoint
        status,
        in_game: status === 'in_game',
        game_id: game.id || game.game_id || gameId
      }
    })

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
  try {
    const response = await api.put(`/users/${userId}/status`, statusUpdate)
    return response.data
  } catch (error: unknown) {
    return { error: extractErrorMessage(error, 'Error al actualizar el estado del usuario.') }
  }
}
