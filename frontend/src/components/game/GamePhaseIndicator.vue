<template>
  <div class="game-phase-indicator">
    <!-- Indicador principal de fase -->
    <div class="phase-header">
      <div class="phase-info">
        <div class="phase-icon" :style="{ color: phaseInfo.color }">
          {{ phaseInfo.icon }}
        </div>
        <div class="phase-details">
          <h3 class="phase-name">{{ phaseInfo.name }}</h3>
          <p class="phase-description">{{ phaseInfo.description }}</p>
        </div>
      </div>

      <div class="phase-timer" v-if="timeRemaining > 0">
        <div class="timer-display">{{ timeRemainingFormatted }}</div>
        <div class="timer-label">restante</div>
      </div>
    </div>

    <!-- Barra de progreso -->
    <div class="phase-progress" v-if="timeRemaining > 0">
      <ProgressBar
        :value="phaseProgressInverse"
        :showValue="false"
        :class="`progress-${phaseInfo.color}`"
      />
      <div class="progress-info">
        <span class="progress-percentage">{{ phaseProgressInverse }}%</span>
        <span class="progress-time">{{ formatTimeRemaining(timeRemaining) }}</span>
      </div>
    </div>

    <!-- Acciones específicas por fase -->
    <div class="phase-actions" v-if="hasActions">
      <!-- Acciones de día -->
      <div v-if="isDay" class="day-actions">
        <div class="action-card">
          <div class="action-icon">💬</div>
          <div class="action-content">
            <h4>Debate abierto</h4>
            <p>Discute con otros jugadores e identifica a los sospechosos</p>
          </div>
        </div>
      </div>

      <!-- Acciones de noche -->
      <div v-if="isNight" class="night-actions">
        <div class="action-card">
          <div class="action-icon">🌙</div>
          <div class="action-content">
            <h4>Fase nocturna</h4>
            <p>Los roles especiales realizan sus acciones en secreto</p>
          </div>
        </div>
      </div>

      <!-- Acciones de votación -->
      <div v-if="isVoting" class="voting-actions">
        <div class="action-card" :class="{ 'action-urgent': canVote }">
          <div class="action-icon">🗳️</div>
          <div class="action-content">
            <h4>¡Tiempo de votar!</h4>
            <p v-if="canVote">Selecciona a quién eliminar de la partida</p>
            <p v-else>Espera a que todos voten</p>
          </div>
          <div v-if="canVote" class="action-button">
            <Button
              label="Ver votación"
              icon="pi pi-arrow-down"
              size="small"
              @click="scrollToVoting"
            />
          </div>
        </div>
      </div>

      <!-- Estado de espera -->
      <div v-if="isWaiting" class="waiting-actions">
        <div class="action-card">
          <div class="action-icon">⏳</div>
          <div class="action-content">
            <h4>Esperando jugadores</h4>
            <p>Aguarda a que todos se conecten para comenzar</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Controles del host -->
    <div v-if="isHost && canForceNextPhase" class="host-controls">
      <Divider />
      <div class="host-actions">
        <h5>
          <i class="pi pi-crown mr-2"></i>
          Controles del Host
        </h5>
        <div class="flex gap-2">
          <Button
            label="Siguiente Fase"
            icon="pi pi-step-forward"
            severity="warning"
            size="small"
            @click="handleForceNextPhase"
            :disabled="forcePhaseLoading"
          />
          <Button
            label="Info"
            icon="pi pi-info-circle"
            severity="secondary"
            size="small"
            @click="showPhaseInfo = true"
          />
        </div>
      </div>
    </div>

    <!-- Información adicional de la fase -->
    <div v-if="showAdditionalInfo" class="phase-extra-info">
      <Divider />
      <div class="extra-info-content">
        <h5>Información de la fase actual:</h5>
        <ul class="phase-rules">
          <li v-for="rule in currentPhaseRules" :key="rule">{{ rule }}</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Dialog de información de fase -->
  <Dialog
    v-model:visible="showPhaseInfo"
    header="Información de Fases"
    :modal="true"
    :closable="true"
    :style="{ width: '50vw' }"
    :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
  >
    <div class="phase-info-dialog">
      <p>Como host, puedes forzar el cambio a la siguiente fase en cualquier momento.</p>
      <p><strong>Uso recomendado:</strong></p>
      <ul>
        <li>Para acelerar el juego durante testing</li>
        <li>Cuando todos los jugadores han completado sus acciones</li>
        <li>En caso de problemas técnicos</li>
      </ul>
      <Message severity="warn" :closable="false">
        <strong>Precaución:</strong> Cambiar de fase prematuramente puede afectar la jugabilidad.
      </Message>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGamePhase } from '@/composables/useGamePhase'
import { useRealtimeGameStore } from '@/stores/realtime-game'
import { useToast } from 'primevue/usetoast'

