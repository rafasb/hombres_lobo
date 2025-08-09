import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_URL = '/admin/users'

export async function fetchUsers(search = '') {
  const auth = useAuthStore()
  const token = auth.token
  try {
    // El endpoint devuelve un array de usuarios directamente
    const response = await axios.get(`${API_URL}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    // La respuesta es directamente un array de usuarios
    let users = response.data
    if (search) {
      users = users.filter((u: any) => u.username.toLowerCase().includes(search.toLowerCase()))
    }
    return { users }
  } catch (error: any) {
    console.error('Error fetching users:', error)
    return { error: error.response?.data?.detail || 'Error al obtener usuarios.' }
  }
}

export async function deleteUser(userId: string) {
  const auth = useAuthStore()
  const token = auth.token
  try {
    await axios.delete(`${API_URL}/${userId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    return {}
  } catch (error: any) {
    return { error: (error as any).response?.data?.detail || 'Error al eliminar usuario.' }
  }
}

export async function toggleUserRole(userId: string, newRole: string) {
  const auth = useAuthStore()
  const token = auth.token
  try {
    await axios.put(`${API_URL}/${userId}/role?role=${encodeURIComponent(newRole)}`, null, {
      headers: { Authorization: `Bearer ${token}` }
    })
    return {}
  } catch (error: any) {
    return { error: (error as any).response?.data?.detail || 'Error al cambiar el rol.' }
  }
}

// Añadir función para actualizar el estado del usuario
export async function updateUserStatus(userId: string, statusUpdate: { status: string, game_id?: string }) {
  const auth = useAuthStore()
  const token = auth.token
  try {
    const response = await axios.put(
      `/users/${userId}/status`,
      statusUpdate,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    return response.data
  } catch (error: any) {
    return { error: (error as any).response?.data?.detail || 'Error al actualizar el estado del usuario.' }
  }
}
