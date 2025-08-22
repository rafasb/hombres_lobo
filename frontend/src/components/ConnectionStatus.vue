<template>
  <div class="card mb-3">
    <div class="card-body">
      <!-- Estado principal de conexión -->
      <div class="d-flex align-items-center mb-2" :class="headerClass">
        <span
          class="me-2"
          :class="['status-dot', {
            'bg-success': props.connectionStatusClass === 'connected',
            'bg-warning': props.connectionStatusClass === 'reconnecting',
            'bg-danger': props.connectionStatusClass !== 'connected' && props.connectionStatusClass !== 'reconnecting'
          }]"
          aria-hidden="true"
        ></span>

        <div class="flex-grow-1">
          <div class="fw-semibold">{{ props.connectionStatusText }}</div>
          <div v-if="props.gameConnectionState.lastUpdate" class="small text-muted">
            Última actualización: {{ formatTime(props.gameConnectionState.lastUpdate) }}
          </div>
        </div>

        <div class="ms-2 text-end d-none d-sm-block">
          <small class="text-muted">{{ props.gameConnectionState.connectedPlayersCount }} / {{ props.gameConnectionState.totalPlayersCount }}</small>
        </div>
      </div>

      <!-- Estado del usuario en el juego -->
      <div :class="['mb-3 p-2 rounded', props.isUserActiveInLobby ? 'border-start border-4 border-success bg-success bg-opacity-10' : 'bg-light']">
        <div class="small fw-medium">{{ props.connectionHealthText }}</div>
      </div>

      <!-- Estadísticas de jugadores conectados -->
      <div v-if="props.gameConnectionState.totalPlayersCount > 0">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <div class="fw-semibold">Estado de jugadores</div>
          <div class="text-muted small d-sm-none">{{ props.gameConnectionState.connectedPlayersCount }} / {{ props.gameConnectionState.totalPlayersCount }}</div>
        </div>

        <!-- Lista detallada de jugadores (expandible) -->
        <ul v-if="showPlayersDetail" class="list-group mb-2">
          <li
            v-for="player in props.gameConnectionState.playersStatus"
            :key="player.playerId"
            class="list-group-item d-flex align-items-center justify-content-between"
          >
            <div class="d-flex align-items-center">
              <span :class="['player-dot me-2', player.isConnected ? 'bg-success' : 'bg-danger']" aria-hidden="true"></span>
              <span class="fw-medium">{{ player.username }}</span>
            </div>
            <div class="small text-muted">
              <span v-if="player.lastSeen">{{ formatLastSeen(player.lastSeen) }}</span>
            </div>
          </li>
        </ul>

        <button @click="showPlayersDetail = !showPlayersDetail" class="btn btn-sm btn-outline-secondary">
          {{ showPlayersDetail ? 'Ocultar detalles' : 'Ver detalles' }}
        </button>
      </div>

      <!-- Acciones de conexión -->
      <div v-if="!props.connectionStatus.isConnected" class="mt-3 text-center">
        <button @click="reconnect" class="btn btn-primary" :disabled="props.connectionStatus.isReconnecting">
          {{ props.connectionStatus.isReconnecting ? 'Reconectando...' : 'Reconectar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { GameConnectionState } from '../composables/useGameConnection'
import type { ConnectionStatus } from '../types'

interface Props {
  gameConnectionState: GameConnectionState
  connectionStatus: ConnectionStatus
  connectionStatusText: string
  connectionStatusClass: string
  isUserActiveInLobby: boolean
  connectionHealthText: string
}

interface Emits {
  (e: 'reconnect'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const showPlayersDetail = ref(false)

const headerClass = computed(() => {
  return {
    'text-success': props.connectionStatusClass === 'connected',
    'text-warning': props.connectionStatusClass === 'reconnecting',
    'text-danger': props.connectionStatusClass !== 'connected' && props.connectionStatusClass !== 'reconnecting'
  }
})

const reconnect = () => {
  emit('reconnect')
}

const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('es-ES', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  })
}

const formatLastSeen = (date: Date): string => {
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diff < 60) return 'hace un momento'
  if (diff < 3600) return `hace ${Math.floor(diff / 60)} min`
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)} h`
  return date.toLocaleDateString('es-ES')
}
</script>
<style scoped>
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.player-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.fw-medium { font-weight: 600; }
</style>
