<template>
  <div class="admin-container">
    <h2>Administración de usuarios</h2>
    <div class="admin-search">
      <input v-model="search" type="text" placeholder="Buscar usuario..." />
      <button @click="fetchUsersList">Buscar</button>
    </div>
    <div v-if="loading">Cargando usuarios...</div>
    <div v-if="error" class="admin-error">{{ error }}</div>
    <table v-if="users.length" class="admin-table">
      <thead>
        <tr>
          <th>Usuario</th>
          <th>ID</th>
          <th>Rol</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.username }}</td>
          <td>{{ user.id }}</td>
          <td>{{ user.role }}</td>
          <td>
            <button @click="toggleRole(user)">{{ user.role === 'admin' ? 'Convertir en jugador' : 'Convertir en admin' }}</button>
            <button @click="deleteUserHandler(user)">Eliminar</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else-if="!loading && !error" class="admin-empty">No hay usuarios para mostrar.</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { fetchUsers, deleteUser, toggleUserRole } from '../services/userService.ts'

const auth = useAuthStore()

interface User {
  id: string;
  username: string;
  role: string;
}

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

// Cargar usuarios cuando se monta el componente
onMounted(async () => {
  // Asegurar que el usuario esté cargado antes de verificar permisos
  await auth.loadUserFromToken()
  
  if (auth.isAdmin) {
    fetchUsersList()
  } else {
    error.value = 'No tienes permisos de administrador para ver esta página'
  }
})
</script>

<style src="../styles/admin.css"></style>
