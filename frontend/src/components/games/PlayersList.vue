<template>
  <div class="players-list">
    <!-- Empty state -->
    <div v-if="!players || players.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="pi pi-users"></i>
      </div>
      <h3>No hay jugadores aún</h3>
      <p>Esperando a que se unan otros jugadores...</p>
    </div>

    <!-- Players grid -->
    <div v-else class="players-grid">
      <div
        v-for="player in players"
        :key="player.id"
        class="player-card"
        :class="{
          'is-host': player.id === hostId,
          'is-current-user': player.id === currentUserId,
          'is-offline': player.status === 'inactive'
        }"
      >
        <!-- Player avatar -->
        <div class="player-avatar">
          <div class="avatar-circle">
            <i class="pi pi-user"></i>
          </div>
          <!-- Host crown -->
          <div v-if="player.id === hostId" class="host-crown">
            <i class="pi pi-crown" title="Creador del juego"></i>
          </div>
          <!-- Status indicator -->
          <div
            class="status-indicator"
            :class="{
              'status-online': player.status === 'active',
              'status-offline': player.status === 'inactive'
            }"
            :title="getStatusText(player.status)"
          ></div>
        </div>

        <!-- Player info -->
        <div class="player-info">
          <div class="player-name">
            {{ player.username }}
            <span v-if="player.id === currentUserId" class="you-label">(Tú)</span>
          </div>
          <div class="player-email">
            {{ player.email }}
          </div>

          <!-- Player role badge (if assigned) -->
          <div v-if="playerRole(player.id)" class="player-role">
            <Tag
              :value="playerRole(player.id)"
              severity="secondary"
              class="role-tag"
            />
          </div>

          <!-- Player status -->
          <div class="player-status">
            <div class="status-row">
              <span class="status-label">Estado:</span>
              <Tag
                :value="getStatusLabel(player.status)"
                :severity="getStatusSeverity(player.status)"
                class="status-tag"
              />
            </div>

            <!-- Connection time -->
            <div class="connection-info">
              <i class="pi pi-clock"></i>
              <span>Unido {{ formatJoinTime(player.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Player actions (for host only) -->
        <div v-if="showHostActions && isCurrentUserHost && player.id !== hostId" class="player-actions">
          <Button
            icon="pi pi-times"
            class="p-button-text p-button-sm p-button-danger"
            title="Expulsar jugador"
            @click="$emit('kick-player', player.id)"
          />
        </div>
      </div>
    </div>

    <!-- Players summary -->
    <div v-if="players && players.length > 0" class="players-summary">
      <div class="summary-stats">
        <div class="stat-item">
          <i class="pi pi-users"></i>
          <span>{{ players.length }} jugador{{ players.length !== 1 ? 'es' : '' }}</span>
        </div>
        <div class="stat-item">
          <i class="pi pi-check-circle"></i>
          <span>{{ onlinePlayers }} activo{{ onlinePlayers !== 1 ? 's' : '' }}</span>
        </div>
        <div v-if="offlinePlayers > 0" class="stat-item warning">
          <i class="pi pi-exclamation-triangle"></i>
          <span>{{ offlinePlayers }} desconectado{{ offlinePlayers !== 1 ? 's' : '' }}</span>
        </div>
      </div>

      <!-- Waiting message -->
      <div v-if="needMorePlayers" class="waiting-message">
        <Message severity="info" :closable="false">
          <div class="waiting-content">
            <i class="pi pi-hourglass"></i>
            <div>
              <strong>Esperando más jugadores</strong>
              <p>Se necesitan al menos {{ minimumPlayers - players.length }} jugador{{ (minimumPlayers - players.length) !== 1 ? 'es' : '' }} más para comenzar</p>
            </div>
          </div>
        </Message>
      </div>

      <!-- Ready to start message -->
      <div v-else-if="isCurrentUserHost" class="ready-message">
        <Message severity="success" :closable="false">
          <div class="ready-content">
            <i class="pi pi-check-circle"></i>
            <div>
              <strong>¡Listo para comenzar!</strong>
              <p>Ya hay suficientes jugadores. Puedes iniciar la partida cuando estés listo.</p>
            </div>
          </div>
        </Message>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Message from 'primevue/message'

// Props
interface Player {
  id: string
  username: string
  email: string
  role: 'admin' | 'player'
  status: 'active' | 'inactive' | 'banned'
  hashed_password: string
  created_at: string
  updated_at: string
}

interface Props {
  players: Player[]
  hostId: string
  currentUserId?: string
  showHostActions?: boolean
  minimumPlayers?: number
  gameRoles?: Record<string, any>
}

const props = withDefaults(defineProps<Props>(), {
  showHostActions: true,
  minimumPlayers: 4,
  gameRoles: () => ({})
})

// Emits
defineEmits<{
  'kick-player': [playerId: string]
}>()

// Computed properties
const isCurrentUserHost = computed(() => {
  return props.currentUserId === props.hostId
})

const onlinePlayers = computed(() => {
  return props.players.filter(p => p.status === 'active').length
})

const offlinePlayers = computed(() => {
  return props.players.filter(p => p.status === 'inactive').length
})

const needMorePlayers = computed(() => {
  return props.players.length < props.minimumPlayers
})

// Methods
const playerRole = (playerId: string) => {
  const roleEntry = Object.entries(props.gameRoles).find(([_, roleInfo]: [string, any]) =>
    roleInfo.model_player_id === playerId
  )
  return roleEntry ? roleEntry[1].role : null
}

const getStatusText = (status: string) => {
  const statusMap = {
    'active': 'Conectado',
    'inactive': 'Desconectado',
    'banned': 'Expulsado'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getStatusLabel = (status: string) => {
  const statusMap = {
    'active': 'Activo',
    'inactive': 'Inactivo',
    'banned': 'Expulsado'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getStatusSeverity = (status: string) => {
  const severityMap = {
    'active': 'success',
    'inactive': 'warning',
    'banned': 'danger'
  }
  return severityMap[status as keyof typeof severityMap] || 'secondary'
}

const formatJoinTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))

  if (diffInMinutes < 1) return 'hace un momento'
  if (diffInMinutes < 60) return `hace ${diffInMinutes} minuto${diffInMinutes !== 1 ? 's' : ''}`

  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `hace ${diffInHours} hora${diffInHours !== 1 ? 's' : ''}`

  return date.toLocaleDateString('es-ES', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.players-list {
  padding: 0;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-color-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.players-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.player-card {
  background: var(--surface-0);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  position: relative;
  transition: all 0.2s ease-in-out;
}

.player-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.player-card.is-current-user {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(59, 130, 246, 0.02) 100%);
  border-color: var(--primary-color);
}

.player-card.is-host {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(245, 158, 11, 0.02) 100%);
  border-color: #f59e0b;
}

.player-card.is-offline {
  opacity: 0.7;
  filter: grayscale(20%);
}

.player-avatar {
  position: relative;
  margin-bottom: 1rem;
  display: flex;
  justify-content: center;
}

.avatar-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  position: relative;
}

.host-crown {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #f59e0b;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  border: 2px solid var(--surface-0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid var(--surface-0);
}

.status-indicator.status-online {
  background: #10b981;
}

.status-indicator.status-offline {
  background: #94a3b8;
}

.player-info {
  text-align: center;
}

.player-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
  word-break: break-word;
}

.you-label {
  font-size: 0.875rem;
  color: var(--primary-color);
  font-weight: 500;
}

.player-email {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
  word-break: break-word;
}

.player-role {
  margin-bottom: 1rem;
}

.role-tag {
  font-size: 0.75rem;
}

.player-status {
  border-top: 1px solid var(--border-color);
  padding-top: 1rem;
}

.status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.status-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.status-tag {
  font-size: 0.75rem;
}

.connection-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.player-actions {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
}

.players-summary {
  border-top: 1px solid var(--border-color);
  padding-top: 1.5rem;
}

.summary-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--surface-100);
  border-radius: 20px;
  font-size: 0.875rem;
  color: var(--text-color);
}

.stat-item.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.stat-item i {
  font-size: 0.875rem;
}

.waiting-message,
.ready-message {
  margin-top: 1rem;
}

.waiting-content,
.ready-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.waiting-content i,
.ready-content i {
  font-size: 1.25rem;
  margin-top: 0.125rem;
}

.waiting-content div,
.ready-content div {
  flex: 1;
}

.waiting-content strong,
.ready-content strong {
  display: block;
  margin-bottom: 0.25rem;
}

.waiting-content p,
.ready-content p {
  margin: 0;
  font-size: 0.875rem;
  opacity: 0.9;
}

/* Responsive design */
@media (max-width: 768px) {
  .players-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .player-card {
    padding: 1rem;
  }

  .avatar-circle {
    width: 50px;
    height: 50px;
    font-size: 1.25rem;
  }

  .host-crown {
    width: 20px;
    height: 20px;
    font-size: 0.625rem;
  }

  .summary-stats {
    justify-content: center;
  }

  .stat-item {
    font-size: 0.75rem;
    padding: 0.375rem 0.75rem;
  }
}
</style>
