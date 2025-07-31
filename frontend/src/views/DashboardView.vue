<template>
  <div class="dashboard-view">
    <div class="dashboard-header">
      <h1>Dashboard - Hombres Lobo</h1>
      <p>¡Bienvenido, {{ authStore.user?.username }}!</p>
    </div>

    <div class="dashboard-content">
      <div class="user-info">
        <h2>Información del Usuario</h2>
        <p><strong>Usuario:</strong> {{ authStore.user?.username }}</p>
        <p><strong>Email:</strong> {{ authStore.user?.email }}</p>
        <p><strong>ID:</strong> {{ authStore.user?.id }}</p>
      </div>

      <div class="actions">
        <Button
          @click="router.push('/games')"
          label="Gestión de Juegos"
          icon="pi pi-users"
          class="games-btn"
        />
        <Button
          @click="router.push('/test-websocket')"
          label="Test WebSocket"
          icon="pi pi-bolt"
          severity="info"
          class="test-ws-btn"
        />
        <Button
          @click="authStore.logout"
          label="Cerrar Sesión"
          severity="secondary"
          class="logout-btn"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'
import Button from 'primevue/button'

const authStore = useAuthStore()
const router = useRouter()

// Verificar autenticación al montar
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
  }
})

// Sobrescribir logout para redirigir
const originalLogout = authStore.logout
authStore.logout = () => {
  originalLogout()
  router.push('/login')
}
</script>

<style src="../assets/styles/dashboard-view.css" scoped></style>
