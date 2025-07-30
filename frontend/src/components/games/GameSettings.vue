<template>
  <div class="game-settings">
    <!-- Settings form -->
    <form @submit.prevent="saveSettings" class="settings-form">
      <!-- Basic game settings -->
      <div class="settings-section">
        <h4 class="section-title">
          <i class="pi pi-cog"></i>
          Configuración Básica
        </h4>

        <div class="field">
          <label for="game-name">Nombre del Juego</label>
          <InputText
            id="game-name"
            v-model="formData.name"
            :disabled="!canEdit"
            placeholder="Nombre de la partida"
            class="w-full"
          />
          <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
        </div>

        <div class="field">
          <label for="max-players">Jugadores Máximos</label>
          <div class="slider-container">
            <Slider
              id="max-players"
              v-model="formData.max_players"
              :min="4"
              :max="24"
              :disabled="!canEdit"
              class="player-slider"
            />
            <div class="slider-info">
              <span class="current-value">{{ formData.max_players }}</span>
              <span class="slider-range">4 - 24 jugadores</span>
            </div>
          </div>
          <small v-if="errors.max_players" class="p-error">{{ errors.max_players }}</small>
        </div>
      </div>

      <!-- Role configuration -->
      <div class="settings-section">
        <h4 class="section-title">
          <i class="pi pi-users"></i>
          Configuración de Roles
        </h4>

        <div class="roles-config">
          <!-- Auto-distribution info -->
          <div class="auto-roles-info">
            <Message severity="info" :closable="false">
              <div class="info-content">
                <i class="pi pi-info-circle"></i>
                <div>
                  <strong>Distribución Automática</strong>
                  <p>Los roles se asignarán automáticamente según el número de jugadores.</p>
                </div>
              </div>
            </Message>
          </div>

          <!-- Role distribution preview -->
          <div class="role-distribution">
            <h5>Vista previa para {{ formData.max_players }} jugadores:</h5>
            <div class="roles-preview">
              <div v-for="role in getRoleDistribution(formData.max_players)" :key="role.name" class="role-preview-item">
                <div class="role-info">
                  <i :class="role.icon" :style="{ color: role.color }"></i>
                  <span class="role-name">{{ role.name }}</span>
                </div>
                <Badge :value="role.count" />
              </div>
            </div>
          </div>

          <!-- Advanced role settings (if enabled) -->
          <div v-if="showAdvancedRoles" class="advanced-roles">
            <Divider />
            <h5>Configuración Avanzada de Roles</h5>

            <div class="field">
              <div class="field-checkbox">
                <Checkbox
                  id="enable-cupid"
                  v-model="formData.roles.cupid_enabled"
                  :binary="true"
                  :disabled="!canEdit"
                />
                <label for="enable-cupid">Incluir Cupido</label>
              </div>
              <small>El Cupido puede emparejar a dos jugadores como amantes</small>
            </div>

            <div class="field">
              <div class="field-checkbox">
                <Checkbox
                  id="enable-witch"
                  v-model="formData.roles.witch_enabled"
                  :binary="true"
                  :disabled="!canEdit"
                />
                <label for="enable-witch">Incluir Bruja</label>
              </div>
              <small>La Bruja puede salvar o envenenar jugadores</small>
            </div>

            <div class="field">
              <div class="field-checkbox">
                <Checkbox
                  id="enable-seer"
                  v-model="formData.roles.seer_enabled"
                  :binary="true"
                  :disabled="!canEdit"
                />
                <label for="enable-seer">Incluir Vidente</label>
              </div>
              <small>El Vidente puede ver el rol de otros jugadores</small>
            </div>

            <div class="field">
              <div class="field-checkbox">
                <Checkbox
                  id="enable-hunter"
                  v-model="formData.roles.hunter_enabled"
                  :binary="true"
                  :disabled="!canEdit"
                />
                <label for="enable-hunter">Incluir Cazador</label>
              </div>
              <small>El Cazador puede eliminar a otro jugador al morir</small>
            </div>
          </div>

          <!-- Toggle advanced settings -->
          <div class="advanced-toggle">
            <Button
              :label="showAdvancedRoles ? 'Ocultar opciones avanzadas' : 'Mostrar opciones avanzadas'"
              :icon="showAdvancedRoles ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
              class="p-button-text p-button-sm"
              @click="showAdvancedRoles = !showAdvancedRoles"
            />
          </div>
        </div>
      </div>

      <!-- Game rules -->
      <div class="settings-section">
        <h4 class="section-title">
          <i class="pi pi-book"></i>
          Reglas del Juego
        </h4>

        <div class="field">
          <div class="field-checkbox">
            <Checkbox
              id="allow-dead-chat"
              v-model="formData.rules.allow_dead_chat"
              :binary="true"
              :disabled="!canEdit"
            />
            <label for="allow-dead-chat">Permitir chat de muertos</label>
          </div>
          <small>Los jugadores eliminados pueden chatear entre ellos</small>
        </div>

        <div class="field">
          <div class="field-checkbox">
            <Checkbox
              id="show-role-on-death"
              v-model="formData.rules.show_role_on_death"
              :binary="true"
              :disabled="!canEdit"
            />
            <label for="show-role-on-death">Mostrar rol al morir</label>
          </div>
          <small>El rol del jugador se revela cuando es eliminado</small>
        </div>

        <div class="field">
          <label for="day-duration">Duración del día (minutos)</label>
          <div class="slider-container">
            <Slider
              id="day-duration"
              v-model="formData.rules.day_duration_minutes"
              :min="2"
              :max="15"
              :disabled="!canEdit"
              class="duration-slider"
            />
            <div class="slider-info">
              <span class="current-value">{{ formData.rules.day_duration_minutes }} min</span>
              <span class="slider-range">2 - 15 minutos</span>
            </div>
          </div>
        </div>

        <div class="field">
          <label for="night-duration">Duración de la noche (minutos)</label>
          <div class="slider-container">
            <Slider
              id="night-duration"
              v-model="formData.rules.night_duration_minutes"
              :min="1"
              :max="10"
              :disabled="!canEdit"
              class="duration-slider"
            />
            <div class="slider-info">
              <span class="current-value">{{ formData.rules.night_duration_minutes }} min</span>
              <span class="slider-range">1 - 10 minutos</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Action buttons -->
      <div v-if="canEdit" class="settings-actions">
        <Button
          type="submit"
          label="Guardar Configuración"
          icon="pi pi-save"
          :loading="isSaving"
          class="p-button-success"
        />
        <Button
          type="button"
          label="Restablecer"
          icon="pi pi-refresh"
          @click="resetSettings"
          class="p-button-outlined"
          :disabled="isSaving"
        />
      </div>

      <!-- Read-only message -->
      <div v-else class="readonly-message">
        <Message severity="info" :closable="false">
          <i class="pi pi-lock"></i>
          Solo el creador del juego puede modificar la configuración.
        </Message>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import InputText from 'primevue/inputtext'
