<template>
  <div class="debug-info">
    <h3>🐛 Debug Info - Games Store</h3>
    <div class="debug-section">
      <h4>Estado del Store:</h4>
      <ul>
        <li>isLoading: {{ gamesStore.isLoading }}</li>
        <li>error: {{ gamesStore.error || 'sin errores' }}</li>
        <li>games.length: {{ gamesStore.games.length }}</li>
        <li>availableGames.length: {{ gamesStore.availableGames.length }}</li>
      </ul>
    </div>

    <div class="debug-section">
      <h4>Pruebas de API:</h4>
      <Button
        label="Test Fetch Games"
        @click="testFetchGames"
        :loading="testing"
        class="p-button-sm"
      />
      <p v-if="testResult" :class="testResult.type">{{ testResult.message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import { useGamesStore } from '../stores/games'

const gamesStore = useGamesStore()
const testing = ref(false)
const testResult = ref<{type: string, message: string} | null>(null)

const testFetchGames = async () => {
  testing.value = true
  testResult.value = null

  try {
    const success = await gamesStore.fetchGames()
    testResult.value = {
      type: 'success',
      message: `✅ API funcionando. Juegos obtenidos: ${gamesStore.games.length}`
    }
  } catch (error: any) {
    testResult.value = {
      type: 'error',
      message: `❌ Error: ${error.message || 'Error desconocido'}`
    }
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.debug-info {
  background: #f8f9fa;
  border: 2px dashed #6c757d;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
  font-family: monospace;
}

.debug-section {
  margin: 1rem 0;
}

.debug-section h4 {
  margin: 0.5rem 0;
  color: #495057;
}

.debug-section ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.success {
  color: #28a745;
  font-weight: bold;
}

.error {
  color: #dc3545;
  font-weight: bold;
}
</style>
