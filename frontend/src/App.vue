
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './stores/authStore'

const auth = useAuthStore()

onMounted(async () => {
  // Cargar el usuario desde el token al iniciar la aplicación
  if (auth.token && !auth.user) {
    await auth.loadUserFromToken()
  }
})
</script>