import Slider from 'primevue/slider'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Badge from 'primevue/badge'
import Divider from 'primevue/divider'

// Props
interface Game {
  id: string
  name: string
  creator_id: string
  max_players: number
  players: any[]
  status: string
  roles: Record<string, any>
  created_at: string
  current_round: number
  is_first_night: boolean
}

interface Props {
  game: Game
  canEdit: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update-settings': [settings: any]
}>()

// Reactive state
const isSaving = ref(false)
const showAdvancedRoles = ref(false)

// Form data
const formData = reactive({
  name: props.game.name,
  max_players: props.game.max_players,
  roles: {
    cupid_enabled: true,
    witch_enabled: true,
    seer_enabled: true,
    hunter_enabled: true
  },
  rules: {
    allow_dead_chat: false,
    show_role_on_death: true,
    day_duration_minutes: 8,
    night_duration_minutes: 3
  }
})

// Form validation
const errors = reactive({
  name: '',
  max_players: ''
})

// Watch for prop changes
watch(() => props.game, (newGame) => {
  if (newGame) {
    formData.name = newGame.name
    formData.max_players = newGame.max_players
  }
}, { immediate: true })

// Computed
const isFormValid = computed(() => {
  return formData.name.trim().length > 0 &&
         formData.max_players >= 4 &&
         formData.max_players <= 24
})

// Methods
const validateForm = () => {
  errors.name = ''
  errors.max_players = ''

  if (!formData.name.trim()) {
    errors.name = 'El nombre del juego es requerido'
  }

  if (formData.max_players < 4) {
    errors.max_players = 'Mínimo 4 jugadores'
  } else if (formData.max_players > 24) {
    errors.max_players = 'Máximo 24 jugadores'
  }

  return Object.values(errors).every(error => !error)
}

const saveSettings = async () => {
  if (!validateForm() || !isFormValid.value) return

  isSaving.value = true

  try {
    const settings = {
      name: formData.name.trim(),
      max_players: formData.max_players,
      roles: { ...formData.roles },
      rules: { ...formData.rules }
    }

    // Emit to parent component
    emit('update-settings', settings)

  } catch (error) {
    console.error('Error saving settings:', error)
  } finally {
    isSaving.value = false
  }
}

