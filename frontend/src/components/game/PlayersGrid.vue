<template>
  <div class="players-grid">
    <div class="grid-header">
      <h3 class="m-0">
        <i class="pi pi-users mr-2"></i>
        Jugadores ({{ players.length }})
      </h3>
      <div class="player-stats">
        <Badge :value="livingPlayers.length" severity="success" class="mr-2">
          <i class="pi pi-heart mr-1"></i>
          Vivos
        </Badge>
        <Badge :value="deadPlayers.length" severity="danger">
          <i class="pi pi-times mr-1"></i>
          Muertos
        </Badge>
      </div>
    </div>

    <div class="players-container">
      <div
        v-for="player in sortedPlayers"
        :key="player.id"
        class="player-card"
        :class="getPlayerCardClass(player)"
      >
        <!-- Avatar del jugador -->
        <div class="player-avatar">
          <Avatar
            :label="player.name.charAt(0).toUpperCase()"
            shape="circle"
            :size="isCompactView ? 'normal' : 'large'"
            :style="{ backgroundColor: getPlayerColor(player.id) }"
          />
          <div class="avatar-badges">
            <!-- Badge de estado de conexión -->
            <div
              class="connection-indicator"
              :class="{
                'connected': player.isConnected,
                'disconnected': !player.isConnected
              }"
              :title="player.isConnected ? 'Conectado' : 'Desconectado'"
            ></div>

            <!-- Badge de estado vital -->
            <div v-if="!player.isAlive" class="death-indicator" title="Eliminado">
              💀
            </div>
          </div>
        </div>

        <!-- Información del jugador -->
        <div class="player-info">
          <div class="player-name">
            {{ player.name }}
            <span v-if="isCurrentUser(player)" class="current-user-badge">
              (Tú)
            </span>
          </div>

          <div class="player-details">
            <!-- Estado vital -->
            <div class="vital-status">
              <span v-if="player.isAlive" class="status-alive">
                <i class="pi pi-heart mr-1"></i>
                Vivo
              </span>
              <span v-else class="status-dead">
                <i class="pi pi-times mr-1"></i>
                Eliminado
              </span>
            </div>

            <!-- Rol revelado (si aplica) -->
            <div v-if="player.role && shouldShowRole(player)" class="player-role">
              <i class="pi pi-eye mr-1"></i>
              {{ getRoleDisplayName(player.role) }}
            </div>

            <!-- Información de votación -->
            <div v-if="showVotingInfo && votingSession" class="voting-info">
              <!-- Si el jugador ha votado -->
              <div v-if="hasPlayerVoted(player.id)" class="voted-status">
                <i class="pi pi-check-circle text-green-500 mr-1"></i>
                <span class="text-sm">Ha votado</span>
              </div>

              <!-- Si el jugador está siendo votado -->
              <div v-if="getVotesForPlayer(player.id) > 0" class="vote-count">
                <i class="pi pi-arrow-up text-orange-500 mr-1"></i>
                <span class="text-sm font-semibold">
                  {{ getVotesForPlayer(player.id) }} votos
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones disponibles -->
        <div class="player-actions">
          <!-- Botón de votación -->
          <div v-if="canVoteFor(player)" class="vote-action">
            <Button
              :label="userVote === player.id ? 'Votado' : 'Votar'"
              :icon="userVote === player.id ? 'pi pi-check' : 'pi pi-arrow-up'"
              :severity="userVote === player.id ? 'success' : 'primary'"
              size="small"
              @click="handleVoteClick(player.id)"
            />
          </div>

          <!-- Indicador de objetivo de voto válido -->
          <div v-else-if="isValidVotingTarget(player)" class="vote-target-indicator">
            <i class="pi pi-crosshairs text-orange-500" title="Objetivo válido"></i>
          </div>

          <!-- Menú de acciones adicionales -->
          <div v-if="hasPlayerActions(player)" class="additional-actions">
            <Button
              icon="pi pi-ellipsis-v"
              severity="secondary"
              size="small"
              text
              @click="showPlayerMenu($event, player)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Vista compacta toggle -->
    <div class="view-controls">
      <div class="flex align-items-center gap-2">
        <span class="text-sm">Vista:</span>
        <Button
          :icon="isCompactView ? 'pi pi-th-large' : 'pi pi-list'"
          :label="isCompactView ? 'Expandir' : 'Compactar'"
          severity="secondary"
          size="small"
          text
          @click="toggleView"
        />
      </div>
    </div>
  </div>

  <!-- Menu contextual del jugador -->
  <ContextMenu
    ref="playerContextMenu"
    :model="playerMenuItems"
    @hide="selectedPlayer = null"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRealtimeGameStore } from '@/stores/realtime-game'
