<template>
  <div class="profile-container">
    <h2>Perfil de usuario</h2>
    <div v-if="auth.user">
      <p><strong>Usuario:</strong> {{ auth.user.username }}</p>
      <p><strong>ID:</strong> {{ auth.user.id }}</p>
      <p><strong>Rol:</strong> {{ auth.user.role }}</p>
      <button @click="handleLogout">Cerrar sesión</button>
      <button v-if="auth.isAdmin" @click="router.push('/admin')">Administración de usuarios</button>
    </div>
    <div v-else>
      <p>No hay datos de usuario.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const auth = useAuthStore()

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
}

h2 {
  text-align: center;
  color: #333;
}

.profile-error {
  color: red;
  text-align: center;
}

.logout-btn, .admin-btn {
  display: block;
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn {
  background-color: #d9534f;
  color: white;
}

.admin-btn {
  background-color: #5bc0de;
  color: white;
}
</style>