const resetSettings = () => {
  formData.name = props.game.name
  formData.max_players = props.game.max_players
  formData.roles = {
    cupid_enabled: true,
    witch_enabled: true,
    seer_enabled: true,
    hunter_enabled: true
  }
  formData.rules = {
    allow_dead_chat: false,
    show_role_on_death: true,
    day_duration_minutes: 8,
    night_duration_minutes: 3
  }

  // Clear errors
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })
}

const getRoleDistribution = (playerCount: number) => {
  const roles = []

  // Basic roles calculation based on player count
  const werewolfCount = Math.floor(playerCount / 4) + 1
  const villagerCount = playerCount - werewolfCount - getSpecialRolesCount(playerCount)

  roles.push({
    name: 'Hombres Lobo',
    count: werewolfCount,
    icon: 'pi pi-eye',
    color: '#ef4444'
  })

  roles.push({
    name: 'Aldeanos',
    count: Math.max(1, villagerCount),
    icon: 'pi pi-users',
    color: '#10b981'
  })

  // Special roles
  if (playerCount >= 6 && formData.roles.seer_enabled) {
    roles.push({
      name: 'Vidente',
      count: 1,
      icon: 'pi pi-eye',
      color: '#3b82f6'
    })
  }

  if (playerCount >= 8 && formData.roles.witch_enabled) {
    roles.push({
      name: 'Bruja',
      count: 1,
      icon: 'pi pi-heart',
      color: '#8b5cf6'
    })
  }

  if (playerCount >= 10 && formData.roles.hunter_enabled) {
    roles.push({
      name: 'Cazador',
      count: 1,
      icon: 'pi pi-target',
      color: '#f59e0b'
    })
  }

  if (playerCount >= 12 && formData.roles.cupid_enabled) {
    roles.push({
      name: 'Cupido',
      count: 1,
      icon: 'pi pi-heart-fill',
      color: '#ec4899'
    })
  }

  return roles
}

const getSpecialRolesCount = (playerCount: number) => {
  let count = 0
  if (playerCount >= 6 && formData.roles.seer_enabled) count++
  if (playerCount >= 8 && formData.roles.witch_enabled) count++
  if (playerCount >= 10 && formData.roles.hunter_enabled) count++
  if (playerCount >= 12 && formData.roles.cupid_enabled) count++
  return count
}
</script>

<style scoped>
.game-settings {
  padding: 0;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.settings-section {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  background: var(--surface-0);
}

.section-title {
  margin: 0 0 1.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-color);
  font-size: 1.125rem;
  font-weight: 600;
}

.field {
  margin-bottom: 1.5rem;
}

.field:last-child {
  margin-bottom: 0;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.w-full {
  width: 100%;
}

.slider-container {
  margin-top: 1rem;
}

.player-slider,
.duration-slider {
  width: 100%;
  margin-bottom: 1rem;
}

.slider-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.current-value {
  font-weight: 600;
  color: var(--primary-color);
  font-size: 1rem;
}

.slider-range {
  color: var(--text-color-secondary);
}

.roles-config {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.auto-roles-info {
  margin-bottom: 1rem;
}

.info-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.info-content i {
  font-size: 1.125rem;
  margin-top: 0.125rem;
}

.info-content div {
  flex: 1;
}

.info-content strong {
  display: block;
  margin-bottom: 0.25rem;
}

.info-content p {
  margin: 0;
  font-size: 0.875rem;
  opacity: 0.9;
}

.role-distribution h5 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-weight: 500;
}

.roles-preview {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.role-preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--surface-100);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.role-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.role-info i {
  font-size: 1rem;
}

.role-name {
  font-weight: 500;
  color: var(--text-color);
}

.advanced-roles {
  padding-top: 1rem;
}

.advanced-roles h5 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-weight: 500;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.field-checkbox label {
  margin: 0;
  cursor: pointer;
  font-weight: 500;
}

.field small {
  display: block;
  color: var(--text-color-secondary);
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.advanced-toggle {
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.settings-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem;
  background: var(--surface-50);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.readonly-message {
  padding: 1rem;
  text-align: center;
}

/* Responsive design */
@media (max-width: 768px) {
  .settings-section {
    padding: 1rem;
  }

  .settings-actions {
    flex-direction: column;
    padding: 1rem;
  }

  .settings-actions .p-button {
    width: 100%;
  }

  .roles-preview {
    gap: 0.5rem;
  }

  .role-preview-item {
    padding: 0.5rem;
  }

  .slider-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
