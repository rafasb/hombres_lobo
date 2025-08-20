<template>
  <!-- Modal Header -->
  <div class="modal-header border-0 pb-2">
    <h4 class="modal-title fw-bold text-dark d-flex align-items-center">
      <i class="bi bi-plus-circle-fill me-2 text-primary"></i>
      Crear Nueva Partida
    </h4>
    <button 
      type="button" 
      class="btn-close" 
      @click="$emit('close')"
      aria-label="Cerrar"
    ></button>
  </div>

  <!-- Modal Body -->
  <div class="modal-body px-4 py-3">
    <form @submit.prevent="$emit('create')" id="createGameForm">
      <!-- Nombre de la partida -->
      <div class="mb-4">
        <label for="gameName" class="form-label fw-semibold text-dark">
          <i class="bi bi-controller me-1"></i>
          Nombre de la partida:
        </label>
        <input 
          type="text" 
          id="gameName"
          class="form-control form-control-lg"
          v-model="localGameData.name"
          required
          maxlength="50"
          placeholder="Ej: Partida de los amigos"
          style="border-radius: 10px; border: 2px solid #e9ecef;"
          :class="{ 'is-invalid': !localGameData.name && hasValidation }"
        >
        <div class="form-text">
          <small class="text-muted">
            <i class="bi bi-info-circle me-1"></i>
            Máximo 50 caracteres
          </small>
        </div>
      </div>
      
      <!-- Número máximo de jugadores -->
      <div class="mb-4">
        <label for="maxPlayers" class="form-label fw-semibold text-dark">
          <i class="bi bi-people-fill me-1"></i>
          Número máximo de jugadores:
        </label>
        <select 
          id="maxPlayers" 
          class="form-select form-select-lg"
          v-model="localGameData.maxPlayers"
          required
          style="border-radius: 10px; border: 2px solid #e9ecef;"
        >
          <option value="" disabled>Selecciona el número de jugadores</option>
          <option v-for="n in playerOptions" :key="n" :value="n">
            {{ n }} jugadores
          </option>
        </select>
        <div class="form-text">
          <small class="text-muted">
            <i class="bi bi-lightbulb me-1"></i>
            Se recomienda entre 6-12 jugadores para una mejor experiencia
          </small>
        </div>
      </div>

      <!-- Información adicional -->
      <div class="alert alert-info border-0" style="border-radius: 10px; background: rgba(13, 202, 240, 0.1);">
        <div class="d-flex align-items-start">
          <i class="bi bi-info-circle-fill text-info me-2 mt-1"></i>
          <div>
            <h6 class="alert-heading mb-1">Información de la partida</h6>
            <small class="mb-0">
              Una vez creada la partida, podrás invitar a otros jugadores compartiendo el código de la sala.
              El juego comenzará automáticamente cuando se alcance el número mínimo de jugadores.
            </small>
          </div>
        </div>
      </div>
    </form>
  </div>

  <!-- Modal Footer -->
  <div class="modal-footer border-0 pt-2 px-4 pb-4">
    <div class="d-flex gap-2 w-100">
      <button 
        type="button" 
        class="btn btn-outline-secondary flex-fill py-2"
        @click="$emit('close')"
        :disabled="loading"
        style="border-radius: 10px;"
      >
        <i class="bi bi-x-circle me-1"></i>
        Cancelar
      </button>
      <button 
        type="submit" 
        form="createGameForm"
        class="btn btn-primary flex-fill py-2"
        :disabled="loading || !isFormValid"
        style="border-radius: 10px; box-shadow: 0 2px 10px rgba(0, 123, 255, 0.3);"
      >
        <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
        <i v-else class="bi bi-plus-circle me-1"></i>
        {{ loading ? 'Creando...' : 'Crear Partida' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

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
const hasValidation = ref(false)

// Validación del formulario
const isFormValid = computed(() => {
  return localGameData.value.name.trim().length > 0 && 
         localGameData.value.maxPlayers > 0
})

// Sincronizar cambios locales con el padre
watch(localGameData, (newValue) => {
  emit('update:gameData', newValue)
}, { deep: true })
</script>
