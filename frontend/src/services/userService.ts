import api from './api'
import { extractErrorMessage } from './errorHelper'
import type { User, UserRole } from '../types'

const API_URL = '/admin/users'

export async function fetchUsers(search = ''): Promise<{ users?: User[]; error?: string }> {
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