import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import Divider from 'primevue/divider'
import Dialog from 'primevue/dialog'
import Message from 'primevue/message'

const toast = useToast()
const realtimeGameStore = useRealtimeGameStore()

const {
  currentPhase,
  timeRemaining,
  isHost,
  isWaiting,
  isDay,
  isNight,
  isVoting,
  phaseProgress,
  phaseProgressInverse,
  phaseInfo,
  timeRemainingFormatted,
  canChat,
  canVote,
  canForceNextPhase,
  formatTimeRemaining,
  forceNextPhase
} = useGamePhase()

// Estado local
const showPhaseInfo = ref(false)
const showAdditionalInfo = ref(false)
const forcePhaseLoading = ref(false)

// Computeds
const hasActions = computed(() => {
  return isDay.value || isNight.value || isVoting.value || isWaiting.value
})

const currentPhaseRules = computed(() => {
  const rules: Record<string, string[]> = {
    waiting: [
      'Espera a que todos los jugadores se conecten',
      'El host puede iniciar el juego cuando esté listo'
    ],
    starting: [
      'El juego está comenzando',
      'Se están asignando los roles',
      'Prepárate para la primera noche'
    ],
    night: [
      'Los jugadores no pueden chatear',
      'Los roles especiales actúan en secreto',
      'Los hombres lobo eligen su víctima'
    ],
    day: [
      'Todos pueden participar en el chat',
      'Discute y analiza lo que pasó en la noche',
      'Identifica a los sospechosos'
    ],
    voting: [
      'Solo los jugadores vivos pueden votar',
      'Cada jugador tiene un voto',
      'El jugador con más votos será eliminado'
    ],
    trial: [
      'El acusado puede defenderse',
      'Los demás jugadores pueden hacer preguntas',
      'Tiempo limitado para la defensa'
    ],
    execution: [
      'Se revela el rol del jugador eliminado',
      'Se verifican las condiciones de victoria',
      'Preparación para la siguiente ronda'
    ],
    finished: [
      'El juego ha terminado',
      'Se muestran las estadísticas finales',
      'Se revela quién ganó'
    ]
  }

  return rules[currentPhase.value] || []
})

// Métodos
const handleForceNextPhase = async () => {
  forcePhaseLoading.value = true

  try {
    forceNextPhase()

    toast.add({
      severity: 'success',
      summary: 'Fase avanzada',
      detail: 'Has forzado el cambio a la siguiente fase',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cambiar la fase. Inténtalo de nuevo.',
      life: 3000
    })
  } finally {
    forcePhaseLoading.value = false
  }
}

const scrollToVoting = () => {
  const votingElement = document.querySelector('.voting-panel')
  if (votingElement) {
    votingElement.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<style scoped>
.game-phase-indicator {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.phase-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.phase-icon {
  font-size: 2.5rem;
  filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3));
}

.phase-details h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.phase-details p {
  margin: 0;
  opacity: 0.9;
  font-size: 0.95rem;
}

.phase-timer {
  text-align: center;
}

.timer-display {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.timer-label {
  font-size: 0.75rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.phase-progress {
  margin: 1rem 0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  opacity: 0.9;
}

/* Colores específicos para diferentes fases */
.progress-red :deep(.p-progressbar-value) {
  background: #ef4444;
}

.progress-blue :deep(.p-progressbar-value) {
  background: #3b82f6;
}

.progress-yellow :deep(.p-progressbar-value) {
  background: #f59e0b;
}

.progress-purple :deep(.p-progressbar-value) {
  background: #8b5cf6;
}

.progress-green :deep(.p-progressbar-value) {
  background: #10b981;
}

.phase-actions {
  margin-top: 1rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 0.75rem;
}

.action-card.action-urgent {
  background: rgba(255, 193, 7, 0.2);
  border-color: rgba(255, 193, 7, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.action-icon {
  font-size: 1.5rem;
  min-width: 2rem;
}

.action-content {
  flex: 1;
}

.action-content h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.action-content p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.9;
}

.host-controls {
  margin-top: 1rem;
}

.host-actions h5 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  opacity: 0.9;
}

.phase-extra-info {
  margin-top: 1rem;
}

.extra-info-content h5 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.phase-rules {
  margin: 0;
  padding-left: 1.25rem;
  opacity: 0.9;
}

.phase-rules li {
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

.phase-info-dialog ul {
  margin: 1rem 0;
  padding-left: 1.25rem;
}

.phase-info-dialog li {
  margin-bottom: 0.5rem;
}

@media (max-width: 768px) {
  .game-phase-indicator {
    padding: 1rem;
  }

  .phase-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .phase-icon {
    font-size: 2rem;
  }

  .timer-display {
    font-size: 1.5rem;
  }

  .action-card {
    flex-direction: column;
    text-align: center;
  }

  .host-actions .flex {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
