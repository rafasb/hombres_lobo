
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './stores/authStore'
import { useStoreInitialization } from './composables/useStoreInitialization'

const auth = useAuthStore()
const { initializeGlobalStores } = useStoreInitialization()

onMounted(async () => {
  // Cargar el usuario desde el token al iniciar la aplicación
  if (auth.token && !auth.user) {
    await auth.loadUserFromToken()
  }
})

// Inicializar suscripciones WebSocket globales
initializeGlobalStores()
</script>
