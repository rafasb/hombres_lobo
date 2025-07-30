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

<style scoped>
.dashboard-view {
  min-height: 100vh;
  padding: 2rem;
  background: #f8f9fa;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.dashboard-header h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.dashboard-content {
  max-width: 800px;
  margin: 0 auto;
}

.user-info {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.user-info h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.user-info p {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.actions {
  text-align: center;
}

.logout-btn {
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
}
</style>
