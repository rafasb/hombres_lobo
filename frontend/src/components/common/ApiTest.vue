<template>
  <div class="api-test">
    <h3>Test de Comunicación API</h3>
    <button @click="testConnection" class="test-button">
      Probar Conexión
    </button>
    <div v-if="result" class="result">
      <p><strong>Estado:</strong> {{ result.status }}</p>
      <p><strong>Respuesta:</strong> {{ result.data }}</p>
    </div>
    <div v-if="error" class="error">
      <p><strong>Error:</strong> {{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { apiService } from '@/services/api'

const result = ref<any>(null)
const error = ref<string>('')

const testConnection = async () => {
  try {
    error.value = ''
    const response = await apiService.get('/docs')
    result.value = {
      status: 'Conexión exitosa',
      data: 'Backend respondiendo correctamente'
    }
  } catch (err: any) {
    error.value = err.message || 'Error de conexión'
    result.value = null
  }
}
</script>

<style scoped>
.api-test {
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin: 1rem;
}

.test-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.test-button:hover {
  background-color: #0056b3;
}

.result {
  margin-top: 1rem;
  padding: 0.5rem;
  background-color: #d4edda;
  border-radius: 4px;
}

.error {
  margin-top: 1rem;
  padding: 0.5rem;
  background-color: #f8d7da;
  border-radius: 4px;
}
</style>
