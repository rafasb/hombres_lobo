<template>
  <div class="games-container">
    <!-- Navegación simple -->
    <nav class="games-nav">
      <button class="nav-btn" @click="navigateToGames" :class="{ active: true }">
        🎮 Partidas
      </button>
      <button class="nav-btn" @click="navigateToProfile">
        👤 Perfil
      </button>
      <button v-if="auth.isAdmin" class="nav-btn" @click="navigateToAdmin">
        ⚙️ Admin
      </button>
    </nav>

    <header class="games-header">
      <h1>Partidas Disponibles</h1>
      <button class="btn-create-game" @click="openCreateModal">
        <span class="btn-icon">+</span>
        Crear Partida
      </button>
    </header>

    <!-- Lista de partidas -->
    <div class="games-grid" v-if="hasGames">
      <div 
        class="game-card" 
        v-for="game in games" 
        :key="game.id"
        :class="getGameCardClass(game.status)"
      >
        <div class="game-header">
          <h3 class="game-title">{{ game.name }}</h3>
          <span class="game-status" :class="'status-' + game.status">
            {{ getStatusText(game.status) }}
          </span>
        </div>
        
        <div class="game-info">
          <div class="game-detail">
            <span class="detail-label">Jugadores:</span>
            <span class="detail-value">{{ game.players.length }}/{{ game.max_players }}</span>
          </div>
          
          <div class="game-detail">
            <span class="detail-label">Creador:</span>
            <span class="detail-value">{{ getCreatorName(game) }}</span>
          </div>
          
          <div class="game-detail">
            <span class="detail-label">Creada:</span>
            <span class="detail-value">{{ formatDate(game.created_at) }}</span>
          </div>
          
          <div class="game-detail" v-if="game.status !== 'waiting'">
            <span class="detail-label">Ronda:</span>
            <span class="detail-value">{{ game.current_round }}</span>
          </div>
        </div>
        
        <div class="game-actions">
          <button 
            v-if="canJoinGame(game)" 
            class="btn btn-join"
            @click="joinGame(game.id)"
            :disabled="loading"
          >
            Unirse
          </button>
          
          <button 
            v-if="canLeaveGame(game)" 
            class="btn btn-leave"
            @click="leaveGame(game.id)"
            :disabled="loading"
          >
            Abandonar
          </button>
          
          <button 
            v-if="canViewGame(game)" 
            class="btn btn-view"
            @click="viewGame(game.id)"
          >
            Ver Partida
          </button>
          
          <button 
            v-if="canDeleteGame(game)" 
            class="btn btn-delete"
            @click="deleteGame(game.id)"
            :disabled="loading"
          >
            🗑️ Eliminar
          </button>
        </div>
      </div>
    </div>
    
    <div class="empty-state" v-else-if="!loading">
      <p>No hay partidas disponibles</p>
      <button class="btn-create-game" @click="openCreateModal">
        Crear la primera partida
      </button>
    </div>
    
    <div class="loading-state" v-if="loading">
      <p>Cargando partidas...</p>
    </div>

    <!-- Modal para crear partida -->
    <CreateGameModal
      v-if="showCreateModal"
      :gameData="newGame"
      :playerOptions="playerOptions"
      :loading="loading"
      @close="closeCreateModal"
      @create="createGame"
      @update:gameData="updateNewGame"
    />

    <!-- Mensajes de error/éxito -->
    <div class="notification" v-if="notification" :class="notification.type">
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import CreateGameModal from '../components/CreateGameModal.vue'

// Props para recibir los datos y métodos del composable
interface Props {
  games: any[]
  loading: boolean
  showCreateModal: boolean
  notification: any
  newGame: any
  playerOptions: number[]
  hasGames: boolean
  auth: any
  canJoinGame: (game: any) => boolean
  canLeaveGame: (game: any) => boolean
  canViewGame: (game: any) => boolean
  canDeleteGame: (game: any) => boolean
  getCreatorName: (game: any) => string
  getStatusText: (status: string) => string
  getGameCardClass: (status: string) => string
  formatDate: (dateString: string) => string
}

interface Emits {
  (e: 'createGame'): void
  (e: 'joinGame', gameId: string): void
  (e: 'leaveGame', gameId: string): void
  (e: 'deleteGame', gameId: string): void
  (e: 'viewGame', gameId: string): void
  (e: 'closeCreateModal'): void
  (e: 'openCreateModal'): void
  (e: 'navigateToProfile'): void
  (e: 'navigateToAdmin'): void
  (e: 'navigateToGames'): void
  (e: 'updateNewGame', value: any): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

// Métodos que emiten eventos al padre
const createGame = () => emit('createGame')
const joinGame = (gameId: string) => emit('joinGame', gameId)
const leaveGame = (gameId: string) => emit('leaveGame', gameId)
const deleteGame = (gameId: string) => emit('deleteGame', gameId)
const viewGame = (gameId: string) => emit('viewGame', gameId)
const closeCreateModal = () => emit('closeCreateModal')
const openCreateModal = () => emit('openCreateModal')
const navigateToProfile = () => emit('navigateToProfile')
const navigateToAdmin = () => emit('navigateToAdmin')
const navigateToGames = () => emit('navigateToGames')
const updateNewGame = (value: any) => emit('updateNewGame', value)
</script>