import { useVoting } from '@/composables/useVoting'
import { useToast } from 'primevue/usetoast'

import Avatar from 'primevue/avatar'
import Badge from 'primevue/badge'
import Button from 'primevue/button'
import ContextMenu from 'primevue/contextmenu'

// Interfaces
interface Player {
  id: string
  name: string
  isAlive: boolean
  isConnected: boolean
  role?: string
}

const toast = useToast()
const realtimeGameStore = useRealtimeGameStore()

const {
  votingSession,
  userVote,
  canVote,
  isVotingActive,
  validTargets,
  voteCountsByTarget,
  castVote,
  getPlayerName
} = useVoting()

// Referencias
const playerContextMenu = ref()

// Estado local
const isCompactView = ref(false)
const selectedPlayer = ref<Player | null>(null)

// Computeds
const players = computed(() => realtimeGameStore.gameState.players)
const livingPlayers = computed(() => realtimeGameStore.gameState.livingPlayers)
const deadPlayers = computed(() => realtimeGameStore.gameState.deadPlayers)
const currentUser = computed(() => realtimeGameStore.currentUser)

const sortedPlayers = computed(() => {
  return [...players.value].sort((a, b) => {
    // Primero jugadores vivos, luego muertos
    if (a.isAlive !== b.isAlive) {
      return a.isAlive ? -1 : 1
    }

    // Dentro de cada grupo, ordenar por nombre
    return a.name.localeCompare(b.name)
  })
})

const showVotingInfo = computed(() => {
  return isVotingActive.value && votingSession.value
})

const playerMenuItems = computed(() => {
  if (!selectedPlayer.value) return []

  const player = selectedPlayer.value
  const items = []

  // Opción de ver perfil (placeholder)
  items.push({
    label: 'Ver perfil',
    icon: 'pi pi-user',
    command: () => {
      // TODO: Implementar vista de perfil
      console.log('Ver perfil de', player.name)
    }
  })

  // Opciones específicas según el contexto
  if (player.isAlive && canVoteFor(player)) {
    items.push({
      separator: true
    })
    items.push({
      label: userVote.value === player.id ? 'Cambiar voto' : 'Votar',
      icon: 'pi pi-arrow-up',
      command: () => handleVoteClick(player.id)
    })
  }

  return items
})

// Métodos
const getPlayerCardClass = (player: Player) => {
  const classes = ['player-card-item']

  if (!player.isAlive) classes.push('player-dead')
  if (!player.isConnected) classes.push('player-disconnected')
  if (isCurrentUser(player)) classes.push('current-user')
  if (userVote.value === player.id) classes.push('voted-for')
  if (isVotingActive.value && canVoteFor(player)) classes.push('votable')

  return classes.join(' ')
}

const getPlayerColor = (playerId: string): string => {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8C471', '#82E0AA', '#AED6F1', '#D7BDE2'
  ]
  const hash = playerId.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0)
    return a & a
  }, 0)
  return colors[Math.abs(hash) % colors.length]
}

const isCurrentUser = (player: Player): boolean => {
  return currentUser.value?.id.toString() === player.id
}

const shouldShowRole = (player: Player): boolean => {
  // Mostrar rol solo si el jugador está muerto o si es el usuario actual
  return !player.isAlive || isCurrentUser(player)
}

