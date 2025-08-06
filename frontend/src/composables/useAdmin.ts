import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { fetchUsers, deleteUser, toggleUserRole } from '../services/userService'

interface User {
  id: string;
  username: string;
  role: string;
}

export const useAdminComposable = () => {
  const auth = useAuthStore()

  const users = ref<User[]>([])
  const search = ref('')
  const loading = ref(false)
  const error = ref('')

  const fetchUsersList = async () => {
    loading.value = true
    error.value = ''
    users.value = []
    try {
      const result = await fetchUsers(search.value)
      if (result && result.users) {
        users.value = result.users
      } else if (result && result.error) {
        error.value = result.error
      }
    } catch (err) {
      console.error('Error in fetchUsersList:', err)
      error.value = 'Error inesperado al cargar usuarios'
    }
    loading.value = false
  }

  const deleteUserHandler = async (user: User) => {
    if (!confirm(`¿Estás seguro de que deseas eliminar al usuario ${user.username}?`)) {
      return
    }
    
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

  const toggleRole = async (user: User) => {
    const newRole = user.role === 'admin' ? 'player' : 'admin'
    if (!confirm(`¿Estás seguro de que deseas cambiar el rol de ${user.username} a ${newRole}?`)) {
      return
    }
    
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

  // Inicialización
  onMounted(async () => {
    // Asegurar que el usuario esté cargado antes de verificar permisos
    await auth.loadUserFromToken()
    
    if (auth.isAdmin) {
      fetchUsersList()
    } else {
      error.value = 'No tienes permisos de administrador para ver esta página'
    }
  })

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
