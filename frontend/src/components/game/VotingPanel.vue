<template>
  <div class="voting-panel">
    <!-- Encabezado de la votación -->
    <div class="voting-header">
      <div class="flex justify-content-between align-items-center mb-3">
        <h3 class="m-0">
          <i class="pi pi-check-square mr-2"></i>
          Votación Activa
        </h3>
        <div class="voting-timer" v-if="timeRemaining > 0">
          <i class="pi pi-clock mr-1"></i>
          {{ formatTimeRemaining(timeRemaining) }}
        </div>
      </div>

      <!-- Progress bar del tiempo -->
      <ProgressBar
        v-if="timeRemaining > 0"
        :value="timeProgress"
        :showValue="false"
        class="mb-3"
        :class="{ 'progress-danger': timeRemaining < 30 }"
      />

      <!-- Información de votación -->
      <div class="voting-info">
        <div class="flex justify-content-between text-sm mb-2">
          <span>
            <i class="pi pi-users mr-1"></i>
            {{ votingProgress.voted }} / {{ votingProgress.total }} votantes
          </span>
          <span class="text-primary font-semibold">
            {{ votingProgress.percentage }}% completado
          </span>
        </div>
      </div>
    </div>

    <!-- Estado del usuario -->
    <div class="user-voting-status mb-4">
      <div v-if="!isUserEligible" class="voting-disabled">
        <Message severity="info" :closable="false">
          <i class="pi pi-info-circle mr-2"></i>
          No puedes votar en esta ronda
        </Message>
      </div>

      <div v-else-if="hasUserVoted" class="vote-confirmed">
        <Message severity="success" :closable="false">
          <i class="pi pi-check mr-2"></i>
          Has votado por <strong>{{ getPlayerName(userVote!) }}</strong>
        </Message>
        <div class="text-center mt-2">
          <Button
            label="Cambiar voto"
            icon="pi pi-refresh"
            severity="secondary"
            size="small"
            @click="showVoteOptions = true"
          />
        </div>
      </div>

      <div v-else-if="canVote" class="can-vote">
        <Message severity="warn" :closable="false">
          <i class="pi pi-exclamation-triangle mr-2"></i>
          ¡Es tu turno de votar! Selecciona a quién eliminar.
        </Message>
      </div>

      <div v-else class="voting-locked">
        <Message severity="info" :closable="false">
          <i class="pi pi-lock mr-2"></i>
          Votación no disponible en este momento
        </Message>
      </div>
    </div>

    <!-- Lista de objetivos de votación -->
    <div v-if="(canVote && !hasUserVoted) || showVoteOptions" class="voting-targets">
      <h4 class="mb-3">
        <i class="pi pi-users mr-2"></i>
        Selecciona tu voto:
      </h4>

      <div class="target-list">
        <div
          v-for="player in validTargets"
          :key="player.id"
          class="target-card"
          :class="{
            'target-selected': userVote === player.id,
            'target-leading': leadingCandidate?.playerId === player.id
          }"
          @click="handleVoteClick(player.id)"
        >
          <div class="target-info">
            <div class="target-avatar">
              <Avatar
                :label="player.name.charAt(0).toUpperCase()"
                shape="circle"
                size="large"
                :style="{ backgroundColor: getPlayerColor(player.id) }"
              />
            </div>

            <div class="target-details">
              <div class="target-name">{{ player.name }}</div>
              <div class="target-votes" v-if="voteCountsByTarget[player.id]">
                <i class="pi pi-arrow-up mr-1"></i>
                {{ voteCountsByTarget[player.id] }} votos
              </div>
            </div>
          </div>

          <div class="target-actions">
            <Button
              :label="userVote === player.id ? 'Votado' : 'Votar'"
              :icon="userVote === player.id ? 'pi pi-check' : 'pi pi-arrow-up'"
              :severity="userVote === player.id ? 'success' : 'primary'"
              :disabled="!canVote && userVote !== player.id"
              size="small"
            />
          </div>
        </div>
      </div>

      <div v-if="showVoteOptions && hasUserVoted" class="text-center mt-3">
        <Button
          label="Cancelar"
          icon="pi pi-times"
          severity="secondary"
          size="small"
          @click="showVoteOptions = false"
        />
      </div>
    </div>

    <!-- Resultados de la votación -->
    <div v-if="voteResults" class="voting-results mt-4">
      <h4 class="mb-3">
        <i class="pi pi-chart-bar mr-2"></i>
        Resultados de la Votación
      </h4>

      <div v-if="voteResults.tie" class="tie-result">
        <Message severity="warn" :closable="false">
          <i class="pi pi-exclamation-triangle mr-2"></i>
          <strong>¡Empate!</strong> Se necesita una nueva votación.
        </Message>
      </div>

      <div v-else-if="voteResults.winner" class="winner-result">
        <Message severity="error" :closable="false">
          <i class="pi pi-times-circle mr-2"></i>
          <strong>{{ getPlayerName(voteResults.winner) }}</strong> ha sido eliminado.
        </Message>
      </div>

      <!-- Detalle de votos -->
      <div class="vote-breakdown mt-3">
        <h5>Detalle de votos:</h5>
        <div class="vote-counts">
          <div
            v-for="[playerId, count] in Object.entries(voteResults.vote_counts)"
            :key="playerId"
            class="vote-count-item"
          >
            <span class="player-name">{{ getPlayerName(playerId) }}</span>
            <span class="vote-count">{{ count }} votos</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado sin votación activa -->
    <div v-if="!isVotingActive && !voteResults" class="no-voting">
      <div class="text-center p-4">
        <i class="pi pi-clock text-4xl text-400 mb-3"></i>
        <p class="text-600 m-0">No hay votación activa en este momento</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useVoting } from '@/composables/useVoting'
