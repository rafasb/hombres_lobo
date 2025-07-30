<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import Toast from 'primevue/toast'

const authStore = useAuthStore()

onMounted(() => {
  authStore.checkAuth()
})
</script>

<template>
  <div id="app">
    <RouterView />
    <Toast />
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
}
</style>
