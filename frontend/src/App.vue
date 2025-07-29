<script setup lang="ts">
import ApiTest from '@/components/common/ApiTest.vue'
</script>

<template>
  <div id="app">
    <h1>Hombres Lobo - Prueba de Conexión</h1>
    <ApiTest />
    <RouterView />
  </div>
</template>

<style scoped>
#app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}
</style>