import { useToast } from 'primevue/usetoast'

import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import Message from 'primevue/message'
import Avatar from 'primevue/avatar'

const toast = useToast()

const {
  votingSession,
  userVote,
  canVote,
  isVotingActive,
  hasUserVoted,
  validTargets,
  voteResults,
  timeRemaining,
  isUserEligible,
  votingProgress,
  voteCountsByTarget,
  leadingCandidate,
  castVote,
  formatTimeRemaining,
  getPlayerName
} = useVoting()

// Estado local
const showVoteOptions = ref(false)

// Computeds
const timeProgress = computed(() => {
  if (!votingSession.value || timeRemaining.value <= 0) return 0
  const totalTime = votingSession.value.ends_at
    ? new Date(votingSession.value.ends_at).getTime() - new Date(votingSession.value.started_at).getTime()
    : 120000 // 2 minutos por defecto
  const elapsed = totalTime - (timeRemaining.value * 1000)
  return Math.min(100, Math.max(0, (elapsed / totalTime) * 100))
})

// Métodos
const handleVoteClick = async (playerId: string) => {
  if (!canVote.value && userVote.value !== playerId) {
    toast.add({
      severity: 'warn',
      summary: 'No puedes votar',
      detail: 'No tienes permisos para votar en este momento',
      life: 3000
    })
    return
  }

  try {
    castVote(playerId)
    showVoteOptions.value = false

    toast.add({
      severity: 'success',
      summary: 'Voto emitido',
      detail: `Has votado por ${getPlayerName(playerId)}`,
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error al votar',
      detail: 'No se pudo registrar tu voto. Inténtalo de nuevo.',
      life: 3000
    })
  }
}

const getPlayerColor = (playerId: string): string => {
  // Generar color consistente basado en el ID
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
  ]
  const hash = playerId.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0)
    return a & a
  }, 0)
  return colors[Math.abs(hash) % colors.length]
}
</script>

<style scoped>
.voting-panel {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.voting-header {
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.voting-timer {
  background: var(--primary-color);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.progress-danger :deep(.p-progressbar-value) {
  background: #ef4444;
}

.target-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.target-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.target-card:hover {
  border-color: var(--primary-color);
  background: var(--primary-50);
}

.target-card.target-selected {
  border-color: var(--green-500);
  background: var(--green-50);
}

.target-card.target-leading {
  border-color: var(--orange-500);
  background: var(--orange-50);
}

.target-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.target-details {
  display: flex;
  flex-direction: column;
}

.target-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.target-votes {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.vote-breakdown {
  background: var(--surface-50);
  padding: 1rem;
  border-radius: 8px;
}

.vote-count-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--surface-200);
}

.vote-count-item:last-child {
  border-bottom: none;
}

.no-voting {
  text-align: center;
  color: var(--text-color-secondary);
}

@media (max-width: 768px) {
  .voting-panel {
    padding: 1rem;
  }

  .target-card {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }

  .target-info {
    flex-direction: column;
    text-align: center;
  }
}
</style>
