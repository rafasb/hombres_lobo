<template>
  <Dialog
    v-model:visible="isVisible"
    modal
    header="Crear Nuevo Juego"
    :style="{ width: '450px' }"
    :closable="!isLoading"
    :closeOnEscape="!isLoading"
    class="create-game-modal"
  >
    <form @submit.prevent="handleSubmit" class="game-form">
      <div class="field">
        <label for="gameName" class="field-label">
          <i class="pi pi-bookmark"></i>
          Nombre del Juego *
        </label>
        <InputText
          id="gameName"
          v-model="formData.name"
          :class="{ 'p-invalid': errors.name }"
          placeholder="Ej: Partida de la Noche"
          :disabled="isLoading"
          autofocus
        />
        <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
      </div>

      <div class="field">
        <label for="maxPlayers" class="field-label">
          <i class="pi pi-users"></i>
          Número Máximo de Jugadores *
        </label>
        <div class="slider-container">
          <Slider
            id="maxPlayers"
            v-model="formData.max_players"
            :min="4"
            :max="24"
            :disabled="isLoading"
            class="player-slider"
          />
          <div class="slider-info">
            <span class="current-value">{{ formData.max_players }} jugadores</span>
            <span class="slider-range">4 - 24</span>
          </div>
        </div>
        <small v-if="errors.max_players" class="p-error">{{ errors.max_players }}</small>
      </div>

      <div class="field">
        <div class="info-panel">
          <h4><i class="pi pi-info-circle"></i> Información del Juego</h4>
          <ul class="game-info-list">
            <li>
              <strong>Jugadores:</strong> {{ formData.max_players }}
              <span class="player-distribution">({{ getPlayerDistribution() }})</span>
            </li>
            <li><strong>Duración estimada:</strong> {{ getEstimatedDuration() }}</li>
            <li><strong>Dificultad:</strong> {{ getDifficulty() }}</li>
          </ul>
        </div>
      </div>

      <div v-if="error" class="error-message">
        <Message severity="error" :closable="false">
          <i class="pi pi-exclamation-triangle"></i>
          {{ error }}
        </Message>
      </div>
    </form>

    <template #footer>
      <div class="modal-footer">
        <Button
          label="Cancelar"
          icon="pi pi-times"
          class="p-button-text"
          @click="handleCancel"
          :disabled="isLoading"
        />
        <Button
          label="Crear Juego"
          icon="pi pi-check"
          class="p-button-success"
          @click="handleSubmit"
          :loading="isLoading"
          :disabled="!isFormValid"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Slider from 'primevue/slider'
import Button from 'primevue/button'
import Message from 'primevue/message'

// Props
interface Props {
  visible: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'game-created': [gameData: { name: string; max_players: number }]
}>()

// Estado reactivo
const isLoading = ref(false)
const error = ref('')

// Datos del formulario
const formData = ref({
  name: '',
  max_players: 8
})

// Errores de validación
const errors = ref<Record<string, string>>({})

// Computed
const isVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const isFormValid = computed(() => {
  return (
    formData.value.name.trim().length >= 3 &&
    formData.value.max_players >= 4 &&
    formData.value.max_players <= 24 &&
    Object.keys(errors.value).length === 0
  )
})

// Funciones de utilidad para mostrar información del juego
const getPlayerDistribution = (): string => {
  const players = formData.value.max_players
  const werewolves = Math.floor(players / 4) // Aproximadamente 1 hombre lobo por cada 4 jugadores
  const villagers = players - werewolves
  return `${werewolves} lobos, ${villagers} aldeanos`
}

const getEstimatedDuration = (): string => {
  const players = formData.value.max_players
  if (players <= 6) return '20-30 min'
  if (players <= 12) return '30-45 min'
  if (players <= 18) return '45-60 min'
  return '60-90 min'
}

const getDifficulty = (): string => {
  const players = formData.value.max_players
  if (players <= 6) return 'Fácil'
  if (players <= 12) return 'Intermedio'
  if (players <= 18) return 'Avanzado'
  return 'Experto'
}

// Validación
const validateForm = () => {
  errors.value = {}

  // Validar nombre
  if (!formData.value.name.trim()) {
    errors.value.name = 'El nombre del juego es obligatorio'
  } else if (formData.value.name.trim().length < 3) {
    errors.value.name = 'El nombre debe tener al menos 3 caracteres'
  } else if (formData.value.name.trim().length > 50) {
    errors.value.name = 'El nombre no puede tener más de 50 caracteres'
  }

  // Validar número de jugadores
  if (formData.value.max_players < 4) {
    errors.value.max_players = 'Mínimo 4 jugadores'
  } else if (formData.value.max_players > 24) {
    errors.value.max_players = 'Máximo 24 jugadores'
  }
}

// Manejadores de eventos
const handleSubmit = async () => {
  validateForm()

  if (!isFormValid.value) {
    return
  }

  try {
    isLoading.value = true
    error.value = ''

    // Emitir evento con los datos del juego
    emit('game-created', {
      name: formData.value.name.trim(),
      max_players: formData.value.max_players
    })

    // Resetear formulario
    resetForm()

  } catch (err: any) {
    error.value = err.message || 'Error al crear el juego'
  } finally {
    isLoading.value = false
  }
}

const handleCancel = () => {
  if (!isLoading.value) {
    resetForm()
    isVisible.value = false
  }
}

const resetForm = () => {
  formData.value = {
    name: '',
    max_players: 8
  }
  errors.value = {}
  error.value = ''
}

// Watchers
watch(() => formData.value.name, () => {
  if (errors.value.name) {
    validateForm()
  }
})

watch(() => formData.value.max_players, () => {
  if (errors.value.max_players) {
    validateForm()
  }
})

// Resetear cuando se abre el modal
watch(() => props.visible, (newValue) => {
  if (newValue) {
    resetForm()
  }
})
</script>

<style scoped>
.create-game-modal :deep(.p-dialog-content) {
  padding-bottom: 0;
}

.game-form {
  padding: 0.5rem 0;
}

.field {
  margin-bottom: 1.5rem;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.slider-container {
  margin-top: 0.5rem;
}

.player-slider {
  width: 100%;
  margin-bottom: 1rem;
}

.slider-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-value {
  font-weight: 600;
  color: var(--primary-color);
  font-size: 1.1rem;
}

.player-distribution {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
  margin-left: 0.5rem;
}

.slider-range {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.info-panel {
  background: var(--surface-50);
  border: 1px solid var(--surface-200);
  border-radius: 6px;
  padding: 1rem;
}

.info-panel h4 {
  margin: 0 0 0.75rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--primary-color);
  font-size: 1rem;
}

.game-info-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.game-info-list li {
  padding: 0.25rem 0;
  color: var(--text-color-secondary);
}

.error-message {
  margin-top: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--surface-200);
}

/* Responsive */
@media (max-width: 480px) {
  .create-game-modal :deep(.p-dialog) {
    width: 95vw !important;
    margin: 1rem;
  }

  .slider-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
