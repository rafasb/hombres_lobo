<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <h2>Crear Nueva Partida</h2>
      <form @submit.prevent="$emit('create')">
        <div class="form-group">
          <label for="gameName">Nombre de la partida:</label>
          <input 
            type="text" 
            id="gameName"
            v-model="localGameData.name"
            required
            maxlength="50"
            placeholder="Ingresa el nombre de la partida"
          >
        </div>
        
        <div class="form-group">
          <label for="maxPlayers">Número máximo de jugadores:</label>
          <select 
            id="maxPlayers" 
            v-model="localGameData.maxPlayers"
            required
          >
            <option v-for="n in playerOptions" :key="n" :value="n">{{ n }}</option>
          </select>
        </div>
        
        <div class="modal-actions">
          <button type="button" class="btn btn-cancel" @click="$emit('close')">
            Cancelar
          </button>
          <button type="submit" class="btn btn-create" :disabled="loading">
            Crear Partida
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  gameData: {
    name: string
    maxPlayers: number
  }
  playerOptions: number[]
  loading: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'create'): void
  (e: 'update:gameData', value: { name: string, maxPlayers: number }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const localGameData = ref({ ...props.gameData })

// Solo sincronizar cambios locales con el padre
watch(localGameData, (newValue) => {
  emit('update:gameData', newValue)
}, { deep: true })
</script>
