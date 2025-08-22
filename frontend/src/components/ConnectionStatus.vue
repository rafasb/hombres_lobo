<template>
  <div class="connection-status">
    <!-- Estado principal de conexión -->
    <div class="connection-header" :class="`status-${props.connectionStatusClass}`">
      <div class="connection-icon">
        <div v-if="props.connectionStatusClass === 'connected'" class="status-dot connected"></div>
        <div v-else-if="props.connectionStatusClass === 'reconnecting'" class="status-dot reconnecting"></div>
        <div v-else class="status-dot disconnected"></div>
      </div>
      <div class="connection-info">
        <div class="connection-text">{{ props.connectionStatusText }}</div>
        <div v-if="props.gameConnectionState.lastUpdate" class="last-update">
          Última actualización: {{ formatTime(props.gameConnectionState.lastUpdate) }}
        </div>
      </div>
    </div>

    <!-- Estado del usuario en el juego -->
    <div class="user-status" :class="{ 'active': props.isUserActiveInLobby }">
      <div class="user-status-text">{{ props.connectionHealthText }}</div>
    </div>

    <!-- Estadísticas de jugadores conectados -->
    <div v-if="props.gameConnectionState.totalPlayersCount > 0" class="players-stats">
      <div class="stats-header">
        <span class="stats-title">Estado de jugadores</span>
        <span class="stats-count">
          {{ props.gameConnectionState.connectedPlayersCount }} / {{ props.gameConnectionState.totalPlayersCount }} conectados
        </span>
      </div>
      
      <!-- Lista detallada de jugadores (expandible) -->
      <div v-if="showPlayersDetail" class="players-detail">
        <div 
          v-for="player in props.gameConnectionState.playersStatus" 
          :key="player.playerId"
          class="player-status-item"
          :class="{ 'connected': player.isConnected }"
        >
          <div class="player-status-dot" :class="{ 'online': player.isConnected }"></div>
          <span class="player-name">{{ player.username }}</span>
          <span v-if="player.lastSeen" class="last-seen">
            {{ formatLastSeen(player.lastSeen) }}
          </span>
        </div>
      </div>

      <!-- Toggle para mostrar/ocultar detalles -->
      <button 
        @click="showPlayersDetail = !showPlayersDetail"
        class="toggle-details-btn"
      >
        {{ showPlayersDetail ? 'Ocultar detalles' : 'Ver detalles' }}
      </button>
    </div>

    <!-- Acciones de conexión -->
    <div v-if="!props.connectionStatus.isConnected" class="connection-actions">
      <button @click="reconnect" class="reconnect-btn" :disabled="props.connectionStatus.isReconnecting">
        {{ props.connectionStatus.isReconnecting ? 'Reconectando...' : 'Reconectar' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
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
.connection-status {
  background: var(--background-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.connection-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.connection-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: relative;
}

.status-dot.connected {
  background-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.3);
}

.status-dot.reconnecting {
  background-color: #f59e0b;
  animation: pulse 2s infinite;
}

.status-dot.disconnected {
  background-color: #ef4444;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.connection-info {
  flex: 1;
}

.connection-text {
  font-weight: 600;
  margin-bottom: 2px;
}

.status-connected .connection-text {
  color: #10b981;
}

.status-reconnecting .connection-text {
  color: #f59e0b;
}

.status-disconnected .connection-text {
  color: #ef4444;
}

.last-update {
  font-size: 12px;
  color: var(--text-secondary);
}

.user-status {
  padding: 8px 12px;
  background: var(--background-tertiary);
  border-radius: 6px;
  margin-bottom: 12px;
  border-left: 4px solid var(--border-color);
}

.user-status.active {
  border-left-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.user-status-text {
  font-size: 14px;
  font-weight: 500;
}

.players-stats {
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.stats-title {
  font-weight: 600;
  color: var(--text-primary);
}

.stats-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.players-detail {
  margin: 12px 0;
}

.player-status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
}

.player-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ef4444;
}

.player-status-dot.online {
  background-color: #10b981;
}

.player-name {
  font-weight: 500;
  flex: 1;
}

.last-seen {
  font-size: 12px;
  color: var(--text-secondary);
}

.toggle-details-btn {
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-details-btn:hover {
  background: var(--background-tertiary);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.connection-actions {
  margin-top: 12px;
  text-align: center;
}

.reconnect-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.reconnect-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.reconnect-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .connection-status {
    padding: 12px;
  }
  
  .stats-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .player-status-item {
    padding: 8px 0;
  }
}
</style>
