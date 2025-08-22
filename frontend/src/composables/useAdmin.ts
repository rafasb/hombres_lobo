import { ref } from 'vue'
import { adminFetchUsers, deleteUser, toggleUserRole } from '../services/userService'
import type { AdminUser } from '../types'

export const useAdminComposable = () => {
  const users = ref<AdminUser[]>([])
  const search = ref('')
  const loading = ref(false)
  const error = ref('')

  const fetchUsersList = async () => {
    loading.value = true
    error.value = ''
    users.value = []
    try {
      const result = await adminFetchUsers(search.value)
      if (result && result.users) {
        users.value = result.users.map(user => ({
          id: user.id,
          username: user.username,
          role: user.role
        }))
      } else if (result && result.error) {
        error.value = result.error
      }
    } catch (err) {
      console.error('Error in fetchUsersList:', err)
      error.value = 'Error inesperado al cargar usuarios'
    }
    loading.value = false
  }

  const deleteUserHandler = async (user: AdminUser) => {
    loading.value = true
    error.value = ''
    const result = await deleteUser(user.id)
    if (result && result.error) {
      error.value = result.error
    } else {
      await fetchUsersList()
    }
    loading.value = false
  }

  const toggleRole = async (user: AdminUser, newRole: 'admin' | 'player') => {
    loading.value = true
    error.value = ''
    const result = await toggleUserRole(user.id, newRole)
    if (result && result.error) {
      error.value = result.error
    } else {
      await fetchUsersList()
    }
    loading.value = false
  }

  // La inicialización y control de acceso se gestionan fuera del composable

  return {
    users,
    search,
    loading,
    error,
    fetchUsersList,
    deleteUserHandler,
    toggleRole
  }
}