const getRoleDisplayName = (role: string): string => {
  const roleNames: Record<string, string> = {
    'villager': 'Aldeano',
    'werewolf': 'Hombre Lobo',
    'seer': 'Vidente',
    'witch': 'Bruja',
    'hunter': 'Cazador',
    'sheriff': 'Sheriff',
    'cupid': 'Cupido',
    'wild_child': 'Niño Salvaje'
  }
  return roleNames[role] || role
}

const canVoteFor = (player: Player): boolean => {
  return canVote.value &&
         isVotingActive.value &&
         validTargets.value.some(target => target.id === player.id)
}

const isValidVotingTarget = (player: Player): boolean => {
  return isVotingActive.value &&
         validTargets.value.some(target => target.id === player.id) &&
         !canVote.value
}

const hasPlayerVoted = (playerId: string): boolean => {
  if (!votingSession.value) return false
  return votingSession.value.votes.some(vote => vote.voter_id === playerId)
}

const getVotesForPlayer = (playerId: string): number => {
  return voteCountsByTarget.value[playerId] || 0
}

const hasPlayerActions = (player: Player): boolean => {
  // Por ahora solo mostrar menú para jugadores vivos o el usuario actual
  return player.isAlive || isCurrentUser(player)
}

const handleVoteClick = (playerId: string) => {
  // Encontrar el jugador por ID
  const player = players.value.find(p => p.id === playerId)
  if (!player || !canVoteFor(player)) return

  try {
    castVote(playerId)

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
      detail: 'No se pudo registrar tu voto',
      life: 3000
    })
  }
}

const showPlayerMenu = (event: Event, player: Player) => {
  selectedPlayer.value = player
  playerContextMenu.value.show(event)
}

const toggleView = () => {
  isCompactView.value = !isCompactView.value
}
</script>

<style scoped>
.players-grid {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.player-stats {
  display: flex;
  gap: 0.5rem;
}

.players-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.player-card-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  transition: all 0.2s ease;
  background: white;
}

.player-card-item:hover {
  border-color: var(--primary-200);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.player-card-item.current-user {
  border-color: var(--blue-500);
  background: var(--blue-50);
}

.player-card-item.player-dead {
  opacity: 0.7;
  background: var(--surface-100);
}

.player-card-item.player-disconnected {
  border-style: dashed;
  opacity: 0.6;
}

.player-card-item.voted-for {
  border-color: var(--green-500);
  background: var(--green-50);
}

.player-card-item.votable {
  cursor: pointer;
  border-color: var(--orange-300);
}

.player-card-item.votable:hover {
  border-color: var(--orange-500);
  background: var(--orange-50);
}

.player-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar-badges {
  position: absolute;
  top: -4px;
  right: -4px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.connection-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.connection-indicator.connected {
  background: #10b981;
}

.connection-indicator.disconnected {
  background: #ef4444;
}

.death-indicator {
  font-size: 0.75rem;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.player-info {
  flex: 1;
  min-width: 0;
}

.player-name {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.current-user-badge {
  font-size: 0.75rem;
  color: var(--blue-600);
  font-weight: 500;
}

.player-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.vital-status {
  font-size: 0.875rem;
}

.status-alive {
  color: var(--green-600);
}

.status-dead {
  color: var(--red-600);
}

.player-role {
  font-size: 0.875rem;
  color: var(--purple-600);
  font-weight: 500;
}

.voting-info {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.voted-status {
  color: var(--green-600);
}

.vote-count {
  color: var(--orange-600);
}

.player-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.view-controls {
  display: flex;
  justify-content: center;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

/* Vista compacta */
.players-container.compact {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

.compact .player-card-item {
  padding: 0.75rem;
}

.compact .player-name {
  font-size: 0.875rem;
}

.compact .player-details {
  font-size: 0.75rem;
}

@media (max-width: 768px) {
  .players-container {
    grid-template-columns: 1fr;
  }

  .grid-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .player-card-item {
    padding: 0.75rem;
  }
}
</style>
