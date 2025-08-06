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
import { useAdminComposable } from '../composables/useAdmin.ts'

const {
  users,
  search,
  loading,
  error,
  fetchUsersList,
  deleteUserHandler,
  toggleRole
} = useAdminComposable()
</script>

<style src="../styles/admin.css"></style>
