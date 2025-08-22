<template>
  <div class="card h-100 game-card-hover"
       :class="getBootstrapCardClass(game.status)"
       style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: none; border-radius: 15px; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1); transition: transform 0.3s ease;">

    <div class="card-header d-flex justify-content-between align-items-center border-0 pb-2" style="background: transparent;">
      <h5 class="card-title mb-0 fw-bold text-dark text-truncate" style="max-width: 200px;">
        {{ game.name }}
      </h5>
      <span class="badge fs-6" :class="getStatusBadgeClass(game.status)">
        {{ getStatusText(game.status) }}
      </span>
    </div>

    <div class="card-body pt-2">
      <div class="mb-3">
        <div class="d-flex justify-content-between mb-2">
          <span class="text-muted">Jugadores:</span>
          <span class="fw-semibold">{{ game.players.length }}/{{ game.max_players }}</span>
        </div>

        <div class="d-flex justify-content-between mb-2">
          <span class="text-muted">Creador:</span>
          <span class="fw-semibold text-truncate" style="max-width: 120px;">{{ getCreatorName(game) }}</span>
        </div>

        <div class="d-flex justify-content-between mb-2">
          <span class="text-muted">Creada:</span>
          <span class="fw-semibold">{{ formatDate(game.created_at || '') }}</span>
        </div>

        <div class="d-flex justify-content-between mb-2" v-if="game.status !== 'waiting'">
          <span class="text-muted">Ronda:</span>
          <span class="fw-semibold">{{ game.current_round }}</span>
        </div>
      </div>

      <div class="d-flex flex-wrap gap-2">
        <button v-if="canJoinGame(game)"
                class="btn btn-success flex-fill"
                @click="$emit('join', game.id)"
                :disabled="loading"
                style="border-radius: 10px;">
          <i class="bi bi-box-arrow-in-right me-1"></i>
          Unirse
        </button>

        <button v-if="canLeaveGame(game)"
                class="btn btn-warning flex-fill"
                @click="$emit('leave', game.id)"
                :disabled="loading"
                style="border-radius: 10px;">
          <i class="bi bi-box-arrow-left me-1"></i>
          Abandonar
        </button>

        <button v-if="canViewGame(game)"
                class="btn btn-info flex-fill"
                @click="$emit('view', game.id)"
                style="border-radius: 10px;">
          <i class="bi bi-eye me-1"></i>
          Ver
        </button>

        <button v-if="canDeleteGame(game)"
                class="btn btn-danger flex-fill"
                @click="$emit('delete', game.id)"
                :disabled="loading"
                style="border-radius: 10px;">
          <i class="bi bi-trash me-1"></i>
          Eliminar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getBootstrapCardClass as _getBootstrapCardClass, getStatusBadgeClass as _getStatusBadgeClass, getStatusText as _getStatusText } from '../composables/useStatusHelpers'
import type { Game } from '../types'

interface Props {
  game: Game
  loading?: boolean
  canJoinGame: (game: Game) => boolean
  canLeaveGame: (game: Game) => boolean
  canViewGame: (game: Game) => boolean
  canDeleteGame: (game: Game) => boolean
  getCreatorName: (game: Game) => string
  formatDate: (dateString: string) => string
}

const props = defineProps<Props>()
defineEmits<{
  (e: 'join', gameId: string): void
  (e: 'leave', gameId: string): void
  (e: 'view', gameId: string): void
  (e: 'delete', gameId: string): void
}>()

// Expose helpers and props to template
const getBootstrapCardClass = _getBootstrapCardClass
const getStatusBadgeClass = _getStatusBadgeClass
const getStatusText = _getStatusText

// Expose props for template
const { game, loading = false, canJoinGame, canLeaveGame, canViewGame, canDeleteGame, getCreatorName, formatDate } = props
</script>

<style scoped>
.game-card-hover:hover { transform: translateY(-5px); }
</style>
